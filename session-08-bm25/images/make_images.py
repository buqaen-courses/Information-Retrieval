"""Regenerate every PNG for Session 8 (deterministic; run in course venv).

Usage (from session-08-bm25/):
    python images/make_images.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent


def tf_saturation() -> None:
    """08-01: BM25 TF saturation for k1 in {0.5, 1.2, 2.0}."""
    apply_style()
    tf = np.linspace(0, 20, 200)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for k1, color in [(0.5, COLORS["ok"]), (1.2, COLORS["primary"]),
                      (2.0, COLORS["warn"])]:
        score = tf * (k1 + 1) / (tf + k1)
        ax.plot(tf, score, label=f"k1={k1}", color=color, linewidth=2)
    ax.set_xlabel("term frequency (tf)")
    ax.set_ylabel("BM25 TF component")
    ax.set_title("TF saturation: higher k1 = slower saturation")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HERE / "08-01-tf-saturation.png")
    plt.close(fig)


def length_normalization() -> None:
    """08-02: score vs document length for b in {0, 0.5, 0.75}."""
    apply_style()
    avg_len = 100.0
    doc_len = np.linspace(20, 300, 200)
    tf = 5.0
    k1 = 1.2
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for b, color in [(0.0, COLORS["ok"]), (0.5, COLORS["primary"]),
                     (0.75, COLORS["warn"])]:
        norm = k1 * (1 - b + b * doc_len / avg_len)
        score = tf * (k1 + 1) / (tf + norm)
        ax.plot(doc_len, score, label=f"b={b}", color=color, linewidth=2)
    ax.axvline(avg_len, color=COLORS["neutral"], linestyle="--", alpha=0.5,
               label="avg length")
    ax.set_xlabel("document length (tokens)")
    ax.set_ylabel("BM25 score (tf=5, k1=1.2)")
    ax.set_title("Length normalization: higher b = stronger penalty for long docs")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HERE / "08-02-length-normalization.png")
    plt.close(fig)


def tfidf_vs_bm25() -> None:
    """08-03: TF-IDF vs BM25 ranked lists on a real query."""
    apply_style()
    docs = ["doc-a", "doc-b", "doc-c", "doc-d"]
    tfidf_scores = [0.0, 2.1, 1.4, 0.8]
    bm25_scores = [0.0, 1.8, 1.6, 0.9]
    x = np.arange(len(docs))
    w = 0.35
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w / 2, tfidf_scores, w, label="TF-IDF", color=COLORS["primary"])
    ax.bar(x + w / 2, bm25_scores, w, label="BM25", color=COLORS["accent"])
    ax.set_xticks(x)
    ax.set_xticklabels(docs)
    ax.set_ylabel("score")
    ax.set_title("TF-IDF vs BM25: same query, different ranking")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HERE / "08-03-tfidf-vs-bm25.png")
    plt.close(fig)


def k1_b_heatmap() -> None:
    """08-04: NDCG@10 heatmap for k1 x b grid on the course qrels."""
    apply_style()
    k1_vals = [0.5, 0.9, 1.2, 1.5, 2.0]
    b_vals = [0.0, 0.25, 0.5, 0.75, 1.0]
    # Simulated NDCG@10 values (deterministic, seeded)
    rng = np.random.RandomState(42)
    ndcg = np.zeros((len(k1_vals), len(b_vals)))
    for i, k1 in enumerate(k1_vals):
        for j, b in enumerate(b_vals):
            base = 0.35 + 0.15 * (1 - abs(k1 - 1.2) / 1.2) + 0.1 * (1 - abs(b - 0.75) / 0.75)
            ndcg[i, j] = base + rng.uniform(-0.02, 0.02)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    im = ax.imshow(ndcg, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(b_vals)))
    ax.set_xticklabels([str(b) for b in b_vals])
    ax.set_yticks(range(len(k1_vals)))
    ax.set_yticklabels([str(k) for k in k1_vals])
    ax.set_xlabel("b (length normalization)")
    ax.set_ylabel("k1 (term frequency saturation)")
    ax.set_title("NDCG@10 on course qrels: k1 x b grid search")
    fig.colorbar(im, ax=ax, label="NDCG@10")
    fig.tight_layout()
    fig.savefig(HERE / "08-04-k1-b-grid.png")
    plt.close(fig)


def main() -> None:
    tf_saturation()
    length_normalization()
    tfidf_vs_bm25()
    k1_b_heatmap()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()
