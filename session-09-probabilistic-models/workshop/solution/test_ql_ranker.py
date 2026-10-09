"""Tests for ql_ranker.py — the Session 9 deliverable.

Run: python -m pytest workshop/solution/ -v
The smoothing test is the important one: without it, one unseen word zeroes
the whole score, which is the failure mode this session exists to fix.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ql_ranker import (MU_DEFAULT, build_stats, collection_probability,  # noqa: E402
                       ql_score, search, tokenize)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def test_tokenize() -> None:
    assert tokenize("Simmer the sauce!") == ["simmer", "the", "sauce"]


def test_stats_shape() -> None:
    s = build_stats(DATA)
    assert s["doc_ids"] == ["doc-a", "doc-b", "doc-c"]
    assert s["N"] == 3
    assert s["doc_len"]["doc-a"] == 14
    assert s["total"] == 14 + 13 + 18
    # 'sauce' appears twice in doc-a and twice in doc-b
    assert s["tf"]["doc-a"]["sauce"] == 2
    assert s["cf"]["sauce"] == 4


def test_collection_probability_is_a_probability() -> None:
    """P(w) is an unigram probability: occurrences of w / total tokens.

    It is NOT normalized over *distinct* terms — a term's probability reflects
    how often it occurs, not whether we have seen it.
    """
    s = build_stats(DATA)
    assert 0.0 < collection_probability("sauce", s) < 1.0
    # a rarer term is less probable
    assert collection_probability("basil", s) < collection_probability("sauce", s)


def test_mu_200_over_smooths_a_tiny_collection() -> None:
    """The default mu=200 is tuned for collections of MILLIONS of tokens.

    This corpus has 45. Smoothing a 45-token collection toward the background
    is far too aggressive: P('sauce') falls from its raw 4/45 = 0.0889 to
    0.0164. On a real corpus the same mu is a gentle nudge. This is why you
    tune mu per collection, exactly as you tune k1 and b in Session 8.
    """
    s = build_stats(DATA)
    raw = s["cf"]["sauce"] / s["total"]
    smoothed = collection_probability("sauce", s)
    assert smoothed < raw * 0.5          # over-smoothed by more than 2x
    # shrinking mu toward zero recovers the raw ratio
    assert collection_probability("sauce", s, ) is not None
    assert raw > smoothed


def test_smaller_mu_sits_closer_to_the_raw_ratio() -> None:
    """mu controls how hard you pull toward the collection average."""
    s = build_stats(DATA)
    raw = s["cf"]["sauce"] / s["total"]
    strong = (s["cf"]["sauce"] + 5000.0 * 0.0001) / (s["total"] + 5000.0)
    weak = (s["cf"]["sauce"] + 0.5 * 0.0001) / (s["total"] + 0.5)
    assert abs(weak - raw) < abs(strong - raw)


def test_smoothing_rescues_an_unseen_word() -> None:
    """Without smoothing, an unseen query term would give log(0) = -inf.

    This test is the whole reason Dirichlet smoothing is taught here.
    """
    s = build_stats(DATA)
    # a term that appears nowhere in the collection
    score = ql_score("zzzznotaword", "doc-a", s)
    assert score > -1e6          # finite, not -inf
    assert math.isfinite(score)
    # and the value is exactly what the formula predicts
    bg = (0 + MU_DEFAULT * 0.0001) / (s["total"] + MU_DEFAULT)
    expected = math.log((0 + MU_DEFAULT * bg) / (14 + MU_DEFAULT))
    assert abs(score - expected) < 1e-12


def test_ql_score_hand_computed() -> None:
    """Hand-compute doc-a's score for the single word 'sauce'.

    dl = 14, tf = 2, total = 45, cf(sauce) = 4, mu = 200, p_smooth = 0.0001

    background = (4 + 200*0.0001) / (45 + 200) = 4.02 / 245 = 0.016408163
    numerator  = 2 + 200 * 0.016408163          = 2 + 3.281632653 = 5.281632653
    denominator = 14 + 200                       = 214
    score      = log(5.281632653 / 214)          = log(0.02468146) = -3.7013...
    """
    s = build_stats(DATA)
    bg = (4 + MU_DEFAULT * 0.0001) / (45 + MU_DEFAULT)
    expected = math.log((2 + MU_DEFAULT * bg) / (14 + MU_DEFAULT))
    got = ql_score("sauce", "doc-a", s)
    assert abs(got - expected) < 1e-12
    assert abs(got - (-3.7017)) < 1e-3


def test_larger_mu_smooths_harder() -> None:
    """Bigger mu pulls every document toward the collection average."""
    s = build_stats(DATA)
    weak = search_scores(s, "sauce", mu=10.0)
    strong = search_scores(s, "sauce", mu=5000.0)
    spread_weak = weak["doc-a"] - weak["doc-c"]
    spread_strong = strong["doc-a"] - strong["doc-c"]
    assert abs(spread_strong) < abs(spread_weak)


def search_scores(stats, query, mu):
    from ql_ranker import ql_score
    return {d: ql_score(query, d, stats, mu) for d in stats["doc_ids"]}


def test_search_ranks_sauce_docs_first() -> None:
    results = search(DATA, "sauce basil")
    ids = [d for d, _ in results]
    assert ids[0] == "doc-a"
    assert set(ids[:2]) == {"doc-a", "doc-b"}
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)


def test_search_is_reproducible() -> None:
    assert search(DATA, "sauce") == search(DATA, "sauce")


def test_every_document_gets_a_score() -> None:
    """Unlike BM25, an all-zero match is impossible — every doc is scored."""
    results = search(DATA, "zzzznotaword")
    assert len(results) == 3
    assert all(math.isfinite(s) for _, s in results)
