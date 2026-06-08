---
slug: wireshark
title: Wireshark
level: 3
related: [pcap, ethernet, ip]
next: [pcap]
tags: [tool]
---

## 概要
Wiresharkは、ネットワークを流れるパケットをキャプチャして可視化する定番の解析ツールです。各パケットを [[osi]] の層ごとに分解し、Ethernet/IP/TCP/UDPの中身を人間が読める形で表示します。

## なぜ必要か
通信トラブルは「実際に何が流れているか」を見ないと解決できません。Wiresharkはフィルタリングや統計機能で、膨大なパケットから問題を絞り込めます。学習用にも、教科書の知識を実物で確認できる強力な手段です。

## 自動運転での利用例
車載Ethernetの開発・検証では、SOME/IPやDoIPの通信が仕様通りか、遅延や再送が無いかをWiresharkで確認します。キャプチャ結果は [[pcap]] ファイルとして保存・共有されます。

## 関連用語
キャプチャ結果の保存形式が [[pcap]]、解析対象の最下層が [[ethernet]] と [[ip]] です。

## 次に学ぶべき内容
キャプチャの保存形式であり、本アプリで解析できる [[pcap]] を学びましょう。

## 図解
```mermaid
graph LR
  ECU["車載ゲートウェイECU"] -->|Ethernet| PC["Wireshark
(診断ワークステーション)"]
  PC --> PL["パケット一覧
DoIP / SOME/IP / CAN"]
  PL --> PD["パケット詳細
プロトコル解析"]
  PD --> PB["バイト列
16進数生データ"]
```
