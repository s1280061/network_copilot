---
slug: capacitor
title: コンデンサ（静電容量・充放電）
level: 2
category: Electronics
related: [electric-field, alternating-current, ohms-law, electromagnetic-induction]
next: []
tags: [capacitor, capacitance, charge, rc-circuit, electronics]
---

## 概要
コンデンサは「電荷を蓄えるデバイス」です。2枚の金属板の間に電場を生じさせてエネルギーを蓄えます。電源のノイズ除去・タイマー回路・フィルタ・DRAM・非接触ICカードなど、あらゆる電子回路に使われています。

## 静電容量（キャパシタンス）

$$C = \frac{Q}{V}$$

- **C**：静電容量 [F（ファラド）]
- **Q**：電荷量 [C]
- **V**：電圧 [V]

```python
import numpy as np
import matplotlib.pyplot as plt

# 平行板コンデンサの容量
epsilon_0 = 8.854e-12   # 真空の誘電率 [F/m]

def parallel_plate_capacitor(epsilon_r, A, d):
    """
    平行板コンデンサの静電容量
    epsilon_r: 比誘電率, A: 板の面積 [m²], d: 板間距離 [m]
    """
    return epsilon_r * epsilon_0 * A / d

# 代表的な誘電体
dielectrics = {
    "真空 / 空気": 1.0,
    "ポリエチレン": 2.3,
    "ガラス":      7.0,
    "セラミック（BaTiO₃）": 1200,
}

A = 1e-4    # 1cm² の板
d = 1e-6    # 1μm の板間距離

for material, eps_r in dielectrics.items():
    C = parallel_plate_capacitor(eps_r, A, d)
    print(f"{material:25s}: {C*1e12:.1f} pF")
```

## コンデンサの充放電

コンデンサをRC回路で充電/放電する時定数 τ = RC

```python
def rc_charge(V0, R, C, t):
    """RC回路の充電曲線"""
    tau = R * C
    return V0 * (1 - np.exp(-t / tau))

def rc_discharge(V0, R, C, t):
    """RC回路の放電曲線"""
    tau = R * C
    return V0 * np.exp(-t / tau)

# R = 10kΩ, C = 100μF
R = 10e3      # 10 kΩ
C = 100e-6    # 100 μF
V_supply = 5  # V
tau = R * C
print(f"時定数 τ = RC = {tau*1000:.0f} ms")
print(f"5τ = {5*tau*1000:.0f} ms で充電ほぼ完了（99.3%）")

t = np.linspace(0, 5 * tau, 500)
V_charge    = rc_charge(V_supply, R, C, t)
V_discharge = rc_discharge(V_supply, R, C, t)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(t * 1000, V_charge, "b-", lw=2)
axes[0].axhline(V_supply * 0.632, color="gray", linestyle="--", label="63.2%（1τ）")
axes[0].axhline(V_supply * 0.993, color="red",  linestyle="--", label="99.3%（5τ）")
axes[0].set_xlabel("時間 [ms]")
axes[0].set_ylabel("電圧 [V]")
axes[0].set_title("コンデンサの充電")
axes[0].legend()
axes[0].grid(True)

axes[1].plot(t * 1000, V_discharge, "r-", lw=2)
axes[1].axhline(V_supply * 0.368, color="gray", linestyle="--", label="36.8%（1τ）")
axes[1].set_xlabel("時間 [ms]")
axes[1].set_ylabel("電圧 [V]")
axes[1].set_title("コンデンサの放電")
axes[1].legend()
axes[1].grid(True)
plt.tight_layout()
plt.show()
```

## コンデンサの直列・並列

```python
def series_capacitance(*caps):
    """直列合成容量（抵抗の並列と同じ計算）"""
    return 1 / sum(1/C for C in caps)

def parallel_capacitance(*caps):
    """並列合成容量（抵抗の直列と同じ計算）"""
    return sum(caps)

# 例
C1, C2, C3 = 10e-6, 22e-6, 47e-6   # μF

C_series   = series_capacitance(C1, C2, C3)
C_parallel = parallel_capacitance(C1, C2, C3)

print(f"直列合成: {C_series*1e6:.2f} μF（最小容量より小さい）")
print(f"並列合成: {C_parallel*1e6:.0f} μF（各容量の和）")
```

## コンデンサに蓄えられるエネルギー

$$E = \frac{1}{2} C V^2$$

```python
def capacitor_energy(C, V):
    return 0.5 * C * V**2

# 電源デカップリングコンデンサ（100μF, 5V）
E_decoupling = capacitor_energy(100e-6, 5)
print(f"デカップリングコンデンサ: {E_decoupling * 1000:.2f} mJ")

# スーパーキャパシタ（EVの回生制動用, 3000F, 2.7V）
E_supercap = capacitor_energy(3000, 2.7)
print(f"スーパーキャパシタ: {E_supercap:.0f} J = {E_supercap/3600:.4f} Wh")

# 一般的なリチウムイオン電池 18650（3.7V, 3Ah）との比較
E_battery = 3.7 * 3 * 3600   # J
print(f"リチウム電池 18650: {E_battery:.0f} J = {E_battery/3600:.1f} Wh")
print(f"エネルギー密度比: スーパーキャパシタは電池の {E_supercap/E_battery*100:.2f}%")
```

## ローパスフィルタ（RC フィルタ）

```python
def rc_lowpass_gain(f, R, C):
    """RC ローパスフィルタのゲイン（-3dBカットオフ周波数）"""
    omega = 2 * np.pi * f
    H = 1 / np.sqrt(1 + (omega * R * C)**2)
    return H

# カットオフ周波数 fc = 1/(2πRC)
R_f, C_f = 1e3, 1e-6    # 1kΩ, 1μF
fc = 1 / (2 * np.pi * R_f * C_f)
print(f"カットオフ周波数: {fc:.1f} Hz")

f_range = np.logspace(1, 6, 300)
gain    = rc_lowpass_gain(f_range, R_f, C_f)
gain_dB = 20 * np.log10(gain)

plt.figure(figsize=(9, 4))
plt.semilogx(f_range, gain_dB, "b-", lw=2)
plt.axvline(fc, color="red", linestyle="--", label=f"fc = {fc:.0f} Hz (-3dB)")
plt.axhline(-3, color="gray", linestyle=":")
plt.xlabel("周波数 [Hz]")
plt.ylabel("ゲイン [dB]")
plt.title("RC ローパスフィルタの周波数特性")
plt.legend()
plt.grid(True)
plt.show()
```
