---
slug: wifi
title: Wi-Fi（IEEE 802.11）の仕組みと規格
level: 2
category: Wireless
related: [wireless-basics, bluetooth, lte-5g, ethernet]
next: []
tags: [wifi, ieee80211, wireless-lan, 802.11ax, ofdm, networking]
---

## 概要
Wi-Fi（IEEE 802.11）は世界中で使われている無線LAN規格です。「なぜ5GHzは速いが繋がりにくいのか」「Wi-Fi 6は何が違うのか」を物理層から理解しましょう。車載では駐車場の地図更新・ディーラーでの診断・路車間通信の補助に使われます。

## Wi-Fi 規格の進化

```python
import numpy as np

wifi_standards = {
    "Wi-Fi 1（802.11b）": {"year": 1999, "band": "2.4GHz", "max_mbps": 11,    "tech": "DSSS"},
    "Wi-Fi 2（802.11a）": {"year": 1999, "band": "5GHz",   "max_mbps": 54,    "tech": "OFDM"},
    "Wi-Fi 3（802.11g）": {"year": 2003, "band": "2.4GHz", "max_mbps": 54,    "tech": "OFDM"},
    "Wi-Fi 4（802.11n）": {"year": 2009, "band": "2.4/5GHz","max_mbps": 600,   "tech": "MIMO+OFDM"},
    "Wi-Fi 5（802.11ac）":{"year": 2013, "band": "5GHz",   "max_mbps": 6934,  "tech": "MU-MIMO+256QAM"},
    "Wi-Fi 6（802.11ax）":{"year": 2019, "band": "2.4/5GHz","max_mbps": 9608,  "tech": "OFDMA+1024QAM"},
    "Wi-Fi 6E":          {"year": 2021, "band": "6GHz",    "max_mbps": 9608,  "tech": "Wi-Fi 6 + 6GHz"},
    "Wi-Fi 7（802.11be）":{"year": 2024, "band": "2.4/5/6GHz","max_mbps": 46120,"tech": "MLO+4096QAM"},
}

print(f"{'規格':22s} {'年':5s} {'周波数帯':10s} {'最大速度':10s} {'技術'}")
print("-" * 75)
for name, spec in wifi_standards.items():
    print(f"{name:22s} {spec['year']:4d}  {spec['band']:10s} {spec['max_mbps']:6d} Mbps  {spec['tech']}")
```

## OFDM（直交周波数分割多重）

Wi-Fiの高速化を支える変調技術：

```python
import matplotlib.pyplot as plt

# OFDMは複数のサブキャリアに並列でデータを乗せる
n_subcarriers = 52   # 802.11g の場合（データ用48 + パイロット4）
bandwidth = 20e6     # 20MHz チャンネル
subcarrier_spacing = bandwidth / 64   # 312.5kHz

t = np.linspace(0, 4e-6, 1000)   # 1シンボル期間（4μs）

fig, ax = plt.subplots(figsize=(12, 5))
for i in range(0, 12):   # 最初の12サブキャリアを可視化
    f_sub = (i + 1) * subcarrier_spacing
    phase = np.random.choice([0, np.pi/2, np.pi, 3*np.pi/2])  # QPSK
    wave  = np.cos(2 * np.pi * f_sub * t + phase) * 0.3
    ax.plot(t * 1e6, wave + i, alpha=0.7, lw=1)
ax.set_xlabel("時間 [μs]")
ax.set_ylabel("サブキャリア番号")
ax.set_title("OFDM: 複数のサブキャリアが直交して並列送信")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# データレートの計算
def wifi_data_rate(n_subcarriers, bits_per_symbol, coding_rate, n_streams, symbol_duration_us):
    """Wi-Fiの理論データレート計算"""
    symbols_per_second = 1e6 / symbol_duration_us
    bits_per_ofdm_symbol = n_subcarriers * bits_per_symbol * coding_rate * n_streams
    return bits_per_ofdm_symbol * symbols_per_second / 1e6  # Mbps

# Wi-Fi 5（802.11ac, 80MHz ch, 256QAM, 3/4コーディング, 1ストリーム）
rate = wifi_data_rate(234, 8, 3/4, 1, 3.6)  # 8bits=256QAM
print(f"Wi-Fi 5（80MHz, 1stream）: {rate:.0f} Mbps")

# Wi-Fi 6（802.11ax, 80MHz ch, 1024QAM, 5/6コーディング, 1ストリーム）
rate6 = wifi_data_rate(234, 10, 5/6, 1, 13.6)  # 10bits=1024QAM
print(f"Wi-Fi 6（80MHz, 1stream）: {rate6:.0f} Mbps")
```

## 2.4GHz vs 5GHz の特性

```python
import math

c = 3e8

def compare_bands():
    bands = {
        "2.4GHz（ch1: 2412MHz）": {
            "freq": 2412e6,
            "channels": 3,       # 非重複チャンネル数（日本）
            "wall_penetration": "良好",
            "interference": "多い（電子レンジ・Bluetoothと干渉）",
            "range": "広い（〜100m屋内）",
        },
        "5GHz（ch36〜）": {
            "freq": 5180e6,
            "channels": 19,      # W52/W53/W56
            "wall_penetration": "やや苦手（減衰大きい）",
            "interference": "少ない（専用帯域が多い）",
            "range": "狭い（〜50m屋内）",
        },
        "6GHz（Wi-Fi 6E）": {
            "freq": 5945e6,
            "channels": 59,      # 最大
            "wall_penetration": "苦手（新規格）",
            "interference": "ほぼなし（新規割当帯域）",
            "range": "短め（〜30m屋内）",
        },
    }

    for band, props in bands.items():
        lam = c / props["freq"]
        print(f"\n【{band}】")
        print(f"  波長:       {lam*100:.1f} cm")
        print(f"  非重複ch数: {props['channels']} ch")
        print(f"  壁越え:     {props['wall_penetration']}")
        print(f"  干渉:       {props['interference']}")
        print(f"  到達距離:   {props['range']}")

compare_bands()
```

## MIMOとビームフォーミング

```python
# MIMO: Multiple Input Multiple Output
# 複数のアンテナで同時に複数ストリームを送受信

def mimo_capacity(n_tx, n_rx, snr_dB, bandwidth_Hz):
    """MIMO通信容量の概算（並列チャンネル数 = min(Tx,Rx)）"""
    n_streams = min(n_tx, n_rx)
    snr_linear = 10 ** (snr_dB / 10)
    # 各ストリームがSNR/n_streams を使うと仮定
    snr_per_stream = snr_linear / n_streams
    C = bandwidth_Hz * n_streams * np.log2(1 + snr_per_stream)
    return C / 1e6   # Mbps

snr = 25   # dB
bw = 80e6  # 80MHz
print("MIMO構成ごとの通信容量（80MHz, SNR=25dB）:")
for n in [1, 2, 4, 8]:
    C = mimo_capacity(n, n, snr, bw)
    print(f"  {n}×{n} MIMO: {C:.0f} Mbps")

# Wi-Fi 6 の OFDMA（上り下りで複数デバイスを同時接続）
print("\nOFDMA（Wi-Fi 6の革新）:")
print("  Wi-Fi 5以前: 1つのデバイスが帯域を占有して送信（順番待ち）")
print("  Wi-Fi 6:    帯域を分割して複数デバイスを同時送信（OFDMA）")
print("  → 混雑環境（空港・スタジアム・車内）で特に効果大")
```

## 車載Wi-Fi（テレマティクス・OTA）

```python
# 自動車でのWi-Fi活用シーン
automotive_wifi = {
    "地図データOTA更新": {
        "データ量": "数GB〜20GB",
        "頻度": "月1〜4回",
        "接続先": "ディーラー駐車場 or 自宅Wi-Fi",
        "規格": "Wi-Fi 5/6（高速ダウンロード優先）",
    },
    "ECUソフトウェアOTA": {
        "データ量": "10MB〜数GB",
        "頻度": "年数回",
        "接続先": "ホームWi-Fi or セルラー（LTE/5G）",
        "規格": "Wi-Fi 5/6 または LTE",
    },
    "車内Wi-Fiホットスポット": {
        "データ量": "乗客のストリーミング",
        "接続先": "4G LTE回線をWi-Fiとして車内に提供",
        "規格": "Wi-Fi 5（車内）+ LTE（外部）",
    },
    "ディーラー診断": {
        "データ量": "診断データ・ログ転送",
        "接続先": "ディーラーのローカルネットワーク",
        "規格": "Wi-Fi 4/5 + 専用診断ツール",
    },
}

for scene, info in automotive_wifi.items():
    print(f"\n【{scene}】")
    for k, v in info.items():
        print(f"  {k}: {v}")
```
