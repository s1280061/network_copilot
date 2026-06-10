---
slug: automotive-transmission
title: 変速機・ギア比（トランスミッション）
level: 2
category: Automotive
related: [automotive-torque, automotive-engine, ev-battery]
next: []
tags: [transmission, gear, ratio, automotive, powertrain, cvt]
---

## 概要
変速機（トランスミッション）はエンジンの回転数・トルクを走行状況に合わせて最適に変換する装置です。ギア比を変えることで「発進時は大きな力」「高速時は静かな回転」を両立します。MT・AT・CVT・EVドライブの仕組みを理解しましょう。

## ギア比の基本

$$i = \frac{n_{in}}{n_{out}} = \frac{T_{out}}{T_{in}}$$

```python
import numpy as np
import matplotlib.pyplot as plt

def gear_output(T_in, n_in, gear_ratio, final_ratio=4.0, efficiency=0.95):
    """変速機出力側のトルクと回転数を計算"""
    T_out = T_in * gear_ratio * final_ratio * efficiency
    n_out = n_in / (gear_ratio * final_ratio)   # rpm（タイヤの回転数）
    return T_out, n_out

# 典型的な5速MTのギア比
gear_ratios = {
    "1速": 3.50,
    "2速": 2.05,
    "3速": 1.38,
    "4速": 1.00,
    "5速": 0.79,
    "後退": 3.80,
}
final_ratio = 4.06   # ファイナルギア比

T_engine = 180   # N·m（中回転域トルク）
n_engine = 3000  # rpm

print(f"エンジン: {T_engine}N·m @ {n_engine}rpm\n")
print(f"{'ギア':6s} {'変速比':6s} {'車輪トルク':10s} {'車速(km/h)':12s}")
print("-" * 50)

tire_radius = 0.3   # m

for gear, ratio in gear_ratios.items():
    if gear == "後退": continue
    T_wheel, n_wheel = gear_output(T_engine, n_engine, ratio, final_ratio)
    # 車速計算: v = ω × r = (2πn/60) × r
    v_ms  = (2 * np.pi * n_wheel / 60) * tire_radius
    v_kmh = v_ms * 3.6
    print(f"{gear:4s}  {ratio:5.2f}  {T_wheel:8.0f} N·m  {v_kmh:8.1f} km/h")
```

## 各ギアの車速−エンジン回転数の関係

```python
# 各ギアでの車速と回転数の対応
v_range = np.linspace(0, 200, 200)   # km/h

fig, ax = plt.subplots(figsize=(10, 6))
for gear, ratio in gear_ratios.items():
    if gear == "後退": continue
    # v [km/h] = 2π × rpm / 60 × r_tire × 3.6 / (ratio × final)
    rpm_vals = v_range / 3.6 / tire_radius * 60 / (2 * np.pi) * ratio * final_ratio
    # レッドゾーン上限
    mask = rpm_vals < 7000
    ax.plot(v_range[mask], rpm_vals[mask], lw=2, label=gear)

ax.axhline(6500, color="red",  linestyle="--", alpha=0.5, label="レッドゾーン")
ax.axhline(1000, color="gray", linestyle="--", alpha=0.5, label="アイドル")
ax.fill_between([0, 200], [6500, 6500], [7000, 7000], color="red", alpha=0.1)
ax.set_xlabel("車速 [km/h]")
ax.set_ylabel("エンジン回転数 [rpm]")
ax.set_title("5速MTの各ギアにおける車速−回転数特性")
ax.legend()
ax.set_ylim(0, 7500)
ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.show()
```

## CVT（無段変速機）

```python
# CVTはプーリー径を連続的に変化させてギア比を無段階制御
def cvt_ratio(v_kmh, rpm_target=2500, final=4.0):
    """目標回転数を維持するCVTのギア比計算"""
    v_ms = v_kmh / 3.6
    n_wheel = v_ms / tire_radius * 60 / (2 * np.pi)   # 車輪rpm
    ratio = rpm_target / (n_wheel * final)
    return max(0.4, min(ratio, 3.5))   # CVTの変速比範囲でクリップ

v_range = np.linspace(5, 180, 300)
ratios  = [cvt_ratio(v) for v in v_range]
rpms    = [cvt_ratio(v) * v / 3.6 / tire_radius * 60 / (2*np.pi) * final_ratio
           for v in v_range]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(v_range, ratios, "g-", lw=2)
axes[0].set_xlabel("車速 [km/h]")
axes[0].set_ylabel("変速比")
axes[0].set_title("CVTの変速比（目標2500rpm維持）")
axes[0].grid(True)

axes[1].plot(v_range, rpms, "g-", lw=2, label="CVT")
# MT 4速で比較
rpm_4th = [v / 3.6 / tire_radius * 60 / (2*np.pi) * gear_ratios["4速"] * final_ratio
           for v in v_range]
axes[1].plot(v_range, rpm_4th, "b--", lw=1.5, alpha=0.7, label="MT 4速（固定）")
axes[1].axhline(2500, color="red", linestyle=":", label="目標rpm")
axes[1].set_xlabel("車速 [km/h]")
axes[1].set_ylabel("エンジン回転数 [rpm]")
axes[1].set_title("CVT vs MT のエンジン回転数")
axes[1].legend()
axes[1].grid(True)
plt.tight_layout()
plt.show()
```

## EVのシングルスピードドライブ

```python
# EVは変速機が不要（モーターが0rpmからトルク発生）
print("=== EV vs ICE の駆動系比較 ===\n")

components = {
    "ガソリン車（MT）": ["エンジン", "クラッチ", "変速機（5〜6速）",
                        "プロペラシャフト", "ディファレンシャル", "ドライブシャフト"],
    "ガソリン車（AT）": ["エンジン", "トルクコンバーター", "AT（6〜10速）",
                        "プロペラシャフト", "ディファレンシャル", "ドライブシャフト"],
    "BEV（後輪駆動）":  ["モーター（1つ）", "シングルスピードリダクションギア",
                        "ディファレンシャル", "ドライブシャフト"],
}

for car_type, parts in components.items():
    print(f"【{car_type}】")
    for i, p in enumerate(parts):
        arrow = " → " if i < len(parts)-1 else ""
        print(f"  {p}{arrow}", end="")
    print("\n")

print("EVが変速機不要な理由:")
print("  ① モーターは0rpmから最大トルクを発生")
print("  ② 回転数は0〜16,000rpm超まで幅広い")
print("  ③ リダクションギア（減速比6〜12）1段で十分")
print("  → 部品点数が大幅削減 → 軽量・低コスト・高信頼性")
```

## トルクコンバーター（AT）

```python
# トルクコンバーター: 流体を使ったトルク増幅装置
# ストール状態（出力側静止）では トルク比 ≈ 2〜3倍
def torque_converter(T_engine, slip_ratio):
    """
    トルクコンバーターの特性（概略）
    slip_ratio: 入出力回転比（0=ストール, 1=直結）
    """
    # 簡易モデル: スリップが大きいほどトルク倍増
    torque_ratio = 2.5 - 1.5 * slip_ratio   # ストール時2.5倍, 直結時1.0倍
    efficiency   = slip_ratio * (2 - slip_ratio)  # 効率はスリップで低下
    return T_engine * torque_ratio, efficiency

slip_range = np.linspace(0, 1, 100)
T_out_list, eff_list = zip(*[torque_converter(200, s) for s in slip_range])

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(slip_range, T_out_list, "r-", lw=2)
axes[0].axhline(200, color="gray", linestyle="--", label="エンジントルク")
axes[0].set_xlabel("速度比 (出力rpm / 入力rpm)")
axes[0].set_ylabel("出力トルク [N·m]")
axes[0].set_title("トルクコンバーターの出力トルク")
axes[0].legend()
axes[0].grid(True)

axes[1].plot(slip_range, [e*100 for e in eff_list], "b-", lw=2)
axes[1].axvline(0.85, color="red", linestyle="--", label="ロックアップ点（≈85%）")
axes[1].set_xlabel("速度比")
axes[1].set_ylabel("効率 [%]")
axes[1].set_title("トルクコンバーターの効率")
axes[1].legend()
axes[1].grid(True)
plt.tight_layout()
plt.show()
```
