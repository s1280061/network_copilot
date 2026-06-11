"""
Generate chart images for article embedding.
Run from repo root: python backend/gen_charts.py
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

# ──────────────────────────────────────────────────────────
# statistics.md
# ──────────────────────────────────────────────────────────
def chart_normal_distribution():
    from scipy.stats import norm
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    x = np.linspace(-4, 4, 400)
    for mu, sigma, color in [(0, 1, "#4C72B0"), (1, 0.5, "#DD8452"), (-1, 1.5, "#55A868")]:
        axes[0].plot(x, norm.pdf(x, mu, sigma), lw=2,
                     label=f"μ={mu}, σ={sigma}")
    axes[0].set_title("正規分布（パラメータ比較）")
    axes[0].set_xlabel("x"); axes[0].set_ylabel("確率密度")
    axes[0].legend(fontsize=9)

    rng = np.random.default_rng(42)
    data = rng.normal(170, 6, 500)
    axes[1].hist(data, bins=30, color="#4C72B0", edgecolor="white", alpha=0.85, density=True)
    xh = np.linspace(data.min(), data.max(), 300)
    axes[1].plot(xh, norm.pdf(xh, data.mean(), data.std()), "r-", lw=2, label="理論曲線")
    axes[1].axvline(data.mean(), color="red", linestyle="--", lw=1.5, label=f"平均={data.mean():.1f}")
    axes[1].set_title("身長の分布（N=500, μ=170, σ=6）")
    axes[1].set_xlabel("身長 [cm]"); axes[1].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{OUT}/statistics-normal.png"); plt.close()
    print("✓ statistics-normal.png")

# ──────────────────────────────────────────────────────────
# regression-analysis.md
# ──────────────────────────────────────────────────────────
def chart_regression():
    from scipy.stats import norm
    rng = np.random.default_rng(42)
    n = 80
    temp = rng.uniform(15, 35, n)
    sales = 2.5 * temp - 20 + rng.normal(0, 5, n)

    # OLS by hand
    X = np.column_stack([np.ones(n), temp])
    beta = np.linalg.lstsq(X, sales, rcond=None)[0]
    x_line = np.linspace(14, 36, 200)
    y_line = beta[0] + beta[1] * x_line

    ss_res = np.sum((sales - (beta[0] + beta[1]*temp))**2)
    ss_tot = np.sum((sales - sales.mean())**2)
    r2 = 1 - ss_res / ss_tot

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    axes[0].scatter(temp, sales, alpha=0.6, color="#4C72B0", s=30, label="観測値")
    axes[0].plot(x_line, y_line, "r-", lw=2, label=f"回帰直線 R²={r2:.3f}")
    axes[0].set_xlabel("気温 [℃]"); axes[0].set_ylabel("アイス販売数")
    axes[0].set_title("単回帰分析：気温 vs 販売数")
    axes[0].legend(fontsize=9)

    residuals = sales - (beta[0] + beta[1]*temp)
    fitted = beta[0] + beta[1]*temp
    axes[1].scatter(fitted, residuals, alpha=0.6, color="#55A868", s=30)
    axes[1].axhline(0, color="red", linestyle="--", lw=1.5)
    axes[1].set_xlabel("当てはめ値"); axes[1].set_ylabel("残差")
    axes[1].set_title("残差プロット（等分散性の確認）")

    plt.tight_layout()
    plt.savefig(f"{OUT}/regression-analysis.png"); plt.close()
    print("✓ regression-analysis.png")

# ──────────────────────────────────────────────────────────
# time-series-statistics.md
# ──────────────────────────────────────────────────────────
def chart_timeseries():
    import pandas as pd

    rng = np.random.default_rng(42)
    n = 120
    t = np.arange(n)
    trend = 0.05 * t
    seasonal = 5 * np.sin(2 * np.pi * t / 12)
    noise = rng.normal(0, 1, n)
    series = trend + seasonal + noise + 20

    idx = pd.date_range("2014-01", periods=n, freq="ME")
    ts = pd.Series(series, index=idx)

    # manual decompose (additive)
    window = 13
    trend_comp = ts.rolling(window, center=True).mean()

    fig, axes = plt.subplots(3, 1, figsize=(11, 7), sharex=True)
    ts.plot(ax=axes[0], color="#4C72B0", lw=1.2)
    axes[0].set_title("観測値（月次データ）"); axes[0].set_ylabel("値")

    trend_comp.plot(ax=axes[1], color="#DD8452", lw=2)
    axes[1].set_title("トレンド成分（移動平均 13期間）"); axes[1].set_ylabel("値")

    resid = ts - trend_comp
    resid.plot(ax=axes[2], color="#55A868", lw=1, alpha=0.8)
    axes[2].axhline(0, color="gray", linestyle="--", lw=1)
    axes[2].set_title("残差（トレンド除去後）"); axes[2].set_ylabel("値")

    plt.tight_layout()
    plt.savefig(f"{OUT}/timeseries-decompose.png"); plt.close()
    print("✓ timeseries-decompose.png")

    # ARIMA-like forecast (simple AR(1) for demo)
    rng2 = np.random.default_rng(123)
    n2 = 120
    t2 = np.arange(n2)
    elec = 500 + 0.3*t2 + 80*np.sin(2*np.pi*t2/12) + rng2.normal(0, 15, n2)
    idx2 = pd.date_range("2015-01", periods=n2, freq="ME")
    ts_elec = pd.Series(elec, index=idx2)
    train = ts_elec[:-12]; test = ts_elec[-12:]

    # naive forecast: last 12 seasonal average
    forecast_vals = []
    for i in range(12):
        past_same_month = train[train.index.month == test.index[i].month]
        forecast_vals.append(past_same_month.iloc[-1] + 0.3*12)
    import pandas as pd
    forecast = pd.Series(forecast_vals, index=test.index)
    mae = np.abs(test.values - forecast.values).mean()

    fig, ax = plt.subplots(figsize=(11, 4))
    train.plot(ax=ax, label="訓練データ", color="#4C72B0")
    test.plot(ax=ax, label="実測値", color="#55A868", lw=2)
    forecast.plot(ax=ax, label=f"予測値（MAE={mae:.1f}）", color="#C44E52", lw=2, linestyle="--")
    ax.fill_between(forecast.index,
                    forecast.values - 2*mae,
                    forecast.values + 2*mae,
                    alpha=0.2, color="#C44E52", label="予測区間（±2×MAE）")
    ax.set_title("月次電力消費量の予測（12ヶ月先）")
    ax.set_ylabel("消費量 [kWh]"); ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(f"{OUT}/timeseries-forecast.png"); plt.close()
    print("✓ timeseries-forecast.png")

# ──────────────────────────────────────────────────────────
# clustering.md
# ──────────────────────────────────────────────────────────
def chart_clustering():
    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(42)
    X, y_true = make_blobs(n_samples=300, centers=4, cluster_std=0.9, random_state=42)
    scaler = StandardScaler()
    X_s = scaler.fit_transform(X)

    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # raw data
    axes[0].scatter(X_s[:, 0], X_s[:, 1], alpha=0.5, color="gray", s=20)
    axes[0].set_title("元データ（ラベルなし）")
    axes[0].set_xlabel("特徴量1"); axes[0].set_ylabel("特徴量2")

    # K-means k=4
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = km.fit_predict(X_s)
    for k in range(4):
        mask = labels == k
        axes[1].scatter(X_s[mask, 0], X_s[mask, 1], alpha=0.6, color=colors[k], s=20)
    axes[1].scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1],
                    c="black", marker="X", s=150, zorder=5, label="重心")
    axes[1].set_title("K-means（k=4）"); axes[1].legend(fontsize=9)
    axes[1].set_xlabel("特徴量1")

    # Elbow method
    inertias = []
    ks = range(1, 9)
    for k in ks:
        inertias.append(KMeans(n_clusters=k, random_state=42, n_init=10).fit(X_s).inertia_)
    axes[2].plot(ks, inertias, "o-", color="#4C72B0", lw=2)
    axes[2].axvline(4, color="red", linestyle="--", lw=1.5, label="エルボー点 k=4")
    axes[2].set_title("エルボー法（最適 k の選択）")
    axes[2].set_xlabel("クラスタ数 k"); axes[2].set_ylabel("慣性（Within-cluster SS）")
    axes[2].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{OUT}/clustering-kmeans.png"); plt.close()
    print("✓ clustering-kmeans.png")

# ──────────────────────────────────────────────────────────
# deep-learning.md
# ──────────────────────────────────────────────────────────
def chart_deep_learning():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # Activation functions
    x = np.linspace(-4, 4, 300)
    sigmoid = 1 / (1 + np.exp(-x))
    tanh = np.tanh(x)
    relu = np.maximum(0, x)
    leaky = np.where(x >= 0, x, 0.1 * x)

    axes[0].plot(x, sigmoid, lw=2, label="Sigmoid")
    axes[0].plot(x, tanh,    lw=2, label="Tanh")
    axes[0].plot(x, relu,    lw=2, label="ReLU")
    axes[0].plot(x, leaky,   lw=2, label="Leaky ReLU", linestyle="--")
    axes[0].axhline(0, color="gray", lw=0.8)
    axes[0].set_title("活性化関数の比較")
    axes[0].set_xlabel("入力 x"); axes[0].set_ylabel("出力")
    axes[0].legend(fontsize=9)

    # Simulated training curves
    epochs = np.arange(1, 51)
    rng = np.random.default_rng(42)
    train_loss = 2.0 * np.exp(-0.08 * epochs) + 0.05 + rng.normal(0, 0.02, 50)
    val_loss   = 2.0 * np.exp(-0.07 * epochs) + 0.15 + rng.normal(0, 0.03, 50)
    train_acc  = 1 - 0.9 * np.exp(-0.09 * epochs) + rng.normal(0, 0.01, 50)
    val_acc    = 1 - 0.9 * np.exp(-0.08 * epochs) - 0.03 + rng.normal(0, 0.015, 50)

    axes[1].plot(epochs, train_loss, lw=2, label="訓練損失", color="#4C72B0")
    axes[1].plot(epochs, val_loss,   lw=2, label="検証損失", color="#DD8452")
    axes[1].set_title("学習曲線（損失）")
    axes[1].set_xlabel("エポック"); axes[1].set_ylabel("Loss（交差エントロピー）")
    axes[1].legend(fontsize=9)

    axes[2].plot(epochs, np.clip(train_acc, 0, 1), lw=2, label="訓練精度", color="#55A868")
    axes[2].plot(epochs, np.clip(val_acc,   0, 1), lw=2, label="検証精度", color="#C44E52")
    axes[2].set_title("学習曲線（精度）")
    axes[2].set_xlabel("エポック"); axes[2].set_ylabel("Accuracy")
    axes[2].set_ylim(0, 1.05); axes[2].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{OUT}/deep-learning-curves.png"); plt.close()
    print("✓ deep-learning-curves.png")

# ──────────────────────────────────────────────────────────
# linear-regression.md
# ──────────────────────────────────────────────────────────
def chart_linear_regression():
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import make_pipeline

    rng = np.random.default_rng(42)
    n = 60
    X_1d = rng.uniform(0, 10, n)
    y = 2*X_1d + 1 + rng.normal(0, 2, n)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # linear vs poly fit
    x_line = np.linspace(0, 10, 200).reshape(-1, 1)
    for deg, color, label in [(1, "#4C72B0", "線形（次数1）"),
                               (3, "#DD8452", "多項式（次数3）"),
                               (8, "#C44E52", "過学習（次数8）")]:
        model = make_pipeline(PolynomialFeatures(deg), LinearRegression())
        model.fit(X_1d.reshape(-1, 1), y)
        axes[0].plot(x_line, model.predict(x_line), lw=2, label=label, color=color)
    axes[0].scatter(X_1d, y, alpha=0.4, s=20, color="gray")
    axes[0].set_title("モデル複雑度と過学習")
    axes[0].set_xlabel("x"); axes[0].set_ylabel("y")
    axes[0].set_ylim(-5, 25); axes[0].legend(fontsize=9)

    # Ridge vs Lasso coefficient paths
    from sklearn.datasets import make_regression
    X_r, y_r = make_regression(n_samples=100, n_features=10, noise=10, random_state=42)
    alphas = np.logspace(-2, 3, 50)
    ridge_coefs = [Ridge(alpha=a).fit(X_r, y_r).coef_ for a in alphas]
    lasso_coefs = [Lasso(alpha=a, max_iter=5000).fit(X_r, y_r).coef_ for a in alphas]

    for coef_path in np.array(ridge_coefs).T:
        axes[1].plot(np.log10(alphas), coef_path, lw=1, alpha=0.7)
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].set_title("Ridge：正則化パス（係数の変化）")
    axes[1].set_xlabel("log₁₀(α)"); axes[1].set_ylabel("係数")

    for coef_path in np.array(lasso_coefs).T:
        axes[2].plot(np.log10(alphas), coef_path, lw=1, alpha=0.7)
    axes[2].axhline(0, color="black", lw=0.8)
    axes[2].set_title("Lasso：正則化パス（スパース化）")
    axes[2].set_xlabel("log₁₀(α)"); axes[2].set_ylabel("係数")

    plt.tight_layout()
    plt.savefig(f"{OUT}/linear-regression-paths.png"); plt.close()
    print("✓ linear-regression-paths.png")

# ──────────────────────────────────────────────────────────
# dimensionality-reduction.md
# ──────────────────────────────────────────────────────────
def chart_dimensionality():
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.datasets import load_digits

    digits = load_digits()
    X, y = digits.data, digits.target

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # PCA 2D
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X)
    scatter = axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap="tab10", s=5, alpha=0.7)
    axes[0].set_title(f"PCA（2次元）\n寄与率: {pca.explained_variance_ratio_.sum()*100:.1f}%")
    axes[0].set_xlabel("PC1"); axes[0].set_ylabel("PC2")
    plt.colorbar(scatter, ax=axes[0], label="数字クラス")

    # PCA explained variance
    pca_full = PCA(random_state=42).fit(X)
    cumvar = np.cumsum(pca_full.explained_variance_ratio_) * 100
    axes[1].plot(range(1, len(cumvar)+1), cumvar, color="#4C72B0", lw=2)
    axes[1].axhline(90, color="red", linestyle="--", lw=1.5, label="90%")
    axes[1].axhline(95, color="orange", linestyle="--", lw=1.5, label="95%")
    axes[1].set_title("PCA：累積寄与率")
    axes[1].set_xlabel("主成分数"); axes[1].set_ylabel("累積寄与率 [%]")
    axes[1].set_xlim(0, 50); axes[1].legend(fontsize=9)

    # t-SNE 2D
    tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=500)
    X_tsne = tsne.fit_transform(X)
    scatter2 = axes[2].scatter(X_tsne[:, 0], X_tsne[:, 1], c=y, cmap="tab10", s=5, alpha=0.7)
    axes[2].set_title("t-SNE（2次元）\n各数字クラスが明確に分離")
    axes[2].set_xlabel("t-SNE 1"); axes[2].set_ylabel("t-SNE 2")
    plt.colorbar(scatter2, ax=axes[2], label="数字クラス")

    plt.tight_layout()
    plt.savefig(f"{OUT}/dimensionality-reduction.png"); plt.close()
    print("✓ dimensionality-reduction.png")

# ──────────────────────────────────────────────────────────
# classification.md
# ──────────────────────────────────────────────────────────
def chart_classification():
    from sklearn.datasets import make_classification
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import confusion_matrix, roc_curve, auc
    from sklearn.model_selection import train_test_split

    rng = np.random.default_rng(42)
    X, y = make_classification(n_samples=500, n_features=2, n_redundant=0,
                                n_clusters_per_class=1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # Decision boundary (Logistic)
    lr = LogisticRegression(random_state=42).fit(X_train, y_train)
    xx, yy = np.meshgrid(np.linspace(X[:,0].min()-0.5, X[:,0].max()+0.5, 200),
                         np.linspace(X[:,1].min()-0.5, X[:,1].max()+0.5, 200))
    Z = lr.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    axes[0].contourf(xx, yy, Z, alpha=0.3, cmap="coolwarm")
    for c, color in [(0, "#4C72B0"), (1, "#C44E52")]:
        mask = y_test == c
        axes[0].scatter(X_test[mask, 0], X_test[mask, 1], c=color, s=20, alpha=0.7, label=f"クラス{c}")
    axes[0].set_title("ロジスティック回帰\n決定境界")
    axes[0].set_xlabel("特徴量1"); axes[0].set_ylabel("特徴量2")
    axes[0].legend(fontsize=9)

    # Confusion matrix
    y_pred = lr.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    im = axes[1].imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            axes[1].text(j, i, cm[i, j], ha="center", va="center", fontsize=14,
                         color="white" if cm[i, j] > cm.max()/2 else "black")
    axes[1].set_xticks([0,1]); axes[1].set_yticks([0,1])
    axes[1].set_xticklabels(["予測:0","予測:1"]); axes[1].set_yticklabels(["実際:0","実際:1"])
    axes[1].set_title("混同行列\n（ロジスティック回帰）")

    # ROC curve
    for model, name, color in [
        (LogisticRegression(random_state=42), "ロジスティック回帰", "#4C72B0"),
        (RandomForestClassifier(random_state=42), "ランダムフォレスト", "#DD8452"),
    ]:
        model.fit(X_train, y_train)
        prob = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, prob)
        roc_auc = auc(fpr, tpr)
        axes[2].plot(fpr, tpr, lw=2, color=color, label=f"{name} (AUC={roc_auc:.3f})")
    axes[2].plot([0,1],[0,1],"--",color="gray",lw=1,label="ランダム (AUC=0.5)")
    axes[2].set_title("ROC曲線")
    axes[2].set_xlabel("偽陽性率 (FPR)"); axes[2].set_ylabel("真陽性率 (TPR)")
    axes[2].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{OUT}/classification-roc.png"); plt.close()
    print("✓ classification-roc.png")

# ──────────────────────────────────────────────────────────
# gradient-boosting.md
# ──────────────────────────────────────────────────────────
def chart_gradient_boosting():
    from sklearn.datasets import make_regression
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error

    X, y = make_regression(n_samples=500, n_features=10, noise=20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # Learning curves for different n_estimators
    n_trees = [1, 5, 10, 20, 50, 100, 200]
    gb_train_rmse, gb_test_rmse = [], []
    rf_train_rmse, rf_test_rmse = [], []

    for n in n_trees:
        gb = GradientBoostingRegressor(n_estimators=n, random_state=42).fit(X_train, y_train)
        gb_train_rmse.append(mean_squared_error(y_train, gb.predict(X_train))**0.5)
        gb_test_rmse.append(mean_squared_error(y_test,  gb.predict(X_test))**0.5)

        rf = RandomForestRegressor(n_estimators=n, random_state=42).fit(X_train, y_train)
        rf_train_rmse.append(mean_squared_error(y_train, rf.predict(X_train))**0.5)
        rf_test_rmse.append(mean_squared_error(y_test,  rf.predict(X_test))**0.5)

    axes[0].plot(n_trees, gb_test_rmse, "o-", lw=2, color="#4C72B0", label="GBM テスト")
    axes[0].plot(n_trees, rf_test_rmse, "s-", lw=2, color="#DD8452", label="RF テスト")
    axes[0].plot(n_trees, gb_train_rmse, "--", lw=1.5, color="#4C72B0", alpha=0.5, label="GBM 訓練")
    axes[0].plot(n_trees, rf_train_rmse, "--", lw=1.5, color="#DD8452", alpha=0.5, label="RF 訓練")
    axes[0].set_title("木の数 vs RMSE（GBM vs RF）")
    axes[0].set_xlabel("木の数"); axes[0].set_ylabel("RMSE"); axes[0].legend(fontsize=9)

    # Feature importance
    gb_final = GradientBoostingRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
    importances = gb_final.feature_importances_
    feat_names = [f"特徴量{i+1}" for i in range(10)]
    sorted_idx = np.argsort(importances)
    axes[1].barh(np.array(feat_names)[sorted_idx], importances[sorted_idx], color="#4C72B0", alpha=0.85)
    axes[1].set_title("特徴量重要度（GBM, 100木）")
    axes[1].set_xlabel("重要度スコア")

    plt.tight_layout()
    plt.savefig(f"{OUT}/gradient-boosting.png"); plt.close()
    print("✓ gradient-boosting.png")

# ──────────────────────────────────────────────────────────
# anomaly-detection.md
# ──────────────────────────────────────────────────────────
def chart_anomaly():
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(42)
    n_normal = 300
    X_normal = rng.multivariate_normal([0, 0], [[1, 0.5],[0.5, 1]], n_normal)
    X_anom   = rng.uniform(-4, 4, (20, 2))
    X = np.vstack([X_normal, X_anom])
    y_true = np.array([1]*n_normal + [-1]*20)

    iso = IsolationForest(contamination=0.06, random_state=42)
    y_pred = iso.fit_predict(X)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    colors = np.where(y_pred == -1, "#C44E52", "#4C72B0")
    axes[0].scatter(X[:, 0], X[:, 1], c=colors, s=20, alpha=0.7)
    normal_patch  = mpatches.Patch(color="#4C72B0", label="正常")
    anomaly_patch = mpatches.Patch(color="#C44E52", label="異常（検出）")
    axes[0].legend(handles=[normal_patch, anomaly_patch], fontsize=9)
    axes[0].set_title("Isolation Forest による異常検知")
    axes[0].set_xlabel("特徴量1"); axes[0].set_ylabel("特徴量2")

    # Anomaly score distribution
    scores = iso.score_samples(X)
    threshold = np.percentile(scores, 6)
    axes[1].hist(scores[y_true==1],  bins=30, color="#4C72B0", alpha=0.7, label="正常", density=True)
    axes[1].hist(scores[y_true==-1], bins=10, color="#C44E52", alpha=0.8, label="異常", density=True)
    axes[1].axvline(threshold, color="black", linestyle="--", lw=1.5, label=f"閾値={threshold:.2f}")
    axes[1].set_title("異常スコア分布")
    axes[1].set_xlabel("Anomaly Score"); axes[1].set_ylabel("密度")
    axes[1].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{OUT}/anomaly-detection.png"); plt.close()
    print("✓ anomaly-detection.png")

# ──────────────────────────────────────────────────────────
# multivariate-statistics.md  (correlation heatmap + PCA biplot)
# ──────────────────────────────────────────────────────────
def chart_multivariate():
    from sklearn.datasets import load_iris
    from sklearn.decomposition import PCA

    iris = load_iris()
    import pandas as pd
    df = pd.DataFrame(iris.data, columns=["がく片長", "がく片幅", "花弁長", "花弁幅"])

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # Correlation heatmap
    corr = df.corr()
    im = axes[0].imshow(corr.values, cmap="RdYlBu_r", vmin=-1, vmax=1)
    plt.colorbar(im, ax=axes[0])
    for i in range(4):
        for j in range(4):
            axes[0].text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center", fontsize=10)
    axes[0].set_xticks(range(4)); axes[0].set_yticks(range(4))
    axes[0].set_xticklabels(df.columns, rotation=30, ha="right")
    axes[0].set_yticklabels(df.columns)
    axes[0].set_title("相関行列ヒートマップ（Iris）")

    # PCA biplot
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(iris.data)
    colors_iris = ["#4C72B0", "#DD8452", "#55A868"]
    for cls in range(3):
        mask = iris.target == cls
        axes[1].scatter(X_pca[mask,0], X_pca[mask,1], color=colors_iris[cls],
                        s=20, alpha=0.7, label=iris.target_names[cls])
    # Loading vectors
    scale = 2.5
    for i, name in enumerate(df.columns):
        axes[1].annotate("", xy=(pca.components_[0,i]*scale, pca.components_[1,i]*scale),
                         xytext=(0, 0),
                         arrowprops=dict(arrowstyle="->", color="red", lw=1.5))
        axes[1].text(pca.components_[0,i]*scale*1.15, pca.components_[1,i]*scale*1.15,
                     name, color="red", fontsize=9)
    axes[1].set_title(f"PCA バイプロット\nPC1={pca.explained_variance_ratio_[0]*100:.0f}%、"
                      f"PC2={pca.explained_variance_ratio_[1]*100:.0f}%")
    axes[1].set_xlabel("PC1"); axes[1].set_ylabel("PC2")
    axes[1].legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(f"{OUT}/multivariate-statistics.png"); plt.close()
    print("✓ multivariate-statistics.png")


if __name__ == "__main__":
    chart_normal_distribution()
    chart_regression()
    chart_timeseries()
    chart_clustering()
    chart_deep_learning()
    chart_linear_regression()
    chart_dimensionality()
    chart_classification()
    chart_gradient_boosting()
    chart_anomaly()
    chart_multivariate()
    print("\n全チャート生成完了 →", OUT)
