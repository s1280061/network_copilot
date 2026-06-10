---
slug: pandas
title: Pandas（DataFrame・データ操作）
level: 2
category: Python
related: [numpy, matplotlib, data-cleaning]
next: [matplotlib]
tags: [python, pandas, dataframe, data-science]
---

## 概要
PandasはExcel的な表形式データを扱うライブラリです。`DataFrame`（表）と`Series`（列）が中心で、CSVの読み込み・集計・結合・整形を数行のコードで行えます。

## DataFrameの作成

```python
import pandas as pd

# 辞書から作成
df = pd.DataFrame({
    "name":  ["Alice", "Bob", "Carol", "Dave"],
    "age":   [25, 30, 22, 35],
    "score": [88, 92, 78, 95],
})

print(df)
#     name  age  score
# 0  Alice   25     88
# 1    Bob   30     92
# 2  Carol   22     78
# 3   Dave   35     95
```

## CSVの読み書き

```python
df = pd.read_csv("data.csv")       # 読み込み
df.to_csv("output.csv", index=False)  # 書き出し
```

## 基本的な確認

```python
df.head()        # 先頭5行
df.tail(3)       # 末尾3行
df.shape         # (行数, 列数)
df.info()        # 型・欠損値の概要
df.describe()    # 数値列の基本統計量
```

## 列の選択とフィルタ

```python
# 1列選択（Series）
print(df["score"])

# 複数列
print(df[["name", "score"]])

# 条件フィルタ
high = df[df["score"] >= 90]
young_high = df[(df["age"] < 30) & (df["score"] >= 80)]
```

## 集計・グループ化

```python
# 単純集計
print(df["score"].mean())   # 88.25
print(df["score"].max())    # 95

# グループ集計
grouped = df.groupby("department")["score"].agg(["mean", "max", "count"])
```

## 欠損値の処理

```python
df.isnull().sum()            # 欠損数を確認
df.dropna()                  # 欠損行を削除
df.fillna(0)                 # 0で埋める
df["age"].fillna(df["age"].mean())  # 平均で補完
```

## 列の追加・変換

```python
df["grade"] = df["score"].apply(lambda x: "A" if x >= 90 else "B")
df["age_double"] = df["age"] * 2
```

## 次に学ぶべき内容
DataFrameのデータを [[matplotlib]] でグラフ化する方法を学びましょう。
