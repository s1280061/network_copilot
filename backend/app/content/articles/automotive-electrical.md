---
slug: automotive-electrical
title: 車載電気システム（12V/48V・ハーネス・ECU）
level: 2
category: Automotive
related: [electricity-basics, ohms-law, electric-power, semiconductor, ev-battery]
next: [ev-battery]
tags: [automotive, electrical, 12v, 48v, harness, ecu, can, electronics]
---

## 概要
現代の自動車には100個以上のECU（電子制御ユニット）と数kmのワイヤーハーネスが搭載されています。電気の基礎知識が車の設計・整備・診断に直結します。「電気の基礎（V=RI）」を自動車の文脈で理解しましょう。

## 車載電源システムの概要

```
車載電源アーキテクチャ:

  バッテリー（12V / 48V）
       ↓
  ヒューズボックス / スマートジャンクションボックス
       ↓
  ┌────────────────────────────┐
  │ エンジンECU   │ ブレーキECU │
  │ トランスミッションECU      │
  │ ボディECU     │ エアコンECU │
  │ メーターECU   │ エアバッグECU│
  └────────────────────────────┘
  すべてCAN/LIN/Ethernetネットワークで接続
```

```python
import numpy as np

# 12V 鉛バッテリーの基本特性
battery = {
    "公称電圧":    12,       # V（実際は12.6V充電完了, 11.8V放電限界）
    "容量":        60,       # Ah（60Ah = 60A × 1時間 = 720Wh）
    "冷間始動電流": 550,      # CCA (Cold Cranking Amps at -18°C)
    "内部抵抗":    0.01,     # Ω（新品時）
}

# スターターモーター始動時の電圧降下
I_starter = 200  # A（始動電流）
R_internal = 0.01
V_drop = I_starter * R_internal
print(f"始動時電圧降下: {V_drop} V → バッテリー端子は {12 - V_drop} V")

# 消費電流の内訳（エンジン動作中）
current_consumers = {
    "ECU群（全部）":       20,   # A
    "ヘッドライト（LED）": 5,
    "エアコンブロア":      15,
    "電動パワステ":         8,
    "ホーン":               5,   # 瞬時
    "シートヒーター":      10,
    "リアデフォッガー":    12,
}
total_I = sum(current_consumers.values())
print(f"\n合計消費電流: {total_I} A")
print(f"オルタネーター必要出力: {total_I * 14.4:.0f} W（≈{total_I*14.4/1000:.1f}kW）")
```

## オルタネーター（発電機）

```python
# オルタネーター: エンジン駆動で14V前後の直流を発電
def alternator_power(engine_rpm, pulley_ratio=2.5, alt_efficiency=0.65):
    """
    オルタネーターの発電量計算
    pulley_ratio: エンジン/オルタネーター プーリー比
    """
    alt_rpm = engine_rpm * pulley_ratio
    # 代表的なオルタネーター特性（80A定格）
    if alt_rpm < 1000:
        I_max = 0
    elif alt_rpm < 2000:
        I_max = 80 * (alt_rpm - 1000) / 1000
    else:
        I_max = 80   # 定格電流 80A

    P_out = 14.4 * I_max * alt_efficiency   # W
    return alt_rpm, I_max, P_out

print("エンジン回転数とオルタネーター出力:")
for rpm in [600, 800, 1000, 1500, 2000, 3000]:
    alt_rpm, I, P = alternator_power(rpm)
    print(f"  {rpm:4d} rpm → ALT {alt_rpm:.0f} rpm: {I:.0f} A, {P:.0f} W")
```

## ワイヤーハーネスの設計

```python
# 電線のサイズ選択（許容電流と電圧降下）
# AWG/sq mm → 許容電流の対応
wire_specs = {
    "0.3 sq": {"I_max": 7,  "R_per_m": 0.062},  # Ω/m
    "0.5 sq": {"I_max": 10, "R_per_m": 0.038},
    "0.85sq": {"I_max": 13, "R_per_m": 0.022},
    "1.25sq": {"I_max": 19, "R_per_m": 0.015},
    "2.0 sq": {"I_max": 25, "R_per_m": 0.0092},
    "3.0 sq": {"I_max": 32, "R_per_m": 0.0062},
    "5.0 sq": {"I_max": 42, "R_per_m": 0.0037},
}

def select_wire(I_load, length_m, V_supply=12, V_drop_max=0.5):
    """
    負荷電流と配線長から最適な電線サイズを選択
    V_drop_max: 許容電圧降下 [V]
    """
    print(f"負荷電流: {I_load}A, 配線長: {length_m}m")
    print(f"（往復 {length_m*2}m = 電圧降下計算に使用）")
    for sq, spec in wire_specs.items():
        if I_load <= spec["I_max"]:
            V_drop = I_load * spec["R_per_m"] * length_m * 2
            ok = "✅" if V_drop <= V_drop_max else "⚠️"
            print(f"  {sq}: {V_drop:.3f}V降下 {ok}")
            if V_drop <= V_drop_max:
                print(f"  → {sq} を推奨")
                return sq
    return "規格外（並列敷設を検討）"

select_wire(I_load=10, length_m=3)
print()
select_wire(I_load=25, length_m=5)
```

## ECUの電源回路

```python
# ECUへの電源供給の典型パターン
ecu_power_patterns = {
    "常時電源（+B）": {
        "電圧": "12V（バッテリー直結）",
        "用途": "メモリ保持・時計・盗難防止",
        "ECU側処理": "スリープ中も微小電流消費（暗電流 5〜15mA）",
    },
    "イグニッション電源（IG）": {
        "電圧": "12V（キーON/エンジンON時）",
        "用途": "ECU本体の動作電源",
        "ECU側処理": "IG-ONで起動、IG-OFFで後処理してスリープ",
    },
    "アクセサリー電源（ACC）": {
        "電圧": "12V（ACC位置以降）",
        "用途": "ラジオ・ナビ・パワーウィンドウ",
        "ECU側処理": "エンジン停止でも動作",
    },
}

for power_type, info in ecu_power_patterns.items():
    print(f"【{power_type}】")
    for k, v in info.items():
        print(f"  {k}: {v}")
    print()

# ECU内部の電源降圧
print("ECU内部の電圧変換:")
print("  12V → 5V: リニアレギュレーター or DC-DCコンバーター")
print("  5V  → 3.3V: LDO（Low Dropout Regulator）")
print("  3.3V → 1.2V: CPU コアへの供給")
print()

# 電圧降圧の効率比較
V_in, V_out, I_load = 12, 5, 1.0
# リニアレギュレーター（熱で捨てる）
P_heat_linear = (V_in - V_out) * I_load
P_out = V_out * I_load
eta_linear = P_out / (V_in * I_load)
print(f"リニアレギュレーター: 効率 {eta_linear*100:.0f}%（発熱 {P_heat_linear}W）")

# スイッチングコンバーター（効率良好）
eta_switching = 0.90
P_in_sw = P_out / eta_switching
print(f"スイッチングDC-DC:   効率 {eta_switching*100:.0f}%（発熱 {P_in_sw-P_out:.1f}W）")
```

## 48V マイルドハイブリッドシステム

```python
# 最新の自動車では 12V + 48V のデュアル電源
system_48v = {
    "概要": "エンジンアシスト・回生ブレーキ用の補助電源システム",
    "採用車種": "Mercedes A-Class, BMW 5系, Audi A6 など",
    "メリット": [
        "回生制動で燃費 10〜15% 向上",
        "電動コンプレッサー・電動スーパーチャージャーが使える",
        "スタート/ストップの滑らかな動作",
        "完全EVより安価（バッテリー小型）",
    ],
    "コンポーネント": {
        "BSG":    "ベルト駆動スタータージェネレーター（12kW程度）",
        "48Vバッテリー": "リチウムイオン 0.5〜1kWh",
        "DC-DC変換器": "48V ↔ 12V 変換（双方向）",
    },
}

print("=== 48V マイルドハイブリッド ===")
print(f"概要: {system_48v['概要']}")
print("\nメリット:")
for benefit in system_48v["メリット"]:
    print(f"  ・{benefit}")
print("\nコンポーネント:")
for comp, desc in system_48v["コンポーネント"].items():
    print(f"  {comp}: {desc}")

# 回生エネルギーの計算
m = 1500   # kg
v1 = 100 / 3.6  # 100km/h → m/s
v2 = 0
KE = 0.5 * m * (v1**2 - v2**2)   # 運動エネルギー [J]
eta_regen = 0.60   # 回収効率
E_recovered = KE * eta_regen
print(f"\n100→0km/hブレーキの回生エネルギー: {E_recovered/3600:.2f} Wh")
```
