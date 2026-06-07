---
slug: howto-wireshark-someip
title: WiresharkでSOME/IPを解析する
level: 3
category: Howto
difficulty: 中級
related: [wireshark, some-ip, udp, pcap]
next: [howto-tcpdump-capture]
tags: [howto, tool, some-ip]
---

## やること
Wiresharkを使って、車載EthernetのSOME/IPパケットを可視化・解析する手順を説明します。

## 前提条件
- Wireshark 4.x インストール済み
- 解析対象のpcapファイル、またはEthernetインターフェースへの接続

## ステップ1: SOME/IP ディセクタを有効化

Wiresharkは標準でSOME/IPに対応しています。

1. `Edit` → `Preferences` → `Protocols` → `SOMEIP` を開く
2. UDPポート **30490**（SOME/IP-SD）と任意のサービスポートを登録
3. `SOMEIP-SD` も同様に有効化

## ステップ2: キャプチャ or ファイルを開く

```
# pcapファイルを開く場合
File → Open → vehicle_capture.pcap

# ライブキャプチャの場合
Capture → Interfaces → 対象インターフェースを選択 → Start
```

## ステップ3: SOME/IP でフィルタ

Wireshark のフィルタバーに以下を入力：

```
someip
```

SD(サービスディスカバリ)だけ見たい場合：

```
someip.messageid == 0xffff8100
```

特定のService IDで絞り込む：

```
someip.serviceid == 0x1234
```

## ステップ4: パケット詳細を読む

パケットを選択すると下部に詳細が展開されます：

- **Service ID** — どのサービスか
- **Method ID** — メソッド呼び出し(0x0xxx) or イベント(0x8xxx)
- **Message Type** — REQUEST / RESPONSE / NOTIFICATION
- **Payload** — 実データ(16進数 + 型定義があれば自動デコード)

## ステップ5: 統計を確認

`Statistics` → `Endpoints` でECUごとの通信量を把握。  
`Statistics` → `IO Graph` でSOME/IPトラフィックの時系列変化を確認できます。

## よくあるトラブル

| 症状 | 確認ポイント |
|------|-------------|
| パケットが `UDP` のまま | ポート設定が未登録 |
| Payloadが読めない | SOME/IPの型定義(FIBEX/arxml)をインポートしていない |
| SDパケットだけ見える | サービスが起動していない — ECUの状態確認 |

## 関連用語
[[wireshark]] の基本操作、[[some-ip]] のプロトコル仕様、[[pcap]] ファイルの扱い方。
