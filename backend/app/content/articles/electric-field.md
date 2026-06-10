---
slug: electric-field
title: 電場とクーロンの法則
level: 2
category: Electronics
related: [electricity-basics, capacitor, ohms-law]
next: [capacitor]
tags: [electric-field, coulomb, charge, electronics, physics]
---

## 概要
電場（電界）は「電荷の周りに生じる力の場」です。クーロンの法則は2つの電荷の間に働く力を表します。コンデンサ・絶縁体・半導体デバイスの動作原理はすべてこの電場の概念から理解できます。

## クーロンの法則

2つの点電荷の間に働く静電気力：

$$F = k \frac{q_1 \times q_2}{r^2}$$

- **F**：力 [N（ニュートン）]
- **k**：クーロン定数 = 9.0 × 10⁹ [N·m²/C²]
- **q₁, q₂**：電荷量 [C（クーロン）]
- **r**：距離 [m]

```python
import numpy as np
import matplotlib.pyplot as plt

k = 9.0e9   # クーロン定数 [N·m²/C²]
e = 1.6e-19  # 電気素量（電子1個の電荷）[C]

def coulomb_force(q1, q2, r):
    """クーロン力 [N]"""
    F = k * abs(q1) * abs(q2) / r**2
    sign = 1 if q1 * q2 > 0 else -1   # 同符号=斥力, 異符号=引力
    return F * sign

# 陽子と電子の引力（水素原子のボーア半径: 5.29e-11 m）
r_bohr = 5.29e-11
F = coulomb_force(e, -e, r_bohr)
print(f"水素原子内の引力: {F:.3e} N")   # → 8.238e-08 N

# 距離と力の関係（逆二乗則）
r_range = np.logspace(-10, -7, 100)
F_range = k * e**2 / r_range**2

plt.figure(figsize=(8, 5))
plt.loglog(r_range * 1e9, F_range, "b-", lw=2)
plt.xlabel("距離 [nm]")
plt.ylabel("クーロン力 [N]")
plt.title("電子と陽子間のクーロン力（逆二乗則）")
plt.grid(True)
plt.show()
```

## 電場（電界）

**電場 E** は、その点に置いた単位電荷 (+1C) に働く力の向き・大きさを表します。

$$E = \frac{F}{q} = k \frac{Q}{r^2}$$

- 単位：V/m または N/C

```python
def electric_field(Q, r):
    """点電荷Qから距離rでの電場 [V/m]"""
    return k * abs(Q) / r**2

# 電場の可視化（2D）
x = np.linspace(-2, 2, 30)
y = np.linspace(-2, 2, 30)
X, Y = np.meshgrid(x, y)

# +電荷を原点に置く
Q = 1e-9   # 1 nC
r  = np.sqrt(X**2 + Y**2 + 1e-10)   # ゼロ除算防止
E  = k * Q / r**2
Ex = E * X / r
Ey = E * Y / r

plt.figure(figsize=(7, 6))
plt.streamplot(X, Y, Ex, Ey, density=1.5, color="steelblue", linewidth=1)
plt.plot(0, 0, "ro", ms=12, label="+Q")
plt.axis("equal")
plt.title("点電荷の電場（電気力線）")
plt.legend()
plt.show()
```

## 電位（電圧）と電場の関係

電位差（電圧）は電場に沿った積分です。

$$V = -\int E \, dr = k \frac{Q}{r}$$

```python
def electric_potential(Q, r):
    """点電荷Qから距離rでの電位 [V]"""
    return k * Q / r

# 点電荷 (Q=1nC) からの電位分布
r_vals = np.linspace(0.1, 5, 100)   # m
Q = 1e-9  # 1 nC

V_vals = electric_potential(Q, r_vals)
E_vals = electric_field(Q, r_vals)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(r_vals * 100, V_vals, "b-", lw=2)
axes[0].set_xlabel("距離 [cm]")
axes[0].set_ylabel("電位 [V]")
axes[0].set_title("電位の距離依存性（∝ 1/r）")
axes[0].grid(True)

axes[1].plot(r_vals * 100, E_vals, "r-", lw=2)
axes[1].set_xlabel("距離 [cm]")
axes[1].set_ylabel("電場 [V/m]")
axes[1].set_title("電場の距離依存性（∝ 1/r²）")
axes[1].grid(True)
plt.tight_layout()
plt.show()
```

## 電場と絶縁破壊

```python
# 絶縁体の絶縁破壊電界強度
breakdown_fields = {
    "空気":           3e6,    # V/m
    "シリコン":       3e7,
    "酸化シリコン":   1e9,
    "窒化シリコン":   1e10,
}

print("=== 絶縁破壊電界 ===")
for material, E_bd in breakdown_fields.items():
    print(f"{material:12s}: {E_bd:.0e} V/m")

# 雷：大気中の絶縁破壊
cloud_voltage = 100e6   # 1億ボルト（概算）
cloud_height  = 1000    # m
E_thunder = cloud_voltage / cloud_height
print(f"\n雷雲の電場: {E_thunder:.0e} V/m （大気の限界 3×10⁶ V/m を超えると放電）")

# IC回路のゲート酸化膜（10nm, 5V）
t_ox = 10e-9   # 10nm
V_gate = 5
E_gate = V_gate / t_ox
print(f"MOSFETゲート電場: {E_gate:.0e} V/m（設計上は酸化膜限界の1/10以下に）")
```

## 帯電と静電気

```python
# 静電気エネルギー
def static_energy(C, V):
    """コンデンサ（または帯電体）に蓄えられたエネルギー [J]"""
    return 0.5 * C * V**2

# 人体の帯電（例: C≈200pF, V≈10000V）
C_body = 200e-12   # 200 pF
V_body = 10000     # 10 kV（歩行時の帯電）
E_static = static_energy(C_body, V_body)
print(f"人体の静電エネルギー: {E_static*1000:.1f} mJ")
# IC は数十mJ で破壊されることがある → ESD 対策が重要
```
