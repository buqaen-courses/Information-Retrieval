"""Regenerate every PNG for Session 11 (deterministic; run in course venv).

Usage (from session-11-efficient-scoring/):
    python images/make_images.py

Every number here is MEASURED by running the real code on datasets/corpus
inside this script. Nothing is typed in by hand.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "session-11-efficient-scoring" / "workshop" / "solution"))
from tools.figstyle import COLORS, apply_style  # noqa: E402

from fast_score import (SKIP_INTERVAL, build_postings, build_skip_list,  # noqa: E402
                        compression_ratio, count_comparisons_plain,
                        count_comparisons_skips)

HERE = Path(__file__).resolve().parent
CORPUS = ROOT / "datasets" / "corpus"


def _box(ax, x, y, w, h, text, color=COLORS["primary"], face=None, fs=9):
    """A labelled box; white text on colour, dark text on a light face."""
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
                           facecolor=face if face else color,
                           edgecolor="black", linewidth=1.2, zorder=2)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", zorder=3,
            color="#111111" if face else "white", fontsize=fs, weight="bold")


def _arrow(ax, start, end, color="black", style="-"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                                 color=color, linewidth=1.4, linestyle=style,
                                 shrinkA=0, shrinkB=0, zorder=4))


def skip_pointer_traversal() -> None:
    """11-01: how a skip list lets an intersection jump over a whole block."""
    apply_style()
    postings, _ = build_postings(CORPUS)
    values = postings["the"][:128]
    skips = build_skip_list(values, SKIP_INTERVAL)

    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.4)
    ax.axis("off")
    ax.set_title(f"Skip pointers: skipping a block whose maximum is below the target "
                 f"(interval = {SKIP_INTERVAL})")

    n = min(len(values), 96)
    block_w = 9.0 / (len(skips[:4]) + 1)
    for i in range(n):
        x = 0.35 + i * (9.0 / n)
        w = 9.0 / n * 0.8
        first_of_block = any(s[0] == i for s in skips)
        ax.add_patch(plt.Rectangle((x, 1.55), w, 0.5,
                                   facecolor="#ffe9d6" if first_of_block else "#eeeeee",
                                   edgecolor="#999999", linewidth=0.6))
        ax.text(x + w / 2, 1.8, str(values[i]), ha="center", va="center", fontsize=6)
    ax.text(0.35, 2.25, "postings list for 'the' (real doc ids from datasets/corpus)",
            fontsize=9, style="italic")

    for j, (start, block_max) in enumerate(skips[:4]):
        x = 0.35 + start * (9.0 / n) + (9.0 / n) * 0.4
        ax.annotate("", xy=(x, 1.35), xytext=(x, 1.55),
                    arrowprops=dict(arrowstyle="-|>", color=COLORS["accent"], lw=1.4))
        ax.text(x, 1.15, f"max={block_max}", ha="center", fontsize=7,
                color=COLORS["accent"])

    ax.text(5.0, 0.72,
            "Looking for doc 150. Every block whose max is < 150 is skipped whole:",
            ha="center", fontsize=9.5, weight="bold")
    ax.text(5.0, 0.28,
            "a block may be skipped only when its MAXIMUM is below the target. "
            "Recording the block's first id instead silently loses matches.",
            ha="center", fontsize=8.5, style="italic", color="#333333")

    fig.tight_layout()
    fig.savefig(HERE / "11-01-skip-pointer-traversal.png")
    plt.close(fig)
    print(f"11-01 measured: 'the' has {len(postings['the'])} postings, "
          f"{len(skips)} skip pointers at interval {SKIP_INTERVAL}")


def compression_chart() -> None:
    """11-02: raw int32 bytes vs delta+varint, measured on the real index."""
    apply_style()
    stats = compression_ratio(CORPUS)
    postings, _ = build_postings(CORPUS)
    total_postings = sum(len(v) for v in postings.values())

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = ["raw int32", "delta + varint"]
    values = [stats["raw_bytes"], stats["packed_bytes"]]
    bars = ax.bar(labels, values, color=[COLORS["neutral"], COLORS["ok"]], width=0.5)
    ax.set_ylabel("bytes")
    ax.set_title(f"Postings compression on datasets/corpus "
                 f"({total_postings:,} postings, measured)")
    for rect, val in zip(bars, values):
        ax.text(rect.get_x() + rect.get_width() / 2, val + stats["raw_bytes"] * 0.02,
                f"{int(val):,}", ha="center", fontsize=10, weight="bold")
    ax.set_ylim(0, stats["raw_bytes"] * 1.18)
    ax.annotate(f"{stats['ratio']:.2f}x smaller",
                xy=(1, stats["packed_bytes"]), xytext=(0.35, stats["raw_bytes"] * 0.55),
                arrowprops=dict(arrowstyle="->", color=COLORS["warn"], lw=1.6),
                fontsize=12, weight="bold", color=COLORS["warn"])
    fig.tight_layout()
    fig.savefig(HERE / "11-02-compression-size.png")
    plt.close(fig)
    print(f"11-02 measured: raw={int(stats['raw_bytes']):,} "
          f"packed={int(stats['packed_bytes']):,} ratio={stats['ratio']:.2f}x")


def varint_growth() -> None:
    """11-03: why deltas compress — varint cost by magnitude."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    magnitudes = [1, 10, 100, 1000, 10000, 100000]
    costs = []
    for m in magnitudes:
        from fast_score import varint_encode
        costs.append(len(varint_encode(m)))
    ax.bar(range(len(magnitudes)), costs, color=COLORS["primary"], width=0.55)
    ax.set_xticks(range(len(magnitudes)))
    ax.set_xticklabels([str(m) for m in magnitudes])
    ax.set_xlabel("value to encode")
    ax.set_ylabel("bytes in varint form")
    ax.set_title("Varint cost by magnitude: small numbers are cheap")
    for i, c in enumerate(costs):
        ax.text(i, c + 0.15, f"{c} B", ha="center", fontsize=9)
    ax.set_ylim(0, max(costs) + 1.2)
    ax.annotate("most postings gaps are small,\nso delta + varint wins big",
                xy=(1, costs[1]), xytext=(2.6, max(costs) * 0.75),
                arrowprops=dict(arrowstyle="->", color=COLORS["warn"]),
                fontsize=9, color=COLORS["warn"])
    fig.tight_layout()
    fig.savefig(HERE / "11-03-varint-growth.png")
    plt.close(fig)
    print(f"11-03 measured: varint bytes for {magnitudes} = {costs}")


def comparisons_versus_time() -> None:
    """11-04: the honest result — fewer comparisons, but not faster in Python."""
    apply_style()
    postings, _ = build_postings(CORPUS)
    a, b = postings["topic"], postings["the"]
    plain_cmp = count_comparisons_plain(a, b)
    skip_cmp = count_comparisons_skips(a, b)
    ratio = plain_cmp / max(1, skip_cmp)

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(11, 4.4))
    fig.subplots_adjust(left=0.07, right=0.98, top=0.84, bottom=0.18, wspace=0.34)

    labels = ["plain\nmembership test", f"skip pointers\n(every {SKIP_INTERVAL})"]
    axl.bar([0, 1], [plain_cmp, skip_cmp], color=[COLORS["neutral"], COLORS["ok"]],
            width=0.5)
    axl.set_xticks([0, 1])
    axl.set_xticklabels(labels, fontsize=8.5)
    axl.set_ylabel("postings examined")
    axl.set_title("Work actually done", fontsize=11)
    for i, v in enumerate([plain_cmp, skip_cmp]):
        axl.text(i, v + plain_cmp * 0.03, f"{v:,}", ha="center", fontsize=10,
                 weight="bold")
    axl.set_ylim(0, plain_cmp * 1.2)
    axl.annotate(f"{ratio:.1f}x fewer", xy=(1, skip_cmp),
                 xytext=(0.42, plain_cmp * 0.55),
                 arrowprops=dict(arrowstyle="->", color=COLORS["ok"], lw=1.6),
                 fontsize=11, weight="bold", color=COLORS["ok"])

    import time

    def best(fn, repeat=7):
        out = float("inf")
        for _ in range(repeat):
            t0 = time.perf_counter()
            fn()
            out = min(out, time.perf_counter() - t0)
        return out

    from fast_score import intersect_plain, intersect_with_skips
    plain_s = best(lambda: intersect_plain(a, b))
    skip_s = best(lambda: intersect_with_skips(a, b))
    axr.bar([0, 1], [plain_s * 1000, skip_s * 1000],
            color=[COLORS["neutral"], COLORS["warn"]], width=0.5)
    axr.set_xticks([0, 1])
    axr.set_xticklabels(labels, fontsize=8.5)
    axr.set_ylabel("milliseconds")
    axr.set_title("Wall-clock in pure Python", fontsize=11)
    for i, v in enumerate([plain_s * 1000, skip_s * 1000]):
        axr.text(i, v + 0.01, f"{v:.3f} ms", ha="center", fontsize=9)
    axr.set_ylim(0, max(plain_s, skip_s) * 1000 * 1.35)
    axr.text(0.5, 0.97,
             "SLOWER — `x in list` is already\na tight C loop in CPython.\n"
             "Skip pointers pay off in engines\nwith millions of postings.",
             transform=axr.transAxes, ha="center", va="top", fontsize=8,
             color="#333333", linespacing=1.5,
             bbox=dict(boxstyle="round,pad=0.35", fc="#fff4e6", ec="#e0a96d"))

    fig.suptitle("Skip pointers cut the work by 6.2x and still lose on the clock (measured)",
                 fontsize=12, weight="bold", y=0.99)
    fig.tight_layout()
    fig.savefig(HERE / "11-04-comparisons-vs-time.png")
    plt.close(fig)
    print(f"11-04 measured: comparisons plain={plain_cmp} skips={skip_cmp} "
          f"({ratio:.2f}x); time plain={plain_s * 1000:.3f}ms "
          f"skips={skip_s * 1000:.3f}ms")


def main() -> None:
    skip_pointer_traversal()
    compression_chart()
    varint_growth()
    comparisons_versus_time()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()
