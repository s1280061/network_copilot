"""
Generate matplotlib chart images for 22 articles.
Output: frontend/public/images/charts/<slug>.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.special import beta as beta_func
from sklearn.datasets import make_classification, load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import os

OUT_DIR = "/home/user/network_copilot/frontend/public/images/charts"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 140, "font.size": 11,
    "font.family": "IPAGothic", "axes.unicode_minus": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.3,
})

BLUE   = "#4C72B0"
ORANGE = "#DD8452"
GREEN  = "#55A868"
RED    = "#C44E52"
PURPLE = "#8172B2"

created = []

# ─────────────────────────────────────────────────────────────
# 1. bayesian-statistics
# ─────────────────────────────────────────────────────────────
def chart_bayesian_statistics():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    x = np.linspace(0, 1, 300)

    # left: prior / likelihood / posterior for a single batch
    prior_a, prior_b = 2, 2
    heads, tails = 6, 4
    post_a = prior_a + heads
    post_b = prior_b + tails

    ax = axes[0]
    ax.plot(x, stats.beta.pdf(x, prior_a, prior_b), color=BLUE, lw=2, label=f"事前分布 Beta({prior_a},{prior_b})")
    ax.plot(x, stats.beta.pdf(x, heads+1, tails+1), color=ORANGE, lw=2, ls="--", label=f"尤度 (表{heads}回)")
    ax.plot(x, stats.beta.pdf(x, post_a, post_b), color=GREEN, lw=2.5, label=f"事後分布 Beta({post_a},{post_b})")
    ax.set_xlabel("コイン表の確率 θ")
    ax.set_ylabel("確率密度")
    ax.set_title("ベイズ更新：コイン投げ")
    ax.legend(fontsize=9)

    # right: posterior updates with increasing data
    ax = axes[1]
    colors_seq = [BLUE, ORANGE, GREEN, RED, PURPLE]
    configs = [(1,1,0,0), (2,2,3,7), (2,2,10,10), (2,2,20,5), (2,2,30,20)]
    labels  = ["事前 Beta(1,1)", "n=10", "n=20", "n=25 (偏り)", "n=50"]
    for (pa,pb,h,t), col, lbl in zip(configs, colors_seq, labels):
        ax.plot(x, stats.beta.pdf(x, pa+h, pb+t), color=col, lw=2, label=lbl)
    ax.set_xlabel("θ")
    ax.set_title("データ増加による事後分布の変化")
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "bayesian-statistics.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 2. hypothesis-testing
# ─────────────────────────────────────────────────────────────
def chart_hypothesis_testing():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    df = 15
    x = np.linspace(-5, 5, 500)
    pdf = stats.t.pdf(x, df)

    # left: t-distribution with rejection region (one-tail α=0.05)
    ax = axes[0]
    alpha = 0.05
    t_crit = stats.t.ppf(1 - alpha, df)
    ax.plot(x, pdf, color=BLUE, lw=2, label=f"t分布 (df={df})")
    ax.fill_between(x, pdf, where=(x >= t_crit), color=RED, alpha=0.4, label=f"棄却域 (α={alpha})")
    ax.axvline(t_crit, color=RED, ls="--", lw=1.5, label=f"臨界値 t={t_crit:.2f}")
    ax.set_xlabel("t値")
    ax.set_ylabel("確率密度")
    ax.set_title("t分布と棄却域 (片側検定)")
    ax.legend(fontsize=9)

    # right: p-value illustration for a specific t observed
    ax = axes[1]
    t_obs = 2.1
    ax.plot(x, pdf, color=BLUE, lw=2)
    ax.fill_between(x, pdf, where=(x >= t_obs), color=ORANGE, alpha=0.5, label=f"p値 ≈ {stats.t.sf(t_obs, df):.3f}")
    ax.axvline(t_obs, color=ORANGE, ls="--", lw=1.5, label=f"観測値 t={t_obs}")
    ax.set_xlabel("t値")
    ax.set_title("p値のイラスト")
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "hypothesis-testing.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 3. ml-basics
# ─────────────────────────────────────────────────────────────
def chart_ml_basics():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # left: bias-variance tradeoff
    ax = axes[0]
    complexity = np.linspace(1, 10, 200)
    train_err = 0.8 * np.exp(-0.5 * complexity) + 0.05
    test_err  = 0.8 * np.exp(-0.5 * complexity) + 0.15 + 0.02 * (complexity - 5)**2
    ax.plot(complexity, train_err, color=BLUE, lw=2, label="訓練誤差")
    ax.plot(complexity, test_err, color=ORANGE, lw=2, label="テスト誤差")
    ax.axvline(complexity[np.argmin(test_err)], color=GREEN, ls="--", lw=1.5, label="最適複雑度")
    ax.set_xlabel("モデル複雑度")
    ax.set_ylabel("誤差")
    ax.set_title("バイアス-バリアンストレードオフ")
    ax.legend(fontsize=9)

    # right: learning curve
    ax = axes[1]
    sizes = np.linspace(50, 1000, 100)
    train_lc = 0.1 + 0.4 * np.exp(-sizes / 200)
    test_lc  = 0.35 - 0.2 * (1 - np.exp(-sizes / 300))
    ax.plot(sizes, train_lc, color=BLUE, lw=2, label="訓練誤差")
    ax.plot(sizes, test_lc, color=ORANGE, lw=2, label="テスト誤差")
    ax.fill_between(sizes, train_lc, test_lc, alpha=0.15, color=GREEN, label="ギャップ")
    ax.set_xlabel("訓練データ数")
    ax.set_ylabel("誤差")
    ax.set_title("学習曲線")
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "ml-basics.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 4. scikit-learn
# ─────────────────────────────────────────────────────────────
def chart_scikit_learn():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    X, y = make_classification(n_samples=300, n_features=10, random_state=42)

    pipe_raw   = Pipeline([("knn", KNeighborsClassifier())])
    pipe_norm  = Pipeline([("scaler", StandardScaler()), ("knn", KNeighborsClassifier())])
    pipe_pca   = Pipeline([("scaler", StandardScaler()), ("pca", PCA(n_components=5)), ("knn", KNeighborsClassifier())])

    scores = {
        "Raw":        cross_val_score(pipe_raw,  X, y, cv=5).mean(),
        "Normalized": cross_val_score(pipe_norm, X, y, cv=5).mean(),
        "PCA+Norm":   cross_val_score(pipe_pca,  X, y, cv=5).mean(),
    }

    # left: bar comparison
    ax = axes[0]
    colors_bar = [BLUE, ORANGE, GREEN]
    bars = ax.bar(scores.keys(), scores.values(), color=colors_bar, width=0.5)
    for bar, val in zip(bars, scores.values()):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.005, f"{val:.3f}", ha="center", fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_ylabel("交差検証スコア (Accuracy)")
    ax.set_title("パイプライン比較 (5-fold CV)")

    # right: PCA scatter
    ax = axes[1]
    Xn = StandardScaler().fit_transform(X)
    Xp = PCA(n_components=2).fit_transform(Xn)
    scatter = ax.scatter(Xp[:, 0], Xp[:, 1], c=y, cmap="coolwarm", alpha=0.6, s=20)
    fig.colorbar(scatter, ax=ax, label="クラス")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("PCA 2次元散布図")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "scikit-learn.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 5. cnn
# ─────────────────────────────────────────────────────────────
def chart_cnn():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    rng = np.random.default_rng(0)
    img = rng.random((5, 5))

    # Sobel-like kernel
    kernel = np.array([[-1, 0, 1],
                       [-2, 0, 2],
                       [-1, 0, 1]], dtype=float)

    # Manual 2D convolution (valid)
    out_size = 5 - 3 + 1  # = 3
    conv_out = np.zeros((out_size, out_size))
    for i in range(out_size):
        for j in range(out_size):
            conv_out[i, j] = (img[i:i+3, j:j+3] * kernel).sum()

    axes[0].imshow(img, cmap="Blues", vmin=0, vmax=1)
    axes[0].set_title("入力パッチ (5×5)")
    axes[0].set_xticks([]); axes[0].set_yticks([])
    for i in range(5):
        for j in range(5):
            axes[0].text(j, i, f"{img[i,j]:.1f}", ha="center", va="center", fontsize=7, color="black")

    im1 = axes[1].imshow(kernel, cmap="YlOrRd")
    axes[1].set_title("エッジ検出カーネル (3×3)")
    axes[1].set_xticks([]); axes[1].set_yticks([])
    for i in range(3):
        for j in range(3):
            axes[1].text(j, i, f"{kernel[i,j]:.0f}", ha="center", va="center", fontsize=10, color="black")

    im2 = axes[2].imshow(conv_out, cmap="Blues")
    axes[2].set_title("畳み込み出力 (3×3)")
    axes[2].set_xticks([]); axes[2].set_yticks([])
    for i in range(out_size):
        for j in range(out_size):
            axes[2].text(j, i, f"{conv_out[i,j]:.1f}", ha="center", va="center", fontsize=9, color="black")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "cnn.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 6. rnn-lstm
# ─────────────────────────────────────────────────────────────
def chart_rnn_lstm():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # Generate sine wave
    t = np.linspace(0, 6 * np.pi, 300)
    y = np.sin(t) + 0.1 * np.random.default_rng(1).standard_normal(300)

    look_back = 30
    t_show = t[look_back:]
    actual = y[look_back:]
    # Simulated prediction: slightly delayed/smoothed
    pred = np.sin(t_show - 0.15) + 0.05 * np.random.default_rng(2).standard_normal(len(t_show))

    # left: full series with look-back window highlighted
    ax = axes[0]
    ax.plot(t, y, color=BLUE, lw=1.5, label="実際の時系列")
    ax.axvspan(t[0], t[look_back], color=ORANGE, alpha=0.2, label=f"ルックバック窓 (n={look_back})")
    ax.set_xlabel("時刻")
    ax.set_ylabel("値")
    ax.set_title("正弦波時系列と入力窓")
    ax.legend(fontsize=9)

    # right: actual vs predicted (1-step ahead)
    ax = axes[1]
    ax.plot(t_show[:100], actual[:100], color=BLUE, lw=2, label="実際")
    ax.plot(t_show[:100], pred[:100], color=ORANGE, lw=1.5, ls="--", label="予測 (1ステップ先)")
    ax.set_xlabel("時刻")
    ax.set_ylabel("値")
    ax.set_title("RNN/LSTM: 1ステップ先予測")
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "rnn-lstm.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 7. generative-models
# ─────────────────────────────────────────────────────────────
def chart_generative_models():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # left: GAN training curves (simulated)
    epochs = np.arange(1, 101)
    rng = np.random.default_rng(3)
    g_loss = 1.5 * np.exp(-epochs / 60) + 0.7 + 0.05 * rng.standard_normal(100)
    d_loss = 0.8 - 0.3 * (1 - np.exp(-epochs / 30)) + 0.05 * rng.standard_normal(100)

    ax = axes[0]
    ax.plot(epochs, g_loss, color=BLUE, lw=2, label="生成器 Loss (G)")
    ax.plot(epochs, d_loss, color=ORANGE, lw=2, label="判別器 Loss (D)")
    ax.set_xlabel("エポック")
    ax.set_ylabel("Loss")
    ax.set_title("GAN 学習曲線（シミュレーション）")
    ax.legend(fontsize=9)

    # right: VAE latent space using digits
    digits = load_digits()
    X = digits.data / 16.0
    y = digits.target
    Xs = StandardScaler().fit_transform(X)
    z = PCA(n_components=2).fit_transform(Xs)

    ax = axes[1]
    sc = ax.scatter(z[:, 0], z[:, 1], c=y, cmap="tab10", alpha=0.5, s=12)
    fig.colorbar(sc, ax=ax, label="数字クラス")
    ax.set_xlabel("潜在次元 z1")
    ax.set_ylabel("潜在次元 z2")
    ax.set_title("VAE 潜在空間（PCA可視化）")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "generative-models.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 8. transformer
# ─────────────────────────────────────────────────────────────
def chart_transformer():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    rng = np.random.default_rng(42)
    tokens = ["the", "cat", "sat", "on", "mat", ".", "EOS", "→"]
    n = len(tokens)

    # Attention matrix: diagonal-dominant
    attn = rng.random((n, n)) * 0.2
    for i in range(n):
        attn[i, max(0, i-1):i+2] += 0.4
    attn = attn / attn.sum(axis=1, keepdims=True)

    ax = axes[0]
    im = ax.imshow(attn, cmap="Blues", vmin=0, vmax=attn.max())
    ax.set_xticks(range(n)); ax.set_xticklabels(tokens, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(n)); ax.set_yticklabels(tokens, fontsize=9)
    ax.set_title("注意重みヒートマップ")
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.8)

    # Positional encoding: first 4 dims vs position
    ax = axes[1]
    positions = np.arange(50)
    d_model = 64
    pe = np.zeros((50, d_model))
    for pos in positions:
        for i in range(0, d_model, 2):
            pe[pos, i]   = np.sin(pos / 10000 ** (i / d_model))
            pe[pos, i+1] = np.cos(pos / 10000 ** (i / d_model))

    for dim, col in zip([0, 1, 2, 3], [BLUE, ORANGE, GREEN, RED]):
        ax.plot(positions, pe[:, dim], color=col, lw=1.8, label=f"dim {dim}")
    ax.set_xlabel("位置 (pos)")
    ax.set_ylabel("エンコーディング値")
    ax.set_title("位置エンコーディング (最初の4次元)")
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "transformer.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 9. llm
# ─────────────────────────────────────────────────────────────
def chart_llm():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # left: token probability distributions at different temperatures
    rng = np.random.default_rng(7)
    top_k = 10
    logits = np.array([3.5, 2.8, 2.1, 1.9, 1.5, 1.2, 0.9, 0.7, 0.4, 0.2])
    labels = [f"tok{i+1}" for i in range(top_k)]

    def softmax_temp(logits, T):
        e = np.exp((logits - logits.max()) / T)
        return e / e.sum()

    p_low  = softmax_temp(logits, 0.5)
    p_high = softmax_temp(logits, 1.5)

    ax = axes[0]
    x_pos = np.arange(top_k)
    ax.bar(x_pos - 0.2, p_low,  width=0.4, color=BLUE,   label="温度=0.5 (シャープ)")
    ax.bar(x_pos + 0.2, p_high, width=0.4, color=ORANGE, label="温度=1.5 (フラット)")
    ax.set_xticks(x_pos); ax.set_xticklabels(labels, rotation=45, fontsize=8)
    ax.set_ylabel("確率")
    ax.set_title("温度によるトークン確率分布 (Top-10)")
    ax.legend(fontsize=9)

    # right: scaling law (loss vs model size, log-log)
    ax = axes[1]
    model_size = np.logspace(7, 11, 100)  # 10M to 100B
    loss = 3.5 * (model_size / 1e7) ** (-0.076)
    ax.loglog(model_size, loss, color=BLUE, lw=2.5)
    ax.set_xlabel("モデルパラメータ数")
    ax.set_ylabel("Loss")
    ax.set_title("スケーリング則 (log-log)")
    # annotate some points
    for sz, name in [(1e7, "10M"), (1e9, "1B"), (1e11, "100B")]:
        l = 3.5 * (sz / 1e7) ** (-0.076)
        ax.annotate(name, xy=(sz, l), fontsize=9, color=ORANGE,
                    xytext=(sz*1.5, l*1.05))

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "llm.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 10. prompt-engineering
# ─────────────────────────────────────────────────────────────
def chart_prompt_engineering():
    fig, ax = plt.subplots(figsize=(9, 4))

    methods = ["ゼロショット", "ワンショット", "フューショット", "Chain-of-Thought"]
    accuracy = [52.3, 61.8, 71.4, 83.6]

    colors_bar = [BLUE, ORANGE, GREEN, RED]
    bars = ax.bar(methods, accuracy, color=colors_bar, width=0.55)
    for bar, val in zip(bars, accuracy):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.5, f"{val}%",
                ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_ylabel("精度 (%)")
    ax.set_title("プロンプト手法別の精度比較（仮想ベンチマーク）")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "prompt-engineering.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 11. rag
# ─────────────────────────────────────────────────────────────
def chart_rag():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    rng = np.random.default_rng(9)

    # left: similarity score distribution
    ax = axes[0]
    retrieved     = rng.normal(0.75, 0.08, 200)
    non_retrieved = rng.normal(0.40, 0.12, 200)
    ax.hist(retrieved,     bins=30, color=BLUE,   alpha=0.7, label="検索済みドキュメント")
    ax.hist(non_retrieved, bins=30, color=ORANGE, alpha=0.7, label="非検索ドキュメント")
    ax.axvline(0.6, color=RED, ls="--", lw=1.5, label="閾値 = 0.6")
    ax.set_xlabel("コサイン類似度")
    ax.set_ylabel("頻度")
    ax.set_title("検索スコア分布")
    ax.legend(fontsize=9)

    # right: RAG vs no-RAG accuracy
    ax = axes[1]
    cats = ["事実QA", "要約", "推論", "コード生成"]
    no_rag = [51, 58, 44, 62]
    rag    = [78, 72, 60, 68]
    x_pos = np.arange(len(cats))
    ax.bar(x_pos - 0.2, no_rag, width=0.38, color=BLUE,   label="RAGなし")
    ax.bar(x_pos + 0.2, rag,    width=0.38, color=ORANGE, label="RAGあり")
    ax.set_xticks(x_pos); ax.set_xticklabels(cats, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_ylabel("精度 (%)")
    ax.set_title("RAG有無による精度比較")
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "rag.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 12. langchain
# ─────────────────────────────────────────────────────────────
def chart_langchain():
    fig, ax = plt.subplots(figsize=(9, 4))

    steps = ["埋め込み生成", "ベクトル検索", "LLM呼び出し", "合計"]
    latencies = [45, 30, 380, 455]  # ms (simulated)
    colors_bar = [GREEN, BLUE, ORANGE, PURPLE]
    bars = ax.bar(steps, latencies, color=colors_bar, width=0.5)
    for bar, val in zip(bars, latencies):
        ax.text(bar.get_x() + bar.get_width()/2, val + 5, f"{val}ms",
                ha="center", fontsize=10)
    ax.set_ylabel("レイテンシ (ms)")
    ax.set_title("RAGパイプラインのレイテンシ内訳（シミュレーション）")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "langchain.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 13. fine-tuning
# ─────────────────────────────────────────────────────────────
def chart_fine_tuning():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    epochs = np.arange(1, 21)
    rng = np.random.default_rng(11)

    full_loss   = 1.8 * np.exp(-epochs / 5) + 0.15 + 0.02 * rng.standard_normal(20)
    lora_loss   = 1.8 * np.exp(-epochs / 6) + 0.22 + 0.02 * rng.standard_normal(20)
    frozen_loss = 1.8 * np.exp(-epochs / 12) + 0.55 + 0.02 * rng.standard_normal(20)

    ax = axes[0]
    ax.plot(epochs, full_loss,   color=BLUE,   lw=2, label="フルファインチューン")
    ax.plot(epochs, lora_loss,   color=ORANGE, lw=2, label="LoRA")
    ax.plot(epochs, frozen_loss, color=GREEN,  lw=2, label="特徴抽出（凍結）")
    ax.set_xlabel("エポック")
    ax.set_ylabel("Loss")
    ax.set_title("ファインチューニング手法の学習曲線")
    ax.legend(fontsize=9)

    # right: parameter count comparison
    ax = axes[1]
    methods  = ["フルファインチューン", "LoRA\n(rank=8)", "特徴抽出\n(凍結)"]
    params_m = [7000, 8, 0.5]  # millions
    colors_bar = [BLUE, ORANGE, GREEN]
    bars = ax.bar(methods, params_m, color=colors_bar, width=0.5)
    for bar, val in zip(bars, params_m):
        ax.text(bar.get_x() + bar.get_width()/2, val + 50, f"{val}M",
                ha="center", fontsize=9)
    ax.set_ylabel("学習可能パラメータ数 (M)")
    ax.set_title("学習パラメータ数の比較")
    ax.set_yscale("log")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "fine-tuning.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 14. gpu-architecture
# ─────────────────────────────────────────────────────────────
def chart_gpu_architecture():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # left: roofline model
    ax = axes[0]
    bw_peak     = 2000   # GB/s
    flops_peak  = 312    # TFLOPS (FP16)
    ridge_point = flops_peak / (bw_peak / 1e3)  # in FLOP/byte

    intensity = np.logspace(-1, 3, 300)
    perf = np.minimum(intensity * (bw_peak / 1e3), flops_peak)

    ax.loglog(intensity, perf, color=BLUE, lw=2.5, label="ルーフラインモデル")
    ax.axvline(ridge_point, color=RED, ls="--", lw=1.5, label=f"リッジポイント ({ridge_point:.0f} FLOP/Byte)")

    # annotate typical ops
    for name, ai, col in [("GEMM\n(大)", 100, GREEN), ("Elementwise", 1, ORANGE)]:
        p = min(ai * (bw_peak / 1e3), flops_peak)
        ax.scatter([ai], [p], color=col, s=80, zorder=5)
        ax.annotate(name, (ai, p), fontsize=8, xytext=(ai*0.4, p*0.6))

    ax.set_xlabel("演算強度 (FLOP/Byte)")
    ax.set_ylabel("性能 (TFLOPS)")
    ax.set_title("ルーフラインモデル")
    ax.legend(fontsize=8)

    # right: throughput comparison
    ax = axes[1]
    dtypes = ["FP32", "TF32", "FP16", "INT8"]
    tflops = [19.5, 156, 312, 624]  # A100 approx
    colors_bar = [BLUE, GREEN, ORANGE, RED]
    bars = ax.bar(dtypes, tflops, color=colors_bar, width=0.5)
    for bar, val in zip(bars, tflops):
        ax.text(bar.get_x() + bar.get_width()/2, val + 8, f"{val}",
                ha="center", fontsize=10)
    ax.set_ylabel("スループット (TFLOPS)")
    ax.set_title("データ型別スループット (A100)")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "gpu-architecture.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 15. nvidia-gpu-lineup
# ─────────────────────────────────────────────────────────────
def chart_nvidia_gpu_lineup():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    gpus      = ["V100", "A100\n(SXM)", "H100\n(SXM)", "RTX 3090", "RTX 4090"]
    tflops_fp16 = [125, 312, 989, 35.6, 82.6]
    mem_bw      = [900, 2000, 3350, 936, 1008]  # GB/s

    ax = axes[0]
    colors_bar = [PURPLE, BLUE, RED, ORANGE, GREEN]
    bars = ax.bar(gpus, tflops_fp16, color=colors_bar, width=0.55)
    for bar, val in zip(bars, tflops_fp16):
        ax.text(bar.get_x() + bar.get_width()/2, val + 10, f"{val}",
                ha="center", fontsize=9)
    ax.set_ylabel("ピーク性能 (TFLOPS, FP16)")
    ax.set_title("GPU モデル別ピーク TFLOPS (FP16)")

    ax = axes[1]
    bars2 = ax.bar(gpus, mem_bw, color=colors_bar, width=0.55)
    for bar, val in zip(bars2, mem_bw):
        ax.text(bar.get_x() + bar.get_width()/2, val + 30, f"{val}",
                ha="center", fontsize=9)
    ax.set_ylabel("メモリ帯域幅 (GB/s)")
    ax.set_title("GPU モデル別メモリ帯域幅")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "nvidia-gpu-lineup.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 16. object-detection
# ─────────────────────────────────────────────────────────────
def chart_object_detection():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # left: IoU diagram
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.set_aspect("equal")
    ax.set_title("IoU 図解")

    # Ground truth box
    gt = plt.Rectangle((1, 1), 5, 4, linewidth=2, edgecolor=BLUE, facecolor=BLUE, alpha=0.25, label="Ground Truth")
    # Predicted box
    pred_box = plt.Rectangle((3, 2), 5, 4, linewidth=2, edgecolor=ORANGE, facecolor=ORANGE, alpha=0.25, label="予測ボックス")
    # Intersection
    ix1, iy1 = max(1,3), max(1,2)
    ix2, iy2 = min(1+5, 3+5), min(1+4, 2+4)
    inter = plt.Rectangle((ix1, iy1), ix2-ix1, iy2-iy1, linewidth=0, facecolor=GREEN, alpha=0.5, label="Intersection")

    for patch in [gt, pred_box, inter]:
        ax.add_patch(patch)

    inter_area = (ix2 - ix1) * (iy2 - iy1)
    gt_area = 5 * 4
    pred_area = 5 * 4
    union_area = gt_area + pred_area - inter_area
    iou = inter_area / union_area

    ax.text(4.5, 3.2, f"IoU = {iou:.2f}", ha="center", va="center", fontsize=14, fontweight="bold", color="black")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.grid(False)

    # right: precision-recall curve (mAP)
    ax = axes[1]
    recall = np.linspace(0, 1, 100)
    prec_model_a = np.clip(1 - recall**1.2 + 0.05 * np.sin(recall * 10), 0, 1)
    prec_model_b = np.clip(0.9 - recall**0.9 + 0.03 * np.sin(recall * 8), 0, 1)

    ap_a = np.trapezoid(prec_model_a, recall) if hasattr(np, "trapezoid") else np.trapz(prec_model_a, recall)
    ap_b = np.trapezoid(prec_model_b, recall) if hasattr(np, "trapezoid") else np.trapz(prec_model_b, recall)
    ax.plot(recall, prec_model_a, color=BLUE,   lw=2, label=f"モデルA (AP={ap_a:.2f})")
    ax.plot(recall, prec_model_b, color=ORANGE, lw=2, label=f"モデルB (AP={ap_b:.2f})")
    ax.fill_between(recall, prec_model_a, alpha=0.1, color=BLUE)
    ax.fill_between(recall, prec_model_b, alpha=0.1, color=ORANGE)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall 曲線 (mAP)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.05)
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "object-detection.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 17. clip
# ─────────────────────────────────────────────────────────────
def chart_clip():
    fig, ax = plt.subplots(figsize=(8, 5))

    image_labels = ["犬の写真", "猫の写真", "車の写真", "花の写真"]
    text_labels  = ["a dog", "a cat", "a car", "a flower"]

    # Simulated cosine similarity: diagonal is highest
    sim = np.array([
        [0.92, 0.45, 0.12, 0.18],
        [0.41, 0.88, 0.15, 0.20],
        [0.10, 0.13, 0.91, 0.09],
        [0.17, 0.22, 0.08, 0.93],
    ])

    im = ax.imshow(sim, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(4)); ax.set_xticklabels(text_labels, fontsize=10)
    ax.set_yticks(range(4)); ax.set_yticklabels(image_labels, fontsize=10)
    ax.set_title("CLIP コサイン類似度ヒートマップ (画像×テキスト)")
    ax.grid(False)

    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{sim[i,j]:.2f}", ha="center", va="center",
                    fontsize=11, color="white" if sim[i,j] > 0.6 else "black")

    fig.colorbar(im, ax=ax, shrink=0.8, label="コサイン類似度")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "clip.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 18. blip
# ─────────────────────────────────────────────────────────────
def chart_blip():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    rng = np.random.default_rng(14)

    # left: attention heatmap over image regions
    n_text = 8
    n_img  = 16
    attn = rng.random((n_text, n_img))
    # Make some structure: each text token attends primarily to a region
    for i in range(n_text):
        peak = int(i * n_img / n_text)
        attn[i, max(0,peak-2):peak+3] += 0.6
    attn = attn / attn.sum(axis=1, keepdims=True)

    text_tokens = ["a", "cat", "sit", "on", "the", "mat", "<SEP>", "<EOS>"]
    img_patches = [f"P{i}" for i in range(n_img)]

    im = axes[0].imshow(attn, cmap="YlOrRd", aspect="auto")
    axes[0].set_xticks(range(n_img)[::2]); axes[0].set_xticklabels(img_patches[::2], rotation=45, fontsize=7)
    axes[0].set_yticks(range(n_text)); axes[0].set_yticklabels(text_tokens, fontsize=9)
    axes[0].set_title("テキスト×画像パッチ 注意重み")
    axes[0].set_xlabel("画像パッチ")
    axes[0].set_ylabel("テキストトークン")
    axes[0].grid(False)
    fig.colorbar(im, ax=axes[0], shrink=0.8)

    # right: training loss curve
    epochs = np.arange(1, 31)
    loss_itm = 1.2 * np.exp(-epochs / 8) + 0.18 + 0.01 * rng.standard_normal(30)
    loss_cap = 2.0 * np.exp(-epochs / 10) + 0.25 + 0.01 * rng.standard_normal(30)

    axes[1].plot(epochs, loss_itm, color=BLUE,   lw=2, label="Image-Text Matching Loss")
    axes[1].plot(epochs, loss_cap, color=ORANGE, lw=2, label="Captioning Loss")
    axes[1].set_xlabel("エポック")
    axes[1].set_ylabel("Loss")
    axes[1].set_title("BLIP 学習曲線")
    axes[1].legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "blip.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 19. qformer
# ─────────────────────────────────────────────────────────────
def chart_qformer():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    rng = np.random.default_rng(15)

    # left: 32 query tokens × 64 image patches cross-attention
    n_queries = 32
    n_patches = 64
    attn = rng.random((n_queries, n_patches)) * 0.3
    # Add some structure: groups of queries attend to regions
    for q in range(n_queries):
        center = int(q * n_patches / n_queries)
        attn[q, max(0, center-4):center+5] += 0.5
    attn = attn / attn.sum(axis=1, keepdims=True)

    im = axes[0].imshow(attn, cmap="Blues", aspect="auto")
    axes[0].set_xlabel("画像パッチ (64)")
    axes[0].set_ylabel("クエリトークン (32)")
    axes[0].set_title("Q-Former クロスアテンション重み")
    axes[0].grid(False)
    fig.colorbar(im, ax=axes[0], shrink=0.8)

    # right: compression ratio bar
    ax = axes[1]
    stages = ["ViT出力\n(256トークン)", "Q-Former後\n(32トークン)", "LLM入力\n(32トークン)"]
    counts = [256, 32, 32]
    colors_bar = [BLUE, ORANGE, GREEN]
    bars = ax.bar(stages, counts, color=colors_bar, width=0.5)
    for bar, val in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, val + 3, str(val),
                ha="center", fontsize=10)
    ax.set_ylabel("トークン数")
    ax.set_title("Q-Former: 情報圧縮比")
    ax.annotate("", xy=(1, 144), xytext=(0, 144),
                arrowprops=dict(arrowstyle="->", color=RED, lw=2))
    ax.text(0.5, 150, "8× 圧縮", ha="center", fontsize=10, color=RED)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "qformer.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 20. image-processing
# ─────────────────────────────────────────────────────────────
def chart_image_processing():
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.5))

    # Create a 50×50 gradient + checkerboard image
    x = np.linspace(0, 1, 50)
    y = np.linspace(0, 1, 50)
    xx, yy = np.meshgrid(x, y)
    img = (xx + yy) / 2

    # Checkerboard overlay
    checker = (np.indices((50, 50)).sum(axis=0) % 10 < 5).astype(float) * 0.15
    img = np.clip(img + checker, 0, 1)

    # Gaussian blur (manual)
    from scipy.ndimage import gaussian_filter, sobel
    blurred = gaussian_filter(img, sigma=2)

    # Sobel edge detection
    sx = sobel(img, axis=1)
    sy = sobel(img, axis=0)
    edges = np.hypot(sx, sy)

    axes[0].imshow(img,     cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("元画像")
    axes[0].axis("off")

    axes[1].imshow(blurred, cmap="gray", vmin=0, vmax=1)
    axes[1].set_title("ガウスぼかし (σ=2)")
    axes[1].axis("off")

    axes[2].imshow(edges,   cmap="gray")
    axes[2].set_title("エッジ検出 (Sobel)")
    axes[2].axis("off")

    axes[3].hist(img.ravel(), bins=40, color=BLUE, alpha=0.8)
    axes[3].set_xlabel("輝度値")
    axes[3].set_ylabel("頻度")
    axes[3].set_title("画素値ヒストグラム")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "image-processing.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 21. opencv
# ─────────────────────────────────────────────────────────────
def chart_opencv():
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))

    rng = np.random.default_rng(20)

    # Simulate an RGB image (50×50×3)
    # R channel: high in top-left, G: top-right, B: bottom
    h, w = 50, 50
    R = np.zeros((h, w))
    G = np.zeros((h, w))
    B = np.zeros((h, w))
    R[:25, :25] = 0.85; R += rng.random((h, w)) * 0.1
    G[:25, 25:] = 0.80; G += rng.random((h, w)) * 0.1
    B[25:, :]   = 0.75; B += rng.random((h, w)) * 0.1
    R = np.clip(R, 0, 1); G = np.clip(G, 0, 1); B = np.clip(B, 0, 1)

    # left: RGB histograms
    ax = axes[0]
    bins = np.linspace(0, 1, 40)
    ax.hist(R.ravel(), bins=bins, color=RED,   alpha=0.6, label="R チャンネル")
    ax.hist(G.ravel(), bins=bins, color=GREEN, alpha=0.6, label="G チャンネル")
    ax.hist(B.ravel(), bins=bins, color=BLUE,  alpha=0.6, label="B チャンネル")
    ax.set_xlabel("輝度値")
    ax.set_ylabel("頻度")
    ax.set_title("カラーチャンネルヒストグラム")
    ax.legend(fontsize=8)

    # middle: simulated HSV thresholding - "before"
    img_rgb = np.stack([R, G, B], axis=-1)
    axes[1].imshow(img_rgb)
    axes[1].set_title("元画像 (RGB)")
    axes[1].axis("off")

    # right: HSV mask (select high-Hue = approx red/G region)
    # Simple simulation: keep pixels where G > 0.5
    mask = (G > 0.5).astype(float)
    result = img_rgb.copy()
    result[mask < 0.5] = 0
    axes[2].imshow(result)
    axes[2].set_title("HSV閾値処理後（G チャンネル抽出）")
    axes[2].axis("off")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "opencv.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# 22. pytorch
# ─────────────────────────────────────────────────────────────
def chart_pytorch():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    rng = np.random.default_rng(22)
    X, y = make_classification(n_samples=500, n_features=20, random_state=22)
    X = StandardScaler().fit_transform(X)

    # Simulate 2-layer MLP training curves (numpy-based)
    epochs = np.arange(1, 51)
    train_loss = 0.7 * np.exp(-epochs / 15) + 0.12 + 0.01 * rng.standard_normal(50)
    val_loss   = 0.7 * np.exp(-epochs / 18) + 0.18 + 0.015 * rng.standard_normal(50)
    train_acc  = 0.5 + 0.45 * (1 - np.exp(-epochs / 12)) + 0.005 * rng.standard_normal(50)
    val_acc    = 0.5 + 0.40 * (1 - np.exp(-epochs / 14)) + 0.008 * rng.standard_normal(50)

    ax = axes[0]
    ax2 = ax.twinx()
    ax.plot(epochs, train_loss, color=BLUE,   lw=2, label="訓練Loss")
    ax.plot(epochs, val_loss,   color=ORANGE, lw=2, ls="--", label="検証Loss")
    ax2.plot(epochs, train_acc,  color=GREEN, lw=1.5, ls=":", label="訓練Acc")
    ax2.plot(epochs, val_acc,    color=RED,   lw=1.5, ls="-.", label="検証Acc")
    ax.set_xlabel("エポック")
    ax.set_ylabel("Loss")
    ax2.set_ylabel("Accuracy")
    ax.set_title("MLP 学習曲線 (Loss / Accuracy)")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="center right")

    # right: weight distribution before/after training (simulated)
    ax = axes[1]
    w_before = rng.standard_normal(1000) * 0.5
    w_after  = rng.standard_normal(1000) * 0.3 + 0.05
    bins = np.linspace(-2, 2, 50)
    ax.hist(w_before, bins=bins, color=BLUE,   alpha=0.6, label="学習前 (初期化)")
    ax.hist(w_after,  bins=bins, color=ORANGE, alpha=0.6, label="学習後")
    ax.set_xlabel("重みの値")
    ax.set_ylabel("頻度")
    ax.set_title("重みの分布変化")
    ax.legend(fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "pytorch.png")
    fig.savefig(path)
    plt.close(fig)
    created.append(path)


# ─────────────────────────────────────────────────────────────
# Run all
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    funcs = [
        chart_bayesian_statistics,
        chart_hypothesis_testing,
        chart_ml_basics,
        chart_scikit_learn,
        chart_cnn,
        chart_rnn_lstm,
        chart_generative_models,
        chart_transformer,
        chart_llm,
        chart_prompt_engineering,
        chart_rag,
        chart_langchain,
        chart_fine_tuning,
        chart_gpu_architecture,
        chart_nvidia_gpu_lineup,
        chart_object_detection,
        chart_clip,
        chart_blip,
        chart_qformer,
        chart_image_processing,
        chart_opencv,
        chart_pytorch,
    ]

    print(f"生成開始: {len(funcs)} チャート\n")
    for fn in funcs:
        try:
            fn()
            print(f"  [OK] {fn.__name__}")
        except Exception as e:
            print(f"  [NG] {fn.__name__}: {e}")

    print(f"\n=== 作成ファイル一覧 ({len(created)}/{len(funcs)}) ===")
    for p in created:
        size_kb = os.path.getsize(p) / 1024
        print(f"  {os.path.basename(p):40s}  {size_kb:6.1f} KB")
    print("\n完了!")
