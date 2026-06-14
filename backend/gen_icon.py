"""
Generate app icons for Network Copilot web app.
Outputs: icon-512.png, icon-192.png, favicon-32.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle, FancyBboxPatch
import matplotlib.patheffects as pe

def draw_icon(size=512):
    dpi = 100
    fig_size = size / dpi
    fig, ax = plt.subplots(figsize=(fig_size, fig_size), dpi=dpi)
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")

    # ── 背景グラデーション（同心円で擬似表現） ──
    for r, alpha in zip(np.linspace(0.72, 0.05, 20), np.linspace(0.04, 0.0, 20)):
        circle = Circle((0.5, 0.5), r, color="#6366f1", alpha=alpha, zorder=0)
        ax.add_patch(circle)

    # ── ノード定義（中心 + 外周6個 + 中間3個） ──
    # 中心
    center = np.array([0.5, 0.5])

    # 外周ノード（六角形配置）
    angles_outer = np.linspace(0, 2 * np.pi, 7)[:-1] + np.pi / 6
    r_outer = 0.30
    outer = np.column_stack([
        0.5 + r_outer * np.cos(angles_outer),
        0.5 + r_outer * np.sin(angles_outer)
    ])

    # 中間ノード（3個）
    angles_mid = np.array([np.pi/2 + np.pi/3, np.pi/2 + np.pi, np.pi/2 + 5*np.pi/3])
    r_mid = 0.155
    mid = np.column_stack([
        0.5 + r_mid * np.cos(angles_mid),
        0.5 + r_mid * np.sin(angles_mid)
    ])

    # ── エッジ（線）──
    edge_style = dict(color="#818cf8", alpha=0.45, linewidth=size/256, zorder=1)
    # 中心 → 外周
    for node in outer:
        ax.plot([center[0], node[0]], [center[1], node[1]], **edge_style)
    # 中心 → 中間
    for node in mid:
        ax.plot([center[0], node[0]], [center[1], node[1]],
                color="#38bdf8", alpha=0.5, linewidth=size/300, zorder=1)
    # 外周 同士（隣接）
    for i in range(len(outer)):
        j = (i + 1) % len(outer)
        ax.plot([outer[i][0], outer[j][0]], [outer[i][1], outer[j][1]],
                color="#818cf8", alpha=0.25, linewidth=size/400, zorder=1)
    # 中間 → 外周（近いもの）
    for m in mid:
        dists = np.linalg.norm(outer - m, axis=1)
        nearest = np.argsort(dists)[:2]
        for ni in nearest:
            ax.plot([m[0], outer[ni][0]], [m[1], outer[ni][1]],
                    color="#38bdf8", alpha=0.3, linewidth=size/400, zorder=1)

    # ── ノード描画 ──
    r_c  = 0.095   # 中心ノード半径
    r_o  = 0.038   # 外周ノード
    r_m  = 0.028   # 中間ノード

    # 外周ノード（インディゴ）
    outer_colors = ["#818cf8","#a5b4fc","#818cf8","#c7d2fe","#818cf8","#a5b4fc"]
    for node, col in zip(outer, outer_colors):
        # グロー
        glow = Circle(node, r_o * 1.9, color=col, alpha=0.12, zorder=2)
        ax.add_patch(glow)
        dot = Circle(node, r_o, color=col, zorder=3)
        ax.add_patch(dot)
        inner = Circle(node, r_o * 0.5, color="white", alpha=0.6, zorder=4)
        ax.add_patch(inner)

    # 中間ノード（シアン）
    for node in mid:
        glow = Circle(node, r_m * 2.2, color="#38bdf8", alpha=0.15, zorder=2)
        ax.add_patch(glow)
        dot = Circle(node, r_m, color="#38bdf8", zorder=3)
        ax.add_patch(dot)

    # 中心ノード（グラデーション風：外→内の同心円）
    for r, col, al in [
        (r_c * 1.8, "#6366f1", 0.15),
        (r_c * 1.3, "#6366f1", 0.25),
        (r_c,       "#6366f1", 1.0),
        (r_c * 0.7, "#818cf8", 1.0),
        (r_c * 0.4, "#c7d2fe", 1.0),
    ]:
        ax.add_patch(Circle(center, r, color=col, alpha=al, zorder=5))

    # 中心に "N" テキスト
    fs = size * 0.14
    ax.text(0.5, 0.5, "N",
            ha="center", va="center",
            fontsize=fs, fontweight="bold",
            color="white", zorder=6,
            fontfamily="DejaVu Sans",
            path_effects=[pe.withStroke(linewidth=size/160, foreground="#4338ca")])

    plt.tight_layout(pad=0)
    return fig

# 512×512
fig = draw_icon(512)
fig.savefig("frontend/public/icon-512.png", dpi=100, bbox_inches="tight",
            facecolor="#0f172a", pad_inches=0)
plt.close()
print("✓ icon-512.png")

# 192×192
fig = draw_icon(192)
fig.savefig("frontend/public/icon-192.png", dpi=100, bbox_inches="tight",
            facecolor="#0f172a", pad_inches=0)
plt.close()
print("✓ icon-192.png")

# 32×32 favicon
fig = draw_icon(32)
fig.savefig("frontend/public/favicon-32.png", dpi=100, bbox_inches="tight",
            facecolor="#0f172a", pad_inches=0)
plt.close()
print("✓ favicon-32.png")

print("Done.")
