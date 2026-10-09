"""Tests for metrics.py — the Session 10 deliverable.

Every expected value here is hand-checked on a 10-document example whose
relevant documents land at ranks 3, 4, 5, 6 and 8.

Run: python -m pytest workshop/solution/ -v
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import (RANKED, RELEVANT, JUDGED, average_precision, dcg_at_k,  # noqa: E402
                     evaluate_run, f1, f1_at_k, mean, ndcg_at_k, precision_at_k,
                     r_precision, recall_at_k, reciprocal_rank)

K = 10


# ---- precision / recall ----------------------------------------------------

def test_precision_at_k() -> None:
    # 5 relevant among the 10 returned
    assert precision_at_k(RANKED, RELEVANT, K) == 0.5
    # top 2 = d4, d2 — both irrelevant
    assert precision_at_k(RANKED, RELEVANT, 2) == 0.0
    # top 4 = d4, d2, d1, d9 — two relevant
    assert precision_at_k(RANKED, RELEVANT, 4) == 0.5


def test_recall_at_k() -> None:
    # every relevant document is somewhere in the list
    assert recall_at_k(RANKED, RELEVANT, K) == 1.0
    # only 2 of 5 relevant fit in the top 4
    assert recall_at_k(RANKED, RELEVANT, 4) == 0.4


def test_precision_and_recall_trade_off() -> None:
    """The whole point of F1: deep lists raise recall and wreck precision."""
    p, r = precision_at_k(RANKED, RELEVANT, 10), recall_at_k(RANKED, RELEVANT, 10)
    assert f1(p, r) == 2 * p * r / (p + r)
    assert f1_at_k(RANKED, RELEVANT, 10) == f1(p, r)
    assert f1(0.0, 0.0) == 0.0


def test_r_precision_cuts_at_R() -> None:
    # R = 5; top 5 = [d4, d2, d1, d9, d7] of which d1, d9, d7 are relevant
    assert r_precision(RANKED, RELEVANT) == 0.6


# ---- rank-aware ------------------------------------------------------------

def test_reciprocal_rank_uses_the_FIRST_hit() -> None:
    # d1 is the first relevant document, at position 3
    assert reciprocal_rank(RANKED, RELEVANT) == 1 / 3
    assert reciprocal_rank(["x", "d1", "d3"], RELEVANT) == 0.5
    assert reciprocal_rank(["a", "b"], RELEVANT) == 0.0


def test_average_precision_hand_computed() -> None:
    """AP = mean of precision at each relevant hit.

    hits land at ranks 3, 4, 5, 6, 8 -> precisions 1/3, 2/4, 3/5, 4/6, 5/8
    AP = (1/3 + 2/4 + 3/5 + 4/6 + 5/8) / 5
    """
    expected = (1 / 3 + 2 / 4 + 3 / 5 + 4 / 6 + 5 / 8) / 5
    assert average_precision(RANKED, RELEVANT) == expected
    assert average_precision(["a", "b"], RELEVANT) == 0.0


def test_perfect_run_scores_one() -> None:
    perfect = ["d1", "d3", "d5", "d7", "d9", "d4", "d8", "d2", "d6", "d10"]
    assert average_precision(perfect, RELEVANT) == 1.0
    assert reciprocal_rank(perfect, RELEVANT) == 1.0
    assert r_precision(perfect, RELEVANT) == 1.0
    assert recall_at_k(perfect, RELEVANT, K) == 1.0
    # precision is NOT 1.0 here — there are only 5 relevant documents in a
    # 10-long list. That is why P@k and R-precision disagree on the example.
    assert precision_at_k(perfect, RELEVANT, K) == 0.5


# ---- NDCG ------------------------------------------------------------------

def test_ndcg_perfect_is_one() -> None:
    # best grades first: the three grade-2 docs, then the two grade-1 docs
    perfect = ["d1", "d5", "d9", "d3", "d7", "d4", "d8", "d2", "d6", "d10"]
    assert ndcg_at_k(perfect, JUDGED, K) == 1.0


def test_ndcg_hand_computed() -> None:
    """DCG with gain = 2^rel - 1, discount = log2(rank+1)."""
    gains = [2 ** JUDGED.get(d, 0) - 1 for d in RANKED]
    expected_dcg = dcg_at_k(gains, K)
    ideal = sorted((2 ** g - 1 for g in JUDGED.values() if g > 0), reverse=True)
    expected = expected_dcg / dcg_at_k(ideal, K)
    assert ndcg_at_k(RANKED, JUDGED, K) == expected
    assert 0.6 < ndcg_at_k(RANKED, JUDGED, K) < 0.7


def test_ndcg_is_bounded() -> None:
    assert 0.0 <= ndcg_at_k(RANKED, JUDGED, K) <= 1.0
    assert ndcg_at_k(RANKED, {}, K) == 0.0


def test_ndcg_prefers_high_grade_first() -> None:
    """Swapping a grade-2 and a grade-1 document must change the score."""
    a = ndcg_at_k(["d1", "d3"], JUDGED, K)   # grade 2 then grade 1
    b = ndcg_at_k(["d3", "d1"], JUDGED, K)   # grade 1 then grade 2
    assert a > b


def test_discount_curve() -> None:
    """The first position contributes most; the curve flattens fast."""
    assert dcg_at_k([1.0], 1) == 1.0
    assert dcg_at_k([0.0, 1.0], 2) < dcg_at_k([1.0, 0.0], 2)


# ---- averaging over queries ------------------------------------------------

def test_mean() -> None:
    assert mean([1.0, 0.0, 0.5]) == 0.5
    assert mean([]) == 0.0


def test_evaluate_run_returns_one_row() -> None:
    run = {"q1": RANKED, "q2": RANKED[::-1]}
    qrels = {"q1": JUDGED, "q2": JUDGED}
    row = evaluate_run(run, qrels, k=K)
    assert set(row) == {"P@10", "R@10", "R-precision", "MRR", "MAP", "NDCG@10"}
    for value in row.values():
        assert 0.0 <= value <= 1.0


def test_evaluate_run_skips_unjudged_queries() -> None:
    run = {"q1": RANKED, "qX": ["a", "b"]}
    row = evaluate_run(run, {"q1": JUDGED}, k=K)
    # only q1 counted, so MRR is the single value, not an average with junk
    assert abs(row["MRR"] - 1 / 3) < 1e-9


def test_evaluate_run_on_perfect_run() -> None:
    perfect = ["d1", "d5", "d9", "d3", "d7", "d4", "d8", "d2", "d6", "d10"]
    row = evaluate_run({"q1": perfect}, {"q1": JUDGED}, k=K)
    assert row["MRR"] == 1.0
    assert row["MAP"] == 1.0
    assert row["NDCG@10"] == 1.0
