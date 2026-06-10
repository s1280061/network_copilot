---
slug: wireless-basics
title: 無線通信の基礎（電波・周波数・変調）
level: 1
category: Wireless
related: [wifi, bluetooth, lte-5g, v2x-wireless, electromagnetic-induction]
next: [wifi]
tags: [wireless, radio, frequency, modulation, antenna, basics]
---

## 概要
無線通信は電磁波（電波）を使って情報を伝える技術です。Wi-Fi・Bluetooth・5G・車載V2X・GPSはすべて異なる周波数帯の電波を使っています。「なぜ5GHzのWi-Fiは壁に弱いのか」「なぜ5Gは速いのか」を電波の物理から理解しましょう。

## 電波の基本性質

$$c = f \times \lambda$$

- **c**：光速 = 3 × 10⁸ m/s
- **f**：周波数 [Hz]
- **λ**（ラムダ）：波長 [m]

```python
import numpy as np
import matplotlib.pyplot as plt

c = 3e8   # 光速 [m/s]

# 主要な無線通信の周波数と波長
freq_bands = {
    "AM ラジオ":         1e6,
    "FM ラジオ":        100e6,
    "GPS（L1）":      1575.42e6,
    "Wi-Fi 2.4GHz":   2.4e9,
    "Wi-Fi 5GHz":     5.0e9,
    "Wi-Fi 6E（6GHz）":6.0e9,
    "Bluetooth":       2.4e9,
    "4G LTE（Band1）": 2.1e9,
    "5G Sub-6GHz":     3.5e9,
    "5G ミリ波":       28e9,
    "V2X（DSRC）":     5.9e9,
}

print(f"{'通信方式':20s} {'周波数':15s} {'波長':12s}")
print("-" * 50)
for name, f in freq_bands.items():
    lam = c / f
    if f >= 1e9:   f_str = f"{f/1e9:.2f} GHz"
    elif f >= 1e6: f_str = f"{f/1e6:.0f} MHz"
    else:          f_str = f"{f/1e3:.0f} kHz"
    if lam >= 1:   l_str = f"{lam:.2f} m"
    else:          l_str = f"{lam*100:.1f} cm"
    print(f"{name:20s} {f_str:14s} {l_str}")
```

## 電波の伝搬と減衰

```python
# 自由空間伝搬損失（フリスの式）
def free_space_loss_dB(f_Hz, d_m):
    """自由空間伝搬損失 [dB]"""
    lam = c / f_Hz
    L = (4 * np.pi * d_m / lam)**2
    return 10 * np.log10(L)

# 距離と周波数ごとの伝搬損失
distances = [10, 100, 1000]   # m
freqs = {
    "2.4GHz (Wi-Fi)": 2.4e9,
    "5GHz (Wi-Fi)":   5.0e9,
    "28GHz (5G mmW)": 28e9,
}

print("=== 自由空間伝搬損失 ===")
print(f"{'距離':8s}", end="")
for name in freqs: print(f"  {name:18s}", end="")
print()
for d in distances:
    print(f"{d:6d} m", end="")
    for name, f in freqs.items():
        L = free_space_loss_dB(f, d)
        print(f"  {L:6.1f} dB         ", end="")
    print()

print("\n→ 周波数が高いほど減衰が大きい")
print("→ 5GHz Wi-Fiが2.4GHzより壁に弱い理由")
print("→ 5Gミリ波が超高速だが屋外専用になる理由")
```

## 変調方式

```python
# 変調: 情報を電波に乗せる方法
t = np.linspace(0, 1, 1000)
f_carrier = 10   # 搬送波周波数
f_message = 1    # 信号周波数

carrier = np.cos(2 * np.pi * f_carrier * t)
message = np.cos(2 * np.pi * f_message * t)

# AM変調（振幅変調）
am_modulation = 0.5
am_signal = (1 + am_modulation * message) * carrier

# FM変調（周波数変調）
kf = 3
phase_fm = 2 * np.pi * f_carrier * t + kf * np.cumsum(message) / 1000
fm_signal = np.cos(phase_fm)

# BPSK（位相変調の基本）
bits = np.repeat([1, -1, 1, 1, -1, 1, -1, -1, 1, 1], 100)
bpsk_signal = bits * carrier

fig, axes = plt.subplots(4, 1, figsize=(12, 8))
axes[0].plot(t, message, "g-", lw=1.5); axes[0].set_title("元の信号（情報）"); axes[0].set_ylabel("振幅")
axes[1].plot(t, am_signal, "b-", lw=1);   axes[1].set_title("AM（振幅変調）"); axes[1].set_ylabel("振幅")
axes[2].plot(t, fm_signal, "r-", lw=1);   axes[2].set_title("FM（周波数変調）"); axes[2].set_ylabel("振幅")
axes[3].plot(t, bpsk_signal, "m-", lw=1); axes[3].set_title("BPSK（位相変調）"); axes[3].set_ylabel("振幅")
axes[3].set_xlabel("時間")
for ax in axes: ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.show()
```

## シャノンの定理（通信容量の限界）

$$C = B \times \log_2\left(1 + \frac{S}{N}\right)$$

```python
def channel_capacity(bandwidth_Hz, snr_dB):
    """シャノン限界通信容量 [bps]"""
    snr_linear = 10 ** (snr_dB / 10)
    C = bandwidth_Hz * np.log2(1 + snr_linear)
    return C

# 各通信規格の理論上限
print("=== シャノン限界による通信容量上限 ===")
scenarios = [
    ("Wi-Fi 2.4GHz（20MHz ch, SNR=25dB）", 20e6,  25),
    ("Wi-Fi 5GHz（80MHz ch, SNR=30dB）",   80e6,  30),
    ("Wi-Fi 6（160MHz ch, SNR=35dB）",    160e6,  35),
    ("5G Sub-6（100MHz ch, SNR=20dB）",   100e6,  20),
    ("5G mmW（400MHz ch, SNR=20dB）",     400e6,  20),
    ("有線 Gigabit Ethernet",             500e6,  40),
]
for name, B, snr in scenarios:
    C = channel_capacity(B, snr)
    print(f"  {name:40s}: {C/1e6:6.0f} Mbps")
```

## アンテナの基本

```python
# ダイポールアンテナの最適長 = λ/2
def dipole_length(f_Hz):
    """半波長ダイポールアンテナの長さ [cm]"""
    lam = c / f_Hz
    return lam / 2 * 100   # cm

print("アンテナの最適サイズ:")
antennas = {
    "2.4GHz Wi-Fi":  2.4e9,
    "5GHz Wi-Fi":    5.0e9,
    "5G 3.5GHz":     3.5e9,
    "5G 28GHz":      28e9,
    "V2X 5.9GHz":    5.9e9,
}
for name, f in antennas.items():
    L = dipole_length(f)
    print(f"  {name:16s}: λ/2 = {L:.1f} cm")

print("\n→ 周波数が高い（波長が短い）ほどアンテナを小型化できる")
print("→ スマートフォンに5G/Wi-Fi/Bluetoothが全部入る理由")
```
