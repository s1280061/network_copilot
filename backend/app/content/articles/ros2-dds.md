---
slug: ros2-dds
title: ROS2 DDS
level: 5
related: [some-ip, sdv, adas-comm, udp]
next: [sdv]
tags: [middleware, robotics]
---

## 概要
ROS2(Robot Operating System 2)は、ロボット・自動運転ソフト開発のフレームワークです。その通信基盤に **DDS(Data Distribution Service)** を採用し、Pub/Sub型でノード間がデータをやり取りします。リアルタイム性と分散性に優れます。

## なぜ必要か
自動運転ソフトは多数のモジュール(認識・計画・制御)が並行動作し、大量のデータを低遅延で共有する必要があります。DDSは発見・QoS制御・多対多通信を標準で備え、こうした要求に応えます。

## 自動運転での利用例
Autowareなどの自動運転スタックはROS2上で構築され、LiDAR点群やカメラ画像、車両状態をDDSで配信します。車載では [[some-ip]] とDDSが用途で使い分けられ、両者の橋渡し(ゲートウェイ)も検討されます。

## 関連用語
車載のサービス通信が [[some-ip]]、土台のトランスポートが [[udp]]、全体の潮流が [[sdv]] です。

## 次に学ぶべき内容
これらが向かう先、[[sdv]](ソフトウェア定義車両)を学びましょう。
