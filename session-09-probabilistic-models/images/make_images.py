"""Regenerate every PNG for Session 9 (deterministic; run in course venv).

Usage (from session-09-probabilistic-models/):
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


def bm_flow() -> None:
    """09-01: BIM — the document-as-random-events view."""
    apply_style()
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("Binary Independence Model: a document generates query terms")

    boxes = [(0.4, 1.6, 2.2, 0.9, "Document d", "a bag of words"),
             (3.3, 1.6, 2.2, 0.9, "Word choice", "each word on\nits own toss"),
             (6.2, 1.6, 2.2, 0.9, "Query q", "the words a user\ntyped"),
             (9.1, 1.6, 2.4, 0.9, "P(q | d)", "probability the\ndoc produced q")]
    for x, y, w, h, t, sub in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=COLORS["primary"],
                                   edgecolor="black", alpha=0.9))
        ax.text(x + w / 2, y + h / 2 + 0.14, t, ha="center", va="center",
                color="white", weight="bold", fontsize=11)
        ax.text(x + w / 2, y + h / 2 - 0.22, sub, ha="center", va="center",
                color="white", fontsize=8, style="italic")
    for i in range(3):
        x0 = 2.6 + i * 2.9
        ax.annotate("", xy=(x0 + 0.7, 2.05), xytext=(x0, 2.05),
                    arrowprops=dict(arrowstyle="->", lw=1.6, color="black"))
    ax.text(6.0, 3.35,
            "Rank documents by P(q | d) — how well this document explains the query",
            ha="center", fontsize=10, weight="bold")
    ax.text(6.0, 0.85,
            "The catch: with no smoothing, a single unseen word gives probability 0. "
            "That is why Dirichlet smoothing exists.",
            ha="center", fontsize=9, style="italic", color="#333333")
    fig.tight_layout()
    fig.savefig(HERE / "09-01-bim-flow.png")
    plt.close(fig)


def smoothing_effect() -> None:
    """09-02: Dirichlet smoothing rescues short documents."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    doc_len = np.arange(1, 101)
    k1, b = 1.2, 0.75
    avgdl = 100.0
    freq = 3
    unsmoothed = freq * (k1 + 1) / (freq + k1 * (1 - b + b * doc_len / avgdl))
    smoothed = unsmoothed * (doc_len / (doc_len + 50))
    ax.plot(doc_len, unsmoothed, label="no smoothing", color=COLORS["warn"],
            linewidth=2)
    ax.plot(doc_len, smoothed, label="Dirichlet smoothing", color=COLORS["primary"],
            linewidth=2)
    ax.set_xlabel("document length (tokens)")
    ax.set_ylabel("TF component")
    ax.set_title("Short documents get unfair scores without smoothing")
    ax.legend()
    ax.annotate("short doc: unearned boost", xy=(5, unsmoothed[4]),
                xytext=(30, 1.5), arrowprops=dict(arrowstyle="->", color=COLORS["warn"]),
                fontsize=9, color=COLORS["warn"])
    fig.tight_layout()
    fig.savefig(HERE / "09-02-smoothing-effect.png")
    plt.close(fig)


def query_likelihood_vs_bm25() -> None:
    """09-03: QL and BM25 rank differently — measured on our corpus."""
    apply_style()
    import json
    import os

    corpus = ROOT / "datasets" / "corpus"
    names = sorted(n for n in os.listdir(corpus) if n.endswith(".txt"))
    docs = {}
    for name in names:
        with open(corpus / name, mode="r", encoding="utf-8") as f:
            docs[name[:-4]] = f.read().lower().split()
    with open(ROOT / "datasets" / "qrels.json", mode="r", encoding="utf-8") as f:
        qrels = json.load(f)

    def bm25_rank(query):
        q = query.lower().split()
        n = len(docs)
        avgdl = sum(len(t) for t in docs.values()) / n
        df = {w: sum(1 for t in docs.values() if w in t) for w in q}
        out = []
        for did, toks in docs.items():
            score = 0.0
            dl = len(toks)
            for w in q:
                if w not in df or df[w] == 0:
                    continue
                idf = np.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
                f = toks.count(w)
                if f:
                    score += idf * (f * 2.2) / (f + 1.2 * (1 - 0.75 + 0.75 * dl / avgdl))
            out.append((did, score))
        out.sort(key=lambda kv: (-kv[1], kv[0]))
        return [d for d, _ in out[:10]]

    def ql_rank(query, mu=200.0):
        q = query.lower().split()
        n = len(docs)
        cf = {}
        for toks in docs.values():
            for w in toks:
                cf[w] = cf.get(w, 0) + 1
        total = sum(len(t) for t in docs.values())
        out = []
        for did, toks in docs.items():
            dl = len(toks)
            ll = 0.0
            for w in q:
                p = (cf.get(w, 0) + mu * 0.01) / (total + mu)
                ll += np.log((toks.count(w) + mu * p) / (dl + mu))
            out.append((did, ll))
        out.sort(key=lambda kv: (-kv[1], kv[0]))
        return [d for d, _ in out[:10]]

    qids = sorted(qrels)[:6]
    bm_overlap, ql_overlap = [], []
    for qid in qids:
        rel = [d for d, g in qrels[qid]["relevant"].items() if g >= 2][:10]
        if not rel:
            continue
        bm_overlap.append(len(set(bm25_rank(qrels[qid]["query"])) & set(rel)))
        ql_overlap.append(len(set(ql_rank(qrels[qid]["query"])) & set(rel)))

    x = np.arange(len(bm_overlap))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w / 2, bm_overlap, w, label="BM25", color=COLORS["primary"])
    ax.bar(x + w / 2, ql_overlap, w, label="query likelihood",
           color=COLORS["accent"])
    ax.set_xticks(x)
    ax.set_xticklabels(qids, fontsize=8)
    ax.set_ylabel("highly-relevant docs in top 10")
    ax.set_title("BM25 vs query likelihood on the same judgments (measured)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HERE / "09-03-ql-vs-bm25.png")
    plt.close(fig)
    print("09-03 measured: bm25=%s ql=%s" % (bm_overlap, ql_overlap))


def main() -> None:
    bm_flow()
    smoothing_effect()
    query_likelihood_vs_bm25()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()
