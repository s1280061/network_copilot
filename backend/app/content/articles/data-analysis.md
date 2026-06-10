---
slug: data-analysis
title: データ分析の流れ（EDA）
level: 3
category: Python
related: [pandas, matplotlib, seaborn, numpy]
next: []
tags: [python, eda, data-science, analysis]
---

## 概要
EDA（Exploratory Data Analysis：探索的データ分析）は、データの傾向・分布・外れ値・相関をコードで確認していく工程です。機械学習やレポート作成の前に必ず行うステップです。

## 典型的な分析フロー

1. データ読み込み
2. 概要確認（shape・型・欠損）
3. 基本統計量
4. 分布の可視化
5. 相関分析
6. 外れ値・異常値の確認
7. 特徴エンジニアリング

## 1. データ読み込みと概要確認

```python
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("dataset.csv")

print(df.shape)        # (行数, 列数)
print(df.dtypes)       # 各列のデータ型
print(df.isnull().sum()) # 欠損数
print(df.describe())   # 数値列の基本統計
df.head()
```

## 2. 数値列の分布を一括確認

```python
df.hist(figsize=(12, 8), bins=25, edgecolor="white")
plt.suptitle("各数値列のヒストグラム")
plt.tight_layout()
plt.show()
```

## 3. カテゴリ列の値カウント

```python
for col in df.select_dtypes(include="object").columns:
    print(f"\n{col}")
    print(df[col].value_counts())
```

## 4. 相関行列

```python
corr = df.corr(numeric_only=True)

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r",
            vmin=-1, vmax=1, square=True)
plt.title("相関係数マトリクス")
plt.tight_layout()
plt.show()
```

## 5. 外れ値の確認（IQR法）

```python
def count_outliers(series: pd.Series) -> int:
    Q1, Q3 = series.quantile([0.25, 0.75])
    IQR = Q3 - Q1
    return ((series < Q1 - 1.5 * IQR) | (series > Q3 + 1.5 * IQR)).sum()

for col in df.select_dtypes(include="number").columns:
    n = count_outliers(df[col])
    if n:
        print(f"{col}: {n} 件の外れ値")
```

## 6. グループ別の比較

```python
# 例: カテゴリごとのターゲット列の平均
summary = df.groupby("category")["target"].agg(["mean", "std", "count"])
print(summary)

# 可視化
sns.boxplot(data=df, x="category", y="target")
plt.show()
```

## 7. 時系列データの場合

```python
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()

df["value"].resample("M").mean().plot(figsize=(12, 4))
plt.title("月次平均の推移")
plt.grid(True)
plt.show()
```

## チェックリスト

- [ ] shape・dtype・欠損数を確認した
- [ ] 数値列の分布をヒストグラムで見た
- [ ] 外れ値の有無を確認した
- [ ] 相関係数でターゲットとの関係を確認した
- [ ] カテゴリ別の集計をした
