"""Regenerate every PNG for Session 13 (deterministic; run in course venv).

Usage (from session-13-vector-databases/):
    python images/make_images.py

Only schematic diagrams and deterministic measurements are drawn. No timing is
plotted, because wall-clock would make the figures non-reproducible (see
images/measure.py if you want live numbers).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent
PRODUCTS_JSON = ROOT / "datasets" / "fallback_products.json"


def _box(ax, x, y, w, h, text, color=COLORS["primary"], face=None, fs=9):
    """A labelled box: white text on a colour, dark text on a pale fill."""
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
                           facecolor=face if face else color, edgecolor="black",
                           linewidth=1.2, zorder=2)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", zorder=3,
            color="#111111" if face else "white", fontsize=fs, weight="bold")


def _arrow(ax, start, end, color="black", style="-", label=None, rad=0.0):
    """Arrow between two points, optionally curved and labelled."""
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                                 color=color, linewidth=1.4, linestyle=style,
                                 shrinkA=0, shrinkB=0, zorder=4,
                                 connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.12, label,
                ha="center", fontsize=7.5, color=color, zorder=5,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none",
                          alpha=0.85))


def hnsw_layers() -> None:
    """13-01: HNSW — a graph of vectors, searched from the top layer down."""
    apply_style()
    rng = np.random.RandomState(7)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    ax.set_title("HNSW: a graph where neighbours in meaning are connected")

    layers = [("layer 2 (coarse, few long hops)", 3.6, 3, 0.55),
              ("layer 1", 2.5, 6, 0.42),
              ("layer 0 (all vectors)", 1.35, 10, 0.34)]
    colours = [COLORS["warn"], COLORS["accent"], COLORS["primary"]]
    for (label, y, n, size), colour in zip(layers, colours):
        pts = np.column_stack([np.linspace(0.9, 9.1, n),
                               np.full(n, y) + rng.uniform(-0.16, 0.16, n)])
        ax.text(0.15, y + 0.42, label, fontsize=8.5, style="italic", color="#444444")
        ax.scatter(pts[:, 0], pts[:, 1], s=size * 260, color=colour,
                   edgecolor="black", linewidth=0.7, zorder=3)
        if n > 1:
            for a in range(n - 1):
                if rng.rand() < 0.6:
                    ax.plot(pts[a:a + 2, 0], pts[a:a + 2, 1], color="#888888",
                            linewidth=0.8, zorder=1)
    # the descent path from the top layer to a query
    qx = 7.9
    ax.scatter(qx, 0.55, marker="*", s=320, color=COLORS["ok"], zorder=5)
    ax.text(qx + 0.18, 0.55, "query", fontsize=9, weight="bold", color=COLORS["ok"])
    ax.add_patch(FancyArrowPatch((qx, 0.62), (7.6, 3.3), arrowstyle="-|>",
                                 mutation_scale=13, color=COLORS["ok"],
                                 linewidth=1.8, linestyle="--",
                                 connectionstyle="arc3,rad=0.25", zorder=4))
    ax.text(8.35, 2.05, "walk down the graph,\nthen back up the best path",
            fontsize=8.5, color=COLORS["ok"], ha="center")
    fig.tight_layout()
    fig.savefig(HERE / "13-01-hnsw-layers.png")
    plt.close(fig)


def ivf_clusters() -> None:
    """13-02: IVF — partition first, then search only the nearest clusters."""
    apply_style()
    rng = np.random.RandomState(11)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("IVF: cluster the space, then look inside the nearest clusters")

    centres = np.array([[0.30, 0.62], [0.68, 0.72], [0.26, 0.26], [0.72, 0.24]])
    colours = [COLORS["primary"], COLORS["accent"], COLORS["ok"], COLORS["warn"]]
    for k, (c, colour) in enumerate(zip(centres, colours)):
        pts = c + rng.normal(0, 0.055, size=(26, 2))
        ax.scatter(pts[:, 0], pts[:, 1], s=34, color=colour, alpha=0.85,
                   edgecolor="none", zorder=2)
        ax.scatter(c[0], c[1], marker="X", s=260, color=colour, zorder=4,
                   edgecolor="black", linewidth=0.8)
        ax.text(c[0], c[1] + 0.14, f"C{k}", ha="center", fontsize=10,
                weight="bold", color=colour)

    q = np.array([0.66, 0.70])
    ax.scatter(q[0], q[1], marker="*", s=380, color="black", zorder=5)
    ax.text(q[0] + 0.02, q[1] + 0.05, "query", fontsize=9.5, weight="bold")
    ax.add_patch(FancyArrowPatch(q, centres[1], arrowstyle="-|>",
                                 mutation_scale=14, color="black",
                                 linewidth=1.8, linestyle="--",
                                 connectionstyle="arc3,rad=0.2", zorder=5))
    ax.text(0.50, 0.90,
            "the query lands in one cluster — the other three are never read",
            ha="center", fontsize=9.5, weight="bold")
    fig.tight_layout()
    fig.savefig(HERE / "13-02-ivf-clusters.png")
    plt.close(fig)


def pq_segments() -> None:
    """13-03: PQ — compress a vector into a short list of shared sub-vectors."""
    apply_style()
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3.4)
    ax.axis("off")
    ax.set_title("Product quantization: a 384-float vector becomes 16 small codes")

    ax.text(0.15, 3.05, "a 384-float vector, split into 16 blocks of 24",
            fontsize=9.5, weight="bold")
    rng = np.random.RandomState(3)
    cmap = plt.get_cmap("viridis")
    for i in range(16):
        x = 0.35 + i * 0.73
        vals = rng.uniform(0.1, 0.9, 24)
        for j in range(24):
            ax.add_patch(plt.Rectangle((x, 1.95 + j * 0.5 / 24), 0.62,
                                       0.5 / 24,
                                       facecolor=cmap(float(vals[j])),
                                       edgecolor="none"))
        ax.add_patch(FancyBboxPatch((x + 0.04, 1.6), 0.54, 0.3,
                                    boxstyle="round,pad=0.02",
                                    facecolor=COLORS["accent"],
                                    edgecolor="black", linewidth=0.8, zorder=4))
        ax.text(x + 0.31, 1.75, f"code {rng.randint(0, 255)}", ha="center",
                va="center", fontsize=6.5, color="white", zorder=5, weight="bold")

    ax.add_patch(FancyArrowPatch((6.0, 1.45), (6.0, 0.95), arrowstyle="-|>",
                                 mutation_scale=13, color="black", linewidth=1.6))
    ax.text(6.15, 1.2, "look each block up in a shared codebook",
            fontsize=9, ha="left")
    _box(ax, 4.6, 0.15, 2.9, 0.6, "384 floats  →  16 bytes", COLORS["ok"], fs=11)
    fig.tight_layout()
    fig.savefig(HERE / "13-03-pq-segments.png")
    plt.close(fig)


def architecture_comparison() -> None:
    """13-04: server vs embedded — what actually differs."""
    apply_style()
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    ax.set_title("Milvus (server) vs LanceDB (embedded): same queries, different shape")

    # Milvus row
    ax.text(0.12, 4.0, "Milvus — server", fontsize=10.5, weight="bold",
            color=COLORS["primary"])
    y = 3.05
    _box(ax, 0.3, y, 1.9, 0.6, "your app", COLORS["neutral"])
    _box(ax, 3.0, y, 2.0, 0.6, "gRPC / REST", COLORS["primary"])
    _box(ax, 5.8, y, 2.2, 0.6, "Milvus server", COLORS["primary"])
    _box(ax, 8.8, y, 2.9, 0.6, "storage + indexes", face="#e9e9e9", fs=8.5)
    _arrow(ax, (2.2, y + 0.3), (3.0, y + 0.3))
    _arrow(ax, (5.0, y + 0.3), (5.8, y + 0.3))
    _arrow(ax, (8.0, y + 0.3), (8.8, y + 0.3), label="scales to billions")
    ax.text(0.3, y - 0.32, "one process holds vectors in RAM; the client sends vectors over the network",
            fontsize=8.2, style="italic", color="#444444")

    # Lance row
    ax.text(0.12, 2.0, "LanceDB — embedded", fontsize=10.5, weight="bold",
            color=COLORS["accent"])
    y = 1.05
    _box(ax, 0.3, y, 1.9, 0.6, "your app", COLORS["neutral"])
    _box(ax, 3.0, y, 2.0, 0.6, "Python API", COLORS["accent"])
    _box(ax, 5.8, y, 2.2, 0.6, "your process", COLORS["accent"])
    _box(ax, 8.8, y, 2.9, 0.6, "Lance files on disk", face="#e9e9e9", fs=8.5)
    _arrow(ax, (2.2, y + 0.3), (3.0, y + 0.3))
    _arrow(ax, (5.0, y + 0.3), (5.8, y + 0.3))
    _arrow(ax, (8.0, y + 0.3), (8.8, y + 0.3), label="files on your disk")
    ax.text(0.3, y - 0.32, "no server, no network; vectors live in columnar files you can copy",
            fontsize=8.2, style="italic", color="#444444")

    ax.text(6.0, 0.25,
            "This session uses the EMBEDDED form of both: Milvus Lite is a local file "
            "with the server's API,\nand LanceDB is columnar storage with a Python API. "
            "Both answer the same query with no Docker and no network.",
            ha="center", fontsize=9, style="italic", color="#333333")
    fig.tight_layout()
    fig.savefig(HERE / "13-04-architecture-comparison.png")
    plt.close(fig)


def not_btrees() -> None:
    """13-05: why ANN needs different structures than a B-tree."""
    apply_style()
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(11, 4.2))
    fig.subplots_adjust(left=0.05, right=0.98, top=0.82, bottom=0.16, wspace=0.18)
    axl.axis("off")
    axr.axis("off")
    axl.set_xlim(0, 10)
    axl.set_ylim(0, 4)
    axr.set_xlim(0, 10)
    axr.set_ylim(0, 4)

    axl.set_title("What a B-tree gives you: order", fontsize=11.5, color=COLORS["primary"])
    axl.text(5, 3.6, "keys stay sorted, so a RANGE is cheap:\n"
                      "\"everything between 50 and 80\" is a short walk",
             ha="center", fontsize=9.2, color="#333333")
    keys = [3, 7, 12, 18, 23, 31, 38, 44]
    for i, k in enumerate(keys):
        x = 0.5 + i * 1.15
        axl.add_patch(plt.Rectangle((x, 1.9), 0.9, 0.5,
                                    facecolor="#dbe9f7", edgecolor=COLORS["primary"]))
        axl.text(x + 0.45, 2.15, str(k), ha="center", fontsize=9)
    axl.add_patch(plt.Rectangle((0.5 + 3 * 1.15, 1.9), 0.9, 0.5,
                                facecolor="#ffe0e0", edgecolor=COLORS["warn"],
                                linewidth=2))
    axl.add_patch(plt.Rectangle((0.5 + 4 * 1.15, 1.9), 0.9, 0.5,
                                facecolor="#ffe0e0", edgecolor=COLORS["warn"],
                                linewidth=2))
    axl.text(5, 1.2, "one contiguous run = one range query",
             ha="center", fontsize=8.8, style="italic", color="#444444")
    axl.text(5, 0.55, "vectors have no such order:\n\"nearest\" is not a range",
             ha="center", fontsize=9.5, weight="bold", color=COLORS["warn"])

    axr.set_title("What ANN needs: proximity", fontsize=11.5, color=COLORS["accent"])
    rng = np.random.RandomState(5)
    pts = rng.uniform(0.6, 9.4, size=(70, 2))
    axr.scatter(pts[:, 0], pts[:, 1], s=26, color="#c9d6e2", edgecolor="none")
    q = np.array([4.2, 2.6])
    d = np.linalg.norm(pts - q, axis=1)
    near = pts[d <= np.percentile(d, 18)]
    far = pts[d > np.percentile(d, 18)]
    axr.scatter(far[:, 0], far[:, 1], s=26, color="#c9d6e2", edgecolor="none")
    axr.scatter(near[:, 0], near[:, 1], s=52, color=COLORS["accent"],
                edgecolor="black", linewidth=0.4)
    axr.scatter(q[0], q[1], marker="*", s=380, color=COLORS["ok"], zorder=5)
    axr.add_patch(plt.Circle(q, 2.1, fill=False, edgecolor=COLORS["ok"],
                             linestyle="--", linewidth=1.6))
    axr.text(q[0] + 0.25, q[1] + 1.9, "only the points\ninside get compared",
             fontsize=8.6, color=COLORS["ok"])
    axr.text(5, 0.55, "the answer is a SHAPE, not a range:\nHNSW and IVF exist for this",
             ha="center", fontsize=9.5, weight="bold", color=COLORS["accent"])

    fig.suptitle("ANN ≠ ordered keys — a B-tree cannot answer \"what is near this vector\"",
                 fontsize=12, weight="bold", y=0.98)
    fig.tight_layout()
    fig.savefig(HERE / "13-05-not-btrees.png")
    plt.close(fig)


def on_disk_sizes() -> None:
    """13-06: the two stores, measured on the real 128-product catalogue."""
    apply_style()
    products = json.loads(PRODUCTS_JSON.read_text(encoding="utf-8"))
    n = len(products)
    raw = n * 384 * 4                      # float32 per component
    f16 = n * 384 * 2
    pq = n * 16                             # 16 PQ codes, 1 byte each

    fig, ax = plt.subplots(figsize=(8, 4.6))
    labels = ["float32\n(as embedded)", "float16\n(half precision)", "PQ, 16 codes\n(compressed)"]
    values = [raw, f16, pq]
    bars = ax.bar(labels, values, color=[COLORS["primary"], COLORS["accent"],
                                         COLORS["ok"]], width=0.5)
    ax.set_ylabel("bytes")
    ax.set_title(f"Storing {n} products x 384 dimensions (measured arithmetic, "
                 "not a guess)")
    ax.set_yscale("log")
    for rect, v in zip(bars, values):
        ax.text(rect.get_x() + rect.get_width() / 2, v * 1.25, f"{v:,}",
                ha="center", fontsize=10, weight="bold")
    ax.set_ylim(100, raw * 4)
    ax.annotate(f"PQ shrinks storage {raw / pq:.0f}x —\nand accepts a little recall loss",
                xy=(2, pq), xytext=(0.7, raw * 0.25),
                arrowprops=dict(arrowstyle="->", color=COLORS["warn"]),
                fontsize=9, color=COLORS["warn"])
    fig.tight_layout()
    fig.savefig(HERE / "13-06-storage-sizes.png")
    plt.close(fig)
    print(f"13-06 measured: n={n} float32={raw:,} float16={f16:,} pq16={pq:,}")


def main() -> None:
    hnsw_layers()
    ivf_clusters()
    pq_segments()
    architecture_comparison()
    not_btrees()
    on_disk_sizes()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()