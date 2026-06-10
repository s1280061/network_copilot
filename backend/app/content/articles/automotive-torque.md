---
slug: automotive-torque
title: トルクと馬力（自動車工学の基礎）
level: 1
category: Automotive
related: [automotive-engine, automotive-transmission, electric-power]
next: [automotive-engine]
tags: [torque, horsepower, power, automotive, engine, mechanics]
---

## 概要
「トルク」と「馬力（出力）」は自動車の性能を語るうえで最も重要な2つの値です。カタログに必ず記載されていますが、その物理的な意味を正確に理解している人は少ないです。この2つを理解することでエンジン選択・EV設計・ギア比設計の根拠がわかります。

## トルクとは

トルクは「回転させる力のモーメント」です。

$$\tau = F \times r$$

- **τ**（タウ）：トルク [N·m（ニュートンメートル）]
- **F**：力 [N]
- **r**：腕の長さ（回転軸からの距離）[m]

```python
import numpy as np
import matplotlib.pyplot as plt

# トルクの感覚を掴む例
examples = {
    "ドアを開ける（端を押す, 80cm）": (20, 0.8),    # 20N × 0.8m
    "ドアを開ける（軸近くを押す, 5cm）": (20, 0.05), # 20N × 0.05m
    "ボルト締め（レンチ20cm, 50N）":  (50, 0.2),
    "インパクトレンチ":               (None, None),
    "軽自動車エンジン（最大）":        (None, None),
    "トラックエンジン（最大）":        (None, None),
}

print("トルクの具体例:")
print(f"  ドアノブ（端を押す）:  20N × 0.8m = {20*0.8} N·m")
print(f"  ドアノブ（軸近く）:    20N × 0.05m = {20*0.05} N·m  （4倍の力が必要！）")
print(f"  ボルト締め:           50N × 0.2m = {50*0.2} N·m")
print()

# 自動車エンジンのトルク
car_torques = {
    "軽自動車（NA 660cc）":    60,     # N·m
    "コンパクトカー（1.5L）": 130,
    "スポーツカー（2.0L）":   300,
    "SUV（3.5L）":            380,
    "大型トラック（6L）":    2000,
    "テスラ Model S Plaid":  1420,    # EV（モーター直接）
}
for name, torque in car_torques.items():
    print(f"  {name:25s}: {torque:5d} N·m")
```

## 出力（馬力）とトルクの関係

$$P = \tau \times \omega = \tau \times \frac{2\pi n}{60}$$

- **P**：出力 [W]
- **τ**：トルク [N·m]
- **ω**：角速度 [rad/s]
- **n**：回転数 [rpm]

```python
def power_from_torque(torque_Nm, rpm):
    """トルクと回転数から出力を計算"""
    omega = 2 * np.pi * rpm / 60
    power_W = torque_Nm * omega
    power_kW = power_W / 1000
    power_PS = power_kW / 0.7355   # 1PS = 0.7355kW（メートル馬力）
    return power_kW, power_PS

# 典型的なエンジン性能を計算
print("=== エンジン性能の計算 ===")
examples = [
    ("軽自動車（660cc）",    60,  5500),
    ("普通車（2.0L）",      200,  4000),
    ("スポーツカー（2.0L）", 400,  6000),
    ("大型トラック",        2000, 1500),
]
for name, torque, rpm in examples:
    kW, PS = power_from_torque(torque, rpm)
    print(f"  {name:22s}: {torque:4d} N·m × {rpm:4d} rpm = {kW:6.1f} kW ({PS:.0f} PS)")
```

## トルク曲線と出力曲線

```python
# エンジン特性カーブのシミュレーション（2.0L NAエンジン）
def engine_curves(rpm_range):
    """典型的なNA 2.0L エンジンのトルク・出力カーブ"""
    # トルクは中回転域でピーク
    torque = (
        150
        + 60 * np.exp(-((rpm_range - 3500) / 1500)**2)  # ピーク at 3500rpm
        - 20 * (rpm_range / 7000)**3                      # 高回転で低下
    )
    torque = np.clip(torque, 50, 220)
    power_kW = torque * 2 * np.pi * rpm_range / 60 / 1000
    return torque, power_kW

rpm_range = np.linspace(1000, 7000, 500)
torque, power = engine_curves(rpm_range)
power_PS = power / 0.7355

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()

ax1.plot(rpm_range, torque, "r-", lw=2, label="トルク [N·m]")
ax2.plot(rpm_range, power_PS, "b-", lw=2, label="出力 [PS]")

ax1.set_xlabel("エンジン回転数 [rpm]")
ax1.set_ylabel("トルク [N·m]", color="red")
ax2.set_ylabel("出力 [PS]", color="blue")
ax1.set_title("2.0L NAエンジン　トルク・出力カーブ")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
ax1.grid(True, alpha=0.4)
plt.show()

# 最大値
max_torque = torque.max()
max_power  = power_PS.max()
rpm_at_max_torque = rpm_range[torque.argmax()]
rpm_at_max_power  = rpm_range[power_PS.argmax()]
print(f"最大トルク: {max_torque:.0f} N·m at {rpm_at_max_torque:.0f} rpm")
print(f"最大出力:   {max_power:.0f} PS  at {rpm_at_max_power:.0f} rpm")
```

## EVのトルク特性（ガソリン車との違い）

```python
# EVモーターのトルク特性
def ev_torque_curve(rpm_range, T_max=400, rpm_base=3000, P_max_kW=150):
    """
    EVモーターの特性:
    - 定トルク領域（0〜rpm_base）: 最大トルクを維持
    - 定出力領域（rpm_base以上）: 出力一定でトルクが低下
    """
    torque = np.where(
        rpm_range <= rpm_base,
        T_max,
        P_max_kW * 1000 / (2 * np.pi * rpm_range / 60)  # P = T × ω
    )
    return torque

rpm = np.linspace(0, 10000, 500)
T_ev     = ev_torque_curve(rpm)
T_gas, _ = engine_curves(rpm)
P_ev = T_ev * 2 * np.pi * rpm / 60 / 1000

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].plot(rpm, T_ev,  "b-", lw=2, label="EV（永久磁石モーター）")
axes[0].plot(rpm, T_gas, "r-", lw=2, label="ガソリン2.0L NA")
axes[0].set_xlabel("回転数 [rpm]")
axes[0].set_ylabel("トルク [N·m]")
axes[0].set_title("トルク曲線比較")
axes[0].legend()
axes[0].grid(True, alpha=0.4)

axes[1].plot(rpm, P_ev / 0.7355, "b-", lw=2, label="EV")
axes[1].set_xlabel("回転数 [rpm]")
axes[1].set_ylabel("出力 [PS]")
axes[1].set_title("出力曲線（EV）")
axes[1].legend()
axes[1].grid(True, alpha=0.4)
plt.tight_layout()
plt.show()

print("\nEV vs ガソリン車のトルク特性の違い:")
print("  EV:    0rpmから最大トルク → 発進が強烈")
print("  ガソリン: 中回転域でトルクピーク → ギアで回転域を維持が必要")
```

## 駆動力と加速度

```python
def driving_force(torque_engine, gear_ratio, final_ratio, tire_radius, efficiency=0.9):
    """
    エンジントルクから車輪の駆動力を計算
    gear_ratio: 変速比, final_ratio: ファイナルギア比
    tire_radius: タイヤ半径 [m]
    """
    torque_wheel = torque_engine * gear_ratio * final_ratio * efficiency
    force = torque_wheel / tire_radius
    return force, torque_wheel

# 1速発進時の計算
m_car    = 1500   # 車両重量 [kg]
T_engine = 200    # エンジントルク [N·m]
gear1    = 3.5    # 1速変速比
final    = 4.0    # ファイナルギア比
r_tire   = 0.3    # タイヤ半径 [m]

F, T_wheel = driving_force(T_engine, gear1, final, r_tire)
a = F / m_car   # a = F/m

print(f"1速発進時の駆動力: {F:.0f} N")
print(f"車輪トルク:        {T_wheel:.0f} N·m")
print(f"加速度:            {a:.2f} m/s²")
print(f"0→100km/h 概算:    {100/3.6/a:.1f} 秒（空気抵抗・タイヤ滑り無視）")
```
