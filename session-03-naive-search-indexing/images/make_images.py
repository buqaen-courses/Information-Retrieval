"""Regenerate every PNG for Session 3 (deterministic; run in the course venv).

Usage:
    python images/make_images.py        # from session-03-naive-search-indexing/

Every timing in 03-02 and 03-03 is MEASURED here, live, when the script runs:
the same linear-scan / build-index / dict-lookup code the workshop asks for,
pointed at the real datasets/corpus/ (204 docs).  Nothing is invented.

Measurement protocol (printed at the bottom of the run):
  * seed = random.Random(42) picks the query terms, so the benchmark is seeded.
  * 1 warm-up pass first (OS page cache), then REPEATS = 5 timed passes.
  * the MEDIAN pass is reported (timings on a laptop jitter; median is stable).
"""
from __future__ import annotations

import os
import random
import statistics
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent
CORPUS = ROOT / "datasets" / "corpus"

SEED = 42
REPEATS = 5
LOOKUP_BATCH = 1000
PUNCT = ":.,!?;\"'()"


# --------------------------------------------------------------------------
# the code under test -- identical to workshop/solution/search_index.py
# --------------------------------------------------------------------------
def list_txt_files(directory: str) -> list[str]:
    """Return the sorted .txt filenames inside `directory`."""
    names = []
    for name in os.listdir(directory):
        if name.endswith(".txt"):
            names.append(name)
    names.sort()
    return names


def words_of(path: str) -> list[str]:
    """Return the lowercased, punctuation-stripped words of one UTF-8 file."""
    f = open(path, mode="r", encoding="utf-8")
    text = f.read().lower()
    f.close()
    out = []
    for raw in text.split():
        word = raw.strip(PUNCT)
        if word != "":
            out.append(word)
    return out


def scan_for_term(paths: list[str], term: str) -> list[str]:
    """NAIVE: open every file and ask every one -- cost grows with the corpus."""
    hits = []
    for path in paths:
        if term in words_of(path):
            hits.append(path)
    return hits


def build_index(paths: list[str]) -> dict[str, list[str]]:
    """Build {term: [filenames]} in ONE pass -- the work you pay for once."""
    index: dict[str, list[str]] = {}
    for path in paths:
        for word in words_of(path):
            if word not in index:
                index[word] = [path]
            elif index[word][-1] != path:
                # the same term twice in the SAME file -> list that file once
                index[word].append(path)
    return index


def lookup(index: dict[str, list[str]], term: str) -> list[str]:
    """Answer a query with ONE dict lookup -- cost independent of the corpus."""
    if term in index:
        return index[term]
    return []


# --------------------------------------------------------------------------
# measurement helpers
# --------------------------------------------------------------------------
def median_ms(func, repeats: int = REPEATS) -> float:
    """Median wall-clock milliseconds of `func` over `repeats` timed passes."""
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        func()
        samples.append((time.perf_counter() - start) * 1000.0)
    return statistics.median(samples)


def measure_lookup_ms(index: dict[str, list[str]], term: str) -> float:
    """Median ms for ONE lookup, timed as a batch to beat the clock overhead."""
    samples = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        for _ in range(LOOKUP_BATCH):
            lookup(index, term)
        elapsed = (time.perf_counter() - start) * 1000.0
        samples.append(elapsed / LOOKUP_BATCH)
    return statistics.median(samples)


def run_benchmark() -> dict:
    """Measure scan / build / lookup on the real corpus; return the raw numbers."""
    names = list_txt_files(str(CORPUS))
    paths = [str(CORPUS / name) for name in names]
    index = build_index(paths)

    rng = random.Random(SEED)
    keys = sorted(index.keys())
    terms: list[str] = []
    while len(terms) < 5:
        pick = rng.choice(keys)
        if pick not in terms:
            terms.append(pick)

    # warm-up pass so the OS page cache is not charged to the first measurement
    scan_for_term(paths, terms[0])
    lookup(index, terms[0])
    build_index(paths)

    term = terms[1]
    scan_ms = median_ms(lambda: scan_for_term(paths, term))
    build_ms = median_ms(lambda: build_index(paths))
    lookup_ms = measure_lookup_ms(index, term)

    # cost growth: the same two strategies on growing prefixes of the corpus
    growth = []
    for size in (25, 50, 100, 204):
        subset = paths[:size]
        scan_at = median_ms(lambda: scan_for_term(subset, term), repeats=3)
        lookup_at = measure_lookup_ms(index, term)
        growth.append((size, scan_at, lookup_at))

    return {
        "docs": len(paths),
        "terms": len(index),
        "seeded_queries": terms,
        "term": term,
        "scan_ms": scan_ms,
        "build_ms": build_ms,
        "lookup_ms": lookup_ms,
        "speedup": scan_ms / lookup_ms,
        "growth": growth,
        "agrees": scan_for_term(paths, term) == lookup(index, term),
    }


# --------------------------------------------------------------------------
# drawing helpers
# --------------------------------------------------------------------------
def _box(ax, xy, w, h, text, sub="", color=COLORS["primary"], size=10):
    box = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02",
                         facecolor=color, edgecolor="black", alpha=0.85)
    ax.add_patch(box)
    ax.text(xy[0] + w / 2, xy[1] + h / 2 + 0.04, text, ha="center",
            va="center", color="white", fontsize=size, weight="bold")
    if sub:
        ax.text(xy[0] + w / 2, xy[1] - 0.07, sub, ha="center",
                va="top", fontsize=8, style="italic")
    return (xy[0] + w, xy[1] + h / 2)


def _arrow(ax, start, end, color="black", style="-|>", lw=1.5):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, color=color,
                                 linewidth=lw, mutation_scale=12,
                                 shrinkA=1, shrinkB=3))


def _page(ax, xy, w, h, label, color=COLORS["neutral"]):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.01",
                                facecolor="white", edgecolor=color, linewidth=1.4))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, label, ha="center", va="center",
            fontsize=7, color=color)


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
def book_index_analogy() -> None:
    """03-01: page-flipping (linear scan) vs the book index (dict lookup)."""
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.0))

    # left -- page flipping
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("A. Page-flipping  =  linear scan", fontsize=11, weight="bold")
    x = 0.3
    for i in range(1, 10):
        _page(ax, (x, 4.3), 0.82, 1.1, str(i))
        x += 1.02
    ax.text(5, 3.7, "... 204 ...  millions ...", ha="center", fontsize=9,
            style="italic", color=COLORS["neutral"])
    _arrow(ax, (0.5, 5.85), (9.4, 5.85), color=COLORS["warn"], lw=2.0)
    ax.text(5, 6.05, "open page 1, read it, close it, next ...", ha="center",
            fontsize=9, weight="bold", color=COLORS["warn"])
    ax.text(5, 2.3, "Every query pays for every page.", ha="center",
            fontsize=9, weight="bold")
    ax.text(5, 1.5, "Cost grows with the corpus:  O(corpus)",
            ha="center", fontsize=10, color=COLORS["warn"])
    ax.text(5, 0.7, "This is what you will code in workshop Stop 1.",
            ha="center", fontsize=8, style="italic", color=COLORS["neutral"])

    # right -- the index at the back of the book
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("B. The index at the back  =  a dict", fontsize=11, weight="bold")
    ax.add_patch(FancyBboxPatch((0.4, 4.2), 3.5, 2.6,
                                boxstyle="round,pad=0.02",
                                facecolor=COLORS["primary"], alpha=0.15,
                                edgecolor="black", linewidth=1.4))
    ax.text(2.15, 6.35, "INDEX", ha="center", fontsize=10, weight="bold")
    rows = ["rover  ->  7, 42, 88", "basil  ->  12, 61", "tomato  ->  5"]
    for i, row in enumerate(rows):
        ax.text(0.6, 5.85 - i * 0.5, row, ha="left", fontsize=9, family="monospace")
    _arrow(ax, (4.0, 5.5), (6.3, 5.5), color=COLORS["ok"], lw=2.0)
    ax.text(5.15, 5.72, 'one lookup for "rover"', ha="center", fontsize=8,
            weight="bold", color=COLORS["ok"])
    _page(ax, (6.4, 4.2), 0.82, 1.1, "7", COLORS["ok"])
    _page(ax, (7.6, 4.2), 0.82, 1.1, "42", COLORS["ok"])
    _page(ax, (8.8, 4.2), 0.82, 1.1, "88", COLORS["ok"])
    ax.text(5, 2.3, "Do that work ONCE, at index time.", ha="center",
            fontsize=9, weight="bold")
    ax.text(5, 1.5, "Cost is independent of the corpus:  O(query)",
            ha="center", fontsize=10, color=COLORS["ok"])
    ax.text(5, 0.7, "This is what you will code in workshop Stop 2.",
            ha="center", fontsize=8, style="italic", color=COLORS["neutral"])

    fig.tight_layout()
    fig.savefig(HERE / "03-01-page-flipping-vs-book-index.png")
    plt.close(fig)


def timing_chart(data: dict) -> None:
    """03-02: MEASURED cost of one query, linear scan vs dict lookup."""
    apply_style()
    labels = ["linear scan\n(per query)", "build the index\n(ONE-TIME cost)",
              "dict lookup\n(per query)"]
    values = [data["scan_ms"], data["build_ms"], data["lookup_ms"]]
    colors = [COLORS["warn"], COLORS["neutral"], COLORS["ok"]]
    captions = [f'{data["scan_ms"]:.2f} ms', f'{data["build_ms"]:.2f} ms',
                f'{data["lookup_ms"] * 1000:.2f} us']

    fig, ax = plt.subplots(figsize=(8, 4.6))
    bars = ax.bar(labels, values, color=colors, width=0.6)
    ax.set_yscale("log")
    ax.set_ylim(values[2] * 0.3, values[1] * 12)
    ax.set_ylabel("milliseconds for one query  (log scale)")
    ax.set_title(f'Measured on {data["docs"]} corpus docs: the index wins '
                 f'~{data["speedup"]:,.0f}x per query')
    for bar, caption in zip(bars, captions):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.3,
                caption, ha="center", fontsize=10, weight="bold")
    ax.annotate(f'{data["speedup"]:,.0f}x faster\nper query',
                xy=(2, values[2]), xytext=(1.72, values[1] * 0.22),
                fontsize=11, weight="bold", color=COLORS["ok"], ha="center",
                arrowprops=dict(arrowstyle="-|>", color=COLORS["ok"], lw=1.6))
    fig.text(0.5, 0.035,
             f'median of {REPEATS} timed passes after 1 warm-up pass; query term '
             f'"{data["term"]}" picked with random.Random({SEED});',
             ha="center", fontsize=7.5, style="italic")
    fig.text(0.5, 0.008,
             f"lookup timed as a batch of {LOOKUP_BATCH} calls so the stopwatch "
             "itself is not what we measure",
             ha="center", fontsize=7.5, style="italic")
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    fig.savefig(HERE / "03-02-scan-vs-lookup-timing.png")
    plt.close(fig)


def cost_growth(data: dict) -> None:
    """03-03: MEASURED growth -- O(corpus) vs O(query) as the corpus grows."""
    apply_style()
    sizes = [row[0] for row in data["growth"]]
    scans_us = [row[1] * 1000.0 for row in data["growth"]]
    lookups_us = [row[2] * 1000.0 for row in data["growth"]]

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(sizes, scans_us, marker="o", color=COLORS["warn"], linewidth=2.2,
            markersize=7, label="linear scan")
    ax.plot(sizes, lookups_us, marker="s", color=COLORS["ok"], linewidth=2.2,
            markersize=7, label="dict lookup")
    ax.set_yscale("log")
    ax.set_ylim(0.05, max(scans_us) * 4)
    ax.set_xlabel("documents in the corpus")
    ax.set_ylabel("microseconds per query  (log scale)")
    ax.set_title("Same query, growing corpus: one line climbs, one line lies flat")
    ax.legend(loc="center left", framealpha=0.95)
    for x, y in zip(sizes, scans_us):
        ax.annotate(f"{y:,.0f}", (x, y), textcoords="offset points",
                    xytext=(8, -12), ha="left", fontsize=9, color=COLORS["warn"])
    ax.annotate(f"{lookups_us[-1]:.2f} us", (sizes[-1], lookups_us[-1]),
                textcoords="offset points", xytext=(-4, 9), ha="right",
                fontsize=9, color=COLORS["ok"])
    ax.text(0.44, 0.52, "O(corpus)\nmore files, more work\non every single query",
            transform=ax.transAxes, fontsize=10, weight="bold",
            color=COLORS["warn"], ha="center")
    ax.text(0.60, 0.16, "O(query)\nflat, whatever the corpus size",
            transform=ax.transAxes, fontsize=10, weight="bold",
            color=COLORS["ok"], ha="center")
    ax.text(0.44, 0.28,
            f'{sizes[0]} docs -> {sizes[-1]} docs =\n'
            f'{sizes[-1] / sizes[0]:.1f}x more documents, '
            f'{scans_us[-1] / scans_us[0]:.1f}x more scan time',
            transform=ax.transAxes, fontsize=8.5, style="italic",
            color=COLORS["neutral"], ha="center")
    fig.text(0.5, 0.015,
             f'measured on growing prefixes of datasets/corpus/; median of 3 '
             f'timed passes; query term "{data["term"]}" (seed {SEED})',
             ha="center", fontsize=8, style="italic")
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(HERE / "03-03-cost-growth.png")
    plt.close(fig)


def bridge_to_inverted_index() -> None:
    """03-04: term -> files is one step away from a real inverted index."""
    apply_style()
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("One dict, two hops away from a real inverted index")

    steps = [
        (7.3, "TODAY (Session 3) -- term to filenames",
         '{"rover": ["doc-007.txt", "doc-042.txt"]}', COLORS["primary"]),
        (4.6, "HOP 1 -- filenames become document ids",
         '{"rover": ["doc-007", "doc-042"]}', COLORS["accent"]),
        (1.9, "HOP 2 -- remember how many times  (Session 5)",
         'rover -> [(doc-007, 2), (doc-042, 1)]   = a POSTINGS LIST',
         COLORS["ok"]),
    ]
    for y, title, body, color in steps:
        ax.add_patch(FancyBboxPatch((0.5, y), 9.0, 1.85,
                                    boxstyle="round,pad=0.03",
                                    facecolor=color, alpha=0.14,
                                    edgecolor=color, linewidth=2.0))
        ax.text(0.75, y + 1.5, title, ha="left", va="top", fontsize=10,
                weight="bold", color=color)
        ax.text(1.15, y + 0.8, body, ha="left", va="center", fontsize=12,
                family="monospace")

    _arrow(ax, (5.0, 7.3), (5.0, 6.6), color=COLORS["neutral"], lw=2.0)
    ax.text(5.2, 6.88, "filename  ->  document id", ha="left", fontsize=8,
            style="italic")
    _arrow(ax, (5.0, 4.6), (5.0, 3.9), color=COLORS["neutral"], lw=2.0)
    ax.text(5.2, 4.18, "list of names  ->  list of (id, count) pairs", ha="left",
            fontsize=8, style="italic")

    ax.text(5, 0.55, "Sort each list once and the dict IS an inverted index "
                     "-- that is Session 5.", ha="center", fontsize=10.5,
            weight="bold", color=COLORS["warn"])
    ax.text(5, 0.12, "We built it in a dozen lines of plain Python today. "
                     "So can you.", ha="center", fontsize=9, style="italic",
            color=COLORS["neutral"])
    fig.tight_layout()
    fig.savefig(HERE / "03-04-bridge-to-inverted-index.png")
    plt.close(fig)


def main() -> None:
    data = run_benchmark()
    book_index_analogy()
    timing_chart(data)
    cost_growth(data)
    bridge_to_inverted_index()

    print("MEASURED (live, this run) ------------------------------------")
    print(f'corpus docs          : {data["docs"]}')
    print(f'distinct terms       : {data["terms"]}')
    print(f'seeded queries       : {data["seeded_queries"]} (seed {SEED})')
    print(f'linear scan / query  : {data["scan_ms"]:.3f} ms')
    print(f'build index (once)   : {data["build_ms"]:.3f} ms')
    print(f'dict lookup / query  : {data["lookup_ms"] * 1000:.3f} us')
    print(f'per-query speedup    : {data["speedup"]:,.0f}x')
    print(f'scan == lookup       : {data["agrees"]}')
    print("growth (docs, scan_ms, lookup_us):")
    for size, scan_at, lookup_at in data["growth"]:
        print(f'   {size:>4}  {scan_at:8.3f}  {lookup_at * 1000:8.4f}')
    print("-----------------------------------------------------------")
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()
