---
slug: tcpdump
title: tcpdump
level: 3
category: PCAP
difficulty: 中級
related: [pcap, wireshark, tshark]
next: [tshark]
tags: [tool, cli]
---

## 概要
tcpdumpは、コマンドラインでパケットをキャプチャ・表示する定番ツールです。GUIの [[wireshark]] と違い、サーバや組み込み機器など画面の無い環境でも動き、結果を [[pcap]] ファイルに保存できます。

## なぜ必要か
現場の機器に直接GUIを入れられないことは多々あります。tcpdumpなら `tcpdump -i eth0 -w capture.pcap` のように軽量にキャプチャでき、取得したファイルを後でWiresharkで詳細解析する、という流れが作れます。

## 自動運転での利用例
車載のLinuxベースECU(AUTOSAR Adaptiveなど)上でtcpdumpを動かし、SOME/IPやDoIPの通信を `.pcap` で採取します。採取データは本アプリのPCAP解析にもそのままアップロードできます。

## 関連用語
保存形式が [[pcap]]、GUI版が [[wireshark]]、Wireshark系CLIが [[tshark]] です。

## 次に学ぶべき内容
Wireshark由来のCLI [[tshark]] を学びましょう。
