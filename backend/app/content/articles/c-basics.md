---
slug: c-basics
title: C言語の基礎
level: 2
category: C言語
related: [c-pointers, c-structs]
next: [c-pointers]
tags: [c, programming, basics, memory]
---

## なぜ今C言語を学ぶのか

「C言語は古い」と思われがちですが、**組み込み・OS・ネットワークスタック・自動車ECU**の世界では今も最前線で使われています。LinuxカーネルもTCP/IPスタックも、その多くはC言語で書かれています。Pythonの高速な数値演算ライブラリ（NumPy）の内部もCです。

Cを学ぶことで得られる最大の価値は「**コンピュータがどうメモリを扱うか**」の直感です。これを知ると、バグの原因が直感的にわかり、他の言語もより深く理解できるようになります。

## 最初のCプログラム

```c
#include <stdio.h>   /* 標準入出力ライブラリ */

int main(void) {
    printf("Hello, World!\n");
    return 0;
}
```

コンパイルして実行：

```bash
gcc hello.c -o hello
./hello
# Hello, World!
```

| 要素 | 意味 |
|------|------|
| `#include` | ヘッダファイルの読み込み |
| `main()` | プログラムの開始点（エントリポイント） |
| `printf()` | 書式付き出力関数 |
| `return 0` | OSへの終了コード（0 = 正常終了） |

## 変数と基本型

```c
#include <stdio.h>

int main(void) {
    int    age   = 25;          /* 整数（4バイト）          */
    double pi    = 3.14159;     /* 浮動小数点（8バイト）     */
    char   grade = 'A';         /* 文字（1バイト）           */
    int    flag  = 1;           /* C言語にbool型はない（C99以前） */

    printf("age=%d, pi=%.2f, grade=%c\n", age, pi, grade);
    return 0;
}
```

### 主要な型とサイズ（64ビット環境）

| 型 | サイズ | 範囲の目安 | 書式指定子 |
|----|--------|-----------|-----------|
| `char` | 1バイト | -128〜127 | `%c`, `%d` |
| `int` | 4バイト | ±21億 | `%d` |
| `long` | 8バイト | ±約922京 | `%ld` |
| `float` | 4バイト | 有効桁数7桁 | `%f` |
| `double` | 8バイト | 有効桁数15桁 | `%lf` |
| `unsigned int` | 4バイト | 0〜42億 | `%u` |

## メモリ上の変数

変数を宣言すると、コンピュータのメモリ上に**決まったバイト数の領域**が確保されます。

```c
#include <stdio.h>

int main(void) {
    int x = 42;
    printf("値: %d\n", x);
    printf("サイズ: %zu バイト\n", sizeof(x));
    printf("アドレス: %p\n", (void*)&x);  /* & でアドレスを取得 */
    return 0;
}
```

```
値: 42
サイズ: 4 バイト
アドレス: 0x7ffd5a3e1c2c
```

`&x` は「変数 x のアドレス（メモリ上の住所）」です。これがポインタの基礎になります。

## 制御構造

### 条件分岐

```c
int score = 75;

if (score >= 90) {
    printf("優\n");
} else if (score >= 70) {
    printf("良\n");
} else {
    printf("可\n");
}
```

### ループ

```c
/* for ループ */
for (int i = 0; i < 5; i++) {
    printf("%d ", i);  /* 0 1 2 3 4 */
}

/* while ループ */
int n = 10;
while (n > 0) {
    n -= 3;
}
printf("n = %d\n", n);  /* n = -2 */
```

## 配列

```c
#include <stdio.h>

int main(void) {
    int scores[5] = {90, 85, 72, 68, 95};
    int sum = 0;

    for (int i = 0; i < 5; i++) {
        sum += scores[i];
    }
    printf("合計: %d, 平均: %.1f\n", sum, sum / 5.0);

    /* 配列の先頭アドレス */
    printf("配列の先頭: %p\n", (void*)scores);
    printf("scores[0]のアドレス: %p\n", (void*)&scores[0]);
    /* 上の2つは同じアドレスを示す */
    return 0;
}
```

> **重要**: 配列名 `scores` は先頭要素のアドレスと等しい。これがポインタと配列が密接に関係する理由です。

## 関数

```c
#include <stdio.h>

/* 宣言（プロトタイプ） */
int add(int a, int b);
double average(int arr[], int n);

int main(void) {
    int data[] = {10, 20, 30, 40, 50};
    printf("合計: %d\n", add(3, 4));
    printf("平均: %.1f\n", average(data, 5));
    return 0;
}

int add(int a, int b) {
    return a + b;
}

double average(int arr[], int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) sum += arr[i];
    return (double)sum / n;
}
```

### 値渡しの罠

```c
void increment(int x) {
    x++;  /* ローカルコピーが増えるだけ */
}

int main(void) {
    int n = 5;
    increment(n);
    printf("%d\n", n);  /* 5 のまま！変わらない */
    return 0;
}
```

関数の外の変数を変えたいときは**ポインタ渡し**が必要です（次の記事で解説）。

## 文字列

C言語の文字列は「`char`の配列」＋「末尾の`\0`（ヌル文字）」です。

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char name[20] = "Alice";       /* 文字列リテラルで初期化 */
    char buf[20];

    printf("名前: %s\n", name);
    printf("長さ: %zu\n", strlen(name));  /* 5（\0は含まない） */

    strcpy(buf, name);              /* 文字列コピー */
    strcat(buf, " Smith");          /* 文字列連結 */
    printf("フルネーム: %s\n", buf);

    return 0;
}
```

> ⚠️ `char buf[20]` に20文字を超える文字列を入れると**バッファオーバーフロー**（脆弱性の代表例）が起きます。`strncpy(buf, src, sizeof(buf)-1)` で長さを制限するのが安全。

## よくあるミス

| ミス | 症状 | 対策 |
|------|------|------|
| `=` と `==` の混同 | 条件が常にtrueになる | コンパイラ警告を確認 |
| 配列の範囲外アクセス | クラッシュ・未定義動作 | インデックスを確認 |
| 初期化忘れ | 不定値（ゴミ値）を使う | 宣言時に初期化 |
| バッファオーバーフロー | セキュリティ脆弱性 | `strncpy` / `snprintf` を使う |

## まとめ

- C言語は変数がメモリ上の実体として存在し、`&` でそのアドレスを取得できる
- 配列はメモリ上に連続して並び、先頭アドレスで参照される
- 関数は**値渡し**が基本 → 外の変数を変えたいときはポインタが必要
- 文字列は `\0` 終端の `char` 配列 → バッファサイズに注意

次は「**アドレスとポインタ**」で、メモリの仕組みをより深く掘り下げます。
