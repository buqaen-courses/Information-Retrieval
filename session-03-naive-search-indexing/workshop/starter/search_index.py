"""Starter: naive scan vs a term->files dict index — 7 TODOs (hints until done).

Two ways to answer one question: "which documents contain the word X?"
  scan_for_term()  the NAIVE way  — open every file, ask every one.  O(corpus)
  build_index()    the INDEXED way — pay once, in a single pass.
     + lookup()     {"python": ["doc-a.txt", "doc-c.txt"]}   O(query)

Usage (from the session folder, with the course venv active):
    python workshop/starter/search_index.py workshop/data/mini_corpus python

The mini corpus is 4 tiny files you can check by hand:
    doc-a.txt   topic: python / "Python functions return values." /
                            "Lists and dictionaries store objects."
    doc-b.txt   topic: football / "The striker scored twice." /
                              "The goalkeeper saved a shot."
    doc-c.txt   topic: python / "Python lists and dictionaries store objects." /
                            "A virtual environment isolates dependencies."
    doc-d.txt   topic: cooking / "Simmer the tomato sauce slowly." /
                             "Chop fresh basil for the pasta."

This file RUNS without crashing: the first unfinished TODO prints a hint and
stops, so you always see how far you got. Work top to bottom; every TODO shows
the exact snippet shape to write. Compare with workshop/solution/ afterwards.
"""

import os
import sys
import time

TODO_COUNT = 7

REPEATS = 5          # timed passes; the MEDIAN one is reported
LOOKUP_BATCH = 1000  # a lookup is too fast to time one at a time -- do 1000
OUT_PATH = os.path.join("workshop", "benchmark.png")   # stays inside this session
PUNCT = ":.,!?;\"'()"


# --------------------------------------------------------------------------
# GIVEN TO YOU -- Session 1 material (open, lower, split, strip). Nothing to do.
# --------------------------------------------------------------------------
def words_of(path):
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


# --------------------------------------------------------------------------
# TODO-1  -- know which files we are searching
# --------------------------------------------------------------------------
def list_txt_files(directory):
    """Return the sorted .txt filenames inside `directory`."""
    # TODO-1: Snippet shape:
    #     names = []
    #     for name in os.listdir(directory):
    #         if name.endswith(".txt"):
    #             names.append(name)
    #     names.sort()
    #     return names
    # (os.listdir(folder) hands back the names of everything in a folder, as
    #  strings. .endswith(".txt") is a yes/no test. names.sort() puts them in
    #  alphabetical order so every run prints the same thing.)
    raise NotImplementedError("TODO-1 not done yet - list the .txt filenames")


# --------------------------------------------------------------------------
# TODO-2  -- the naive scanner: the honest, slow, obvious way
# --------------------------------------------------------------------------
def scan_for_term(directory, names, term):
    """NAIVE SEARCH: open every file and ask every one. Returns the hits."""
    # TODO-2: Snippet shape:
    #     hits = []
    #     for name in names:
    #         path = os.path.join(directory, name)
    #         if term in words_of(path):
    #             hits.append(name)
    #     return hits
    # (os.path.join(folder, name) glues a folder and a filename together with
    #  the right separator. `term in words_of(path)` is the "ask this file" test:
    #  it is True when the term appears as a whole word.)
    raise NotImplementedError("TODO-2 not done yet - open every file, ask every one")


# --------------------------------------------------------------------------
# TODO-3  -- the index: do that asking ONCE, remember the answers
# --------------------------------------------------------------------------
def build_index(directory, names):
    """Build {term: [filenames]} in ONE pass over the corpus."""
    # TODO-3: Snippet shape:
    #     index = {}
    #     for name in names:
    #         path = os.path.join(directory, name)
    #         for word in words_of(path):
    #             if word not in index:
    #                 index[word] = [name]
    #             elif index[word][-1] != name:
    #                 index[word].append(name)
    #     return index
    # (`word not in index` is a yes/no test on the dict's keys. `[-1]` is the
    #  LAST item of the list, and because we finish one file before the next,
    #  the last item is the only one we could have just added twice.)
    raise NotImplementedError("TODO-3 not done yet - build the term -> files dict")


# --------------------------------------------------------------------------
# TODO-4  -- the query: one lookup, done
# --------------------------------------------------------------------------
def lookup(index, term):
    """Answer a query with ONE dict lookup. Unknown term -> empty list."""
    # TODO-4: Snippet shape:
    #     if term in index:
    #         return index[term]
    #     return []
    # (index[term] READS the value behind a key; the `in` test first stops you
    #  getting a KeyError when the word was never seen.)
    raise NotImplementedError("TODO-4 not done yet - return index[term] in one lookup")


# --------------------------------------------------------------------------
# TODO-5  -- measure both strategies honestly
# --------------------------------------------------------------------------
def benchmark(directory, names, index, term, repeats=REPEATS):
    """Return median ms for: a linear scan, an index build, and ONE lookup."""
    # TODO-5: Snippet shape:
    #     scan_times = []
    #     build_times = []
    #     lookup_times = []
    #     for _ in range(repeats):
    #         start = time.perf_counter()
    #         scan_for_term(directory, names, term)
    #         scan_times.append((time.perf_counter() - start) * 1000.0)
    #         start = time.perf_counter()
    #         build_index(directory, names)
    #         build_times.append((time.perf_counter() - start) * 1000.0)
    #         start = time.perf_counter()
    #         for _ in range(LOOKUP_BATCH):
    #             lookup(index, term)
    #         lookup_times.append((time.perf_counter() - start) * 1000.0 / LOOKUP_BATCH)
    #     return {
    #         "scan_ms": sorted(scan_times)[len(scan_times) // 2],
    #         "build_ms": sorted(build_times)[len(build_times) // 2],
    #         "lookup_ms": sorted(lookup_times)[len(lookup_times) // 2],
    #     }
    # (time.perf_counter() is Python's finest stopwatch — seconds as a float.
    #  Subtract the two readings and multiply by 1000.0 for milliseconds.
    #  A single lookup takes ~0.0002 ms, far below what a stopwatch can see, so
    #  we time LOOKUP_BATCH of them and divide. sorted(...)[n // 2] is the MEDIAN
    #  of the passes — the middle value, immune to one unlucky slow run.)
    raise NotImplementedError("TODO-5 not done yet - time the scan, the build and the lookup")


# --------------------------------------------------------------------------
# TODO-6  -- the report you can diff against Expected output
# --------------------------------------------------------------------------
def format_report(directory, names, term, scanned, found, terms):
    """Return the deterministic correctness report as one string."""
    # TODO-6: Snippet shape:
    #     lines = []
    #     lines.append("corpus: " + directory)
    #     lines.append("docs: " + str(len(names)))
    #     lines.append("term: " + term)
    #     lines.append("linear scan: " + str(scanned))
    #     lines.append("dict lookup: " + str(found))
    #     lines.append("same answer: " + str(scanned == found))
    #     lines.append("distinct terms: " + str(terms))
    #     return "\n".join(lines)
    # (str() turns a number or a list into text so you can glue it on with "+".
    #  "\n".join(lines) glues the list back together with one newline per item.)
    raise NotImplementedError("TODO-6 not done yet - build the text report")


# --------------------------------------------------------------------------
# TODO-7  -- the deliverable: a chart that shows the index winning
# --------------------------------------------------------------------------
def plot_benchmark(times, out_path):
    """Draw per-query cost (scan vs index) and save it to out_path."""
    # TODO-7: Snippet shape:
    #     import matplotlib.pyplot as plt
    #     fig, ax = plt.subplots(figsize=(7, 4.2))
    #     labels = ["linear scan", "build index (once)", "dict lookup"]
    #     values = [times["scan_ms"], times["build_ms"], times["lookup_ms"]]
    #     bars = ax.bar(labels, values, color=["#d62728", "#7f7f7f", "#2ca02c"])
    #     ax.set_yscale("log")
    #     ax.set_ylabel("milliseconds (log scale)")
    #     ax.set_title("The index wins: same query, two strategies")
    #     for bar, value in zip(bars, values):
    #         ax.text(bar.get_x() + bar.get_width() / 2, value * 1.3,
    #                 f"{value:.4f} ms", ha="center", fontsize=9, weight="bold")
    #     fig.tight_layout()
    #     fig.savefig(out_path)
    #     plt.close(fig)
    #     return out_path
    # (ax.bar(...) draws the three bars. set_yscale("log") is needed because the
    #  bars differ by five orders of magnitude — without it the green bar would
    #  be a zero-height line. zip() walks two lists side by side.)
    raise NotImplementedError("TODO-7 not done yet - plot the benchmark bars")


# --------------------------------------------------------------------------
# GIVEN TO YOU -- the driver. It just calls your functions in order and
# reports the first TODO that is still missing.
# --------------------------------------------------------------------------
def format_bench(times, repeats=REPEATS):
    """Return the measured timing table (numbers vary from machine to machine)."""
    speedup = times["scan_ms"] / times["lookup_ms"]
    return "\n".join([
        "--- benchmark (median of " + str(repeats) + " timed passes) ---",
        "linear scan : " + f'{times["scan_ms"]:.3f} ms per query',
        "build index : " + f'{times["build_ms"]:.3f} ms once',
        "dict lookup : " + f'{times["lookup_ms"] * 1000:.3f} us per query',
        "speedup     : " + f"{speedup:,.0f}x per query",
    ])


def _hint(exc):
    print(str(exc))
    print("(" + str(TODO_COUNT) + " TODOs total - open starter/search_index.py "
          "and work top to bottom.)")
    return 0


def main(argv=None):
    args = list(sys.argv[1:]) if argv is None else list(argv)
    if len(args) < 2:
        print("usage: python search_index.py <directory> <term> [--bench]")
        return 2
    directory = args[0]
    term = args[1]
    try:
        names = list_txt_files(directory)
        scanned = scan_for_term(directory, names, term)
        index = build_index(directory, names)
        found = lookup(index, term)
        print(format_report(directory, names, term, scanned, found, len(index)))
        if "--bench" not in args:
            return 0
        times = benchmark(directory, names, index, term)
        print(format_bench(times))
        print("plot written to: " + plot_benchmark(times, OUT_PATH))
    except NotImplementedError as exc:
        return _hint(exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
