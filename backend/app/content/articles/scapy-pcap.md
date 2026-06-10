---
slug: scapy-pcap
title: ScapyによるPCAP解析
level: 3
category: PCAP
related: [scapy-basics, wireshark, tcpdump, pcap, scapy-automotive]
next: [scapy-automotive]
tags: [scapy, python, pcap, analysis, network]
---

## 概要
ScapyはPCAPファイルの読み書き・フィルタリング・統計集計・プロトコル解析をPythonコードで自動化できます。Wiresharkが手動の目視分析なら、Scapyは**バッチ処理・大量ファイルの自動解析**に強みがあります。

## なぜ使うか
数百MBのPCAPを毎日解析したい、特定パターンのパケットを抽出して集計したい、という場合はScapyのスクリプトが最適です。Wiresharkのエクスポート＋Excelより圧倒的に高速かつ再現性があります。

## PCAPの読み込み

```python
from scapy.all import rdpcap, PcapReader

# 全パケットを一括読み込み（小〜中規模）
pkts = rdpcap("capture.pcap")
print(f"総パケット数: {len(pkts)}")
print(f"最初のパケット: {pkts[0].summary()}")

# 大きなファイルはイテレータで省メモリ処理
with PcapReader("large.pcap") as reader:
    for i, pkt in enumerate(reader):
        if i >= 100:
            break
        print(pkt.summary())
```

## 基本的な統計を取る

```python
from scapy.all import rdpcap, IP, TCP, UDP, Ether
from collections import Counter
import pandas as pd

pkts = rdpcap("capture.pcap")

# プロトコル分布
protocols = Counter()
for pkt in pkts:
    if pkt.haslayer("IP"):
        if pkt.haslayer("TCP"):
            protocols["TCP"] += 1
        elif pkt.haslayer("UDP"):
            protocols["UDP"] += 1
        elif pkt.haslayer("ICMP"):
            protocols["ICMP"] += 1
        else:
            protocols["Other IP"] += 1
    elif pkt.haslayer("ARP"):
        protocols["ARP"] += 1
    else:
        protocols["Other"] += 1

print(pd.Series(protocols).sort_values(ascending=False))

# 送受信アドレスのトップ10
src_ips = Counter(pkt[IP].src for pkt in pkts if pkt.haslayer(IP))
dst_ips = Counter(pkt[IP].dst for pkt in pkts if pkt.haslayer(IP))
print("送信元 Top10:")
print(pd.Series(src_ips.most_common(10)))
```

## 通信ペアとフロー分析

```python
from collections import defaultdict

flows = defaultdict(lambda: {"count": 0, "bytes": 0})

for pkt in pkts:
    if pkt.haslayer(IP) and (pkt.haslayer(TCP) or pkt.haslayer(UDP)):
        layer = TCP if pkt.haslayer(TCP) else UDP
        key = (
            pkt[IP].src, pkt[layer].sport,
            pkt[IP].dst, pkt[layer].dport,
            "TCP" if pkt.haslayer(TCP) else "UDP",
        )
        flows[key]["count"] += 1
        flows[key]["bytes"] += len(pkt)

# DataFrame に変換して集計
df_flows = pd.DataFrame([
    {"src_ip": k[0], "sport": k[1], "dst_ip": k[2], "dport": k[3],
     "proto": k[4], "packets": v["count"], "bytes": v["bytes"]}
    for k, v in flows.items()
])

print(df_flows.sort_values("bytes", ascending=False).head(10))
```

## タイムスタンプを使った時系列分析

```python
import matplotlib.pyplot as plt
import numpy as np

# タイムスタンプと転送量を取得
timestamps = [float(pkt.time) for pkt in pkts if pkt.haslayer(IP)]
sizes      = [len(pkt) for pkt in pkts if pkt.haslayer(IP)]

if timestamps:
    t0  = min(timestamps)
    rel = [t - t0 for t in timestamps]

    # 1秒ごとのパケット数をカウント
    bins = np.arange(0, max(rel) + 1, 1.0)
    counts, edges = np.histogram(rel, bins=bins)

    fig, axes = plt.subplots(2, 1, figsize=(12, 6))
    axes[0].bar(edges[:-1], counts, width=0.9, color="steelblue")
    axes[0].set_xlabel("時刻（秒）")
    axes[0].set_ylabel("パケット数/秒")
    axes[0].set_title("パケット到着レート")

    # バイト数の時系列
    axes[1].scatter(rel, sizes, s=1, alpha=0.3, color="coral")
    axes[1].set_xlabel("時刻（秒）")
    axes[1].set_ylabel("パケットサイズ（バイト）")
    axes[1].set_title("パケットサイズの時系列")

    plt.tight_layout()
    plt.show()
```

## HTTPリクエスト/レスポンスを抽出する

```python
from scapy.all import TCP, Raw

def extract_http(pkts):
    requests  = []
    responses = []

    for pkt in pkts:
        if not (pkt.haslayer(TCP) and pkt.haslayer(Raw)):
            continue
        payload = pkt[Raw].load
        try:
            text = payload.decode("utf-8", errors="ignore")
        except Exception:
            continue

        if text.startswith(("GET ", "POST ", "PUT ", "DELETE ", "HEAD ")):
            lines  = text.split("\r\n")
            method, path, *_ = lines[0].split(" ", 2) + ["", ""]
            host   = next((l.split(": ")[1] for l in lines if l.startswith("Host:")), "")
            requests.append({
                "src": pkt[IP].src, "dst": pkt[IP].dst,
                "method": method, "host": host, "path": path,
            })
        elif text.startswith("HTTP/"):
            status = text.split("\r\n")[0]
            responses.append({"src": pkt[IP].src, "status": status})

    return pd.DataFrame(requests), pd.DataFrame(responses)

req_df, res_df = extract_http(pkts)
print(req_df.head())
```

## 異常パケットの検出

```python
anomalies = []

for pkt in pkts:
    reason = []

    # TTLが異常に低い
    if pkt.haslayer(IP) and pkt[IP].ttl < 5:
        reason.append(f"低TTL={pkt[IP].ttl}")

    # パケットサイズが極端に大きい
    if len(pkt) > 9000:
        reason.append(f"巨大パケット={len(pkt)}B")

    # TCPフラグの異常な組み合わせ（NULL/XMAS スキャン）
    if pkt.haslayer(TCP):
        flags = pkt[TCP].flags
        if flags == 0:
            reason.append("NULLスキャン疑い")
        if int(flags) == 0x29:  # FIN+PSH+URG
            reason.append("XMASスキャン疑い")

    if reason:
        anomalies.append({
            "time":   float(pkt.time),
            "src":    pkt[IP].src if pkt.haslayer(IP) else "N/A",
            "reason": " / ".join(reason),
        })

df_anomaly = pd.DataFrame(anomalies)
if not df_anomaly.empty:
    print(f"異常パケット: {len(df_anomaly)} 件")
    print(df_anomaly.head(10))
```

## PCAPの書き出しとフィルタリング

```python
from scapy.all import wrpcap

# 特定の条件でフィルタして保存
tcp_pkts  = [p for p in pkts if p.haslayer(TCP)]
http_pkts = [p for p in pkts if p.haslayer(TCP) and p.haslayer(Raw)
             and b"HTTP" in p[Raw].load]

wrpcap("tcp_only.pcap",  tcp_pkts)
wrpcap("http_only.pcap", http_pkts)
print(f"TCP: {len(tcp_pkts)}, HTTP: {len(http_pkts)} パケットを保存")
```

## 次に学ぶべき内容
車載通信（CAN/DoIP）の解析を [[scapy-automotive]] で学びましょう。
