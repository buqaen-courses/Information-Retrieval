"""Tests for solution/search_index.py.

Expected values are hand-computed from the 4 tiny files in
workshop/data/mini_corpus/ so you can check them by eye:

    doc-a.txt  topic: python | Python functions return values.
                            | Lists and dictionaries store objects.
    doc-b.txt  topic: football | The striker scored twice.
                              | The goalkeeper saved a shot.
    doc-c.txt  topic: python | Python lists and dictionaries store objects.
                            | A virtual environment isolates dependencies.
    doc-d.txt  topic: cooking | Simmer the tomato sauce slowly.
                             | Chop fresh basil for the pasta.
"""
import os

from search_index import (benchmark, build_index, format_bench, format_report,
                          list_txt_files, lookup, plot_benchmark, scan_for_term,
                          words_of)

HERE = os.path.dirname(os.path.abspath(__file__))
MINI = os.path.normpath(os.path.join(HERE, os.pardir, "data", "mini_corpus"))
CORPUS = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir, os.pardir,
                                       "datasets", "corpus"))


def test_list_txt_files_is_sorted_and_txt_only():
    # 4 .txt files, alphabetically: a, b, c, d
    assert list_txt_files(MINI) == ["doc-a.txt", "doc-b.txt", "doc-c.txt",
                                    "doc-d.txt"]


def test_words_of_strips_case_and_punctuation(tmp_path):
    f = tmp_path / "tiny.txt"
    f.write_text("Topic: Python.\nPython, python!\n", encoding="utf-8")
    # "Topic:" -> "topic", "Python." -> "python", "Python," -> "python",
    # "python!" -> "python"  => 4 words, no punctuation left
    assert words_of(str(f)) == ["topic", "python", "python", "python"]


def test_scan_for_term_hand_checked():
    names = list_txt_files(MINI)
    # "python" appears in doc-a (topic line) and doc-c (topic line + body)
    assert scan_for_term(MINI, names, "python") == ["doc-a.txt", "doc-c.txt"]
    # "shot" appears only in doc-b
    assert scan_for_term(MINI, names, "shot") == ["doc-b.txt"]
    # a word nobody wrote
    assert scan_for_term(MINI, names, "dough") == []


def test_build_index_hand_checked():
    index = build_index(MINI, list_txt_files(MINI))
    assert index["python"] == ["doc-a.txt", "doc-c.txt"]
    assert index["shot"] == ["doc-b.txt"]
    assert index["basil"] == ["doc-d.txt"]
    # a file listed ONCE per term even when the term repeats inside it:
    # "the" appears 3 times in doc-b and 3 times in doc-d
    assert index["the"] == ["doc-b.txt", "doc-d.txt"]
    # hand-counted distinct words across the 4 files: 10 + 8 + 5 + 10
    assert len(index) == 33


def test_build_index_never_repeats_a_file():
    index = build_index(MINI, list_txt_files(MINI))
    for term, names in index.items():
        assert len(names) == len(set(names)), term


def test_lookup_unknown_term_returns_empty_list():
    index = build_index(MINI, list_txt_files(MINI))
    assert lookup(index, "carousel") == []
    assert lookup(index, "python") == ["doc-a.txt", "doc-c.txt"]


def test_scan_and_index_agree_on_the_real_corpus():
    """The whole point of the session: both strategies must answer alike."""
    names = list_txt_files(CORPUS)
    assert len(names) == 204
    index = build_index(CORPUS, names)
    for term in ["rovers", "basil", "tomato", "python", "football", "carousel"]:
        assert scan_for_term(CORPUS, names, term) == lookup(index, term), term
    # hand-checkable counts on the real corpus (34 docs per topic)
    assert len(lookup(index, "python")) == 34
    assert len(lookup(index, "rovers")) == 14
    assert len(lookup(index, "carousel")) == 0
    assert len(index) == 221


def test_benchmark_reports_three_positive_numbers():
    names = list_txt_files(MINI)
    index = build_index(MINI, names)
    times = benchmark(MINI, names, index, "python", repeats=3)
    for key in ["scan_ms", "build_ms", "lookup_ms"]:
        assert times[key] > 0.0
    # the index must beat brute force by orders of magnitude, not a hair
    assert times["scan_ms"] > times["lookup_ms"] * 100


def test_format_report_is_deterministic():
    names = list_txt_files(MINI)
    scanned = scan_for_term(MINI, names, "python")
    found = lookup(build_index(MINI, names), "python")
    assert format_report(MINI, names, "python", scanned, found, 33) == (
        "corpus: " + MINI + "\n"
        "docs: 4\n"
        "term: python\n"
        "linear scan: ['doc-a.txt', 'doc-c.txt']\n"
        "dict lookup: ['doc-a.txt', 'doc-c.txt']\n"
        "same answer: True\n"
        "distinct terms: 33"
    )


def test_format_bench_has_a_speedup_line():
    text = format_bench({"scan_ms": 30.0, "build_ms": 31.0, "lookup_ms": 0.0002})
    assert "median of 5 timed passes" in text
    assert "30.000 ms per query" in text
    assert text.strip().endswith("150,000x per query")


def test_plot_benchmark_writes_a_png(tmp_path):
    out = str(tmp_path / "chart.png")
    got = plot_benchmark({"scan_ms": 30.0, "build_ms": 31.0,
                          "lookup_ms": 0.0002}, out)
    assert got == out
    assert os.path.getsize(out) > 1000
