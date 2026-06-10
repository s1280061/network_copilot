---
slug: bluetooth
title: Bluetooth（Classic/BLE）の仕組みと車載応用
level: 2
category: Wireless
related: [wireless-basics, wifi, lte-5g, v2x-wireless]
next: []
tags: [bluetooth, ble, bluetooth-le, automotive, wireless, pairing]
---

## 概要
BluetoothはIEEE 802.15.1を基にしたWPAN（無線個人エリアネットワーク）規格です。スマートフォンのハンズフリー通話・音楽ストリーミング・ワイヤレスイヤホン・車載診断ツールまで広く使われています。2.4GHz帯を周波数ホッピングで使うのが特徴です。

## Bluetooth Classic vs BLE の比較

```python
comparison = {
    "特性": ["最大速度", "通信距離", "消費電力", "接続確立時間", "主な用途"],
    "Bluetooth Classic": ["3 Mbps（EDR）", "10〜100m", "高め（連続通信）",
                          "〜3秒", "音声（HFP/A2DP）・データ"],
    "BLE（Bluetooth LE）": ["2 Mbps（BT5）", "50〜400m", "極低（間欠送信）",
                            "〜6ms（BT5）", "センサー・IoT・位置情報"],
}

for key in comparison["特性"]:
    i = comparison["特性"].index(key)
    classic = comparison["Bluetooth Classic"][i]
    ble = comparison["BLE（Bluetooth LE）"][i]
    print(f"{key:12s}: Classic={classic:25s} | BLE={ble}")
```

## 周波数ホッピング（FHSS）

```python
import numpy as np
import matplotlib.pyplot as plt

# Bluetooth は 2.4GHz 帯を 79 チャンネル（1MHz 間隔）に分割
# 1秒間に 1600回ホッピング（625μs ごと）

n_hops = 50
channels = np.arange(0, 79)
np.random.seed(42)
hop_sequence = np.random.choice(channels, n_hops, replace=False)

plt.figure(figsize=(12, 4))
plt.step(range(n_hops), hop_sequence, where="post", lw=1.5, color="steelblue")
plt.scatter(range(n_hops), hop_sequence, s=20, color="red", zorder=5)
plt.xlabel("時間（スロット番号 × 625μs）")
plt.ylabel("チャンネル番号（周波数）")
plt.title("Bluetoothの周波数ホッピング（FHSS）\n→ 干渉を受けても別チャンネルへ逃げられる")
plt.grid(True, alpha=0.3)
plt.show()

print("FHSSの利点:")
print("  ① Wi-Fi・電子レンジの干渉を回避")
print("  ② 盗聴が困難（どのチャンネルか予測困難）")
print("  ③ 複数のBluetoothデバイスが共存可能")
```

## BLEの通信フロー

```python
# BLEのアドバタイジング → スキャン → 接続フロー
ble_flow = """
BLE 接続確立フロー:

  デバイスA（Peripheral）         デバイスB（Central）
  例: タイヤ空気圧センサー        例: スマートフォン/車載ECU
      ↓
  [Advertising]                    [Scanning]
  広告パケット送信                  チャンネルをスキャン
  （37, 38, 39ch, 100ms間隔）
                    ────────────→
                     ADV_IND
                    ←────────────
                     SCAN_REQ       (Active Scan の場合)
                    ────────────→
                     SCAN_RSP
                    ←────────────
                     CONNECT_IND    接続要求
      ↓
  [Connection]                     [Connection]
  データチャンネルに移行（0〜36ch）
  Connection Interval: 7.5ms〜4000ms
"""
print(ble_flow)
```

## GATT（汎用属性プロファイル）

```python
# BLEのデータ構造: Profile > Service > Characteristic
ble_gatt = {
    "タイヤ空気圧センサー（TPMS）": {
        "Service UUID": "0x1816（Cycling Power）",
        "Characteristics": {
            "空気圧 [kPa]":   {"UUID": "0x2A6D", "Properties": "Notify", "format": "uint16"},
            "温度 [0.01°C]":  {"UUID": "0x2A1C", "Properties": "Notify", "format": "int16"},
            "バッテリー [%]":  {"UUID": "0x2A19", "Properties": "Read",   "format": "uint8"},
        }
    },
    "OBD2診断ドングル（BLE版）": {
        "Service UUID": "0xFFE0（カスタム）",
        "Characteristics": {
            "AT コマンド送信": {"UUID": "0xFFE1", "Properties": "Write", "format": "string"},
            "ECU レスポンス":  {"UUID": "0xFFE1", "Properties": "Notify","format": "string"},
        }
    },
}

for device, spec in ble_gatt.items():
    print(f"\n【{device}】")
    print(f"  Service: {spec['Service UUID']}")
    for char_name, char_spec in spec["Characteristics"].items():
        print(f"  {char_name:18s}: {char_spec['Properties']} | {char_spec['format']}")
```

## Bluetooth のプロファイルと車載応用

```python
profiles = {
    "HFP（Hands-Free Profile）":      "ハンズフリー通話（カーナビ・ステアリングスイッチ）",
    "A2DP（Advanced Audio Distribution）": "音楽ストリーミング（CD品質〜AAC/aptX）",
    "AVRCP（AV Remote Control）":     "再生/停止/曲送り（ステアリングボタン）",
    "SPP（Serial Port Profile）":     "シリアル通信エミュレーション（OBD2ドングル）",
    "PBAP（Phone Book Access）":      "連絡先取得（カーナビへ電話帳同期）",
    "MAP（Message Access）":          "SMS/メール読み上げ",
    "BLE TPMS":                       "タイヤ空気圧モニタリング（車載受信機）",
    "BLE キーレスエントリー（UWB補助）": "スマートフォンを車のキーとして使用",
    "BLE RSSI測位":                   "スマートパーキング・接近検知",
}

print("Bluetooth プロファイル一覧（車載関連）:")
for profile, usage in profiles.items():
    print(f"  {profile:40s}: {usage}")
```

## Bluetooth 5.x の新機能

```python
bt_versions = {
    "BT 4.0": {"year": 2010, "max_range": 50,  "max_speed_mbps": 1, "feature": "BLE導入"},
    "BT 4.2": {"year": 2014, "max_range": 50,  "max_speed_mbps": 1, "feature": "LE セキュア接続"},
    "BT 5.0": {"year": 2016, "max_range": 400, "max_speed_mbps": 2, "feature": "距離4倍・速度2倍"},
    "BT 5.1": {"year": 2019, "max_range": 400, "max_speed_mbps": 2, "feature": "方向探知（AoA/AoD）"},
    "BT 5.2": {"year": 2020, "max_range": 400, "max_speed_mbps": 2, "feature": "LE Audio（LC3コーデック）"},
    "BT 5.3": {"year": 2021, "max_range": 400, "max_speed_mbps": 2, "feature": "接続信頼性向上"},
    "BT 5.4": {"year": 2023, "max_range": 400, "max_speed_mbps": 2, "feature": "PAwR（広告型双方向）"},
}

print(f"{'バージョン':8s} {'年':5s} {'距離':8s} {'速度':8s} {'主要機能'}")
for v, spec in bt_versions.items():
    print(f"{v:8s} {spec['year']:4d}  {spec['max_range']:4d}m   {spec['max_speed_mbps']}Mbps   {spec['feature']}")

print("\nBT 5.1 AoA（到来角方向探知）→ 車の周囲 10cm 精度の位置検知 → 将来のデジタルキー")
```
