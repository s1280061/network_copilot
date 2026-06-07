---
slug: tshark
title: tshark
level: 3
category: PCAP
difficulty: 中級
related: [wireshark, tcpdump, pcap]
next: [doip]
tags: [tool, cli]
---

## 概要
tsharkは、[[wireshark]] のコマンドライン版です。Wiresharkと同じ強力なプロトコル解析(ディセクタ)を持ちつつ、CLIで動くため自動化やバッチ処理に向いています。表示フィルタで欲しい情報だけを抽出できます。

## なぜ必要か
[[wireshark]] のGUIは対話的解析に最適ですが、大量の [[pcap]] を機械的に処理したり、CI/テストに組み込むにはCLIが必要です。tsharkはWireshark並の解析力をスクリプトから使えます。

## 自動運転での利用例
回帰テストで「採取したPCAPにSOME/IPのエラーが含まれていないか」を tshark のフィルタで自動チェックする、といった使い方ができます。例えば SOME/IP のメッセージ種別だけを抽出して集計する処理を自動化できます。

## 関連用語
GUI版が [[wireshark]]、軽量キャプチャが [[tcpdump]]、対象ファイルが [[pcap]] です。

## 次に学ぶべき内容
車載診断通信 [[doip]] を学びましょう。
