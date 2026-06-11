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
「センサーデータを読んで集計し、異常があればアラートを出す」――このような処理を数十行で書けるのがPythonの強みです。シンプルな文法と豊富なライブラリにより、データサイエンスの標準言語となっています。変数・リスト・辞書・制御構文を押さえておくと、NumPy・Pandasへスムーズに移行できます。「機械学習のエラーが読めない」という問題の9割は、Python基礎の理解不足から来ます。

## 活用シーン
- **ログ解析**: テキストファイルを読んでリスト・辞書に格納し、条件抽出
- **自動化スクリプト**: ファイル操作・CSV処理・APIコール
- **データ前処理**: NumPy/Pandasに渡す前のデータ変換・クリーニング

## なぜ必要か
機械学習・統計分析・グラフ描画はすべてPythonコードで記述します。「変数に何が入っているか」「リストをどう操作するか」という基礎が曖昧だと、ライブラリのエラー原因が掴めません。土台を固めることで、複雑なデータ処理もスムーズに書けるようになります。

## 変数と型

```python
# 主要なデータ型
x     = 42          # int（整数）
y     = 3.14        # float（小数）
name  = "Alice"     # str（文字列）
flag  = True        # bool（真偽値）

print(type(x))      # <class 'int'>

# f文字列（Python 3.6+）で整形出力
print(f"{name} のスコアは {x} 点（{y:.1f} 換算）")
# → Alice のスコアは 42 点（3.1 換算）
```

## リスト — 順序付きコレクション

```python
scores = [90, 85, 72, 95, 60]

# インデックスとスライス
print(scores[0])        # 90（先頭）
print(scores[-1])       # 60（末尾）
print(scores[1:4])      # [85, 72, 95]

# 追加・削除
scores.append(88)       # 末尾に追加
scores.insert(0, 100)   # 先頭に挿入
scores.remove(60)       # 値を指定して削除

# リスト内包表記（Pythonらしい書き方）
passed  = [s for s in scores if s >= 80]   # 合格者のみ
doubled = [s * 2 for s in scores]          # 全スコア2倍

# 集計
print(f"最高: {max(scores)}, 最低: {min(scores)}, 合計: {sum(scores)}")
```

## 辞書 — キーと値のマッピング

```python
sensor = {
    "id":    "sensor_01",
    "type":  "temperature",
    "value": 36.5,
    "unit":  "celsius",
}

# 値の取得
print(sensor["value"])                    # 36.5
print(sensor.get("location", "unknown"))  # キーが無ければデフォルト値

# 追加・更新
sensor["timestamp"] = "2025-01-15T09:00:00"
sensor["value"]     = 37.1

# 全キー・値を走査
for key, val in sensor.items():
    print(f"  {key}: {val}")

# 辞書のリスト（テーブルデータの最も基本的な表現）
readings = [
    {"id": "s01", "value": 36.5},
    {"id": "s02", "value": 40.2},
    {"id": "s03", "value": 35.8},
]
high_temp = [r for r in readings if r["value"] > 38]
```

## 制御構文

```python
# if / elif / else
score = 75
if score >= 90:
    grade = "A"
elif score >= 70:
    grade = "B"
else:
    grade = "C"

# for ループ（enumerate で番号付き）
names = ["Alice", "Bob", "Carol"]
for i, name in enumerate(names, start=1):
    print(f"{i}. {name}")

# while ループ
n = 1
while n <= 5:
    print(n)
    n += 1
```

## 関数

```python
def calc_stats(data: list[float]) -> dict:
    """リストの基本統計量を返す"""
    n   = len(data)
    avg = sum(data) / n
    mn  = min(data)
    mx  = max(data)
    return {"count": n, "mean": avg, "min": mn, "max": mx}

result = calc_stats([88, 72, 95, 60, 83])
print(result)
# → {'count': 5, 'mean': 79.6, 'min': 60, 'max': 95}
```

## よく使う組み込み関数

| 関数 | 用途 | 例 |
|---|---|---|
| `len()` | 要素数 | `len([1,2,3])` → 3 |
| `range()` | 連番生成 | `list(range(5))` → [0,1,2,3,4] |
| `zip()` | 複数リストを組み合わせ | `zip(a, b)` |
| `enumerate()` | インデックス付きfor | `enumerate(lst)` |
| `sorted()` | ソート（元リスト変更なし） | `sorted(lst, reverse=True)` |
| `isinstance()` | 型チェック | `isinstance(x, int)` |

## パフォーマンス可視化

![データ構造の特性比較とリスト内包表記の速度](/images/charts/python-basics.png)

## データ構造の使い分け

```mermaid
graph LR
  A[データの形] --> B{順序が必要?}
  B -->|Yes| C[リスト list]
  B -->|No| D{重複不要?}
  D -->|Yes| E[セット set]
  D -->|No| F{キーで引く?}
  F -->|Yes| G[辞書 dict]
  F -->|No| H[タプル tuple]
```

## よくある間違いと対処法

1. **インデントエラー（IndentationError）** → Pythonはインデントが文法。タブとスペースを混在させない。エディタで「スペース4つ」に統一する設定をする。
2. **リストの浅いコピー** → `b = a` とするとaとbは同じリストを指す。変更したくない場合は `b = a.copy()` または `b = a[:]` を使う。
3. **`range()` の末尾は含まれない** → `range(1, 5)` は `[1, 2, 3, 4]`（5は含まれない）。頻出の混乱ポイント。
4. **辞書のキーが存在しない（KeyError）** → `dict[key]` の代わりに `dict.get(key, デフォルト値)` を使うと安全。

## まとめ

- リストは `[]` で順序付き、辞書は `{}` でキー引き、セットは重複不可
- リスト内包表記 `[x for x in lst if cond]` はforループより高速で読みやすい
- `enumerate()` でインデックス付きfor、`zip()` で複数リストを同時に処理
- 関数は `def` で定義し、型ヒント（`-> dict`）をつけると読みやすい
- `range(start, stop, step)` の stop は**含まれない**ことに注意

## 次に学ぶべき内容
大量の数値データを高速処理する [[numpy]] へ進みましょう。
