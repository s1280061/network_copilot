---
slug: lin
title: LIN バス
level: 2
category: Automotive Bus
difficulty: 初級
related: [can, can-fd, ethernet]
next: [can]
tags: [automotive, bus, l2]
---

## 概要
LIN(Local Interconnect Network)は、**低コスト**・低速な車載シリアルバスです。1本のワイヤで最大19.2 kbpsの通信を行い、**マスター/スレーブ**構成で動作します。CANより安価で、シート調整・ドアミラー・ワイパーなどシンプルな制御に使われます。

## なぜ必要か
CANは信頼性が高い反面、トランシーバーや配線コストが高めです。LINは**シングルワイヤ**で12V電源ラインを使い回せるため、費用対効果の高い補助バスとして普及しました。1台の車に40本以上のLINバスが搭載されることもあります。

## 仕組み
マスターECUがヘッダ(Break+Sync+ID)を送り、スレーブがIDに応じてレスポンスを返します。スレーブはアドレスを持たず、IDで自分への呼びかけを認識します。衝突検知機構はなく、マスターがスケジューリングを管理します。

## 自動運転での利用例
ADAS ECUが主カメラをEthernetで制御する一方、サイドミラーの角度調整モーターはLINで制御するという混在構成が一般的です。LINは帯域が低いため、センサデータの転送ではなくアクチュエータ制御に限定されます。

## 関連用語
帯域が必要な用途は [[can]] や [[ethernet]] へ移行します。高速化版として [[can-fd]] があります。

## 次に学ぶべき内容
より高速で信頼性の高い [[can]] へ進みましょう。

## 図解
```mermaid
sequenceDiagram
  participant M as マスターECU
  participant S1 as スレーブ1 (ミラーモーター)
  participant S2 as スレーブ2 (シート調整)
  M->>S1: ヘッダ (Break + Sync + ID=0x10)
  S1->>M: レスポンス (モーター角度データ)
  M->>S2: ヘッダ (ID=0x20)
  S2->>M: レスポンス (シート位置データ)
  Note over M: スケジュール管理はマスターのみ
```
