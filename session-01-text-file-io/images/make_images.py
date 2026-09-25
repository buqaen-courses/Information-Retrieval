"""Regenerate every PNG for Session 1 (deterministic; run in course venv).

Usage:
    python images/make_images.py        # from session-01-text-file-io/
"""
from __future__ import annotations

import string
import sys
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent


def _box(ax, xy, w, h, text, sub="", color=COLORS["primary"]):
    box = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02",
                         facecolor=color, edgecolor="black", alpha=0.85)
    ax.add_patch(box)
    ax.text(xy[0] + w / 2, xy[1] + h / 2 + 0.03, text, ha="center",
            va="center", color="white", fontsize=10, weight="bold")
    if sub:
        ax.text(xy[0] + w / 2, xy[1] - 0.06, sub, ha="center",
                va="top", fontsize=8, style="italic")
    return (xy[0] + w, xy[1] + h / 2)


def _arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                                 color="black", linewidth=1.5,
                                 mutation_scale=12, shrinkA=1, shrinkB=3))


def roadmap():
    """01-01: the course pipeline crawl->parse->index->query->rank->evaluate."""
    apply_style()
    fig, ax = plt.subplots(figsize=(9, 2.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.2)
    ax.axis("off")
    ax.set_title("The IR pipeline — one session per box (this course)")
    steps = [("CRAWL", "S17-19"), ("PARSE", "S18"), ("INDEX", "S5"),
             ("QUERY", "S6-7"), ("RANK", "S8-9"), ("EVALUATE", "S10")]
    colors = [COLORS["primary"], COLORS["accent"], COLORS["primary"],
              COLORS["accent"], COLORS["primary"], COLORS["ok"]]
    x = 0.15
    prev = None
    for (label, sub), c in zip(steps, colors):
        end = _box(ax, (x, 0.8), 1.35, 0.7, label, sub, c)
        start = (x, 1.15)
        if prev is not None:
            _arrow(ax, prev, start)
        prev = end
        x += 1.6
    ax.text(5, 0.25, "YOU ARE HERE (S1) → reading files is where every pipeline starts",
            ha="center", fontsize=9, weight="bold")
    fig.tight_layout()
    fig.savefig(HERE / "01-01-roadmap-pipeline.png")
    plt.close(fig)


def lifecycle():
    """01-02: file-object lifecycle open->read/write->flush->close."""
    apply_style()
    fig, ax = plt.subplots(figsize=(9, 2.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.2)
    ax.axis("off")
    ax.set_title("A file object's life: open → use → flush → close")
    steps = [("open()", "get a handle"), ("read/write", "move data"),
             ("flush()", "push buffer"), ("close()", "release handle")]
    x = 0.3
    prev = None
    for label, sub in steps:
        end = _box(ax, (x, 0.8), 1.7, 0.7, label, sub)
        if prev is not None:
            _arrow(ax, prev, (x, 1.15))
        prev = end
        x += 2.3
    ax.text(5, 0.25, "Forgetting close() = leaking handles. 'with' blocks fix that (see 01-04).",
            ha="center", fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(HERE / "01-02-file-lifecycle.png")
    plt.close(fig)


def encode_decode():
    """01-03: str <-> bytes via encode/decode with an explicit encoding."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 3.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.6)
    ax.axis("off")
    ax.set_title("Text (str) vs bytes: encode → / → decode (UTF-8)")
    _box(ax, (0.5, 1.0), 2.6, 0.8, "str 'سلام café'", "human text")
    _box(ax, (6.9, 1.0), 2.6, 0.8, "bytes b'...'", "disk / network", COLORS["accent"])
    _arrow(ax, (3.1, 1.55), (6.9, 1.55))
    _arrow(ax, (6.9, 1.25), (3.1, 1.25))
    ax.text(5.0, 1.72, ".encode('utf-8') →", ha="center", fontsize=9, weight="bold")
    ax.text(5.0, 1.05, "← .decode('utf-8')", ha="center", fontsize=9, weight="bold")
    ax.text(5.0, 0.35, "Wrong encoding = mojibake (garbled text). Always state UTF-8.",
            ha="center", fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(HERE / "01-03-encode-decode.png")
    plt.close(fig)


def context_manager():
    """01-04: manual open/close vs 'with' block (the safe pattern)."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.0)
    ax.axis("off")
    ax.set_title("Manual close (risky) vs 'with' block (safe)")
    _box(ax, (0.4, 1.9), 4.0, 0.6, "f = open(...) ... f.close()", "crash before close = leak",
         COLORS["warn"])
    _box(ax, (5.6, 1.9), 4.0, 0.6, "with open(...) as f: ...", "auto-close, even on error",
         COLORS["ok"])
    ax.text(5.0, 1.2, "Analogy: borrowing a library book by hand vs a self-returning book.",
            ha="center", fontsize=9, style="italic")
    ax.text(5.0, 0.7, "Rule of thumb: if you type open(, type with first.",
            ha="center", fontsize=10, weight="bold")
    fig.tight_layout()
    fig.savefig(HERE / "01-04-context-manager.png")
    plt.close(fig)


def wordcount_chart():
    """01-05: REAL top-8 word counts from a seeded corpus doc (not invented)."""
    apply_style()
    sample = ROOT / "datasets" / "corpus" / "doc-001.txt"
    text = sample.read_text(encoding="utf-8").lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = [w for w in text.split() if len(w) > 2]
    top = Counter(words).most_common(8)
    labels = [w for w, _ in top]
    values = [c for _, c in top]
    fig, ax = plt.subplots(figsize=(8, 4.0))
    ax.bar(labels, values, color=COLORS["primary"])
    ax.set_title("Real data: top-8 words in datasets/corpus/doc-001.txt")
    ax.set_xlabel("word")
    ax.set_ylabel("count")
    for x, v in enumerate(values):
        ax.text(x, v + 0.05, str(v), ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(HERE / "01-05-wordcount-doc001.png")
    plt.close(fig)
    print("wordcount source:", sample.name, dict(top))


def open_under_hood():
    """01-06: layers crossed by open(): file object -> buffer -> OS handle -> disk."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    ax.set_title("What open() actually builds (no data moves yet)")
    _box(ax, (0.3, 1.8), 2.2, 0.7, "your code", 'f = open(...)')
    _box(ax, (2.9, 1.8), 2.2, 0.7, "file object", "buffer + position")
    _box(ax, (5.5, 1.8), 2.2, 0.7, "OS handle", "file descriptor", COLORS["accent"])
    _box(ax, (8.1, 1.8), 1.6, 0.7, "disk", "bytes", COLORS["neutral"])
    for a, b in [(2.5, 2.9), (5.1, 5.5), (7.7, 8.1)]:
        _arrow(ax, (a, 2.15), (b, 2.15))
    ax.text(5.0, 1.2, "read() pulls bytes up this chain and decodes them to str.",
            ha="center", fontsize=9, style="italic")
    ax.text(5.0, 0.75, 'Exception: mode="w" empties the file immediately at open() time.',
            ha="center", fontsize=9, weight="bold")
    fig.tight_layout()
    fig.savefig(HERE / "01-06-open-under-hood.png")
    plt.close(fig)


def main() -> None:
    roadmap()
    lifecycle()
    encode_decode()
    context_manager()
    wordcount_chart()
    open_under_hood()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()
