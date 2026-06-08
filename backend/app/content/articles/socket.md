---
slug: socket
title: Socket
level: 3
related: [port, tcp, udp, wireshark]
next: [wireshark]
tags: [api]
---

## 概要
ソケットは、IPアドレスとポート番号の組で表される「通信のエンドポイント(出入口)」であり、プログラムがネットワーク通信を行うためのAPIでもあります。アプリはソケットを開いてデータを読み書きします。

## なぜ必要か
OSやネットワークの複雑さを隠し、アプリ開発者が「ファイルの読み書き」に近い感覚で通信を扱えるようにするのがソケットです。TCP/UDP通信を実装する際の基本単位です。

## 自動運転での利用例
ECU上のアプリはUDP/TCPソケットを開いて他ECUと通信します。SOME/IPミドルウェアも内部ではソケットを使ってメッセージを送受信しています。

## 関連用語
ソケットは [[port]] と IP の組で表され、[[tcp]] / [[udp]] のどちらでも使えます。通信の中身を観測するには [[wireshark]] を使います。

## 次に学ぶべき内容
通信を実際に「見る」ためのツール、[[wireshark]] へ進みましょう。

## 図解
```mermaid
sequenceDiagram
  participant App as DoIPアプリ (クライアント)
  participant OS as OS ソケット層
  participant ECU as ゲートウェイECU
  App->>OS: socket() + connect(192.168.1.1:13400)
  OS->>ECU: TCP SYN
  ECU->>OS: SYN-ACK
  OS->>App: 接続完了
  App->>OS: send(UDSリクエスト)
  OS->>ECU: TCP DATA
  ECU->>OS: TCP DATA (UDS応答)
  OS->>App: recv() → 応答データ
```
