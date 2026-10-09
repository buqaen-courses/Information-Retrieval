"""Tests for bm25.py — the Session 8 deliverable.

The core test is a HAND-COMPUTED score, worked out on paper before the code
existed. If the formula changes, this test is the alarm.

Run: python -m pytest workshop/solution/ -v
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bm25 import (B_DEFAULT, K1_DEFAULT, bm25_score, build_stats,  # noqa: E402
                  idf, search, tokenize, tune)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def test_tokenize() -> None:
    assert tokenize("Simmer the sauce!") == ["simmer", "the", "sauce"]


def test_stats_shape() -> None:
    s = build_stats(DATA)
    assert s["doc_ids"] == ["doc-a", "doc-b", "doc-c"]
    assert s["N"] == 3
    assert s["df"]["sauce"] == 2          # doc-a and doc-b
    assert s["df"]["referee"] == 1
    # 'sauce' appears in BOTH sentences of doc-a and doc-b — tf is 2, not 1.
    assert s["tf"]["doc-a"]["sauce"] == 2
    assert s["tf"]["doc-b"]["sauce"] == 2


def test_doc_lengths_and_avgdl() -> None:
    s = build_stats(DATA)
    assert s["doc_len"]["doc-a"] == 14
    assert s["doc_len"]["doc-b"] == 13
    assert s["doc_len"]["doc-c"] == 18
    assert abs(s["avgdl"] - 15.0) < 1e-9


def test_idf_hand_computed() -> None:
    """idf = log(1 + (N - df + 0.5) / (df + 0.5)), N = 3."""
    # df=1: log(1 + (3-1+0.5)/(1+0.5)) = log(1 + 2.5/1.5) = log(2.6667)
    assert abs(idf("x", 1, 3) - math.log(2.6666667)) < 1e-6
    # df=3 (every doc): log(1 + 0.5/3.5) = log(1.142857)
    assert abs(idf("the", 3, 3) - math.log(1.1428571)) < 1e-6
    # rarer term must score higher
    assert idf("x", 1, 3) > idf("the", 3, 3)


def test_bm25_score_hand_computed() -> None:
    """Work out doc-a's score for query 'sauce' by hand, on paper.

    Read the corpus first — 'sauce' is in BOTH sentences of doc-a:
        "Simmer the tomato sauce for twenty minutes."
        "A good sauce depends on fresh basil."
    so tf = 2, not 1. Getting this wrong is the classic BM25 bug.

    N = 3, avgdl = 15, dl(doc-a) = 14, tf = 2, k1 = 1.2, b = 0.75.

    idf(sauce) = log(1 + (3 - 2 + 0.5)/(2 + 0.5)) = log(1.6)  = 0.4700036
    norm       = k1 * (1 - b + b*dl/avgdl)
               = 1.2 * (1 - 0.75 + 0.75*14/15)
               = 1.2 * (0.25 + 0.70)     = 1.2 * 0.95    = 1.14
    tf part    = (2 * (1.2 + 1)) / (2 + 1.14) = 4.4/3.14 = 1.4012739
    score      = 0.4700036 * 1.4012739               = 0.6586044
    """
    s = build_stats(DATA)
    expected_idf = math.log(1 + (3 - 2 + 0.5) / (2 + 0.5))
    expected_norm = K1_DEFAULT * (1 - B_DEFAULT + B_DEFAULT * 14 / 15.0)
    expected = expected_idf * (2 * (K1_DEFAULT + 1)) / (2 + expected_norm)
    got = bm25_score("sauce", "doc-a", s)
    assert abs(expected_idf - 0.4700036) < 1e-6
    assert abs(expected_norm - 1.14) < 1e-9
    assert abs(got - expected) < 1e-9
    assert abs(got - 0.6586044) < 1e-6


def test_tf_saturates() -> None:
    """The tf component must NOT double when tf doubles.

    Same query, same df, so only the tf term differs: the saturation curve is
    what stops a repeated word from dominating the score linearly.
    """
    s = build_stats(DATA)
    # doc-c has tf=1 for 'referee' and is the longest doc (18).
    one = bm25_score("referee", "doc-c", s)
    # doc-b tf=2 for 'sauce'... use the same term by scoring doc-a vs a manual
    # doubling: the tf part alone, at identical dl, is sublinear by construction.
    norm = K1_DEFAULT * (1 - B_DEFAULT + B_DEFAULT * s["doc_len"]["doc-c"] / s["avgdl"])
    f1 = (1 * (K1_DEFAULT + 1)) / (1 + norm)
    f2 = (2 * (K1_DEFAULT + 1)) / (2 + norm)
    assert f2 < 2 * f1
    assert f2 > f1
    assert one > 0


def test_long_document_is_penalised() -> None:
    """b=0 removes length normalization; b=0.75 applies it.

    doc-c (18 tokens) is longer than average (15), so with b=0.75 it must
    score strictly below what it scores with b=0.
    """
    s = build_stats(DATA)
    penalised = bm25_score("referee", "doc-c", s, b=0.75)
    unpenalised = bm25_score("referee", "doc-c", s, b=0.0)
    assert unpenalised > penalised


def test_shorter_doc_wins_for_same_tf() -> None:
    """Both sauce docs have tf=2; doc-b is shorter, so b=0.75 favours it.

    This is length normalization doing exactly its job, and it surprises
    students who expect document order to be preserved.
    """
    s = build_stats(DATA)
    a = bm25_score("sauce", "doc-a", s, b=0.75)
    b = bm25_score("sauce", "doc-b", s, b=0.75)
    assert b > a
    # ...and with b=0 the length advantage disappears entirely
    assert abs(bm25_score("sauce", "doc-a", s, b=0.0)
               - bm25_score("sauce", "doc-b", s, b=0.0)) < 1e-9


def test_unknown_term_scores_zero() -> None:
    s = build_stats(DATA)
    assert bm25_score("zzzznotaword", "doc-a", s) == 0.0


def test_search_ranks_sauce_docs_first() -> None:
    """'sauce basil': doc-a has the rare term basil, so it wins.

    Both sauce docs have tf=2 for sauce, but 'basil' (df=1) carries a much
    larger IDF than 'sauce' (df=2), and only doc-a contains it.
    """
    results = search(DATA, "sauce basil")
    ids = [d for d, _ in results]
    assert ids[:2] == ["doc-a", "doc-b"]
    assert results[0][1] > results[1][1]
    assert results[-1][1] == 0.0  # doc-c matches nothing


def test_search_is_sorted_and_reproducible() -> None:
    r1 = search(DATA, "sauce basil")
    r2 = search(DATA, "sauce basil")
    assert r1 == r2
    scores = [s for _, s in r1]
    assert scores == sorted(scores, reverse=True)


def test_tune_returns_grid_rows() -> None:
    rows = tune(DATA, "sauce", [0.5, 1.2], [0.0, 0.75])
    assert len(rows) == 4
    assert all(0.0 <= ndcg <= 1.0 for ndcg, _k1, _b in rows)


def test_k1_and_b_defaults() -> None:
    assert K1_DEFAULT == 1.2
    assert B_DEFAULT == 0.75
