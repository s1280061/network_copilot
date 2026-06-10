---
slug: matplotlib
title: Matplotlib（グラフ描画）
level: 2
category: Python
related: [numpy, pandas, seaborn]
next: [seaborn]
tags: [python, matplotlib, visualization, data-science]
---

## 概要
MatplotlibはPythonの標準的なグラフ描画ライブラリです。折れ線・棒グラフ・散布図・ヒストグラムなど多種のグラフを細かくカスタマイズできます。

## 基本的な折れ線グラフ

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

plt.figure(figsize=(8, 4))
plt.plot(x, y, label="sin(x)", color="royalblue", linewidth=2)
plt.title("サインカーブ")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
```

## 棒グラフ

```python
categories = ["A", "B", "C", "D"]
values     = [23, 45, 12, 67]

plt.bar(categories, values, color="steelblue", edgecolor="black")
plt.title("カテゴリ別件数")
plt.ylabel("件数")
plt.show()
```

## 散布図

```python
np.random.seed(0)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100)

plt.scatter(x, y, alpha=0.6, color="tomato")
plt.xlabel("x")
plt.ylabel("y")
plt.title("散布図")
plt.show()
```

## ヒストグラム

```python
data = np.random.normal(loc=50, scale=10, size=500)

plt.hist(data, bins=30, color="mediumseagreen", edgecolor="white")
plt.title("正規分布のヒストグラム")
plt.xlabel("値")
plt.ylabel("頻度")
plt.show()
```

## 複数グラフを並べる（subplots）

```python
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

axes[0].plot(x, np.sin(x))
axes[0].set_title("sin(x)")

axes[1].plot(x, np.cos(x), color="orange")
axes[1].set_title("cos(x)")

plt.tight_layout()
plt.show()
```

## グラフを画像として保存

```python
plt.savefig("graph.png", dpi=150, bbox_inches="tight")
```

## 次に学ぶべき内容
統計可視化に強い [[seaborn]] を使うと、より少ないコードできれいなグラフが描けます。
