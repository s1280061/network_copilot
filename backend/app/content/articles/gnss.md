---
slug: gnss
title: GPS/GNSS（全球測位システム）と自動車への応用
level: 2
category: Wireless
related: [wireless-basics, v2x-wireless, lte-5g, automotive-electrical]
next: []
tags: [gps, gnss, positioning, navigation, automotive, wireless]
---

## 概要
GNSS（Global Navigation Satellite System）はGPS・GLONASS・Galileo・みちびきなどの衛星測位システムの総称です。カーナビゲーション・自動運転・タクシー配車・緊急通報（eCall）に不可欠です。「なぜGPSは位置がわかるのか」を電波と時間の物理から理解しましょう。

## GPSの測位原理

$$d_i = c \times (t_{receive} - t_{send_i})$$

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

c = 3e8   # 光速 [m/s]

# GPS の仕組み: 4つ以上の衛星からの距離で位置を特定（三辺測量）
def gps_trilateration(sat_positions, measured_distances):
    """
    衛星位置と測定距離から受信機の位置を計算（2D簡易版）
    sat_positions: [(x1,y1), (x2,y2), (x3,y3)]
    measured_distances: [d1, d2, d3]
    """
    def equations(pos):
        x, y = pos
        eqs = []
        for (sx, sy), d in zip(sat_positions, measured_distances):
            eqs.append((x-sx)**2 + (y-sy)**2 - d**2)
        return eqs[:2]   # 2次元なら2つの方程式

    result = fsolve(equations, [0, 0])
    return result

# 例: 3衛星から測位
sats = [(0, 40000), (35000, 0), (-35000, 0)]  # 単位: km（地上から約20000km）
receiver_true = (100, 200)  # 真の位置 [km]

# 各衛星からの真の距離
true_dists = [np.sqrt((receiver_true[0]-sx)**2 + (receiver_true[1]-sy)**2)
              for sx, sy in sats]

# ノイズを加えた擬似距離（実際はクロック誤差が主因）
noise = np.random.normal(0, 1, 3)  # ±1km のノイズ
meas_dists = [d + n for d, n in zip(true_dists, noise)]

est_pos = gps_trilateration(sats, meas_dists)
error = np.sqrt((est_pos[0]-receiver_true[0])**2 + (est_pos[1]-receiver_true[1])**2)
print(f"真の位置:   ({receiver_true[0]:.1f}, {receiver_true[1]:.1f}) km")
print(f"推定位置:   ({est_pos[0]:.1f}, {est_pos[1]:.1f}) km")
print(f"測位誤差:   {error:.2f} km")
```

## GNSS の種類と精度

```python
gnss_systems = {
    "GPS（米国）": {
        "衛星数": 31,
        "軌道高度_km": 20200,
        "周波数": "L1=1575.42MHz, L2=1227.60MHz",
        "精度_m": 3,
        "状況": "民間 SA廃止（2000年〜）",
    },
    "GLONASS（ロシア）": {
        "衛星数": 24,
        "軌道高度_km": 19100,
        "周波数": "L1=1598.0625〜1605.375MHz（FDMA）",
        "精度_m": 4,
        "状況": "軍事・民間併用",
    },
    "Galileo（EU）": {
        "衛星数": 30,
        "軌道高度_km": 23222,
        "周波数": "E1=1575.42MHz, E5=1176.45MHz",
        "精度_m": 1,
        "状況": "2016〜運用開始",
    },
    "BeiDou（中国）": {
        "衛星数": 35,
        "軌道高度_km": 21528,
        "周波数": "B1=1561.098MHz",
        "精度_m": 2.5,
        "状況": "2020全面運用",
    },
    "みちびき（日本）": {
        "衛星数": 4,
        "軌道高度_km": 32000,
        "周波数": "L1=1575.42MHz（GPS補完）",
        "精度_m": 0.01,
        "状況": "準天頂軌道・高精度（cm級）",
    },
}

print(f"{'システム':18s} {'衛星数':6s} {'精度':6s} {'備考'}")
print("-" * 60)
for name, spec in gnss_systems.items():
    print(f"{name:18s} {spec['衛星数']:4d}機  {spec['精度_m']:4.2f}m  {spec['状況']}")
```

## 測位精度向上の技術

```python
# DGNSS / RTK の仕組み
accuracy_methods = {
    "単独測位（GPS単体）": {
        "精度": "3〜5m",
        "原理": "衛星4個以上から三辺測量",
        "用途": "カーナビ・スマートフォン",
    },
    "SBAS（衛星航法補強）": {
        "精度": "1〜2m",
        "原理": "地上局が誤差を計算→静止衛星で補正信号を配信",
        "用途": "航空・高精度ナビ（MSAS: 日本版SBAS）",
    },
    "DGNSS（差分測位）": {
        "精度": "0.5〜1m",
        "原理": "既知位置の基準局との差分補正",
        "用途": "測量・建設機械・農業機械",
    },
    "RTK（リアルタイムキネマティック）": {
        "精度": "1〜2cm",
        "原理": "搬送波位相を使った高精度測位",
        "用途": "測量・精密農業・自動運転",
    },
    "みちびき（CLAS）": {
        "精度": "6cm",
        "原理": "衛星補強信号 + みちびき補強",
        "用途": "自動運転・農業・ドローン（日本全国）",
    },
}

for method, spec in accuracy_methods.items():
    print(f"【{method}】")
    print(f"  精度: {spec['精度']}  原理: {spec['原理']}")
    print(f"  用途: {spec['用途']}")
    print()
```

## 自動車へのGNSS応用

```python
import datetime

# eCall（欧州義務化の緊急通報システム）
def ecall_message(lat, lon, speed_kmh, heading_deg, timestamp):
    """MSD（Minimum Set of Data）: 事故時に自動送信"""
    return {
        "messageIdentifier": 1,
        "control": {
            "automaticActivation": True,  # 自動起動 or 手動
            "testCall": False,
        },
        "vehicleIdentificationNumber": "JH4DA9350MS017849",
        "vehicleType": "passenger_car",
        "timestamp": timestamp.isoformat(),
        "vehicleLocation": {
            "latitude":  lat,
            "longitude": lon,
            "positionCanBeTrusted": True,
        },
        "vehicleDirection": heading_deg,
        "recentVehicleLocationN1": {"latitude": lat - 0.001, "longitude": lon},
        "numberOfPassengers": 2,
    }

import json
msg = ecall_message(35.6812, 139.7671, 0, 90,
                    datetime.datetime(2024, 3, 15, 14, 30, 0))
print("eCall MSD（事故時緊急通報）:")
print(json.dumps(msg, indent=2, ensure_ascii=False))

# 自動運転での精度要件
print("\n自動運転の測位精度要件:")
requirements = {
    "一般道（レーン維持）":      "< 0.1m（10cm）",
    "高速道路（車線変更）":      "< 0.5m",
    "駐車場（自動駐車）":        "< 0.02m（2cm）",
    "歩行者認識回避（法的）":   "位置確定 + センサーフュージョン",
}
for scenario, req in requirements.items():
    print(f"  {scenario:24s}: {req}")

print("\n→ GNSS単体では不足 → LiDAR/カメラ/HDMAPと融合（センサーフュージョン）が必須")
```
