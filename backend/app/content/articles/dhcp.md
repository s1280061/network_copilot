---
slug: dhcp
title: DHCP
level: 2
category: TCP/IP
difficulty: 中級
related: [ip, subnet, dns]
next: [dns]
tags: [l3]
---

## 概要
DHCP(Dynamic Host Configuration Protocol)は、機器に [[ip]] アドレスやサブネットマスク、ゲートウェイ、DNSサーバなどのネットワーク設定を自動で配布する仕組みです。手動設定の手間とミスを無くします。

## なぜ必要か
多数の機器に一つずつIPを手で設定するのは現実的ではありません。DHCPサーバが空きアドレスを貸し出すことで、機器は接続するだけでネットワークに参加できます。

## 自動運転での利用例
車載ネットワークでは多くのECUが固定IP(静的設定)を使いますが、診断ツールの接続やインフォテインメント機器など、動的にIPを割り当てたい場面でDHCPが利用されます。

## 関連用語
配布対象が [[ip]]、区切りの概念が [[subnet]]、名前解決が [[dns]] です。

## 次に学ぶべき内容
名前からIPを引く [[dns]] を学びましょう。
