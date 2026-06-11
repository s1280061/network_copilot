---
slug: gpu-architecture
title: GPUの仕組み（並列処理・CUDAコア・メモリ階層）
level: 2
category: DL
related: [deep-learning, pytorch, cnn, nvidia-gpu-lineup]
next: [nvidia-gpu-lineup]
tags: [gpu, cuda, parallel-computing, nvidia, hardware, deep-learning]
---

## 概要
GPU（Graphics Processing Unit）はもともとゲームのグラフィックス描画用に設計されましたが、行列演算の並列処理能力がディープラーニングに最適でした。CPUが「少数の賢いコア」で複雑なタスクをこなすのに対し、GPUは「数千の単純なコア」で同じ計算を並列に実行します。

## CPU vs GPU のアーキテクチャ比較

```
CPU（Intel Core i9）            GPU（NVIDIA RTX 4090）
┌─────────────────┐            ┌──────────────────────────────┐
│ コア × 24       │            │ CUDA コア × 16,384            │
│ 高クロック      │            │ Tensor コア × 512             │
│ 大容量キャッシュ │            │ SM（Streaming Multiprocessor）│
│ 分岐予測・OoO   │            │   × 128                      │
│ DDR5 メモリ     │            │ GDDR6X 24GB 1008GB/s          │
└─────────────────┘            └──────────────────────────────┘

CPU の強み: 逐次処理・複雑な制御フロー・低レイテンシ
GPU の強み: 並列処理・行列演算・大規模スループット
```

```python
import numpy as np
import time

# CPU vs GPU の速度差を実感するコード
# 行列積 (4096 × 4096) の計算

def benchmark_matmul():
    N = 4096
    A = np.random.randn(N, N).astype(np.float32)
    B = np.random.randn(N, N).astype(np.float32)

    # CPU（NumPy）
    t0 = time.perf_counter()
    C_cpu = A @ B
    t_cpu = time.perf_counter() - t0

    print(f"CPU (NumPy):   {t_cpu*1000:.1f} ms")

    try:
        import torch
        A_gpu = torch.from_numpy(A).cuda()
        B_gpu = torch.from_numpy(B).cuda()

        # GPU ウォームアップ
        _ = A_gpu @ B_gpu
        torch.cuda.synchronize()

        t0 = time.perf_counter()
        C_gpu = A_gpu @ B_gpu
        torch.cuda.synchronize()   # GPU 完了を待つ
        t_gpu = time.perf_counter() - t0

        print(f"GPU (CUDA):    {t_gpu*1000:.2f} ms")
        print(f"高速化倍率:    {t_cpu/t_gpu:.0f}x")
    except Exception as e:
        print(f"GPU 未使用: {e}")

benchmark_matmul()
```

## CUDA 実行モデル

```
GPU の実行階層:

Grid（カーネル全体）
└── Block（スレッドブロック, 最大 1024 スレッド）
    └── Thread（1つの計算単位）

例: 1024要素の配列に +1 する処理

  Grid = (4 blocks)
  Block = (256 threads)
  → 合計 4 × 256 = 1024 スレッドが同時に動く
```

```python
# CUDA カーネルのコンセプト（Python CuPy で確認）
# pip install cupy-cuda12x

try:
    import cupy as cp

    # CuPy: NumPy と同じ API で GPU を使う
    N = 10_000_000  # 1000万要素

    x_gpu = cp.random.randn(N, dtype=cp.float32)
    y_gpu = cp.random.randn(N, dtype=cp.float32)

    # GPU で要素ごとの演算（全スレッドが同時に動く）
    t0 = time.perf_counter()
    z_gpu = cp.sqrt(x_gpu**2 + y_gpu**2)
    cp.cuda.Stream.null.synchronize()
    t_gpu = time.perf_counter() - t0

    # CPU で同じ計算
    x_cpu = cp.asnumpy(x_gpu)
    y_cpu = cp.asnumpy(y_gpu)
    t0 = time.perf_counter()
    z_cpu = np.sqrt(x_cpu**2 + y_cpu**2)
    t_cpu = time.perf_counter() - t0

    print(f"CPU: {t_cpu*1000:.1f} ms")
    print(f"GPU: {t_gpu*1000:.1f} ms  ({t_cpu/t_gpu:.0f}x 高速)")

except ImportError:
    print("CuPy未インストール（pip install cupy-cuda12x）")
```

## SM（Streaming Multiprocessor）の構造

```
SM（Streaming Multiprocessor）1個の中身（Hopper アーキテクチャ）:

  ┌──────────────────────────────────────────┐
  │ Warp Scheduler × 4                       │
  │ Dispatch Unit  × 4                       │
  ├────────────────┬─────────────────────────┤
  │ CUDA Core × 128│ Tensor Core × 4（FP16） │
  │ (FP32 / INT32) │ （行列積を1クロックで）  │
  ├────────────────┴─────────────────────────┤
  │ Register File  256KB                     │
  │ L1 Cache / Shared Memory  256KB          │
  │ LD/ST Unit × 32   SFU × 16              │
  └──────────────────────────────────────────┘

Warp = 32 スレッドの束（GPU の基本スケジューリング単位）
→ 32スレッドが必ず同じ命令を同時実行（SIMT: Single Instruction Multiple Threads）
```

```python
# Warp の概念を Python で確認
import torch

if torch.cuda.is_available():
    # CUDA デバイス情報の取得
    props = torch.cuda.get_device_properties(0)
    print(f"GPU: {props.name}")
    print(f"SM 数: {props.multi_processor_count}")
    print(f"CUDA コア数（概算）: {props.multi_processor_count * 128}")
    print(f"Warp サイズ: {32} threads")
    print(f"最大スレッド/ブロック: {props.max_threads_per_block}")
    print(f"VRAM: {props.total_memory / 1e9:.1f} GB")
    print(f"メモリ帯域幅（概算）: 利用 nvidia-smi --query-gpu=memory.bandwidth")

# Warp divergence（パフォーマンスに影響する注意点）
print("\n⚠️ Warp Divergence の例:")
print("""
// 悪い例（分岐でwarpが分裂する）
if (threadIdx.x % 2 == 0) {
    // 偶数スレッドだけ実行 → 奇数スレッドは待機
    result = a * b;
} else {
    // 奇数スレッドだけ実行 → 偶数スレッドは待機
    result = a + b;
}
// → 本来同時実行できる 32 スレッドが直列化してしまう！
""")
```

## GPU メモリ階層

```python
# GPU のメモリ階層（速度と容量のトレードオフ）
memory_hierarchy = {
    "レジスタ": {
        "帯域幅": "〜 28 TB/s",
        "レイテンシ": "1 クロック",
        "サイズ": "256 KB / SM",
        "用途": "スレッドローカル変数",
    },
    "L1 / Shared Memory": {
        "帯域幅": "〜 20 TB/s",
        "レイテンシ": "〜 20 クロック",
        "サイズ": "256 KB / SM",
        "用途": "スレッドブロック内でのデータ共有・タイリング",
    },
    "L2 Cache": {
        "帯域幅": "〜 5 TB/s",
        "レイテンシ": "〜 200 クロック",
        "サイズ": "60 MB（H100 SXM）",
        "用途": "DRAM アクセスのキャッシュ",
    },
    "HBM2e / GDDR6X（VRAM）": {
        "帯域幅": "〜 3.35 TB/s（H100 SXM）",
        "レイテンシ": "〜 600 クロック",
        "サイズ": "80 GB（H100 SXM）",
        "用途": "モデルパラメータ・活性化・勾配の格納",
    },
    "CPU RAM（Host Memory）": {
        "帯域幅": "〜 50 GB/s",
        "レイテンシ": "数千クロック + PCIe 転送",
        "サイズ": "DDR5 数百 GB",
        "用途": "データセット・チェックポイント",
    },
}

print(f"{'階層':25s} {'帯域幅':18s} {'サイズ':20s} {'用途'}")
print("-" * 90)
for name, spec in memory_hierarchy.items():
    print(f"{name:25s} {spec['帯域幅']:18s} {spec['サイズ']:20s} {spec['用途']}")
```

## Tensor コアと混合精度学習

```python
# Tensor コアは FP16/BF16 の行列積を専用ハードウェアで超高速化
# A100: 312 TFLOPS (FP16 with sparsity)
# H100: 1,979 TFLOPS (FP8 with sparsity)

import torch

def mixed_precision_example():
    """PyTorch の自動混合精度（AMP）"""
    if not torch.cuda.is_available():
        print("CUDA が必要です")
        return

    model = torch.nn.Sequential(
        torch.nn.Linear(1024, 4096),
        torch.nn.GELU(),
        torch.nn.Linear(4096, 1024),
    ).cuda()

    optimizer = torch.optim.Adam(model.parameters())
    scaler    = torch.cuda.amp.GradScaler()   # FP16 の勾配スケーリング

    x = torch.randn(64, 1024, device="cuda")

    # FP32 での通常学習
    t0 = time.perf_counter()
    for _ in range(100):
        y = model(x)
        loss = y.sum()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    torch.cuda.synchronize()
    t_fp32 = time.perf_counter() - t0

    # FP16 混合精度（Tensor コアを活用）
    t0 = time.perf_counter()
    for _ in range(100):
        with torch.cuda.amp.autocast():   # FP16 でフォワード
            y = model(x)
            loss = y.sum()
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
    torch.cuda.synchronize()
    t_fp16 = time.perf_counter() - t0

    print(f"FP32: {t_fp32*1000:.1f} ms")
    print(f"FP16 (AMP): {t_fp16*1000:.1f} ms  ({t_fp32/t_fp16:.1f}x 高速)")

mixed_precision_example()
```

## GPU 使用率のモニタリング

```python
import subprocess

def gpu_monitor():
    """nvidia-smi でGPU状態を確認"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        for i, line in enumerate(result.stdout.strip().split("\n")):
            name, util, mem_used, mem_total, temp, power = [x.strip() for x in line.split(",")]
            print(f"GPU {i}: {name}")
            print(f"  使用率:     {util}%")
            print(f"  VRAM:       {mem_used}/{mem_total} MiB ({int(mem_used)/int(mem_total)*100:.0f}%)")
            print(f"  温度:        {temp}°C")
            print(f"  消費電力:   {float(power):.0f} W")
    except FileNotFoundError:
        print("nvidia-smi が見つかりません")

# PyTorch でのメモリ確認
if torch.cuda.is_available():
    print(f"割当済み VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")
    print(f"キャッシュ済み: {torch.cuda.memory_reserved()/1e9:.2f} GB")
    print(f"最大使用量:    {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
```

## VRAM が足りないときの対処法

```python
vram_tips = {
    "バッチサイズを減らす": {
        "効果": "VRAM 線形削減",
        "デメリット": "学習が不安定になりやすい",
        "代替": "Gradient Accumulation で等価バッチサイズを維持",
    },
    "混合精度 (FP16/BF16)": {
        "効果": "VRAM 約 50% 削減",
        "コード": "torch.cuda.amp.autocast()",
        "備考": "精度低下はほぼなし、Tensor コア活用で高速化も",
    },
    "Gradient Checkpointing": {
        "効果": "活性化メモリを大幅削減（最大 O(√n) まで）",
        "コード": "model.gradient_checkpointing_enable()",
        "デメリット": "再計算により学習速度 30〜40% 低下",
    },
    "Flash Attention": {
        "効果": "Transformer の Attention 計算を IO-efficient に",
        "コード": "pip install flash-attn",
        "効果量": "Attention の VRAM を大幅削減・高速化",
    },
    "量子化 (INT8/INT4)": {
        "効果": "推論時は VRAM を 50〜75% 削減",
        "コード": "bitsandbytes ライブラリ",
        "備考": "学習には QLoRA を使用",
    },
    "モデル並列 / DeepSpeed": {
        "効果": "複数 GPU にモデルを分散",
        "コード": "deepspeed / accelerate",
        "備考": "ZeRO-3 でパラメータ・勾配・オプティマイザ状態を分散",
    },
}

print("VRAM 不足への対処法:")
for method, info in vram_tips.items():
    print(f"\n【{method}】")
    print(f"  効果: {info['効果']}")
    if 'コード' in info: print(f"  実装: {info['コード']}")
```
