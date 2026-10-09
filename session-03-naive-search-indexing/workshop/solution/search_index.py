"""Naive linear search vs a term -> files dictionary, over a folder of .txt docs.

Two ways to answer the only question a search engine ever starts with:
"which documents contain the word X?"

  1. scan_for_term()  -- the NAIVE way: open every file, read it, ask it.
                          Cost grows with the corpus.  O(corpus)
  2. build_index()    -- the INDEXED way: pay once, in a single pass.
     + lookup()          {"rover": ["doc-007.txt", "doc-042.txt"]}
                          Cost is independent of the corpus.  O(query)

Built with basics only: open(), for loops, plain dicts/lists, sorted().
No pathlib, no Counter, no lambda, no regex.

Usage (from the session folder, with the course venv active):
    python workshop/solution/search_index.py workshop/data/mini_corpus python
    python workshop/solution/search_index.py ../datasets/corpus rovers --bench

`--bench` adds the measured timing table and writes workshop/benchmark.png.
Timing numbers change from machine to machine; the shape never does.
"""
from __future__ import annotations

import os
import sys
import time

REPEATS = 5          # timed passes; the MEDIAN one is reported
LOOKUP_BATCH = 1000  # a lookup is too fast to time one at a time -- do 1000
OUT_PATH = os.path.join("workshop", "benchmark.png")   # stays inside this session
PUNCT = ":.,!?;\"'()"


# --------------------------------------------------------------------------
# given to you (Session 1 material: open, lower, split, strip)
# --------------------------------------------------------------------------
def words_of(path: str) -> list[str]:
    """Return the lowercased, punctuation-stripped words of one UTF-8 file.

    `open(path, mode="r", encoding="utf-8")` asks the OS for the file and hands
    back a buffered file object; `.read()` pulls the bytes through it and
    decodes them to str (mode="r" is read, mode="w" would empty the file first,
    mode="a" would append -- we always want "r" here).
    """
    f = open(path, mode="r", encoding="utf-8")
    text = f.read().lower()
    f.close()
    out = []
    for raw in text.split():
        word = raw.strip(PUNCT)
        if word != "":
            out.append(word)
    return out


# --------------------------------------------------------------------------
# TODO-1  TODO-2  -- the naive scanner
# --------------------------------------------------------------------------
def list_txt_files(directory: str) -> list[str]:
    """Return the sorted .txt filenames inside `directory`."""
    names = []
    for name in os.listdir(directory):
        if name.endswith(".txt"):
            names.append(name)
    names.sort()
    return names


def scan_for_term(directory: str, names: list[str], term: str) -> list[str]:
    """NAIVE SEARCH: open every file and ask every one. O(corpus)."""
    hits = []
    for name in names:
        path = os.path.join(directory, name)
        if term in words_of(path):
            hits.append(name)
    return hits


# --------------------------------------------------------------------------
# TODO-3  TODO-4  -- the index and the one-line query
# --------------------------------------------------------------------------
def build_index(directory: str, names: list[str]) -> dict[str, list[str]]:
    """Build {term: [filenames]} in ONE pass. O(corpus) once, then free."""
    index: dict[str, list[str]] = {}
    for name in names:
        path = os.path.join(directory, name)
        for word in words_of(path):
            if word not in index:
                index[word] = [name]
            elif index[word][-1] != name:
                # the same word twice in the SAME file: list that file once
                index[word].append(name)
    return index


def lookup(index: dict[str, list[str]], term: str) -> list[str]:
    """Answer a query with ONE dict lookup. O(query)."""
    if term in index:
        return index[term]
    return []


# --------------------------------------------------------------------------
# TODO-5  -- measure both strategies honestly
# --------------------------------------------------------------------------
def benchmark(directory: str, names: list[str], index: dict[str, list[str]],
              term: str, repeats: int = REPEATS) -> dict[str, float]:
    """Return median milliseconds for a linear scan, an index build, one lookup."""
    scan_times = []
    build_times = []
    lookup_times = []
    for _ in range(repeats):
        start = time.perf_counter()
        scan_for_term(directory, names, term)
        scan_times.append((time.perf_counter() - start) * 1000.0)

        start = time.perf_counter()
        build_index(directory, names)
        build_times.append((time.perf_counter() - start) * 1000.0)

        start = time.perf_counter()
        for _ in range(LOOKUP_BATCH):
            lookup(index, term)
        lookup_times.append((time.perf_counter() - start) * 1000.0 / LOOKUP_BATCH)

    return {
        "scan_ms": sorted(scan_times)[len(scan_times) // 2],
        "build_ms": sorted(build_times)[len(build_times) // 2],
        "lookup_ms": sorted(lookup_times)[len(lookup_times) // 2],
    }


# --------------------------------------------------------------------------
# TODO-6  TODO-7  -- the report and the chart
# --------------------------------------------------------------------------
def format_report(directory: str, names: list[str], term: str,
                  scanned: list[str], found: list[str],
                  terms: int) -> str:
    """Return the deterministic correctness report (no timings in here)."""
    lines = [
        "corpus: " + directory,
        "docs: " + str(len(names)),
        "term: " + term,
        "linear scan: " + str(scanned),
        "dict lookup: " + str(found),
        "same answer: " + str(scanned == found),
        "distinct terms: " + str(terms),
    ]
    return "\n".join(lines)


def format_bench(times: dict[str, float], repeats: int = REPEATS) -> str:
    """Return the measured timing table (numbers vary per machine)."""
    speedup = times["scan_ms"] / times["lookup_ms"]
    return "\n".join([
        "--- benchmark (median of " + str(repeats) + " timed passes) ---",
        "linear scan : " + f'{times["scan_ms"]:.3f} ms per query',
        "build index : " + f'{times["build_ms"]:.3f} ms once',
        "dict lookup : " + f'{times["lookup_ms"] * 1000:.3f} us per query',
        "speedup     : " + f"{speedup:,.0f}x per query",
    ])


def plot_benchmark(times: dict[str, float], out_path: str) -> str:
    """Draw the deliverable chart: per-query cost, scan vs index. Returns out_path."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4.2))
    labels = ["linear scan", "build index (once)", "dict lookup"]
    values = [times["scan_ms"], times["build_ms"], times["lookup_ms"]]
    bars = ax.bar(labels, values, color=["#d62728", "#7f7f7f", "#2ca02c"])
    ax.set_yscale("log")
    ax.set_ylabel("milliseconds (log scale)")
    ax.set_title("The index wins: same query, two strategies")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value * 1.3,
                f"{value:.4f} ms", ha="center", fontsize=9, weight="bold")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def main(argv: list[str] | None = None) -> int:
    """Run the full report; `--bench` adds timings and writes benchmark.png."""
    args = list(sys.argv[1:]) if argv is None else list(argv)
    if len(args) < 2:
        print("usage: python search_index.py <directory> <term> [--bench]")
        return 2
    directory = args[0]
    term = args[1]

    names = list_txt_files(directory)
    scanned = scan_for_term(directory, names, term)
    index = build_index(directory, names)
    found = lookup(index, term)
    print(format_report(directory, names, term, scanned, found, len(index)))

    if "--bench" not in args:
        return 0
    times = benchmark(directory, names, index, term)
    print(format_bench(times))
    out = plot_benchmark(times, OUT_PATH)
    print("plot written to: " + out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
