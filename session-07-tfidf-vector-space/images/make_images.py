"""Regenerate every PNG for Session 7 (deterministic; run in course venv).

Usage (from session-07-tfidf-vector-space/):
    python images/make_images.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent


def cosine_angle() -> None:
    """07-01: cosine similarity as the angle between two vectors."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Cosine similarity: the angle between query and document")

    q = np.array([1.0, 0.3])
    d1 = np.array([0.9, 0.4])
    d2 = np.array([0.2, 0.9])

    for vec, label, color in [(q, "query", COLORS["warn"]),
                              (d1, "doc A (close)", COLORS["ok"]),
                              (d2, "doc B (far)", COLORS["neutral"])]:
        ax.annotate("", xy=vec, xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2))
        ax.text(vec[0] + 0.05, vec[1] + 0.05, label, color=color, fontsize=10)

    # angle arcs
    from matplotlib.patches import Arc
    ax.add_patch(Arc((0, 0), 0.6, 0.6, angle=0, theta1=0,
                     theta2=math.degrees(math.atan2(d1[1], d1[0])),
                     color=COLORS["ok"], lw=1.5))
    ax.add_patch(Arc((0, 0), 0.8, 0.8, angle=0, theta1=0,
                     theta2=math.degrees(math.atan2(d2[1], d2[0])),
                     color=COLORS["neutral"], lw=1.5))
    ax.text(0.35, 0.12, "θ small → cos ≈ 1", fontsize=8, color=COLORS["ok"])
    ax.text(0.55, 0.35, "θ large → cos ≈ 0", fontsize=8, color=COLORS["neutral"])

    fig.tight_layout()
    fig.savefig(HERE / "07-01-cosine-angle.png")
    plt.close(fig)


def idf_curve() -> None:
    """07-02: IDF as a function of document frequency."""
    apply_style()
    N = 204
    df = np.arange(1, N + 1)
    idf = np.log(1 + (N - df + 0.5) / (df + 0.5))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df, idf, color=COLORS["primary"], linewidth=2)
    ax.fill_between(df, idf, alpha=0.15, color=COLORS["primary"])
    ax.set_xlabel("document frequency (df)")
    ax.set_ylabel("IDF")
    ax.set_title("IDF: rare terms (low df) get high weight")
    ax.annotate("rare term\nhigh IDF", xy=(5, idf[4]), xytext=(30, 3.5),
                arrowprops=dict(arrowstyle="->", color=COLORS["warn"]),
                fontsize=9, color=COLORS["warn"])
    ax.annotate("common term\nlow IDF", xy=(180, idf[179]), xytext=(120, 1.0),
                arrowprops=dict(arrowstyle="->", color=COLORS["neutral"]),
                fontsize=9, color=COLORS["neutral"])
    fig.tight_layout()
    fig.savefig(HERE / "07-02-idf-curve.png")
    plt.close(fig)


def vector_space_scatter() -> None:
    """07-03: 2D vector space with query and documents."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    docs = np.array([[0.8, 0.6], [0.7, 0.5], [0.3, 0.9], [0.2, 0.8],
                     [0.9, 0.2], [0.1, 0.3], [0.5, 0.7], [0.4, 0.4]])
    labels = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"]
    query = np.array([0.75, 0.55])

    ax.scatter(docs[:, 0], docs[:, 1], c=COLORS["primary"], s=80, zorder=3)
    for i, label in enumerate(labels):
        ax.text(docs[i, 0] + 0.02, docs[i, 1] + 0.02, label, fontsize=8)
    ax.scatter(query[0], query[1], c=COLORS["warn"], s=120, marker="*",
               zorder=4, label="query")
    ax.set_xlabel("dimension 1")
    ax.set_ylabel("dimension 2")
    ax.set_title("Vector space: documents and query as points")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HERE / "07-03-vector-space-scatter.png")
    plt.close(fig)


def tf_weighting() -> None:
    """07-04: raw TF vs log TF vs BM25 TF."""
    apply_style()
    tf = np.linspace(0.1, 20, 200)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(tf, tf, label="raw TF", color=COLORS["neutral"], linewidth=2)
    ax.plot(tf, 1 + np.log(tf), label="log TF (1 + log tf)",
            color=COLORS["primary"], linewidth=2)
    k1 = 1.2
    ax.plot(tf, tf * (k1 + 1) / (tf + k1), label="BM25 TF",
            color=COLORS["warn"], linewidth=2)
    ax.set_xlabel("term frequency")
    ax.set_ylabel("weight")
    ax.set_title("TF weighting: raw vs log vs BM25 saturation")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HERE / "07-04-tf-weighting.png")
    plt.close(fig)


def main() -> None:
    cosine_angle()
    idf_curve()
    vector_space_scatter()
    tf_weighting()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()
