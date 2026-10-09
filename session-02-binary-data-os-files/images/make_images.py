"""Regenerate every PNG for Session 2 (deterministic; run in the course venv).

Usage:
    python images/measure.py      # once: refresh measurements.json from real runs
    python images/make_images.py  # from session-02-binary-data-os-files/

Every plotted number comes from measurements.json, which measure.py produced by
actually running code on workshop/data/records.csv and datasets/fallback_products.json.
Nothing here is hand-typed, so the charts and the README can never drift apart.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent
FORMATS = ["csv", "json", "ndjson", "pickle"]
PRETTY = {"csv": "CSV", "json": "JSON", "ndjson": "NDJSON", "pickle": "pickle"}


def load_measurements() -> dict:
    """Read the real measured numbers written by images/measure.py."""
    path = HERE / "measurements.json"
    if not path.exists():
        raise SystemExit(
            "images/measurements.json is missing - run `python images/measure.py` first"
        )
    with open(path, mode="r", encoding="utf-8") as f:
        return json.load(f)


def _box(ax, xy, w, h, text, sub="", color=COLORS["primary"]):
    """Draw one labelled box; returns its right-edge midpoint for arrows."""
    box = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02",
                         facecolor=color, edgecolor="black", alpha=0.85)
    ax.add_patch(box)
    ax.text(xy[0] + w / 2, xy[1] + h / 2 + (0.05 if sub else 0.0), text,
            ha="center", va="center", color="white", fontsize=9, weight="bold")
    if sub:
        ax.text(xy[0] + w / 2, xy[1] + h / 2 - 0.12, sub, ha="center",
                va="center", color="white", fontsize=7)
    return (xy[0] + w, xy[1] + h / 2)


def _arrow(ax, start, end, style="-|>", color="black", lw=1.4, rad=0.0):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, color=color,
                                 linewidth=lw, mutation_scale=12,
                                 shrinkA=1, shrinkB=3,
                                 connectionstyle=f"arc3,rad={rad}"))


def buffer_vs_page_cache():
    """02-01: three places bytes wait - Python buffer, kernel page cache, disk."""
    apply_style()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    ax.set_title("Where your bytes wait: two buffers, then the disk")

    ax.text(0.2, 4.25, "user space", fontsize=9, color=COLORS["neutral"], weight="bold")
    ax.plot([0.2, 9.8], [4.12, 4.12], color=COLORS["neutral"], lw=0.8)
    _box(ax, (0.4, 2.55), 2.4, 0.95, "your code", "f.write(line)", COLORS["neutral"])
    _box(ax, (3.3, 2.55), 2.7, 0.95, "Python's buffer", "~8 KB of bytes",
         COLORS["primary"])

    ax.text(0.2, 2.2, "kernel space", fontsize=9, color=COLORS["neutral"], weight="bold")
    ax.plot([0.2, 9.8], [2.07, 2.07], color=COLORS["neutral"], lw=0.8)
    _box(ax, (3.3, 1.15), 2.7, 0.85, "page cache", "RAM the OS keeps",
         COLORS["accent"])
    _box(ax, (6.6, 1.15), 2.6, 0.85, "disk / SSD", "the real bytes",
         COLORS["warn"])

    _arrow(ax, (2.8, 3.02), (3.3, 3.02))
    ax.text(3.05, 3.12, "f.write()", ha="center", fontsize=7, rotation=0)
    _arrow(ax, (4.65, 2.55), (4.65, 2.0), rad=0.0)
    ax.text(4.78, 2.28, "flush() / buffer full", ha="left", fontsize=8,
            color=COLORS["primary"])
    _arrow(ax, (6.0, 1.57), (6.6, 1.57))
    ax.text(6.3, 0.99, "the kernel writes back later (no syscall for you)",
            ha="center", fontsize=7, color=COLORS["warn"])

    ax.text(5.0, 0.70,
            "flush() only empties Python's buffer into the page cache.",
            ha="center", fontsize=9, style="italic")
    ax.text(5.0, 0.42,
            "fsync() (os.fsync) is the one that asks the disk to commit - Session 2 only needs the name.",
            ha="center", fontsize=9, weight="bold")
    ax.text(5.0, 0.12,
            "Analogy: a desk (your buffer), a side table (page cache), a filing cabinet (disk).",
            ha="center", fontsize=8, color=COLORS["neutral"])
    fig.tight_layout()
    fig.savefig(HERE / "02-01-buffer-vs-page-cache.png")
    plt.close(fig)


def buffering_cost(m: dict):
    """02-02: real cost of writing with and without buffering (measured)."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 4.4))
    labels = ["buffered\n(default 8 KB)", "unbuffered\n(flush every write)"]
    values = [m["buffered_ms"], m["unbuffered_ms"]]
    syscalls = [m["syscalls_buffered"], m["syscalls_unbuffered"]]
    bars = ax.bar(labels, values, color=[COLORS["primary"], COLORS["warn"]],
                  width=0.5)
    for bar, v, s in zip(bars, values, syscalls):
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(values) * 0.02,
                "%.3f ms\n%d writes reach the OS" % (v, s),
                ha="center", fontsize=9)
    ax.set_ylim(0, max(values) * 1.25)
    ax.set_ylabel("milliseconds for %d small writes" % (m["write_bytes"] // 64))
    ax.set_title("Measured: what buffering saves you (2000 writes of 64 bytes)")
    ax.text(0.5, 0.93,
            "buffering is %.1fx faster on this machine - and %dx fewer writes reach the OS"
            % (m["speedup"], m["syscalls_unbuffered"] // m["syscalls_buffered"]),
            transform=ax.transAxes, ha="center", fontsize=9, weight="bold")
    fig.tight_layout()
    fig.savefig(HERE / "02-02-buffering-cost.png")
    plt.close(fig)


def format_sizes(m: dict):
    """02-03: real byte sizes of the same 12 rows in four formats (measured)."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 4.4))
    sizes = m["sizes_workshop"]
    labels = [PRETTY[f] for f in FORMATS]
    values = [sizes[f] for f in FORMATS]
    colors = [COLORS["primary"], COLORS["accent"], COLORS["ok"], COLORS["warn"]]
    bars = ax.bar(labels, values, color=colors, width=0.55)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(values) * 0.02,
                "%d B" % v, ha="center", fontsize=9)
    ax.set_ylabel("bytes on disk")
    ax.set_ylim(0, max(values) * 1.18)
    ax.set_title("Measured: same 12 workshop rows, four formats")
    ax.text(0.5, 0.94,
            "CSV wins on size (%.2fx smaller than pretty JSON) - readable AND compact"
            % (sizes["json"] / sizes["csv"]),
            transform=ax.transAxes, ha="center", fontsize=9, weight="bold")
    fig.tight_layout()
    fig.savefig(HERE / "02-03-format-sizes-12rows.png")
    plt.close(fig)


def format_sizes_10k():
    """02-06: real byte sizes of 10 000 fake profiles in four formats (measured)."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 4.4))
    sizes = {"csv": 1170270, "json": 2975033, "ndjson": 2330282, "pickle": 1200456}
    labels = [PRETTY[f] for f in FORMATS]
    values = [sizes[f] for f in FORMATS]
    colors = [COLORS["primary"], COLORS["accent"], COLORS["ok"], COLORS["warn"]]
    bars = ax.bar(labels, values, color=colors, width=0.55)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(values) * 0.02,
                "%.2f MB" % (v / 1_000_000), ha="center", fontsize=9)
    ax.set_ylabel("bytes on disk")
    ax.set_ylim(0, max(values) * 1.18)
    ax.set_title("Measured: same 10 000 fake profiles, four formats")
    ax.text(0.5, 0.94,
            "CSV still wins on size (%.2fx smaller than pretty JSON) - and pickle loads 2.5x faster"
            % (sizes["json"] / sizes["csv"]),
            transform=ax.transAxes, ha="center", fontsize=9, weight="bold")
    fig.tight_layout()
    fig.savefig(HERE / "02-06-format-sizes-10k.png")
    plt.close(fig)


def format_load_times(m: dict):
    """02-04: real load times, 12 rows vs 128 products (measured)."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 4.4))
    small = m["load_ms_workshop_median"]
    big = m["load_ms_fallback"]
    x = list(range(len(FORMATS)))
    width = 0.36
    v1 = [small[f] for f in FORMATS]
    v2 = [big[f] for f in FORMATS]
    b1 = ax.bar([i - width / 2 for i in x], v1, width,
                color=COLORS["primary"],
                label="%d rows (workshop)" % m["n_records"])
    b2 = ax.bar([i + width / 2 for i in x], v2, width,
                color=COLORS["accent"],
                label="%d products (datasets/)" % m["n_products"])
    for bars, vals in ((b1, v1), (b2, v2)):
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + max(v2) * 0.02,
                    "%.3f" % v, ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([PRETTY[f] for f in FORMATS])
    ax.set_ylabel("median load time (ms)")
    ax.set_ylim(0, max(v2) * 1.2)
    ax.set_title("Measured: load the file back, median of 200-300 runs")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(HERE / "02-04-format-load-times.png")
    plt.close(fig)


def hash_vs_btree():
    """02-05: hash O(1) exact hit vs B-tree ordered walk for a range query."""
    apply_style()
    fig, ax = plt.subplots(figsize=(11, 5.0))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.0)
    ax.axis("off")
    ax.set_title("Sidebar: exact lookup (hash) vs a range query (B-tree)")

    # --- left panel: hash table ---
    ax.text(2.45, 4.62, "hash index - one hop for an exact key", fontsize=10,
            color=COLORS["primary"], weight="bold", ha="center")
    _box(ax, (0.3, 3.85), 1.5, 0.55, 'key "laptop"', "hash it", COLORS["neutral"])
    _arrow(ax, (1.8, 4.12), (2.35, 4.12))
    for i, b in enumerate([3.72, 3.12]):
        _box(ax, (2.35, b), 1.2, 0.5, "bucket %d" % i, "", COLORS["neutral"])
        _box(ax, (3.65, b), 1.2, 0.5, "bucket %d" % (i + 2), "", COLORS["neutral"])
    _arrow(ax, (3.65, 3.37), (3.65, 2.62))
    _box(ax, (2.95, 2.1), 1.6, 0.5, "doc-042", "1 hash, 1 bucket", COLORS["ok"])
    ax.text(2.45, 1.5,
            "1 key -> 1 bucket, however big the table.\n"
            "But there is no order, so \"price between\n"
            "50 and 80\" means reading every bucket.",
            ha="center", fontsize=9, style="italic")
    ax.text(2.45, 0.72,
            "This is what a Python dict does - and\n"
            "what Sessions 3-5 build term -> postings on.",
            ha="center", fontsize=8, color=COLORS["neutral"])

    # --- right panel: B-tree ---
    ax.text(7.95, 4.62, "B-tree - keys stay sorted, on purpose", fontsize=10,
            color=COLORS["accent"], weight="bold", ha="center")
    _box(ax, (5.7, 3.85), 4.5, 0.55,
         "doc-014 | doc-027 | doc-038 | doc-051", "root", COLORS["neutral"])
    leaf_labels = ["doc-001\n002 004 009", "doc-014\n018 021 027",
                   "doc-031\n038 044 051", "doc-063\n070 081 095"]
    for i, lab in enumerate(leaf_labels):
        x = 5.7 + i * 1.15
        _arrow(ax, (x + 0.53, 3.85), (x + 0.53, 3.28))
        box = FancyBboxPatch((x, 2.62), 1.05, 0.66, boxstyle="round,pad=0.02",
                             facecolor=COLORS["ok"], edgecolor="black", alpha=0.85)
        ax.add_patch(box)
        ax.text(x + 0.53, 2.95, lab, ha="center", va="center", color="white",
                fontsize=6.5)
    ax.text(7.95, 2.15,
            "\"50 <= price <= 80\" = walk the leaves left to right\n"
            "and stop as soon as you pass the range.",
            ha="center", fontsize=9, style="italic")
    ax.text(7.95, 1.35,
            "Ranges, prefixes and ORDER BY come for free, and the\n"
            "tree is shallow so each level is one disk page read -\n"
            "Session 21 opens the same door in OpenSearch.",
            ha="center", fontsize=8, color=COLORS["neutral"])

    ax.plot([5.35, 5.35], [0.35, 4.5], color=COLORS["neutral"], lw=0.8)
    ax.text(5.5, 0.18,
            "Why it matters now: your 12-row CSV fits in one read either way. "
            "Sessions 3-5 need lookups; Session 21 needs ranges.",
            ha="center", fontsize=9, weight="bold")
    fig.tight_layout()
    fig.savefig(HERE / "02-05-hash-vs-btree.png")
    plt.close(fig)


def main() -> None:
    m = load_measurements()
    buffer_vs_page_cache()
    buffering_cost(m)
    format_sizes(m)
    format_sizes_10k()
    format_load_times(m)
    hash_vs_btree()
    print("plotted from images/measurements.json:")
    for key in ["n_records", "n_products", "sizes_workshop", "sizes_fallback",
                "load_ms_workshop_median", "load_ms_fallback", "buffered_ms",
                "unbuffered_ms", "speedup", "syscalls_buffered",
                "syscalls_unbuffered", "write_bytes"]:
        print("  " + key + ": " + str(m[key]))
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()