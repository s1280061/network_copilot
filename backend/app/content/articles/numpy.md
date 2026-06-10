---
slug: numpy
title: NumPy（配列・行列演算）
level: 2
category: Python
related: [python-basics, pandas, matplotlib]
next: [pandas]
tags: [python, numpy, array, data-science]
---

## 概要
NumPyはPythonで数値計算を高速に行うための基盤ライブラリです。`ndarray`（多次元配列）を中心に、行列演算・統計・線形代数をC言語並みの速度で処理します。

## 配列の作成

```python
import numpy as np

# リストから作成
a = np.array([1, 2, 3, 4, 5])

# 便利な生成関数
zeros  = np.zeros(5)           # [0. 0. 0. 0. 0.]
ones   = np.ones((2, 3))       # 2行3列の1行列
arange = np.arange(0, 10, 2)  # [0 2 4 6 8]
linspace = np.linspace(0, 1, 5)  # [0.   0.25 0.5  0.75 1.  ]

# 2次元配列（行列）
matrix = np.array([[1, 2, 3],
                   [4, 5, 6]])
print(matrix.shape)  # (2, 3)
```

## 基本演算（ブロードキャスト）

```python
a = np.array([10, 20, 30, 40])

print(a + 5)     # [15 25 35 45]
print(a * 2)     # [20 40 60 80]
print(a ** 2)    # [100 400 900 1600]

b = np.array([1, 2, 3, 4])
print(a + b)     # [11 22 33 44]（要素ごとの加算）
```

## インデックスとスライス

```python
a = np.array([10, 20, 30, 40, 50])

print(a[2])      # 30
print(a[1:4])    # [20 30 40]
print(a[::2])    # [10 30 50]（1つおき）

# 条件フィルタ
print(a[a > 25]) # [30 40 50]
```

## 統計関数

```python
data = np.array([4, 7, 13, 2, 8, 11, 5])

print(np.mean(data))    # 7.14...（平均）
print(np.median(data))  # 7.0（中央値）
print(np.std(data))     # 3.38...（標準偏差）
print(np.min(data))     # 2
print(np.max(data))     # 13
print(np.sum(data))     # 50
```

## 行列演算

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print(A @ B)         # 行列積
print(A.T)           # 転置
print(np.linalg.det(A))  # 行列式
```

## 次に学ぶべき内容
NumPyの配列の上に表形式のデータ操作機能を持つ [[pandas]] を学びましょう。
