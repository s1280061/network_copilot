---
slug: magnetism
title: 磁界・電磁力（フレミングの法則）
level: 2
category: Electronics
related: [electricity-basics, electromagnetic-induction, electric-field]
next: [electromagnetic-induction]
tags: [magnetism, magnetic-field, fleming, electronics, physics]
---

## 概要
電気と磁気は密接に関係しています。電流が流れると磁界が生まれ、磁界の中の電流は力を受けます（電磁力）。この原理がモーター・スピーカー・変圧器・MRIのすべての基盤です。車載システムではABSセンサーやEVのモーター制御に直結します。

```mermaid
graph LR
  I["電流 I"] --> B["磁場 B が発生"]
  B --> F["磁力 / ローレンツ力"]
  F --> U["モーター・スピーカー"]
```

## 磁界（磁場）

磁界の強さ **H** と磁束密度 **B** の関係：

$$B = \mu_0 \mu_r H$$

- **B**：磁束密度 [T（テスラ）]
- **μ₀**：真空の透磁率 = 4π × 10⁻⁷ H/m
- **μᵣ**：比透磁率（空気≒1, 鉄=数千〜数万）

```python
import numpy as np
import matplotlib.pyplot as plt

mu0 = 4 * np.pi * 1e-7   # 真空の透磁率

# 代表的な磁束密度
examples = {
    "地球の磁場":              50e-6,   # 50 μT
    "冷蔵庫マグネット":         5e-3,    # 5 mT
    "スピーカーの磁石":         1.0,
    "MRI（医療用）":            3.0,
    "超伝導マグネット":         20.0,
    "パルスマグネット（実験）": 100.0,
}
for name, B in examples.items():
    print(f"{name:22s}: {B:.3g} T")
```

## 直線電流の周りの磁界

電流 I が流れる長い直線導線の周りに生じる磁場：

$$B = \frac{\mu_0 I}{2\pi r}$$

```python
def B_wire(I, r):
    """直線電流 I から距離 r での磁束密度"""
    return mu0 * I / (2 * np.pi * r)

# 10A の電線から 1cm の距離
B = B_wire(I=10, r=0.01)
print(f"磁束密度: {B*1e6:.1f} μT")   # 200 μT

# 距離との関係
r_vals = np.linspace(0.5e-3, 20e-3, 200)
plt.figure(figsize=(8, 4))
for I in [1, 5, 10]:
    B_vals = B_wire(I, r_vals)
    plt.plot(r_vals * 100, B_vals * 1e3, label=f"I = {I} A")
plt.xlabel("距離 [cm]")
plt.ylabel("磁束密度 [mT]")
plt.title("直線電流周りの磁場（∝ 1/r）")
plt.legend()
plt.grid(True)
plt.show()
```

**数式で表すと**

$$
B = \frac{\mu_0 I}{2\pi r}
$$

直線電流 \(I\) [A] から距離 \(r\) [m] での磁束密度 \(B\) [T]。距離に反比例して弱くなります（\(\mu_0\) は真空の透磁率 [H/m]）。

## フレミングの左手の法則（電磁力）

磁界の中の電流が受ける力（アンペア力）：

$$\vec{F} = I \vec{L} \times \vec{B}$$

```
フレミングの左手の法則:

  中指 → 電流の向き (Current)
  人差し指 → 磁界の向き (field)
  親指 → 力の向き (Force)

  ← 力 ↑
  ↑磁界
  ● 電流（手前向き）
```

```python
def lorentz_force(I, L, B, angle_deg=90):
    """
    直線電流に働くアンペア力
    I: 電流 [A], L: 導線長 [m], B: 磁束密度 [T], angle: 角度 [度]
    """
    angle_rad = np.deg2rad(angle_deg)
    return I * L * B * np.sin(angle_rad)

# モーターのコイル
I_motor = 5     # A
L_coil  = 0.1   # m（コイルの一辺の長さ）
B_motor = 0.5   # T

F = lorentz_force(I_motor, L_coil, B_motor)
print(f"コイル1辺に働く力: {F} N")
```

**数式で表すと**

$$
F = I L B \sin\theta
$$

磁束密度 \(B\) [T] の中で電流 \(I\) [A]、長さ \(L\) [m] の導線が受けるアンペア力 \(F\) [N]。\(\theta\) は電流と磁界のなす角で、直交（\(90^\circ\)）のとき最大になります。

## フレミングの右手の法則（電磁誘導）

```
フレミングの右手の法則（発電機）:

  人差し指 → 磁界の向き
  中指    → 誘導起電力（電流）の向き
  親指    → 導体の運動方向

 ← 運動
 ↑磁界
 ●→ 誘導電流
```

## コイルの磁界（ソレノイド）

```python
def B_solenoid(n, I):
    """ソレノイド内部の磁束密度 [T]"""
    return mu0 * n * I

# n: 単位長さあたりの巻数 [turns/m]
turns   = 1000   # 1000巻
length  = 0.1    # 10cm
n       = turns / length  # 10000 turns/m
I       = 2.0    # A

B = B_solenoid(n, I)
print(f"ソレノイド内の磁束密度: {B*1000:.1f} mT")   # 25.1 mT

# 鉄心を入れると (μr ≈ 1000)
mu_r = 1000
B_iron = B * mu_r
print(f"鉄心入りの磁束密度: {B_iron:.2f} T")         # 25.1 T
```

**数式で表すと**

$$
B = \mu_0 \mu_r n I
$$

ソレノイド内部の磁束密度 \(B\) [T]。\(n\) は単位長さあたりの巻数 [turns/m]、\(I\) は電流 [A]。鉄心（比透磁率 \(\mu_r\)）を入れると磁束密度が大きく増加します。

## DCモーターの原理

```python
def dc_motor_torque(I, N, B, A):
    """
    DCモーターのトルク
    N: コイルの巻数, A: コイルの面積 [m²]
    """
    return N * I * B * A

# 小型DCモーター
N_coil = 100
I_coil = 0.5    # A
B_mot  = 0.3    # T
A_coil = 0.01   # 10cm × 10cm = 0.01 m²

tau = dc_motor_torque(I_coil, N_coil, B_mot, A_coil)
print(f"モータートルク: {tau:.3f} N·m = {tau*100:.1f} N·cm")

# 車載モーターの出力
rpm = 3000                          # 回転数
omega = rpm * 2 * np.pi / 60        # 角速度 [rad/s]
P_motor = tau * omega
print(f"モーター出力: {P_motor:.1f} W")
```

**数式で表すと**

$$
\tau = N I B A, \qquad P = \tau \omega
$$

トルク \(\tau\) [N·m] は巻数 \(N\)、電流 \(I\) [A]、磁束密度 \(B\) [T]、コイル面積 \(A\) [m²] の積。出力 \(P\) [W] はトルクと角速度 \(\omega\) [rad/s] の積で求まります。
