---
slug: v2x-wireless
title: 車載無線通信（V2X・DSRC・C-V2X）
level: 3
category: Wireless
related: [lte-5g, wifi, wireless-basics, v2x, automotive-electrical]
next: []
tags: [v2x, dsrc, c-v2x, vehicle-to-vehicle, automotive, safety, wireless]
---

## 概要
V2X（Vehicle-to-Everything）は車と「あらゆるもの」が通信する技術です。車車間（V2V）・車路間（V2I）・車人間（V2P）・車クラウド（V2N）からなり、信号情報取得・衝突回避・自動運転の重要インフラです。DSRC（専用狭域通信）とC-V2X（セルラーV2X）の2方式があります。

## V2X の種類と応用

```python
v2x_types = {
    "V2V（Vehicle to Vehicle）": {
        "相手": "他車両",
        "用途": ["前方衝突警告", "緊急ブレーキ通知", "死角車両検出"],
        "必要遅延": "< 100ms",
        "通信距離": "300〜1000m",
    },
    "V2I（Vehicle to Infrastructure）": {
        "相手": "信号機・道路センサー・標識",
        "用途": ["SPAT（信号位相・タイミング情報）", "速度勧告", "工事情報"],
        "必要遅延": "< 100ms",
        "通信距離": "300〜1000m",
    },
    "V2P（Vehicle to Pedestrian）": {
        "相手": "歩行者・自転車のスマートフォン",
        "用途": ["横断歩道手前の歩行者警告", "自転車接近警告"],
        "必要遅延": "< 50ms",
        "通信距離": "100〜200m",
    },
    "V2N（Vehicle to Network）": {
        "相手": "クラウドサーバー",
        "用途": ["HDマップ更新", "交通情報", "OTA更新", "フリートマネジメント"],
        "必要遅延": "< 1000ms",
        "通信距離": "全国（セルラー）",
    },
}

for type_name, spec in v2x_types.items():
    print(f"【{type_name}】")
    print(f"  用途: {', '.join(spec['用途'])}")
    print(f"  要求遅延: {spec['必要遅延']}  距離: {spec['通信距離']}")
    print()
```

## DSRC（専用狭域通信）/ IEEE 802.11p

```python
import numpy as np

# DSRC は 5.9GHz 帯（5850〜5925MHz）を使う
# IEEE 802.11p = OCB（Outside the Context of a BSS）通信モード
# 接続確立なしで即座にブロードキャスト可能

dsrc_spec = {
    "周波数帯":   "5.9 GHz（5850〜5925 MHz）",
    "帯域幅":    "10 MHz チャンネル（75MHz帯域を7ch分割）",
    "変調方式":   "OFDM（IEEE 802.11a 準拠）",
    "最大速度":  "27 Mbps（10MHz ch）",
    "遅延":      "< 2ms（接続確立不要）",
    "到達距離":  "300〜1000m（見通し）",
    "採用地域":  "日本（VICS/ETC2.0）、米国（WAVE）、EU（ITS-G5）",
}

print("=== DSRC（IEEE 802.11p）仕様 ===")
for k, v in dsrc_spec.items():
    print(f"  {k}: {v}")

# チャンネル割当（米国 WAVE 規格）
wave_channels = {
    "CH172（5.86GHz）": "Control Channel（CCH）- 安全メッセージ専用",
    "CH174（5.87GHz）": "Service Channel（SCH）",
    "CH176（5.88GHz）": "Service Channel",
    "CH178（5.89GHz）": "Control Channel（CCH）",
    "CH180（5.90GHz）": "Service Channel",
    "CH182（5.91GHz）": "Service Channel",
    "CH184（5.92GHz）": "Service Channel",
}
print("\n米国 WAVE チャンネル割当:")
for ch, desc in wave_channels.items():
    print(f"  {ch}: {desc}")
```

## BSM（Basic Safety Message）

```python
import json

# BSM は V2V の基本安全メッセージ（SAE J2735 規格）
# 10Hz（100ms間隔）でブロードキャスト

def generate_bsm(vehicle_id, lat, lon, speed_ms, heading_deg, accel_ms2):
    """SAE J2735 BSMの簡略版"""
    return {
        "msgID": "BSM",
        "coreData": {
            "id":       f"{vehicle_id:08X}",    # 一時的な匿名ID
            "secMark": 0,                        # ミリ秒タイムスタンプ
            "lat":     lat,
            "lon":     lon,
            "elev":    100,                      # 標高 [0.1m]
            "accuracy": {"semiMajor": 200, "semiMinor": 200},
            "speed":   int(speed_ms * 50),       # 0.02m/s 単位
            "heading": int(heading_deg * 80),    # 0.0125度 単位
            "accel":   {"long": int(accel_ms2 * 100)},  # 0.01m/s² 単位
            "brakes":  {"wheelBrakes": "0000"},
            "size":    {"width": 200, "length": 490},   # cm
        }
    }

bsm = generate_bsm(
    vehicle_id=0xDEADBEEF,
    lat=35.6812,
    lon=139.7671,
    speed_ms=13.9,    # 50km/h
    heading_deg=90,
    accel_ms2=0.0,
)
print("BSM（Basic Safety Message）サンプル:")
print(json.dumps(bsm, indent=2))
```

## C-V2X（Cellular V2X）vs DSRC

```python
comparison = {
    "方式":          ["C-V2X Mode 4（PC5）",    "DSRC/IEEE 802.11p"],
    "規格":          ["3GPP Rel.14/16",          "IEEE 802.11p / ETSI ITS-G5"],
    "周波数":        ["5.9GHz（PC5）or LTE",     "5.9GHz専用"],
    "接続確立":      ["不要（ブロードキャスト）",  "不要（OCBモード）"],
    "遅延":          ["< 5ms（理論）",            "< 2ms（実績）"],
    "距離":          ["〜500m（PC5）",            "〜1000m"],
    "インフラ依存":  ["不要（サイドリンク）",      "不要"],
    "セルラー連携":  ["可能（V2N統合）",          "別途LTE/5G必要"],
    "普及状況":      ["Audi/Ford/韓国自動車",     "日本ETC2.0・米WAVE"],
    "将来性":        ["5G NR-V2X（Rel.16）",      "DSRC+ITS-G5で継続"],
}

print("C-V2X vs DSRC 比較")
print(f"{'項目':12s} {'C-V2X':28s} {'DSRC':28s}")
print("-" * 70)
for i, item in enumerate(comparison["方式"]):
    pass  # ヘッダーは除く

for key in list(comparison.keys())[1:]:
    print(f"{key:12s} {comparison[key][0]:28s} {comparison[key][1]}")
```

## V2X の安全ユースケース実装例

```python
# 前方衝突警告（FCW: Forward Collision Warning）
def fcw_check(ego_speed_ms, ego_pos, other_pos, other_speed_ms, reaction_time=1.5):
    """
    前方車両との衝突時間（TTC）を計算して警告
    ego: 自車, other: 前方車両
    """
    # 相対速度（自車が前方車に近づく速度）
    relative_speed = ego_speed_ms - other_speed_ms

    if relative_speed <= 0:
        return None, "安全（前方車の方が速い）"

    # 2点間の距離（簡易）
    distance = np.sqrt((ego_pos[0] - other_pos[0])**2 +
                       (ego_pos[1] - other_pos[1])**2)

    # TTC（衝突時間）
    ttc = distance / relative_speed

    # 制動距離（v²/2a, a=7m/s²）
    braking_dist = ego_speed_ms**2 / (2 * 7)
    safe_dist = braking_dist + reaction_time * ego_speed_ms

    if ttc < 1.5:
        return ttc, "🔴 緊急警告: 衝突直前"
    elif distance < safe_dist:
        return ttc, "🟡 注意: 車間距離不足"
    else:
        return ttc, "🟢 安全"

# シミュレーション
scenarios = [
    ("高速道路（両車110km/h等速）",   30.6, (0,0), (50,0),  30.6),
    ("前方急ブレーキ（自100km/h前60km/h）", 27.8, (0,0), (40,0), 16.7),
    ("追突直前（自100km/h前静止）",   27.8, (0,0), (30,0),  0.0),
]
for name, v_ego, pos_ego, pos_other, v_other in scenarios:
    ttc, status = fcw_check(v_ego, pos_ego, pos_other, v_other)
    ttc_str = f"{ttc:.1f}s" if ttc else "-"
    print(f"{name}: TTC={ttc_str} → {status}")
```
