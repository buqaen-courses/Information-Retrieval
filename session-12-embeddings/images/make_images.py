"""Regenerate every PNG for Session 12 (deterministic; run in course venv).

Usage (from session-12-embeddings/):
    python images/make_images.py

Sentence embeddings are deterministic once the model is fixed, so the PCA
scatter and the similarity heatmap are byte-identical between runs. No timing
is plotted here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "session-12-embeddings" / "workshop" / "solution"))
from tools.figstyle import COLORS, apply_style  # noqa: E402

from numpy_semantic_search import (embed, load_model, product_sentence,  # noqa: E402
                                   WARMUP)

HERE = Path(__file__).resolve().parent
CORPUS = ROOT / "datasets" / "corpus"

SENTENCES = [
    "soccer boots", "football cleats", "running shoes",
    "a sturdy desk lamp", "a cheap table lamp",
    "a stainless kettle", "an espresso machine",
    "a waterproof jacket", "a canvas backpack",
    "wireless headphones",
]
TOPIC = {
    "footwear": "#1f77b4", "lighting": "#ff7f0e", "kitchen": "#2ca02c",
    "outdoor": "#9467bd", "electronics": "#d62728",
}


def topic_of(sentence: str) -> str:
    """Rough topic label for colouring (only used by this figure)."""
    s = sentence.lower()
    if any(w in s for w in ("boot", "cleat", "shoe")):
        return "footwear"
    if any(w in s for w in ("lamp", "light")):
        return "lighting"
    if any(w in s for w in ("kettle", "espresso", "coffee", "tea")):
        return "kitchen"
    if any(w in s for w in ("jacket", "backpack", "waterproof", "canvas")):
        return "outdoor"
    return "electronics"


def pca_scatter() -> None:
    """12-01: 2D PCA of the 384-d embeddings, coloured by topic."""
    apply_style()
    model = load_model()
    vectors = embed(model, SENTENCES)

    # centre, then project onto the top 2 principal directions
    centred = vectors - vectors.mean(axis=0)
    _u, _s, vt = np.linalg.svd(centred, full_matrices=False)
    proj = centred @ vt[:2].T
    explained = (_s[:2] ** 2 / np.sum(_s ** 2)) * 100

    fig, ax = plt.subplots(figsize=(8, 5.2))
    for i, sentence in enumerate(SENTENCES):
        topic = topic_of(sentence)
        ax.scatter(proj[i, 0], proj[i, 1], s=140, color=TOPIC[topic],
                   edgecolor="black", linewidth=0.6, zorder=3)
        ax.annotate(sentence, (proj[i, 0], proj[i, 1]),
                    textcoords="offset points", xytext=(8, 6), fontsize=8.5)
    ax.set_xlabel(f"PC1 ({explained[0]:.0f}% of variance)")
    ax.set_ylabel(f"PC2 ({explained[1]:.0f}% of variance)")
    ax.set_title("384-d embeddings, squashed to 2-d by PCA\n"
                 "sentences about the same thing end up near each other")
    ax.axhline(0, color="#cccccc", linewidth=0.8, zorder=1)
    ax.axvline(0, color="#cccccc", linewidth=0.8, zorder=1)
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=c, markersize=9,
                          label=t) for t, c in TOPIC.items()]
    ax.legend(handles=handles, fontsize=8.5, loc="best", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(HERE / "12-01-pca-scatter.png")
    plt.close(fig)
    print(f"12-01 measured: PC1={explained[0]:.1f}% PC2={explained[1]:.1f}% "
          f"of variance")


def similarity_heatmap() -> None:
    """12-02: cosine similarity between every pair of 10 sentences."""
    apply_style()
    model = load_model()
    vectors = embed(model, SENTENCES)
    sim = vectors @ vectors.T          # already normalized -> cosine

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(sim, cmap="magma", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(SENTENCES)))
    ax.set_xticklabels(SENTENCES, rotation=90, fontsize=7.5)
    ax.set_yticks(range(len(SENTENCES)))
    ax.set_yticklabels(SENTENCES, fontsize=7.5)
    ax.set_title("Cosine similarity between every pair of sentences")
    for i in range(len(SENTENCES)):
        for j in range(len(SENTENCES)):
            ax.text(j, i, f"{sim[i, j]:.2f}", ha="center", va="center",
                    fontsize=6.5,
                    color="white" if sim[i, j] < 0.6 else "black")
    fig.colorbar(im, ax=ax, label="cosine similarity")
    fig.tight_layout()
    fig.savefig(HERE / "12-02-similarity-heatmap.png")
    plt.close(fig)
    print(f"12-02 measured: diagonal={sim[0, 0]:.4f}, "
          f"soccer/football={sim[0, 1]:.4f}, "
          f"soccer/headphones={sim[0, 9]:.4f}")


def lexical_vs_semantic() -> None:
    """12-03: the query BM25 cannot answer, answered by meaning.

    Measured on the real corpus: how many documents contain each word.
    """
    apply_style()
    import os

    docs: dict[str, list[str]] = {}
    for name in sorted(os.listdir(CORPUS)):
        if not name.endswith(".txt"):
            continue
        with open(CORPUS / name, mode="r", encoding="utf-8") as f:
            docs[name[:-4]] = f.read().lower().split()

    probes = ["soccer", "football", "cleats", "boots", "headphones", "lamp"]
    lexical = [sum(1 for t in doc if w in t) for w in probes for doc in docs.values()]
    counts = []
    for w in probes:
        n = sum(1 for doc in docs.values() if w in doc)
        counts.append(n)

    x = np.arange(len(probes))
    fig, ax = plt.subplots(figsize=(8, 4.6))
    bars = ax.bar(x, counts, color=[COLORS["warn"] if c == 0 else COLORS["ok"]
                                    for c in counts], width=0.55)
    ax.set_xticks(x)
    ax.set_xticklabels(probes, fontsize=9)
    ax.set_ylabel("corpus documents containing the word")
    ax.set_title("Exact-word matching on datasets/corpus: the word people type "
                 "is often absent")
    for rect, c in zip(bars, counts):
        ax.text(rect.get_x() + rect.get_width() / 2, c + 0.8, str(c), ha="center",
                fontsize=10, weight="bold")
    ax.set_ylim(0, max(counts) + 6)
    ax.annotate("a shopper types this;\nno document contains it",
                xy=(0, 0), xytext=(0.6, 12),
                arrowprops=dict(arrowstyle="->", color=COLORS["warn"]),
                fontsize=9, color=COLORS["warn"])
    fig.tight_layout()
    fig.savefig(HERE / "12-03-lexical-gap.png")
    plt.close(fig)
    print(f"12-03 measured: doc counts per word = "
          f"{dict(zip(probes, counts))}")


def ann_problem() -> None:
    """12-04: why brute force stops working — 128 x 128 grows quadratically."""
    apply_style()
    sizes = [100, 1000, 10_000, 100_000, 1_000_000, 10_000_000]
    comparisons = [n * 128 for n in sizes]

    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(range(len(sizes)), comparisons, "o-", color=COLORS["warn"],
            linewidth=2)
    ax.set_xticks(range(len(sizes)))
    ax.set_xticklabels([f"{n:,}" for n in sizes], fontsize=8.5)
    ax.set_yscale("log")
    ax.set_xlabel("documents in the index")
    ax.set_ylabel("dot products for one query (log scale)")
    ax.set_title("Brute-force search grows linearly with the corpus\n"
                 "this is the problem vector databases exist to solve")
    ax.annotate("128 docs: 16k dot products — instant\n"
                "10M docs: 1.28 billion — far too slow",
                xy=(4, comparisons[4]), xytext=(1.2, comparisons[2] / 3),
                arrowprops=dict(arrowstyle="->", color=COLORS["neutral"]),
                fontsize=9, color="#333333",
                bbox=dict(boxstyle="round,pad=0.35", fc="#f4f4f4", ec="#cccccc"))
    fig.tight_layout()
    fig.savefig(HERE / "12-04-ann-problem.png")
    plt.close(fig)
    print(f"12-04 measured: dot products for 128-dim search = "
          f"{comparisons}")


def main() -> None:
    pca_scatter()
    similarity_heatmap()
    lexical_vs_semantic()
    ann_problem()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()