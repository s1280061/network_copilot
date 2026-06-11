---
slug: hypothesis-testing
title: 仮説検定と検定力（t検定・ANOVA・サンプルサイズ設計）
level: 2
category: Python
related: [statistics, bayesian-statistics, linear-regression]
next: [bayesian-statistics]
tags: [hypothesis-testing, t-test, anova, p-value, power, sample-size, statistics]
---

## 概要
仮説検定は「差がある・効果がある」という主張を統計的に評価する手法です。しかし p 値の誤解や検定力の無視は「再現性の危機」の主因です。p 値・効果量・検定力・サンプルサイズ設計を正しく理解することが実務では不可欠です。

## 仮説検定の基本構造

```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# 仮説検定の手順
# 1. H0（帰無仮説）と H1（対立仮説）を設定
# 2. 有意水準 α を決める（慣習的に 0.05）
# 3. 検定統計量を計算
# 4. p 値を求める
# 5. p < α なら H0 を棄却

# 例: 新しい工場ラインの部品寸法（μ=10mm が規格）
rng = np.random.default_rng(42)
measurements = rng.normal(loc=10.15, scale=0.5, size=30)   # 実際はわずかにずれている

# 1標本 t 検定
t_stat, p_val = stats.ttest_1samp(measurements, popmean=10.0)
print(f"t 統計量: {t_stat:.3f}")
print(f"p 値:     {p_val:.4f}")
print(f"平均:     {measurements.mean():.3f}")
print(f"結論: {'H0 棄却（有意差あり）' if p_val < 0.05 else 'H0 保留（有意差なし）'}")
```

## 2標本 t 検定（独立・対応あり）

```python
# 独立2標本 t 検定: A グループ vs B グループ
group_a = rng.normal(100, 15, 50)   # 対照群（平均100）
group_b = rng.normal(108, 15, 50)   # 介入群（平均108）

# Welch の t 検定（等分散を仮定しない、推奨）
t, p = stats.ttest_ind(group_a, group_b, equal_var=False)
print(f"\n独立2標本 t 検定")
print(f"t = {t:.3f}, p = {p:.4f}")

# Cohen's d: 効果量（実務的な大きさの指標）
pooled_std = np.sqrt((group_a.std()**2 + group_b.std()**2) / 2)
cohens_d   = (group_b.mean() - group_a.mean()) / pooled_std
print(f"Cohen's d = {cohens_d:.3f}  ({'小' if abs(cohens_d)<0.5 else '中' if abs(cohens_d)<0.8 else '大'}効果)")

# 対応あり t 検定: 同一被験者の before/after
before = rng.normal(70, 10, 30)
after  = before + rng.normal(5, 3, 30)   # 処置で平均5点改善

t_paired, p_paired = stats.ttest_rel(before, after)
print(f"\n対応あり t 検定")
print(f"t = {t_paired:.3f}, p = {p_paired:.4f}")
print(f"平均変化: {(after - before).mean():.2f}")
```

## ANOVA（分散分析）

```python
# 3グループ以上の比較には ANOVA
# F 検定: グループ間分散 / グループ内分散

# 例: 3種類の施肥方法による収穫量
fertilizer_a = rng.normal(65, 8, 20)
fertilizer_b = rng.normal(72, 8, 20)
fertilizer_c = rng.normal(68, 8, 20)

f_stat, p_anova = stats.f_oneway(fertilizer_a, fertilizer_b, fertilizer_c)
print(f"一元配置 ANOVA: F = {f_stat:.3f}, p = {p_anova:.4f}")

# 有意なら多重比較（Tukey HSD）で差のあるペアを特定
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import pandas as pd

data   = np.concatenate([fertilizer_a, fertilizer_b, fertilizer_c])
groups = ["A"]*20 + ["B"]*20 + ["C"]*20

result = pairwise_tukeyhsd(data, groups, alpha=0.05)
print(result)
# → A-B: 有意差あり, A-C: 有意差なし, B-C: 有意差あり  など

# η² (eta-squared): ANOVA の効果量
ss_between = sum(
    len(g) * (g.mean() - data.mean())**2
    for g in [fertilizer_a, fertilizer_b, fertilizer_c]
)
ss_total = sum((data - data.mean())**2)
eta_sq = ss_between / ss_total
print(f"η² = {eta_sq:.3f}  ({'小' if eta_sq<0.06 else '中' if eta_sq<0.14 else '大'}効果)")
```

## p 値の罠と効果量

```python
# p < 0.05 でも実務的に意味がない差のケース

# 巨大サンプルでは微小差も「有意」になる
rng2 = np.random.default_rng(0)
for n in [30, 300, 3000, 30000]:
    a = rng2.normal(100.0, 15, n)
    b = rng2.normal(100.5, 15, n)   # 差は 0.5 点（実務的には無視できる）
    _, p = stats.ttest_ind(a, b)
    d = 0.5 / 15  # Cohen's d ≈ 0.033（非常に小さな効果）
    print(f"n={n:6d}: p={p:.4f}  {'★有意' if p<0.05 else '  非有意'}  Cohen's d={d:.3f}")

# 教訓: p 値だけで判断せず効果量も必ず報告する
# 効果量の目安 (Cohen, 1988)
# d: 小=0.2, 中=0.5, 大=0.8
# r: 小=0.1, 中=0.3, 大=0.5
# η²: 小=0.01, 中=0.06, 大=0.14
```

## 検定力（Power）分析

```python
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower

# 検定力 = P(H0 を正しく棄却 | H1 が真)
# = 1 − β（β: 第2種過誤の確率）
# 目標: 検定力 ≥ 0.80

power_analysis = TTestIndPower()

# 必要サンプルサイズの計算
effect_size = 0.5    # 中程度の効果
alpha       = 0.05
power       = 0.80

n_required = power_analysis.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power,
    ratio=1.0,          # 2グループ同数
    alternative="two-sided",
)
print(f"必要サンプルサイズ（各グループ）: {np.ceil(n_required):.0f}")

# 検定力曲線: サンプルサイズ vs 検定力
sample_sizes = np.arange(10, 200, 5)
powers = [
    power_analysis.power(effect_size=0.5, nobs1=n, alpha=0.05)
    for n in sample_sizes
]

plt.figure(figsize=(8, 4))
plt.plot(sample_sizes, powers)
plt.axhline(0.80, color="red", linestyle="--", label="目標検定力 0.80")
plt.axvline(n_required, color="orange", linestyle="--", label=f"必要 n={n_required:.0f}")
plt.xlabel("サンプルサイズ（各グループ）")
plt.ylabel("検定力")
plt.title("t 検定の検定力曲線（Cohen's d = 0.5）")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

## 多重検定の補正

```python
from statsmodels.stats.multitest import multipletests

# 複数の検定を同時に行うと偶然有意になる確率が上がる
# α=0.05 で20検定 → 少なくとも1つ偽陽性になる確率 ≈ 1-(0.95)^20 ≈ 64%

p_values = np.array([0.001, 0.008, 0.039, 0.041, 0.042,
                      0.060, 0.074, 0.205, 0.396, 0.510])

# Bonferroni 補正（保守的、独立検定向け）
reject_bon, p_bon, _, _ = multipletests(p_values, alpha=0.05, method="bonferroni")

# Benjamini-Hochberg 補正（FDR制御、探索的研究向け）
reject_bh,  p_bh,  _, _ = multipletests(p_values, alpha=0.05, method="fdr_bh")

print("元の p値  | Bonferroni | BH(FDR)")
print("-" * 40)
for p, r_b, r_h in zip(p_values, reject_bon, reject_bh):
    print(f"{p:.3f}      | {'棄却' if r_b else '保留'}       | {'棄却' if r_h else '保留'}")
```

## ノンパラメトリック検定

```python
# 正規分布を仮定できないデータ（順序尺度・外れ値が多い）に使う

data1 = np.array([2, 4, 6, 8, 10, 12, 100])  # 外れ値あり
data2 = np.array([1, 3, 5, 7, 9, 11, 13])

# Mann-Whitney U 検定（独立2標本 t 検定の代替）
u, p_mw = stats.mannwhitneyu(data1, data2, alternative="two-sided")
print(f"Mann-Whitney U: U={u}, p={p_mw:.4f}")

# Wilcoxon 符号順位検定（対応あり t 検定の代替）
w, p_wil = stats.wilcoxon(data1[:-1], data2[:-1])
print(f"Wilcoxon: W={w}, p={p_wil:.4f}")

# Kruskal-Wallis 検定（一元配置 ANOVA の代替）
g1 = [1, 2, 3, 4, 5]
g2 = [2, 4, 6, 8, 10]
g3 = [1, 3, 5, 7, 9]
h, p_kw = stats.kruskal(g1, g2, g3)
print(f"Kruskal-Wallis: H={h:.3f}, p={p_kw:.4f}")
```

## 検定の選び方チートシート

| データの状況 | 推奨検定 |
|---|---|
| 1標本、正規分布、μ=μ₀? | 1標本 t 検定 |
| 独立2群、正規分布 | Welch の t 検定 |
| 対応あり2群、正規分布 | 対応あり t 検定 |
| 独立2群、非正規 or 順序 | Mann-Whitney U |
| 対応あり2群、非正規 | Wilcoxon 符号順位 |
| 独立3群以上、正規分布 | 一元配置 ANOVA + Tukey HSD |
| 独立3群以上、非正規 | Kruskal-Wallis |
| カテゴリ変数の独立性 | カイ二乗検定 |
| 2変数の相関 | Pearson r (正規) / Spearman ρ (非正規) |
