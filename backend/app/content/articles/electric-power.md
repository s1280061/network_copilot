---
slug: electric-power
title: 電力・電力量とジュール熱
level: 1
category: Electronics
related: [ohms-law, circuit-series-parallel, electricity-basics]
next: []
tags: [power, energy, joule-heat, watt, electronics]
---

## 概要
電力は「1秒あたりに消費するエネルギー」、電力量は「使ったエネルギーの合計」です。家電の消費電力・電池の持ち時間・抵抗の発熱量はすべてここで計算します。車載ECUの熱設計にも不可欠な知識です。

## 電力（P）

$$P = V \times I$$

- **P**：電力 [W（ワット）]
- **V**：電圧 [V]
- **I**：電流 [A]

オームの法則（V = RI）を代入すると3通りの式が導けます：

```
P = V × I         （電圧と電流がわかるとき）
P = I² × R        （電流と抵抗がわかるとき）
P = V² ÷ R        （電圧と抵抗がわかるとき）
```

```python
def calc_power(V=None, I=None, R=None):
    """V, I, R のうち2つから電力を計算"""
    if V is not None and I is not None:
        return V * I,    "P = V × I"
    if I is not None and R is not None:
        return I**2 * R, "P = I² × R"
    if V is not None and R is not None:
        return V**2 / R, "P = V² / R"

P, formula = calc_power(V=100, I=1.0)
print(f"P = {P} W  ({formula})")   # 100W の電球

P, formula = calc_power(I=5, R=2)
print(f"P = {P} W  ({formula})")   # 5A が 2Ω を流れる → 50W

P, formula = calc_power(V=12, R=4)
print(f"P = {P} W  ({formula})")   # 12V, 4Ω → 36W
```

## 電力量（W·h、J）

電力量は「電力 × 時間」で求まります。

$$W = P \times t$$

```python
# 電力量の計算
def calc_energy_kwh(power_W, hours):
    """消費電力量 [kWh]"""
    return power_W * hours / 1000

# 家電の1日あたりの電力量
appliances = {
    "エアコン（冷房）":  (700,  8),   # 700W × 8時間
    "冷蔵庫":          (150, 24),
    "LED電球":          (10,   5),
    "ノートPC":        (50,   6),
    "スマホ充電":       (10,   1),
}

total = 0
for name, (W, h) in appliances.items():
    kwh = calc_energy_kwh(W, h)
    total += kwh
    print(f"{name:18s}: {W:4d}W × {h:2d}h = {kwh:.3f} kWh")
print(f"\n1日の合計: {total:.3f} kWh")
print(f"電気代（30円/kWh）: {total*30:.0f} 円/日")
```

## ジュール熱

電流が抵抗を流れるとき、電気エネルギーが**熱**に変わります。これをジュール熱といいます。

$$Q = I^2 \times R \times t = P \times t$$

```python
import numpy as np
import matplotlib.pyplot as plt

# 抵抗の発熱量シミュレーション
def joule_heat(I, R, t_seconds):
    """発熱量 [J] と温度上昇の概算"""
    Q = I**2 * R * t_seconds
    return Q

# ECU基板の抵抗（1Ω, 100mA）が10分間発熱すると？
I, R, t = 0.1, 1, 600   # 100mA, 1Ω, 600秒
Q = joule_heat(I, R, t)
print(f"発熱量: {Q} J")

# ヒューズが切れる仕組み
# ヒューズは一定以上の電流で溶けるように設計
fuse_ratings = {
    "5A ヒューズ":  5,
    "10A ヒューズ": 10,
    "20A ヒューズ": 20,
}
R_fuse = 0.01   # ヒューズ抵抗 10mΩ
for name, I_rated in fuse_ratings.items():
    P = I_rated**2 * R_fuse
    print(f"{name}: 定格電力 = {P:.2f} W")
```

## 電池の持ち時間

```python
def battery_life(capacity_mAh, current_mA, efficiency=0.8):
    """
    電池容量と消費電流から持ち時間を計算
    efficiency: 取り出せるエネルギーの割合（80%が一般的）
    """
    hours = (capacity_mAh * efficiency) / current_mA
    return hours

# スマートフォン（4000mAh）のバッテリー持ち
scenarios = {
    "スタンバイ（10mA）":        10,
    "通常使用（200mA）":        200,
    "動画視聴（500mA）":        500,
    "高負荷ゲーム（1000mA）": 1000,
}
cap = 4000   # mAh

for scenario, I_mA in scenarios.items():
    h = battery_life(cap, I_mA)
    print(f"{scenario:25s}: {h:.1f} 時間")

# 車載ECU（12V, 50mAh 待機電流）
# 1ヶ月放置するとバッテリーに与える影響
I_ecus_total = 50    # mA（暗電流）
days = 30
charge_consumed = I_ecus_total * 24 * days / 1000   # Ah
print(f"\n30日間の暗電流消費: {charge_consumed:.1f} Ah")
print(f"60Ah バッテリーへの影響: {charge_consumed/60*100:.1f}%")
```

## 電力の単位変換まとめ

```python
# 単位変換
def unit_summary():
    print("=== 電力の単位変換 ===")
    print("1 W  = 1 J/s （1秒に1ジュール消費）")
    print("1 kW = 1000 W")
    print("1 MW = 10⁶ W")
    print()
    print("=== 電力量の単位変換 ===")
    print("1 Wh  = 3600 J")
    print("1 kWh = 3.6 × 10⁶ J")
    print()
    print("=== 代表的な電力値 ===")
    examples = [
        ("LED電球",        "10 W"),
        ("白熱電球",        "100 W"),
        ("電子レンジ",      "1000 W = 1 kW"),
        ("エアコン（冷房）", "700〜2500 W"),
        ("電気自動車モーター","50〜200 kW"),
        ("原子力発電所",    "100万 kW = 1 GW"),
    ]
    for name, power in examples:
        print(f"  {name:20s}: {power}")

unit_summary()
```
