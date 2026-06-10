---
slug: seaborn
title: Seaborn（統計可視化）
level: 3
category: Python
related: [matplotlib, pandas, data-analysis]
next: [data-analysis]
tags: [python, seaborn, visualization, statistics, data-science]
---

## 概要
Seabornは統計的なデータ可視化に特化したライブラリで、MatplotlibをベースにPandasのDataFrameと直接連携できます。美しいデフォルトスタイルと、分布・相関・カテゴリ比較などの高機能グラフが特長です。

## 基本セットアップ

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.set_theme(style="whitegrid")  # グローバルスタイル設定
```

## ヒストグラム + 密度カーブ（histplot）

```python
import numpy as np

data = pd.DataFrame({"score": np.random.normal(70, 15, 200)})

sns.histplot(data=data, x="score", bins=20, kde=True, color="steelblue")
plt.title("スコア分布")
plt.show()
```

## 箱ひげ図（boxplot）

```python
tips = sns.load_dataset("tips")

sns.boxplot(data=tips, x="day", y="total_bill", palette="pastel")
plt.title("曜日別 合計金額")
plt.show()
```

## バイオリンプロット（violinplot）

```python
sns.violinplot(data=tips, x="day", y="tip", inner="quartile", palette="muted")
plt.title("曜日別 チップ分布")
plt.show()
```

## 散布図 + 回帰直線（lmplot）

```python
sns.lmplot(data=tips, x="total_bill", y="tip", hue="sex", height=5)
plt.title("合計金額とチップの関係")
plt.show()
```

## ペアプロット（相関行列の可視化）

```python
iris = sns.load_dataset("iris")
sns.pairplot(iris, hue="species", diag_kind="hist")
plt.show()
```

## ヒートマップ（相関係数）

```python
corr = tips[["total_bill", "tip", "size"]].corr()

sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
plt.title("相関係数マトリクス")
plt.show()
```

## 次に学ぶべき内容
可視化スキルを活かしてデータ全体を分析する流れを [[data-analysis]] で学びましょう。
