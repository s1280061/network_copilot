"""
Generate chart images for Python-category articles.
Run from repo root: python backend/gen_charts_python.py
"""
import os, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore")
OUT = "frontend/public/images/charts"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 140,
    "font.size": 11,
    "font.family": "IPAGothic",
    "axes.unicode_minus": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
})

COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

# ──────────────────────────────────────────────────────────
# python-basics.md
# データ構造ごとの使い分けを棒グラフで + 処理速度比較
# ──────────────────────────────────────────────────────────
def chart_python_basics():
    import time

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # データ構造の特性比較（主観スコア 1-5）
    structs  = ["list", "tuple", "dict", "set", "deque"]
    access   = [5, 5, 5, 2, 3]
    search   = [2, 2, 5, 5, 2]
    append   = [5, 1, 5, 5, 5]

    x = np.arange(len(structs))
    w = 0.25
    axes[0].bar(x - w,   access, w, label="ランダムアクセス", color=COLORS[0], alpha=0.85)
    axes[0].bar(x,       search, w, label="検索速度",         color=COLORS[1], alpha=0.85)
    axes[0].bar(x + w,   append, w, label="末尾追加",         color=COLORS[2], alpha=0.85)
    axes[0].set_xticks(x); axes[0].set_xticklabels(structs)
    axes[0].set_yticks([1,2,3,4,5])
    axes[0].set_yticklabels(["×","△","○","◎","◎+"])
    axes[0].set_title("Pythonデータ構造の特性比較")
    axes[0].set_ylabel("速度・利便性スコア")
    axes[0].legend(fontsize=9)

    # リスト内包表記 vs ループ の速度比較（実測）
    n_trials = 5
    sizes = [1_000, 10_000, 100_000, 500_000]
    loop_times, comp_times = [], []

    for n in sizes:
        # for-loop
        t0 = time.perf_counter()
        for _ in range(n_trials):
            result = []
            for i in range(n):
                result.append(i * 2)
        loop_times.append((time.perf_counter() - t0) / n_trials * 1000)

        # list comprehension
        t0 = time.perf_counter()
        for _ in range(n_trials):
            result = [i * 2 for i in range(n)]
        comp_times.append((time.perf_counter() - t0) / n_trials * 1000)

    axes[1].plot(sizes, loop_times, "o-", lw=2, color=COLORS[3], label="forループ")
    axes[1].plot(sizes, comp_times, "s-", lw=2, color=COLORS[0], label="リスト内包表記")
    axes[1].set_title("forループ vs リスト内包表記（実測）")
    axes[1].set_xlabel("要素数"); axes[1].set_ylabel("実行時間 [ms]")
    axes[1].set_xscale("log"); axes[1].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{OUT}/python-basics.png"); plt.close()
    print("✓ python-basics.png")


# ──────────────────────────────────────────────────────────
# numpy.md
# ブロードキャスト可視化 + NumPy vs list 速度
# ──────────────────────────────────────────────────────────
def chart_numpy():
    import time

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # ブロードキャスト: 2D配列のヒートマップ
    a = np.arange(1, 6).reshape(5, 1)   # (5,1)
    b = np.arange(1, 6).reshape(1, 5)   # (1,5)
    C = a * b                             # (5,5)

    im = axes[0].imshow(C, cmap="Blues", aspect="auto")
    for i in range(5):
        for j in range(5):
            axes[0].text(j, i, str(C[i, j]), ha="center", va="center",
                         fontsize=10, color="white" if C[i,j] > 12 else "black")
    axes[0].set_xticks(range(5)); axes[0].set_xticklabels([f"b={v}" for v in range(1,6)])
    axes[0].set_yticks(range(5)); axes[0].set_yticklabels([f"a={v}" for v in range(1,6)])
    axes[0].set_title("ブロードキャスト: a(5,1) × b(1,5) → (5,5)\n各セル = a[i] × b[j]")
    plt.colorbar(im, ax=axes[0])

    # 速度比較: numpy vs list
    sizes = [1_000, 10_000, 100_000, 1_000_000]
    np_times, list_times = [], []
    n_trials = 3
    for n in sizes:
        arr = np.random.randn(n)
        lst = arr.tolist()

        t0 = time.perf_counter()
        for _ in range(n_trials): np.sum(arr ** 2)
        np_times.append((time.perf_counter() - t0) / n_trials * 1000)

        t0 = time.perf_counter()
        for _ in range(n_trials): sum(x**2 for x in lst)
        list_times.append((time.perf_counter() - t0) / n_trials * 1000)

    axes[1].plot(sizes, list_times, "o-", lw=2, color=COLORS[3], label="Pythonリスト")
    axes[1].plot(sizes, np_times,   "s-", lw=2, color=COLORS[0], label="NumPy配列")
    axes[1].set_title("NumPy vs Pythonリスト\n二乗和の計算速度（実測）")
    axes[1].set_xlabel("要素数"); axes[1].set_ylabel("実行時間 [ms]")
    axes[1].set_xscale("log"); axes[1].set_yscale("log")
    axes[1].legend(fontsize=9)

    # 行列演算の可視化
    rng = np.random.default_rng(42)
    A = rng.integers(1, 9, (4, 4))
    B = rng.integers(1, 9, (4, 4))
    C2 = A @ B

    ax = axes[2]
    ax.axis("off")
    ax.set_title("行列積 A @ B の一部（4×4）")
    col_labels = [f"col{i}" for i in range(4)]
    row_labels = [f"row{i}" for i in range(4)]

    # show A, B, C side by side as text tables
    for label, mat, x0 in [("A", A, 0.0), ("B", B, 0.38), ("A@B", C2, 0.72)]:
        ax.text(x0 + 0.07, 0.97, label, transform=ax.transAxes,
                fontsize=11, fontweight="bold", va="top")
        for i in range(4):
            for j in range(4):
                color = "#4C72B0" if label == "A@B" else "black"
                ax.text(x0 + 0.04 + j * 0.08, 0.85 - i * 0.2,
                        str(mat[i, j]),
                        transform=ax.transAxes,
                        fontsize=9, ha="center", va="top", color=color)
    ax.text(0.33, 0.55, "×", transform=ax.transAxes, fontsize=16, ha="center", va="center")
    ax.text(0.65, 0.55, "=", transform=ax.transAxes, fontsize=16, ha="center", va="center")

    plt.tight_layout()
    plt.savefig(f"{OUT}/numpy.png"); plt.close()
    print("✓ numpy.png")


# ──────────────────────────────────────────────────────────
# pandas.md
# DataFrame可視化: 売上サンプルデータの集計グラフ
# ──────────────────────────────────────────────────────────
def chart_pandas():
    import pandas as pd

    rng = np.random.default_rng(42)

    # サンプル売上データ
    dates = pd.date_range("2024-01-01", periods=90, freq="D")
    categories = rng.choice(["電子機器", "食品", "衣類", "書籍"], size=90)
    sales = (rng.integers(1000, 10000, size=90)
             + (np.arange(90) * 20)  # トレンド
             + 2000 * np.sin(2 * np.pi * np.arange(90) / 30))  # 季節性
    df = pd.DataFrame({"date": dates, "category": categories, "sales": sales.astype(int)})
    df["month"] = df["date"].dt.to_period("M").astype(str)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # カテゴリ別売上集計（棒グラフ）
    cat_sum = df.groupby("category")["sales"].sum().sort_values(ascending=False)
    axes[0].bar(cat_sum.index, cat_sum.values / 1000, color=COLORS[:len(cat_sum)], alpha=0.85)
    axes[0].set_title("カテゴリ別売上合計\n(groupby + sum)")
    axes[0].set_xlabel("カテゴリ"); axes[0].set_ylabel("売上 [千円]")
    axes[0].tick_params(axis="x", rotation=20)

    # 月次売上推移（折れ線）
    monthly = df.groupby("month")["sales"].sum()
    axes[1].plot(range(len(monthly)), monthly.values / 1000, "o-",
                 lw=2, color=COLORS[0], ms=6)
    axes[1].set_xticks(range(len(monthly)))
    axes[1].set_xticklabels(monthly.index, rotation=30, ha="right", fontsize=9)
    axes[1].set_title("月次売上推移\n(resample / groupby月)")
    axes[1].set_ylabel("売上 [千円]")

    # カテゴリ×月 ヒートマップ
    pivot = df.pivot_table(values="sales", index="category", columns="month", aggfunc="sum")
    im = axes[2].imshow(pivot.values / 1000, cmap="YlOrRd", aspect="auto")
    axes[2].set_xticks(range(len(pivot.columns)))
    axes[2].set_xticklabels(pivot.columns, rotation=30, ha="right", fontsize=8)
    axes[2].set_yticks(range(len(pivot.index)))
    axes[2].set_yticklabels(pivot.index, fontsize=9)
    axes[2].set_title("カテゴリ×月 売上ヒートマップ\n(pivot_table)")
    plt.colorbar(im, ax=axes[2], label="売上[千円]")
    axes[2].grid(False)

    plt.tight_layout()
    plt.savefig(f"{OUT}/pandas.png"); plt.close()
    print("✓ pandas.png")


# ──────────────────────────────────────────────────────────
# matplotlib.md
# 折れ線・棒・散布図・ヒストグラムの4グラフ並べて
# ──────────────────────────────────────────────────────────
def chart_matplotlib():
    rng = np.random.default_rng(42)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    # 折れ線グラフ: 月次気温
    months = np.arange(1, 13)
    temp_tokyo  = [5, 6, 10, 15, 20, 24, 28, 30, 26, 21, 15, 8]
    temp_sapporo= [0, 1,  4, 10, 16, 20, 24, 26, 21, 14,  6, 1]
    axes[0, 0].plot(months, temp_tokyo,   "o-", lw=2, color=COLORS[0], label="東京")
    axes[0, 0].plot(months, temp_sapporo, "s-", lw=2, color=COLORS[1], label="札幌")
    axes[0, 0].set_title("月次平均気温（折れ線グラフ）")
    axes[0, 0].set_xlabel("月"); axes[0, 0].set_ylabel("気温 [℃]")
    axes[0, 0].set_xticks(months); axes[0, 0].legend(fontsize=9)
    axes[0, 0].axhline(0, color="gray", lw=0.8, linestyle="--")

    # 棒グラフ: 言語別人気
    langs  = ["Python", "JavaScript", "Java", "TypeScript", "C++"]
    scores = [30.3, 13.8, 11.5, 8.7, 6.5]
    bars = axes[0, 1].bar(langs, scores, color=COLORS, alpha=0.85, edgecolor="white")
    for bar, val in zip(bars, scores):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                        f"{val}%", ha="center", va="bottom", fontsize=9)
    axes[0, 1].set_title("プログラミング言語人気\n（棒グラフ）")
    axes[0, 1].set_ylabel("人気度 [%]"); axes[0, 1].tick_params(axis="x", rotation=20)

    # 散布図: 身長・体重
    height = rng.normal(170, 8, 100)
    weight = 0.6 * height - 50 + rng.normal(0, 5, 100)
    axes[1, 0].scatter(height, weight, alpha=0.6, s=30, color=COLORS[0])
    m, b = np.polyfit(height, weight, 1)
    x_line = np.linspace(150, 195, 100)
    axes[1, 0].plot(x_line, m * x_line + b, "r-", lw=2, label=f"回帰直線")
    axes[1, 0].set_title("身長 vs 体重（散布図）")
    axes[1, 0].set_xlabel("身長 [cm]"); axes[1, 0].set_ylabel("体重 [kg]")
    axes[1, 0].legend(fontsize=9)

    # ヒストグラム: テスト点数の分布
    scores_data = np.concatenate([rng.normal(65, 10, 80), rng.normal(85, 8, 40)])
    axes[1, 1].hist(scores_data, bins=20, color=COLORS[0], edgecolor="white",
                    alpha=0.85, density=True, label="点数分布")
    from scipy.stats import norm
    x_norm = np.linspace(30, 110, 200)
    axes[1, 1].plot(x_norm, norm.pdf(x_norm, scores_data.mean(), scores_data.std()),
                    "r-", lw=2, label="正規分布近似")
    axes[1, 1].axvline(scores_data.mean(), color="red", linestyle="--", lw=1.5,
                       label=f"平均={scores_data.mean():.1f}")
    axes[1, 1].set_title("テスト点数の分布（ヒストグラム）")
    axes[1, 1].set_xlabel("点数"); axes[1, 1].set_ylabel("密度")
    axes[1, 1].legend(fontsize=9)

    plt.suptitle("Matplotlibの主要グラフ一覧（サンプルデータ）", y=1.01, fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{OUT}/matplotlib.png", bbox_inches="tight"); plt.close()
    print("✓ matplotlib.png")


# ──────────────────────────────────────────────────────────
# seaborn.md
# seaborn の代表的なグラフを matplotlib で再現
# ──────────────────────────────────────────────────────────
def chart_seaborn():
    import pandas as pd
    from scipy.stats import gaussian_kde

    rng = np.random.default_rng(42)

    # Irisデータ相当のサンプル
    n = 50
    setosa     = {"がく片長": rng.normal(5.0, 0.35, n), "花弁長": rng.normal(1.5, 0.17, n), "label": "setosa"}
    versicolor = {"がく片長": rng.normal(5.9, 0.52, n), "花弁長": rng.normal(4.3, 0.47, n), "label": "versicolor"}
    virginica  = {"がく片長": rng.normal(6.6, 0.64, n), "花弁長": rng.normal(5.6, 0.55, n), "label": "virginica"}
    df = pd.concat([pd.DataFrame(d) for d in [setosa, versicolor, virginica]], ignore_index=True)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    colors_iris = {c: COLORS[i] for i, c in enumerate(["setosa", "versicolor", "virginica"])}

    # KDE plot (分布)
    for label, color in colors_iris.items():
        data = df[df["label"] == label]["がく片長"].values
        kde = gaussian_kde(data)
        x = np.linspace(3.5, 8.5, 200)
        axes[0].fill_between(x, kde(x), alpha=0.35, color=color)
        axes[0].plot(x, kde(x), lw=2, color=color, label=label)
    axes[0].set_title("がく片長の分布（KDE plot）\n品種ごとのカーネル密度推定")
    axes[0].set_xlabel("がく片長 [cm]"); axes[0].set_ylabel("密度")
    axes[0].legend(fontsize=9)

    # Box plot (カテゴリ比較)
    data_by_class = [df[df["label"] == lb]["花弁長"].values
                     for lb in ["setosa", "versicolor", "virginica"]]
    bp = axes[1].boxplot(data_by_class, patch_artist=True,
                         medianprops={"color": "white", "lw": 2})
    for patch, color in zip(bp["boxes"], COLORS[:3]):
        patch.set_facecolor(color); patch.set_alpha(0.7)
    for i, (data, color) in enumerate(zip(data_by_class, COLORS[:3])):
        x_jitter = rng.uniform(-0.15, 0.15, len(data))
        axes[1].scatter([i+1]*len(data) + x_jitter, data,
                        alpha=0.4, s=15, color=color)
    axes[1].set_xticks([1, 2, 3])
    axes[1].set_xticklabels(["setosa", "versicolor", "virginica"])
    axes[1].set_title("花弁長の比較（Box plot）\n中央値・四分位範囲・外れ値")
    axes[1].set_ylabel("花弁長 [cm]")

    # Scatter + 回帰（品種ごと）
    for label, color in colors_iris.items():
        sub = df[df["label"] == label]
        axes[2].scatter(sub["がく片長"], sub["花弁長"],
                        color=color, alpha=0.6, s=25, label=label)
        m, b = np.polyfit(sub["がく片長"], sub["花弁長"], 1)
        x_r = np.linspace(sub["がく片長"].min(), sub["がく片長"].max(), 50)
        axes[2].plot(x_r, m * x_r + b, lw=1.5, color=color, alpha=0.8)
    axes[2].set_title("がく片長 vs 花弁長\n（scatter + 回帰直線）")
    axes[2].set_xlabel("がく片長 [cm]"); axes[2].set_ylabel("花弁長 [cm]")
    axes[2].legend(fontsize=9)

    plt.suptitle("Seaborn主要グラフ（Iris相当サンプルデータ）", y=1.01, fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{OUT}/seaborn.png", bbox_inches="tight"); plt.close()
    print("✓ seaborn.png")


if __name__ == "__main__":
    chart_python_basics()
    chart_numpy()
    chart_pandas()
    chart_matplotlib()
    chart_seaborn()
    print("\nPythonカテゴリ チャート生成完了 →", OUT)
