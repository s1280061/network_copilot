---
slug: nvidia-gpu-lineup
title: NVIDIA GPU 製品ラインナップ完全ガイド
level: 2
category: DL
related: [gpu-architecture, deep-learning, pytorch, fine-tuning]
next: []
tags: [nvidia, gpu, rtx, a100, h100, geforce, datacenter, hardware]
---

## 概要
NVIDIAはゲーミング用GeForce・プロフェッショナル用RTX/Quadro・データセンター用A100/H100/B200と、用途別に複数の製品ラインを展開しています。「どのGPUを選べばいいか」を性能・VRAM・価格・用途で整理します。AI開発・研究・車載ADASなど目的に応じた選択指針をまとめました。

## NVIDIA GPUアーキテクチャの世代

```python
architectures = {
    "Kepler  (2012)": {"compute": "3.x", "notable": "GTX 680・Tesla K80"},
    "Maxwell (2014)": {"compute": "5.x", "notable": "GTX 980・Tesla M40"},
    "Pascal  (2016)": {"compute": "6.x", "notable": "GTX 1080・P100（初HBM2）"},
    "Volta   (2017)": {"compute": "7.0", "notable": "V100（初 Tensor コア）・Tesla V100"},
    "Turing  (2018)": {"compute": "7.5", "notable": "RTX 2080（初 RT コア）・T4"},
    "Ampere  (2020)": {"compute": "8.x", "notable": "RTX 3090・A100・A30"},
    "Ada Lovelace (2022)": {"compute": "8.9", "notable": "RTX 4090・RTX 4000 Ada"},
    "Hopper  (2022)": {"compute": "9.0", "notable": "H100・H200（データセンター専用）"},
    "Blackwell (2024)": {"compute": "10.x","notable": "B100・B200・RTX 5090・GB200 NVL72"},
}

print(f"{'世代':22s} {'Compute Capability':20s} {'代表製品'}")
print("-" * 70)
for gen, spec in architectures.items():
    print(f"{gen:22s} {spec['compute']:20s} {spec['notable']}")
```

## コンシューマー向け：GeForce RTX シリーズ

```python
geforce_gpus = {
    # RTX 50 系（Blackwell, 2025〜）
    "RTX 5090":  {"VRAM_GB": 32,  "CUDA": 21760, "TDP_W": 575, "price_usd": 1999, "gen": "Blackwell"},
    "RTX 5080":  {"VRAM_GB": 16,  "CUDA": 10752, "TDP_W": 360, "price_usd": 999,  "gen": "Blackwell"},
    "RTX 5070 Ti":{"VRAM_GB": 16, "CUDA": 8960,  "TDP_W": 300, "price_usd": 749,  "gen": "Blackwell"},
    "RTX 5070":  {"VRAM_GB": 12,  "CUDA": 6144,  "TDP_W": 250, "price_usd": 549,  "gen": "Blackwell"},
    # RTX 40 系（Ada Lovelace, 2022〜2024）
    "RTX 4090":  {"VRAM_GB": 24,  "CUDA": 16384, "TDP_W": 450, "price_usd": 1599, "gen": "Ada"},
    "RTX 4080 Super":{"VRAM_GB": 16,"CUDA": 10240,"TDP_W": 320,"price_usd": 999,  "gen": "Ada"},
    "RTX 4070 Ti Super":{"VRAM_GB":16,"CUDA":8448,"TDP_W": 285,"price_usd": 799,  "gen": "Ada"},
    "RTX 4070 Super":{"VRAM_GB": 12,"CUDA": 7168, "TDP_W": 220,"price_usd": 599,  "gen": "Ada"},
    "RTX 4070":  {"VRAM_GB": 12,  "CUDA": 5888,  "TDP_W": 200, "price_usd": 499,  "gen": "Ada"},
    "RTX 4060 Ti":{"VRAM_GB": 16, "CUDA": 4352,  "TDP_W": 165, "price_usd": 499,  "gen": "Ada"},
    "RTX 4060":  {"VRAM_GB": 8,   "CUDA": 3072,  "TDP_W": 115, "price_usd": 299,  "gen": "Ada"},
}

print("GeForce RTX シリーズ（コンシューマー向け）")
print(f"{'モデル':20s} {'VRAM':6s} {'CUDAコア':10s} {'TDP':8s} {'価格(USD)':10s} {'世代'}")
print("-" * 72)
for model, spec in geforce_gpus.items():
    print(f"{model:20s} {spec['VRAM_GB']:3d}GB  {spec['CUDA']:6d}    "
          f"{spec['TDP_W']:4d}W   ${spec['price_usd']:6d}   {spec['gen']}")
```

## プロフェッショナル向け：RTX / Quadro シリーズ

```python
pro_gpus = {
    # RTX Pro シリーズ（Blackwell, 2025）
    "RTX Pro 6000":     {"VRAM_GB": 96,  "ECC": True,  "use": "ハイエンドワークステーション・3D/DL"},
    # NVIDIA RTX Ada シリーズ（2022〜2024）
    "RTX 6000 Ada":     {"VRAM_GB": 48,  "ECC": True,  "use": "大規模モデル推論・3D/CAD"},
    "RTX 5000 Ada":     {"VRAM_GB": 32,  "ECC": True,  "use": "中規模ワークステーション"},
    "RTX 4500 Ada":     {"VRAM_GB": 24,  "ECC": True,  "use": "設計・シミュレーション"},
    "RTX 4000 Ada":     {"VRAM_GB": 20,  "ECC": True,  "use": "コンパクト・省電力"},
    "RTX 4000 SFF Ada": {"VRAM_GB": 20,  "ECC": True,  "use": "スモールフォームファクター"},
    # モバイル向け（ラップトップ）
    "RTX 5000 Ada (Mobile)": {"VRAM_GB": 16, "ECC": False, "use": "モバイルワークステーション"},
}

print("\nNVIDIA RTX プロフェッショナル（旧 Quadro）")
print(f"{'モデル':25s} {'VRAM':6s} {'ECC':5s} {'主な用途'}")
print("-" * 70)
for model, spec in pro_gpus.items():
    ecc = "✅" if spec["ECC"] else "❌"
    print(f"{model:25s} {spec['VRAM_GB']:3d}GB  {ecc:5s} {spec['use']}")

print("\n💡 ECC（Error Correcting Code）メモリ: ビット反転エラーを自動訂正 → 科学計算・医療・自動運転に必須")
```

## データセンター・AI向け：A/H/B シリーズ

```python
dc_gpus = {
    # Blackwell（2024〜）
    "B200 SXM":  {
        "VRAM_GB": 192, "VRAM_type": "HBM3e",
        "FP8_TFLOPS": 4500, "FP16_TFLOPS": 2250,
        "NVLink": "NVLink 5.0 × 18",
        "TDP_W": 1000, "form": "SXM", "note": "最新フラッグシップ",
    },
    "B100 SXM":  {
        "VRAM_GB": 192, "VRAM_type": "HBM3e",
        "FP8_TFLOPS": 3500, "FP16_TFLOPS": 1750,
        "NVLink": "NVLink 5.0",
        "TDP_W": 700,  "form": "SXM", "note": "B200の省電力版",
    },
    "H200 SXM":  {
        "VRAM_GB": 141, "VRAM_type": "HBM3e",
        "FP8_TFLOPS": 1979, "FP16_TFLOPS": 989,
        "NVLink": "NVLink 4.0",
        "TDP_W": 700,  "form": "SXM", "note": "H100+大容量HBM3e",
    },
    "H100 SXM":  {
        "VRAM_GB": 80,  "VRAM_type": "HBM2e",
        "FP8_TFLOPS": 1979, "FP16_TFLOPS": 989,
        "NVLink": "NVLink 4.0 × 18",
        "TDP_W": 700,  "form": "SXM", "note": "LLM学習の現標準",
    },
    "H100 PCIe": {
        "VRAM_GB": 80,  "VRAM_type": "HBM2e",
        "FP8_TFLOPS": 1513, "FP16_TFLOPS": 756,
        "NVLink": "なし",
        "TDP_W": 350,  "form": "PCIe", "note": "標準サーバー搭載",
    },
    "A100 SXM":  {
        "VRAM_GB": 80,  "VRAM_type": "HBM2e",
        "FP8_TFLOPS": None, "FP16_TFLOPS": 312,
        "NVLink": "NVLink 3.0 × 12",
        "TDP_W": 400,  "form": "SXM", "note": "現役（GPT-3 時代の標準）",
    },
    "A100 40GB": {
        "VRAM_GB": 40,  "VRAM_type": "HBM2",
        "FP8_TFLOPS": None, "FP16_TFLOPS": 312,
        "NVLink": "NVLink 3.0",
        "TDP_W": 400,  "form": "SXM", "note": "A100 40GB版",
    },
    "L40S":      {
        "VRAM_GB": 48,  "VRAM_type": "GDDR6",
        "FP8_TFLOPS": 733, "FP16_TFLOPS": 362,
        "NVLink": "なし",
        "TDP_W": 350,  "form": "PCIe", "note": "推論・マルチメディア特化",
    },
    "A10":       {
        "VRAM_GB": 24,  "VRAM_type": "GDDR6",
        "FP8_TFLOPS": None, "FP16_TFLOPS": 125,
        "NVLink": "なし",
        "TDP_W": 150,  "form": "PCIe", "note": "推論・入門データセンター",
    },
}

print("NVIDIA データセンター GPU")
print(f"{'モデル':13s} {'VRAM':8s} {'FP16 TF':10s} {'TDP':7s} {'形状':7s} {'備考'}")
print("-" * 75)
for model, spec in dc_gpus.items():
    fp16 = f"{spec['FP16_TFLOPS']} TF" if spec['FP16_TFLOPS'] else "-"
    print(f"{model:13s} {spec['VRAM_GB']:4d}GB  {fp16:10s} "
          f"{spec['TDP_W']:4d}W  {spec['form']:7s} {spec['note']}")
```

## 用途別 GPU 選択ガイド

```python
selection_guide = {
    "個人ホビー / 入門機械学習": {
        "推奨": "RTX 4070 / RTX 5070",
        "VRAM": "12〜16 GB",
        "理由": "Stable Diffusion・ファインチューニング（LoRA）・中規模モデル推論",
        "価格帯": "5〜10 万円",
    },
    "研究者 / 本格的なモデル開発": {
        "推奨": "RTX 4090 / RTX 5090",
        "VRAM": "24〜32 GB",
        "理由": "LLM 7B 程度の QLoRA 学習・大規模バッチの実験",
        "価格帯": "20〜30 万円",
    },
    "スタートアップ / 中規模学習": {
        "推奨": "A100 PCIe 80GB / H100 PCIe",
        "VRAM": "80 GB",
        "理由": "13B〜30B モデルの学習・推論サービング",
        "価格帯": "クラウドで $2〜$4/時間",
    },
    "大規模 LLM 学習（GPT-4 規模）": {
        "推奨": "H100 SXM × 数百〜数千台",
        "VRAM": "80 GB × N",
        "理由": "NVLink/NVSwitch でノード間を高速接続・テンソル並列",
        "価格帯": "H100 クラスター: $10M〜（数十億円）",
    },
    "推論サービング（API 提供）": {
        "推奨": "L40S / H100 PCIe / A10",
        "VRAM": "24〜80 GB",
        "理由": "コスパ重視・PCIe で標準サーバーに搭載可",
        "価格帯": "クラウドで $0.8〜$3.0/時間",
    },
    "エッジ / 自動車 ADAS": {
        "推奨": "Jetson Orin / Drive Thor",
        "VRAM": "16〜64 GB（共有）",
        "理由": "低消費電力・車載グレード・機能安全（ISO 26262）",
        "価格帯": "Jetson AGX Orin: $500〜",
    },
}

for use_case, spec in selection_guide.items():
    print(f"\n【{use_case}】")
    print(f"  推奨 GPU: {spec['推奨']}")
    print(f"  VRAM:     {spec['VRAM']}")
    print(f"  理由:     {spec['理由']}")
    print(f"  価格感:   {spec['価格帯']}")
```

## NVLink と GPU 並列学習

```python
# NVLink: GPU間の高速インターコネクト
nvlink_specs = {
    "NVLink 2.0 (Volta)":  {"bandwidth_GBs": 300,  "links": 6},
    "NVLink 3.0 (Ampere)": {"bandwidth_GBs": 600,  "links": 12},
    "NVLink 4.0 (Hopper)": {"bandwidth_GBs": 900,  "links": 18},
    "NVLink 5.0 (Blackwell)":{"bandwidth_GBs": 1800, "links": 18},
    "PCIe 5.0 x16（参考）": {"bandwidth_GBs": 128, "links": 1},
}

print("NVLink 世代別帯域幅（双方向）")
for name, spec in nvlink_specs.items():
    bar = "█" * int(spec["bandwidth_GBs"] / 60)
    print(f"  {name:28s}: {spec['bandwidth_GBs']:5d} GB/s  {bar}")

print("""
\nGPU 並列学習の戦略:

  データ並列（DDP）
  ├── 各 GPU が同じモデルを持ち、異なるデータを処理
  ├── 勾配を AllReduce で集約
  └── PyTorch: DistributedDataParallel

  テンソル並列（Tensor Parallelism）
  ├── 重み行列を GPU 間で分割
  ├── NVLink の高帯域幅が必須
  └── Megatron-LM

  パイプライン並列（Pipeline Parallelism）
  ├── モデルの層を GPU に順番に配置
  └── GPipe / PipeDream

  ZeRO（DeepSpeed）
  ├── パラメータ・勾配・オプティマイザ状態を全 GPU に分散
  └── ZeRO-3: 全て分散 → GPU 数に比例した VRAM 削減
""")
```

## 自動車向け GPU：NVIDIA DRIVE / Jetson

```python
automotive_gpus = {
    "Jetson Nano":      {"TOPS": 0.5,  "TDP_W": 5,   "use": "教育・入門エッジAI"},
    "Jetson Orin Nano": {"TOPS": 40,   "TDP_W": 10,  "use": "スマートカメラ・ドローン"},
    "Jetson AGX Orin":  {"TOPS": 275,  "TDP_W": 60,  "use": "自律ロボット・産業AGV"},
    "DRIVE Orin":       {"TOPS": 254,  "TDP_W": 45,  "use": "L2+自動運転（ISO 26262 ASIL-D）"},
    "DRIVE Thor":       {"TOPS": 2000, "TDP_W": 150, "use": "L4自動運転・中央コンピュータ"},
    "DRIVE Hyperion 9": {"TOPS": 2000, "TDP_W": None, "use": "完全自動運転プラットフォーム"},
}

print("NVIDIA 車載/エッジ AI アクセラレーター")
print(f"{'モデル':20s} {'AI性能':10s} {'TDP':8s} {'用途'}")
print("-" * 70)
for model, spec in automotive_gpus.items():
    tdp = f"{spec['TDP_W']}W" if spec['TDP_W'] else "-"
    print(f"{model:20s} {spec['TOPS']:6.0f} TOPS  {tdp:8s} {spec['use']}")

print("\n採用車種（DRIVE Orin）: Mercedes-Benz EQS, Volvo EX90, Li Auto L9 など")
print("採用車種（DRIVE Thor）: 次世代電動車（2025年〜 量産予定）")
```

## クラウド GPU サービス比較

```python
cloud_gpu = {
    "AWS (p4d.24xlarge)":  {"GPU": "A100 × 8",  "VRAM": "320GB", "price_hr": 32.77},
    "AWS (p5.48xlarge)":   {"GPU": "H100 × 8",  "VRAM": "640GB", "price_hr": 98.32},
    "GCP (a3-highgpu-8g)": {"GPU": "H100 × 8",  "VRAM": "640GB", "price_hr": 32.77},
    "Azure NC H100 v5":    {"GPU": "H100 × 8",  "VRAM": "640GB", "price_hr": 36.00},
    "Lambda Cloud":        {"GPU": "H100 × 8",  "VRAM": "640GB", "price_hr": 21.44},
    "RunPod (Secure)":     {"GPU": "H100 SXM×8","VRAM": "640GB", "price_hr": 29.92},
    "Vast.ai (Interruptible)": {"GPU": "H100 × 1","VRAM": "80GB", "price_hr": 2.49},
}

print("クラウド GPU 料金比較（2024年末時点・変動あり）")
print(f"{'サービス':30s} {'GPU':16s} {'VRAM':8s} {'$/hr'}")
print("-" * 65)
for service, spec in cloud_gpu.items():
    print(f"{service:30s} {spec['GPU']:16s} {spec['VRAM']:8s} ${spec['price_hr']:.2f}")

# コスト計算
print("\n70B モデルの Full Fine-tuning（A100 × 8 想定, 10 時間）:")
cost = 32.77 * 10
print(f"  AWS p4d.24xlarge: ${cost:.0f}（約 {cost*150:.0f} 円）")
