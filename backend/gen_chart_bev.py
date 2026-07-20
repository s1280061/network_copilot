"""
Generate an illustration of the BEV (Bird's Eye View) perspective transform.
Output: frontend/public/images/charts/bev-transform.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

OUT_DIR = "/home/user/network_copilot/frontend/public/images/charts"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 140, "font.size": 11,
    "font.family": "IPAGothic", "axes.unicode_minus": False,
})

BLUE = "#4C72B0"
ORANGE = "#DD8452"
GREEN = "#55A868"
RED = "#C44E52"


def draw():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # --- left: camera (perspective) view ---
    ax1.set_title("① カメラ画像（透視投影）", fontsize=12)
    ax1.set_xlim(0, 10); ax1.set_ylim(0, 10)
    ax1.set_aspect("equal")
    # road as a trapezoid (near = wide bottom, far = narrow top)
    road = np.array([[2, 0], [8, 0], [6, 8], [4, 8]])
    ax1.add_patch(plt.Polygon(road, closed=True, facecolor="#cccccc", edgecolor="k"))
    # lane lines converging (perspective)
    ax1.plot([3.0, 4.7], [0, 8], color="white", lw=2)
    ax1.plot([7.0, 5.3], [0, 8], color="white", lw=2)
    ax1.plot([5.0, 5.0], [0, 8], color="yellow", lw=2, ls="--")
    # 4 source points
    src = np.array([[3.0, 1.0], [7.0, 1.0], [5.65, 7.0], [4.35, 7.0]])
    ax1.scatter(src[:, 0], src[:, 1], color=RED, zorder=5, s=60)
    for i, (px, py) in enumerate(src):
        ax1.annotate(f"P{i+1}", (px, py), textcoords="offset points",
                     xytext=(6, 6), color=RED, fontweight="bold")
    ax1.text(5, 9.2, "遠くほど狭く歪む\n（平行線が交わる）", ha="center", fontsize=10)
    ax1.set_xlabel("u [px]"); ax1.set_ylabel("v [px]")

    # --- right: BEV (top-down) view ---
    ax2.set_title("② BEV（俯瞰変換後）", fontsize=12)
    ax2.set_xlim(0, 10); ax2.set_ylim(0, 10)
    ax2.set_aspect("equal")
    # road as a rectangle (parallel lanes)
    rect = np.array([[3, 0], [7, 0], [7, 9], [3, 9]])
    ax2.add_patch(plt.Polygon(rect, closed=True, facecolor="#cccccc", edgecolor="k"))
    ax2.plot([4, 4], [0, 9], color="white", lw=2)
    ax2.plot([6, 6], [0, 9], color="white", lw=2)
    ax2.plot([5, 5], [0, 9], color="yellow", lw=2, ls="--")
    dst = np.array([[4, 1], [6, 1], [6, 8], [4, 8]])
    ax2.scatter(dst[:, 0], dst[:, 1], color=RED, zorder=5, s=60)
    for i, (px, py) in enumerate(dst):
        ax2.annotate(f"P{i+1}'", (px, py), textcoords="offset points",
                     xytext=(6, 6), color=RED, fontweight="bold")
    ax2.text(5, 9.5, "平行線は平行のまま\n（真上から見た地図）", ha="center", fontsize=10)
    ax2.set_xlabel("X [m]"); ax2.set_ylabel("Y [m]")

    # arrow between panels
    fig.text(0.5, 0.5, "→\nH", ha="center", va="center", fontsize=22,
             color=BLUE, fontweight="bold")

    fig.suptitle("透視変換（ホモグラフィ H）による BEV 変換", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(f"{OUT_DIR}/bev-transform.png", bbox_inches="tight")
    plt.close(fig)


draw()
print("done: bev-transform.png")
