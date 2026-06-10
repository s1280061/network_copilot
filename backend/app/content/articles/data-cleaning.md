---
slug: data-cleaning
title: データクリーニング
level: 2
category: Python
related: [pandas, numpy, data-analysis]
next: [data-analysis]
tags: [python, pandas, cleaning, preprocessing, data-science]
---

## 概要
データクリーニングは分析・機械学習の前処理として必須のステップです。欠損値・重複・外れ値・型変換・文字列の正規化を丁寧に行うことで、後工程の精度が大きく変わります。

## 欠損値の処理

```python
import pandas as pd
import numpy as np

df = pd.read_csv("raw_data.csv")

# 欠損の概要
print(df.isnull().sum())
print(df.isnull().mean() * 100)  # 欠損率(%)

# 削除
df_drop = df.dropna()               # 欠損行をすべて削除
df_drop_col = df.drop(columns=["col_with_many_nulls"])

# 補完
df["age"].fillna(df["age"].median(), inplace=True)  # 中央値補完
df["city"].fillna("Unknown", inplace=True)           # 固定値補完
df.fillna(method="ffill", inplace=True)              # 前の値で埋める(時系列)
```

## 重複行の処理

```python
print(df.duplicated().sum())  # 重複件数

df_unique = df.drop_duplicates()
df_unique = df.drop_duplicates(subset=["user_id"])  # 特定列で判定
```

## 型変換

```python
# 文字列 → 数値
df["price"] = pd.to_numeric(df["price"], errors="coerce")  # 変換不可はNaN

# 文字列 → 日付
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

# 日付から特徴量を抽出
df["year"]  = df["date"].dt.year
df["month"] = df["date"].dt.month
df["dow"]   = df["date"].dt.day_of_week  # 0=月曜
```

## 文字列のクリーニング

```python
# 前後の空白を除去
df["name"] = df["name"].str.strip()

# 小文字統一
df["email"] = df["email"].str.lower()

# 正規表現で不要な文字を削除
df["phone"] = df["phone"].str.replace(r"[^\d]", "", regex=True)

# 特定パターンを含む行を除外
df = df[~df["text"].str.contains("test|dummy", case=False, na=False)]
```

## 外れ値の除去（IQR法）

```python
def remove_outliers(df: pd.DataFrame, col: str) -> pd.DataFrame:
    Q1, Q3 = df[col].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    return df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]

df = remove_outliers(df, "price")
```

## カテゴリ変数のエンコード

```python
# ラベルエンコード
df["grade_code"] = df["grade"].map({"A": 0, "B": 1, "C": 2})

# ワンホットエンコード
df = pd.get_dummies(df, columns=["city"], drop_first=True)
```

## 次に学ぶべき内容
クリーンになったデータを [[data-analysis]] でEDA（探索的データ分析）してみましょう。
