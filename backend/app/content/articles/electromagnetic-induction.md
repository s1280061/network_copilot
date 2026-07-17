---
slug: electromagnetic-induction
title: 電磁誘導とファラデーの法則
level: 2
category: Electronics
related: [magnetism, alternating-current, capacitor]
next: [alternating-current]
tags: [electromagnetic-induction, faraday, lenz, transformer, electronics]
---

## 概要
電磁誘導は「磁束の変化が起電力を生む」現象です。1831年にファラデーが発見したこの法則が、発電機・変圧器・非接触充電（ワイヤレス充電）・車載センサー（ABS・クランク角センサー）の原理です。

```mermaid
graph LR
  M["磁束の変化 ΔΦ"] --> E["起電力 V = −dΦ/dt"]
  E --> U["発電機・変圧器・<br/>ワイヤレス充電"]
```

## ファラデーの電磁誘導の法則

$$\varepsilon = -N \frac{\Delta\Phi}{\Delta t}$$

- **ε**：誘導起電力 [V]
- **N**：コイルの巻数
- **ΔΦ**：磁束の変化量 [Wb（ウェーバー）]
- **Δt**：時間の変化 [s]
- マイナス符号：レンツの法則（変化を妨げる向きに誘起）

```python
import numpy as np
import matplotlib.pyplot as plt

def induced_emf(N, dPhi_dt):
    """誘導起電力 [V]"""
    return -N * dPhi_dt

# コイルの中の磁束が変化するとき
t = np.linspace(0, 0.1, 1000)   # 0〜100ms
B_max = 0.5    # T
freq  = 50     # Hz（商用電源）

Phi   = B_max * 0.01 * np.sin(2 * np.pi * freq * t)   # 磁束 Φ = B × A
dPhi  = np.gradient(Phi, t)                              # dΦ/dt

N = 100    # 巻数
emf = induced_emf(N, dPhi)

fig, axes = plt.subplots(2, 1, figsize=(10, 6))
axes[0].plot(t * 1000, Phi * 1000, "b-", lw=2)
axes[0].set_ylabel("磁束 Φ [mWb]")
axes[0].set_title("磁束の時間変化")
axes[0].grid(True)

axes[1].plot(t * 1000, emf, "r-", lw=2)
axes[1].set_xlabel("時間 [ms]")
axes[1].set_ylabel("誘導起電力 [V]")
axes[1].set_title("誘導起電力（磁束の微分）")
axes[1].grid(True)
plt.tight_layout()
plt.show()
```

**数式で表すと**

$$
\varepsilon = -N \frac{d\Phi}{dt}
$$

誘導起電力 \(\varepsilon\) [V] は巻数 \(N\) と磁束 \(\Phi\) [Wb] の時間変化率に比例します。マイナス符号はレンツの法則（変化を妨げる向き）を表します。

## レンツの法則

誘導電流は、磁束の変化を妨げる向きに流れます。

```
磁石を近づける           誘導電流
  N  →→→→    ○←←○
              ↑
        磁石を押し返す力（斥力）が発生

磁石を遠ざける           誘導電流
  N  ←←←←    ○→→○
              ↑
        磁石を引き戻す力（引力）が発生
```

```python
def lenz_force(v_magnet, B, L, R_coil):
    """
    磁石の速度 v から誘導電流・ブレーキ力を計算
    L: 有効コイル長 [m], R_coil: コイル抵抗 [Ω]
    """
    emf   = B * L * v_magnet     # 誘導起電力
    I_ind = emf / R_coil          # 誘導電流
    F_brake = B * I_ind * L       # ブレーキ力（レンツの法則）
    return emf, I_ind, F_brake

# 電磁ブレーキ（リニアモーターカーの制動など）
emf, I, F = lenz_force(v_magnet=10, B=0.5, L=0.2, R_coil=2)
print(f"誘導起電力: {emf} V")
print(f"誘導電流:   {I} A")
print(f"制動力:     {F} N")
```

**数式で表すと**

$$
\varepsilon = BLv, \quad I = \frac{\varepsilon}{R}, \quad F = BIL
$$

速度 \(v\) [m/s] で動く導体に生じる起電力 \(\varepsilon\)、その誘導電流 \(I\)、そして電流が受けるブレーキ力 \(F\) [N]。運動を妨げる向き（レンツの法則）に働きます。

## 変圧器（トランス）

変圧器は電磁誘導で交流電圧を変換します。

$$\frac{V_2}{V_1} = \frac{N_2}{N_1}$$

```python
def transformer(V1, N1, N2, I1=None):
    """
    理想変圧器の計算
    V1: 1次電圧, N1: 1次巻数, N2: 2次巻数
    """
    V2 = V1 * N2 / N1
    I2 = I1 * N1 / N2 if I1 is not None else None
    P_in = V1 * I1 if I1 is not None else None
    P_out = V2 * I2 if I2 is not None else None
    return V2, I2, P_in, P_out

# 電柱の変圧器: 6600V → 100V
V2, I2, P_in, P_out = transformer(6600, 6600, 100, I1=10)
print(f"2次電圧: {V2} V")
print(f"2次電流: {I2} A")
print(f"入力電力: {P_in} W  出力電力: {P_out} W（理想変圧器: P_in = P_out）")

# スマホ充電器: 100V → 5V
V2, _, _, _ = transformer(100, 100, 5)
print(f"\nスマホ充電器 2次電圧: {V2} V")

# 車載用DC-DCコンバーター（12V → 3.3V）
# 実際はスイッチング方式だが変圧比の概念は同じ
ratio = 3.3 / 12
print(f"12V → 3.3V の変圧比: {ratio:.3f}（N2/N1 = {ratio:.3f}）")
```

**数式で表すと**

$$
\frac{V_2}{V_1} = \frac{N_2}{N_1} = \frac{I_1}{I_2}
$$

理想変圧器では電圧比は巻数比 \(N_2/N_1\) に等しく、電流比は逆比になります。損失がなければ入力電力と出力電力は等しくなります（\(V_1 I_1 = V_2 I_2\)）。

## 自己誘導とインダクタンス

コイル自身の電流変化が逆起電力を生みます。

$$\varepsilon = -L \frac{dI}{dt}$$

```python
def self_inductance_emf(L, dI_dt):
    """自己誘導起電力 [V]"""
    return -L * dI_dt

# インダクタ（コイル）の特性
L = 1e-3    # 1 mH（車載フィルター用）

# 電流が急変するとき（スイッチングノイズ）
dI_dt_spike = 1000   # A/s → 1A/ms の変化
emf_spike   = self_inductance_emf(L, dI_dt_spike)
print(f"スイッチングスパイク: {emf_spike} V")

# インダクタに蓄えられるエネルギー
I_coil = 5  # A
E_inductor = 0.5 * L * I_coil**2
print(f"インダクタのエネルギー: {E_inductor * 1000:.2f} mJ")
```

**数式で表すと**

$$
\varepsilon = -L \frac{dI}{dt}, \qquad E = \frac{1}{2} L I^2
$$

自己誘導起電力 \(\varepsilon\) [V] は電流変化率に比例します（\(L\) は自己インダクタンス [H]）。コイルに蓄えられるエネルギー \(E\) [J] は電流の2乗に比例します。

## 車載センサーへの応用

```python
# クランク角センサー（パッシブ型）の動作原理
def crank_sensor_signal(rpm, teeth=60, t_total=0.1):
    """
    歯車の回転で磁束が変化 → 誘導電圧を生成
    rpm: エンジン回転数, teeth: 歯数, t_total: 時間[s]
    """
    f_tooth  = rpm / 60 * teeth   # 歯が通過する周波数 [Hz]
    t        = np.linspace(0, t_total, 5000)
    signal   = np.sin(2 * np.pi * f_tooth * t)
    return t, signal

for rpm in [800, 3000, 6000]:
    t, sig = crank_sensor_signal(rpm)
    f = rpm / 60 * 60
    print(f"RPM {rpm:5d}: センサー信号周波数 {f:.0f} Hz")
```
