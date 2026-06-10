---
slug: python-basics
title: Python基礎（変数・リスト・辞書）
level: 1
category: Python
related: [numpy, pandas]
next: [numpy]
tags: [python, basics, data-science]
---

## 概要
Pythonはシンプルな文法と豊富なライブラリにより、データサイエンスの標準言語となっています。変数・リスト・辞書の使い方を把握しておくと、NumPyやPandasへスムーズに移行できます。

## 変数と型

```python
x = 42          # int
y = 3.14        # float
name = "Alice"  # str
flag = True     # bool

print(type(x))  # <class 'int'>
```

## リスト

```python
scores = [90, 85, 72, 95, 60]

print(scores[0])       # 90（先頭）
print(scores[-1])      # 60（末尾）
print(scores[1:4])     # [85, 72, 95]（スライス）

scores.append(88)      # 末尾に追加
scores.sort()          # 昇順ソート

# リスト内包表記
doubled = [s * 2 for s in scores]
```

## 辞書

```python
person = {"name": "Alice", "age": 30, "city": "Tokyo"}

print(person["name"])        # Alice
person["email"] = "a@b.com"  # 新しいキーを追加

for key, value in person.items():
    print(f"{key}: {value}")
```

## よく使う組み込み関数

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]

print(len(nums))    # 8
print(sum(nums))    # 31
print(min(nums))    # 1
print(max(nums))    # 9
print(sorted(nums)) # [1, 1, 2, 3, 4, 5, 6, 9]
```

## 次に学ぶべき内容
配列演算に特化した [[numpy]] を学ぶと、大量の数値データを高速に処理できます。
