---
slug: alternating-current
title: 交流回路（AC・RMS・インピーダンス）
level: 2
category: Electronics
related: [ohms-law, capacitor, electromagnetic-induction, electric-power]
next: []
tags: [ac, alternating-current, rms, impedance, electronics]
---

## 概要
家庭のコンセントは「交流（AC）」です。直流（DC）と違い、電圧と電流が周期的に向きを変えます。日本では50/60Hzの正弦波交流が使われています。コンデンサ・コイルが絡む回路ではインピーダンスという概念が必要になります。

```mermaid
graph LR
  DC["直流 DC<br/>向き一定（電池）"] -. 比較 .- AC["交流 AC<br/>向きが周期反転"]
  AC --> U["送電・家電<br/>50/60Hz 正弦波"]
```

## 交流波形

$$v(t) = V_m \sin(2\pi f t + \phi)$$

- **V_m**：最大電圧（振幅）[V]
- **f**：周波数 [Hz]
- **φ**：初期位相 [rad]

```python
import numpy as np
import matplotlib.pyplot as plt

f  = 50        # 50 Hz（東日本の商用周波数）
Vm = 141.4     # V（100V実効値の√2倍）
T  = 1 / f     # 周期

t = np.linspace(0, 3*T, 1000)
v = Vm * np.sin(2 * np.pi * f * t)

plt.figure(figsize=(10, 4))
plt.plot(t * 1000, v, "b-", lw=2, label="交流電圧")
plt.axhline(Vm,    color="red",    linestyle="--", alpha=0.7, label=f"最大値 {Vm:.1f}V")
plt.axhline(-Vm,   color="red",    linestyle="--", alpha=0.7)
plt.axhline(100,   color="green",  linestyle=":",  alpha=0.7, label="実効値 100V")
plt.axhline(-100,  color="green",  linestyle=":",  alpha=0.7)
plt.xlabel("時間 [ms]")
plt.ylabel("電圧 [V]")
plt.title("日本の商用交流（50Hz）")
plt.legend()
plt.grid(True)
plt.show()
```

**数式で表すと**

$$
v(t) = V_m \sin(2\pi f t + \phi)
$$

時刻 \(t\) [s] における瞬時電圧 \(v(t)\) [V]。\(V_m\) は最大電圧（振幅）[V]、\(f\) は周波数 [Hz]、\(\phi\) は初期位相 [rad] です。

## 実効値（RMS）

交流の「実力」を表す値。同じ電力を消費する直流電圧に相当します。

$$V_{rms} = \frac{V_m}{\sqrt{2}} \approx 0.707 V_m$$

```python
def calc_rms(signal):
    """RMS（二乗平均平方根）を計算"""
    return np.sqrt(np.mean(signal**2))

# 日本の家庭用電源: 最大値 141.4V → 実効値 100V
Vm_ac = 141.4
Vrms_theory = Vm_ac / np.sqrt(2)
Vrms_calc   = calc_rms(v)

print(f"理論値 Vrms = {Vrms_theory:.1f} V")
print(f"計算値 Vrms = {Vrms_calc:.1f} V")

# 各波形の実効値
t  = np.linspace(0, 1, 10000)
waves = {
    "正弦波（振幅=1）":     np.sin(2*np.pi*50*t),
    "矩形波（振幅=1）":     np.sign(np.sin(2*np.pi*50*t)),
    "三角波（振幅=1）":     2*np.abs(2*(50*t - np.floor(50*t + 0.5))) - 1,
    "直流（1V）":            np.ones(10000),
}
for name, wave in waves.items():
    print(f"{name:22s}: RMS = {calc_rms(wave):.4f}")
```

**数式で表すと**

$$
V_{rms} = \sqrt{\frac{1}{T}\int_0^T v(t)^2\,dt} = \frac{V_m}{\sqrt{2}} \approx 0.707\, V_m
$$

実効値（RMS）は瞬時値の2乗平均平方根。正弦波では最大値 \(V_m\) の \(1/\sqrt{2}\) 倍になり、同じ電力を消費する直流電圧に相当します。

## コンデンサと交流

コンデンサは交流に対して**容量性リアクタンス** Xc を持ちます。

$$X_C = \frac{1}{2\pi f C}$$

```python
def capacitive_reactance(f, C):
    """容量性リアクタンス [Ω]"""
    return 1 / (2 * np.pi * f * C)

C = 100e-6   # 100 μF
f_range = np.logspace(1, 5, 300)
Xc = capacitive_reactance(f_range, C)

plt.figure(figsize=(8, 4))
plt.loglog(f_range, Xc, "b-", lw=2)
plt.xlabel("周波数 [Hz]")
plt.ylabel("リアクタンス Xc [Ω]")
plt.title("コンデンサのリアクタンス（高周波ほど小さい = 交流を通す）")
plt.grid(True)
plt.show()

# 実用例: 電源デカップリング
print("=== デカップリングコンデンサ ===")
for C_val in [100e-12, 10e-9, 100e-9, 10e-6, 100e-6]:
    Xc_1MHz = capacitive_reactance(1e6, C_val)
    print(f"C = {C_val*1e9:.0f} nF: Xc at 1MHz = {Xc_1MHz:.3f} Ω")
```

**数式で表すと**

$$
X_C = \frac{1}{2\pi f C}
$$

容量性リアクタンス \(X_C\) [Ω]。周波数 \(f\) [Hz] や容量 \(C\) [F] が大きいほど小さくなり、高周波の交流をよく通します。

## コイルと交流

コイルは交流に対して**誘導性リアクタンス** XL を持ちます。

$$X_L = 2\pi f L$$

```python
def inductive_reactance(f, L):
    """誘導性リアクタンス [Ω]"""
    return 2 * np.pi * f * L

L = 1e-3   # 1 mH
XL = inductive_reactance(f_range, L)

plt.figure(figsize=(8, 4))
plt.loglog(f_range, XL, "r-", lw=2)
plt.xlabel("周波数 [Hz]")
plt.ylabel("リアクタンス XL [Ω]")
plt.title("コイルのリアクタンス（高周波ほど大きい = 交流を阻む）")
plt.grid(True)
plt.show()
```

**数式で表すと**

$$
X_L = 2\pi f L
$$

誘導性リアクタンス \(X_L\) [Ω]。周波数 \(f\) [Hz] やインダクタンス \(L\) [H] が大きいほど大きくなり、高周波の交流を阻みます。

## インピーダンス（複素数表現）

$$Z = R + jX = R + j(X_L - X_C)$$

```python
import cmath

def impedance(R, L, C, f):
    """RLC直列回路のインピーダンス（複素数）"""
    XL = 2 * np.pi * f * L
    XC = 1 / (2 * np.pi * f * C)
    Z  = complex(R, XL - XC)
    return Z

R = 100    # 100 Ω
L = 10e-3  # 10 mH
C = 1e-6   # 1 μF

for f in [100, 1000, 5000, 10000]:
    Z = impedance(R, L, C, f)
    print(f"f={f:6d} Hz: Z = {abs(Z):.1f} Ω, 位相 = {cmath.phase(Z)*180/np.pi:.1f}°")

# 共振周波数（XL = XC のとき Z が最小）
f_res = 1 / (2 * np.pi * np.sqrt(L * C))
print(f"\n共振周波数: {f_res:.1f} Hz")
```

**数式で表すと**

$$
Z = R + j(X_L - X_C), \qquad f_0 = \frac{1}{2\pi\sqrt{LC}}
$$

RLC直列回路のインピーダンス \(Z\) [Ω]（複素数）。\(|Z| = \sqrt{R^2 + (X_L - X_C)^2}\) で大きさが決まり、\(X_L = X_C\) となる共振周波数 \(f_0\) [Hz] で \(|Z|\) は最小（\(=R\)）になります。

## RLC共振回路

```python
f_range2 = np.linspace(100, 10000, 1000)
Z_vals   = [abs(impedance(R, L, C, f)) for f in f_range2]

plt.figure(figsize=(9, 4))
plt.plot(f_range2, Z_vals, "b-", lw=2)
plt.axvline(f_res, color="red", linestyle="--", label=f"共振 f₀ = {f_res:.0f} Hz")
plt.xlabel("周波数 [Hz]")
plt.ylabel("インピーダンス |Z| [Ω]")
plt.title("RLC直列回路のインピーダンス特性")
plt.legend()
plt.grid(True)
plt.show()
```
