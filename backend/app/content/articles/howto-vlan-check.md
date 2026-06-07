---
slug: howto-vlan-check
title: WiresharkでVLANタグを確認する
level: 2
category: Howto
difficulty: 初級
related: [vlan, wireshark, ethernet, tshark]
next: [howto-tshark-filter]
tags: [howto, tool, vlan, ethernet]
---

## やること
車載EthernetのキャプチャデータにVLANタグ(IEEE 802.1Q)が含まれているかをWiresharkで確認し、VLANごとにトラフィックを分離して解析する手順を説明します。

## 前提条件
- Wiresharkインストール済み
- VLANタグ付きトラフィックのpcapファイル、またはトランクポートへの接続

## ステップ1: VLANタグを確認する

pcapを開いてパケットを選択し、下部の詳細ペインを確認します：

```
Ethernet II
  ▶ 802.1Q Virtual LAN, PRI: 0, DEI: 0, ID: 10
      VLAN ID: 10
      Type: IPv4
```

`802.1Q Virtual LAN` の行があればVLANタグ付きです。

## ステップ2: VLAN IDでフィルタ

```
# VLAN 10 のパケットだけ表示
vlan.id == 10

# VLAN 20 かつ SOME/IP
vlan.id == 20 && someip

# VLANタグ付きパケット全体
vlan
```

## ステップ3: 複数VLANの通信量を比較

`Statistics` → `IO Graph` を開いて：

- グラフ1: フィルタ `vlan.id == 10` (ADASドメイン)
- グラフ2: フィルタ `vlan.id == 20` (IVIドメイン)

時系列で各ドメインのトラフィック量を比較できます。

## ステップ4: tsharkでVLAN IDを一覧化

```bash
# pcap内の全VLAN IDを集計
tshark -r capture.pcap -Y "vlan" \
  -T fields -e vlan.id | sort | uniq -c | sort -rn

# 出力例:
# 1523  10
#  487  20
#   34  30
```

## VLANが見えない場合

キャプチャポイントがアクセスポート(タグなし)の場合、VLANタグは除去されています。VLANタグを観測するにはスイッチのトランクポート(タグ付きポート)かミラーポートに接続してキャプチャする必要があります。

## 車載での典型的なVLAN構成

| VLAN ID | ドメイン |
|---------|---------|
| 10 | ADASカメラ・LiDAR |
| 20 | インフォテインメント(IVI) |
| 30 | 診断(DoIP) |
| 99 | 管理用 |

各ドメインが混在していないかをWiresharkで確認することがセキュリティ監査の第一歩です。

## 関連用語
VLANの概念は [[vlan]]、Wiresharkの基本は [[wireshark]]、高度なフィルタは [[howto-tshark-filter]] を参照。
