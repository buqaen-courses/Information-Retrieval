"""Regenerate every PNG for Session 10 (deterministic; run in course venv).

Usage (from session-10-evaluation/):
    python images/make_images.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "session-10-evaluation" / "workshop" / "solution"))
from metrics import (JUDGED, RANKED, RELEVANT, average_precision,  # noqa: E402
                     ndcg_at_k, precision_at_k, reciprocal_rank)

QRELS = ROOT / "datasets" / "qrels.json"


def pr_grid() -> None:
    """10-01: precision vs recall at increasing k on the worked example."""
    apply_style()
    ks = list(range(1, 11))
    prec = [precision_at_k(RANKED, RELEVANT, k) for k in ks]
    rec = [sum(1 for d in RANKED[:k] if d in set(RELEVANT)) / len(RELEVANT)
           for k in ks]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(ks, prec, "o-", label="precision@k", color=COLORS["primary"])
    ax.plot(ks, rec, "s-", label="recall@k", color=COLORS["accent"])
    ax.set_xlabel("k (results shown)")
    ax.set_ylabel("score")
    ax.set_title("Precision and recall trade off as k grows")
    ax.set_xticks(ks)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.annotate("k=2: precision 0.0\n(the top 2 are both wrong)",
                xy=(2, 0.0), xytext=(3.2, 0.42),
                arrowprops=dict(arrowstyle="->", color=COLORS["warn"]),
                fontsize=8.5, color=COLORS["warn"])
    ax.annotate("k=10: recall 1.0\n(all relevant found)",
                xy=(10, 1.0), xytext=(6.4, 0.78),
                arrowprops=dict(arrowstyle="->", color=COLORS["ok"]),
                fontsize=8.5, color=COLORS["ok"])
    fig.tight_layout()
    fig.savefig(HERE / "10-01-precision-recall-grid.png")
    plt.close(fig)
    print("10-01 measured: precision=%s" % [round(p, 3) for p in prec])
    print("10-01 measured: recall   =%s" % [round(r, 3) for r in rec])


def discount_curve() -> None:
    """10-02: the log2 discount that makes rank 1 worth more than rank 9."""
    apply_style()
    positions = np.arange(1, 21)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(positions, 1 / np.log2(positions + 1), color=COLORS["primary"],
            linewidth=2, label="1 / log2(rank + 1)")
    ax.plot(positions, np.ones_like(positions, dtype=float), "--",
            color=COLORS["neutral"], label="no discount (1.0)")
    ax.plot(positions, 1 / positions, color=COLORS["warn"], linewidth=2,
            label="1 / rank")
    ax.set_xlabel("rank position")
    ax.set_ylabel("weight given to a relevant document")
    ax.set_title("Why NDCG discounts by log2(rank + 1)")
    ax.legend()
    ax.annotate("rank 1 weighs 1.00", xy=(1, 1.0), xytext=(1.4, 0.62),
                arrowprops=dict(arrowstyle="->", color=COLORS["primary"]),
                fontsize=9, color=COLORS["primary"])
    ax.annotate("rank 10 weighs only 0.29", xy=(10, 0.301), xytext=(11, 0.48),
                arrowprops=dict(arrowstyle="->", color=COLORS["primary"]),
                fontsize=9, color=COLORS["primary"])
    fig.tight_layout()
    fig.savefig(HERE / "10-02-ndcg-discount.png")
    plt.close(fig)


def mrr_example() -> None:
    """10-03: MRR on the same list, showing why the FIRST hit dominates."""
    apply_style()
    positions = np.arange(1, 11)
    rr = [reciprocal_rank(RANKED[:p] + RANKED[p:], RELEVANT) for p in positions]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(positions, rr, "o-", color=COLORS["accent"], linewidth=2)
    ax.set_xlabel("first relevant document is found at rank ...")
    ax.set_ylabel("reciprocal rank")
    ax.set_title("MRR: the first hit decides everything")
    ax.set_xticks(positions)
    ax.set_ylim(0, 1.05)
    for x, y in [(1, 1.0), (3, 1 / 3), (5, 0.2), (10, 0.1)]:
        ax.plot(x, y, "o", color=COLORS["warn"], zorder=5)
        ax.text(x + 0.12, y + 0.03, f"{y:.2f}", fontsize=9, color=COLORS["warn"])
    fig.tight_layout()
    fig.savefig(HERE / "10-03-mrr-example.png")
    plt.close(fig)
    print("10-03 measured: MRR on the worked list = %.4f"
          % reciprocal_rank(RANKED, RELEVANT))


def metric_comparison() -> None:
    """10-04: all metrics on one list — they disagree, on purpose."""
    apply_style()
    perfect = ["d1", "d5", "d9", "d3", "d7", "d4", "d8", "d2", "d6", "d10"]
    rows = [
        ("P@10", precision_at_k(RANKED, RELEVANT, 10),
         precision_at_k(perfect, RELEVANT, 10)),
        ("R@10", 1.0, 1.0),
        ("R-prec", 3 / 5, 1.0),
        ("MRR", reciprocal_rank(RANKED, RELEVANT), 1.0),
        ("MAP", average_precision(RANKED, RELEVANT), 1.0),
        ("NDCG@10", ndcg_at_k(RANKED, JUDGED, 10), 1.0),
    ]
    x = np.arange(len(rows))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w / 2, [r[1] for r in rows], w, label="worked list (1 relevant at rank 3)",
           color=COLORS["primary"])
    ax.bar(x + w / 2, [r[2] for r in rows], w, label="perfect ordering",
           color=COLORS["ok"])
    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in rows], fontsize=9)
    ax.set_ylabel("score")
    ax.set_ylim(0, 1.15)
    ax.set_title("Six metrics, one list — they tell different stories")
    ax.legend(fontsize=8)
    for i, r in enumerate(rows):
        ax.text(i - w / 2, r[1] + 0.02, f"{r[1]:.2f}", ha="center", fontsize=8)
        ax.text(i + w / 2, r[2] + 0.02, f"{r[2]:.2f}", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(HERE / "10-04-metric-comparison.png")
    plt.close(fig)
    print("10-04 measured: %s" % {r[0]: round(r[1], 4) for r in rows})


def circular_warning() -> None:
    """10-05: why every ranker scores 1.0 on this corpus — and what that means."""
    apply_style()
    with open(QRELS, mode="r", encoding="utf-8") as f:
        qrels = json.load(f)

    relevant_per_query, top10_possible = [], []
    for qid in sorted(qrels):
        judged = qrels[qid]["relevant"]
        relevant_per_query.append(sum(1 for g in judged.values() if g > 0))
        top10_possible.append(min(10, sum(1 for g in judged.values() if g > 0)))

    fig, ax = plt.subplots(figsize=(8, 4.8))
    qids = sorted(qrels)
    x = np.arange(len(qids))
    ax.bar(x, relevant_per_query, color=COLORS["primary"],
           label="documents judged relevant (per query)")
    ax.bar(x, top10_possible, color=COLORS["ok"],
           label="how many fit in the top 10")
    ax.set_xticks(x)
    ax.set_xticklabels(qids, fontsize=8)
    ax.set_ylabel("documents")
    ax.set_title("Why recall@10 is capped at 0.29 on this collection")
    ax.legend(fontsize=8.5)
    ax.annotate("34 relevant docs, 10 slots\n"
                "-> R@10 can never exceed 10/34 = 0.294",
                xy=(4, 34), xytext=(1.0, 40),
                arrowprops=dict(arrowstyle="->", color=COLORS["warn"]),
                fontsize=9, color=COLORS["warn"])
    fig.tight_layout()
    fig.savefig(HERE / "10-05-recall-ceiling.png")
    plt.close(fig)
    print("10-05 measured: relevant per query = %s" % relevant_per_query[:5])


def main() -> None:
    pr_grid()
    discount_curve()
    mrr_example()
    metric_comparison()
    circular_warning()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()
