---
slug: statistics
title: 統計学の基礎（確率・分布・検定）
level: 2
category: Python
related: [numpy, pandas, data-analysis, seaborn]
next: [data-analysis]
tags: [statistics, python, scipy, data-science]
---

## 概要
統計学はデータから「確かなこと」と「不確かなこと」を区別する学問です。機械学習の精度評価・A/Bテスト・センサーデータ分析など、データを扱うすべての場面の基盤となります。PythonではSciPyとStatsmodelsが主要ライブラリです。

## 基本統計量

```python
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(42)
data = np.random.normal(loc=170, scale=8, size=300)   # 身長データ（cm）

print(f"平均:     {np.mean(data):.2f}")
print(f"中央値:   {np.median(data):.2f}")
print(f"標準偏差: {np.std(data, ddof=1):.2f}")   # 不偏標準偏差
print(f"分散:     {np.var(data, ddof=1):.2f}")
print(f"歪度:     {stats.skew(data):.4f}")         # 0 = 対称
print(f"尖度:     {stats.kurtosis(data):.4f}")     # 0 = 正規分布
print(f"95%信頼区間: {stats.t.interval(0.95, len(data)-1, np.mean(data), stats.sem(data))}")
```

## 主要な確率分布

```python
fig, axes = plt.subplots(2, 3, figsize=(14, 8))

x = np.linspace(-4, 4, 300)

# 正規分布（連続）
axes[0,0].plot(x, stats.norm.pdf(x), color="steelblue", lw=2)
axes[0,0].set_title("正規分布 N(0,1)")

# t分布（小標本）
for df in [1, 5, 30]:
    axes[0,1].plot(x, stats.t.pdf(x, df), label=f"df={df}", lw=2)
axes[0,1].plot(x, stats.norm.pdf(x), "k--", label="Normal", lw=1.5)
axes[0,1].set_title("t分布")
axes[0,1].legend(fontsize=8)

# カイ二乗分布
x_chi = np.linspace(0, 20, 300)
for df in [2, 4, 8]:
    axes[0,2].plot(x_chi, stats.chi2.pdf(x_chi, df), label=f"k={df}", lw=2)
axes[0,2].set_title("カイ二乗分布")
axes[0,2].legend(fontsize=8)

# ポアソン分布（離散）
k = np.arange(0, 20)
for lam in [1, 4, 8]:
    axes[1,0].bar(k + lam*0.1, stats.poisson.pmf(k, lam), width=0.3, alpha=0.6, label=f"λ={lam}")
axes[1,0].set_title("ポアソン分布")
axes[1,0].legend(fontsize=8)

# 二項分布
k = np.arange(0, 21)
for p in [0.3, 0.5, 0.7]:
    axes[1,1].plot(k, stats.binom.pmf(k, 20, p), "o-", label=f"p={p}", lw=2)
axes[1,1].set_title("二項分布 n=20")
axes[1,1].legend(fontsize=8)

# 一様分布
axes[1,2].fill_between([0, 1], [1, 1], color="steelblue", alpha=0.5)
axes[1,2].set_ylim(0, 1.5)
axes[1,2].set_title("一様分布 U(0,1)")

plt.tight_layout()
plt.show()
```

## 仮説検定の流れ

```mermaid
graph TD
  A[帰無仮説 H₀ を設定<br/>「差がない」] --> B[有意水準 α を決める<br/>0.05 が慣例]
  B --> C[検定統計量を計算]
  C --> D[p値を求める]
  D --> E{p値 < α?}
  E -->|Yes| F[H₀ を棄却<br/>有意差あり]
  E -->|No| G[H₀ を採択できない<br/>有意差なし]
```

## t検定（平均の比較）

```python
group_a = np.random.normal(75, 10, 50)   # A群のスコア
group_b = np.random.normal(80, 12, 50)   # B群のスコア

# 独立2標本t検定
t_stat, p_val = stats.ttest_ind(group_a, group_b, equal_var=False)  # Welchのt検定
print(f"t統計量: {t_stat:.3f}  p値: {p_val:.4f}")
print("有意差あり" if p_val < 0.05 else "有意差なし")

# 対応のあるt検定（ビフォー/アフター）
before = np.random.normal(70, 8, 30)
after  = before + np.random.normal(5, 3, 30)   # 介入後に平均+5
t2, p2 = stats.ttest_rel(before, after)
print(f"\n対応t検定: t={t2:.3f}, p={p2:.4f}")

# 効果量（Cohen's d）
pooled_std = np.sqrt((group_a.std()**2 + group_b.std()**2) / 2)
cohens_d   = (group_b.mean() - group_a.mean()) / pooled_std
print(f"効果量 Cohen's d: {cohens_d:.3f}")   # 0.2=小 0.5=中 0.8=大
```

## 分散分析（ANOVA）

```python
# 3グループ以上の平均差を一度に検定
group_c = np.random.normal(85, 10, 50)

f_stat, p_anova = stats.f_oneway(group_a, group_b, group_c)
print(f"一元配置ANOVA: F={f_stat:.3f}, p={p_anova:.4f}")

# 多重比較（Tukey HSD）
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import pandas as pd

data_all    = np.concatenate([group_a, group_b, group_c])
labels_all  = ["A"]*50 + ["B"]*50 + ["C"]*50
tukey = pairwise_tukeyhsd(data_all, labels_all, alpha=0.05)
print(tukey.summary())
```

## 相関と回帰の統計的検定

```python
x = np.random.randn(100)
y = 0.6 * x + np.random.randn(100) * 0.8

# ピアソン相関係数（線形）
r, p = stats.pearsonr(x, y)
print(f"ピアソンr: {r:.3f}  p値: {p:.4f}")

# スピアマン相関（ノンパラ）
rho, p_s = stats.spearmanr(x, y)
print(f"スピアマンρ: {rho:.3f}  p値: {p_s:.4f}")

# 正規性の検定
_, p_norm = stats.shapiro(x[:50])   # Shapiro-Wilk（n<=50）
print(f"Shapiro-Wilk p値: {p_norm:.4f} ({'正規' if p_norm > 0.05 else '非正規'})")
```

## 次に学ぶべき内容
時系列データの統計的分析は [[time-series-analysis]] で学びましょう。
