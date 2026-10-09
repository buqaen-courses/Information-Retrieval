"""Evaluation metrics — the single source of truth for Sessions 16, 22 and 23.

Implements, from scratch and from first principles:
    precision@k, recall@k, F1, R-precision, MRR, MAP, NDCG@k

Everything here is pure stdlib. Copy this file into later workshops rather than
reimplementing it — one implementation, one definition, no drift.

Usage:
    python metrics.py                      # self-test on a hand-checked example
    python metrics.py --demo               # print a worked example per metric
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


# --------------------------------------------------------------------------- #
# Core set measures
# --------------------------------------------------------------------------- #
def precision_at_k(ranked: Sequence[str], relevant: Iterable[str], k: int) -> float:
    """Fraction of the top k results that are relevant.

    "Of the things you showed me, how many did I want?" Rewards precision at
    the top of the list, which is the only place a user looks.
    """
    if k <= 0:
        return 0.0
    rel = set(relevant)
    top = list(ranked)[:k]
    if not top:
        return 0.0
    hits = sum(1 for doc_id in top if doc_id in rel)
    return hits / len(top)


def recall_at_k(ranked: Sequence[str], relevant: Iterable[str], k: int) -> float:
    """Fraction of all relevant documents that appear in the top k.

    "Of everything I wanted, how much did you find?" Rewards coverage, so it
    rewards deep lists — which is why it is never reported alone.
    """
    rel = set(relevant)
    if not rel:
        return 0.0
    top = list(ranked)[:k]
    hits = sum(1 for doc_id in top if doc_id in rel)
    return hits / len(rel)


def f1(precision: float, recall: float) -> float:
    """Harmonic mean of precision and recall — punishes being lopsided."""
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def f1_at_k(ranked: Sequence[str], relevant: Iterable[str], k: int) -> float:
    """F1 of the top k: the harmonic mean of precision@k and recall@k."""
    return f1(precision_at_k(ranked, relevant, k), recall_at_k(ranked, relevant, k))


def r_precision(ranked: Sequence[str], relevant: Iterable[str]) -> float:
    """Precision at R, where R is the number of relevant documents.

    The cleverest cheap metric here: cut the list exactly where the user would
    have run out of relevant items, and ask what fraction of that cut was good.
    Needs no k and no tuning.
    """
    rel = set(relevant)
    if not rel:
        return 0.0
    r = len(rel)
    return precision_at_k(ranked, rel, r)


# --------------------------------------------------------------------------- #
# Rank-aware measures
# --------------------------------------------------------------------------- #
def reciprocal_rank(ranked: Sequence[str], relevant: Iterable[str]) -> float:
    """1 / position of the first relevant hit; 0.0 when there is none.

    Models a user who wants ONE good answer and clicks the first thing useful.
    """
    rel = set(relevant)
    for position, doc_id in enumerate(ranked, start=1):
        if doc_id in rel:
            return 1.0 / position
    return 0.0


def average_precision(ranked: Sequence[str], relevant: Iterable[str]) -> float:
    """Mean of the precision values at each relevant hit, up to the last hit.

    precision@k style averaging that only counts the moments you did something
    right, so a relevant document at rank 1 is worth far more than one at rank
    50. Reaches 1.0 only when every relevant document precedes every wrong one.
    """
    rel = set(relevant)
    if not rel:
        return 0.0
    hits = 0
    total = 0.0
    for position, doc_id in enumerate(ranked, start=1):
        if doc_id in rel:
            hits += 1
            total += hits / position
    return total / len(rel)


def dcg_at_k(gains: Sequence[float], k: int) -> float:
    """Discounted cumulative gain: gains discounted by log2(rank + 1)."""
    return sum(g / math.log2(position + 1)
               for position, g in enumerate(gains[:k], start=1))


def ndcg_at_k(ranked: Sequence[str], judged: dict[str, int], k: int) -> float:
    """Normalized DCG with graded relevance. 1.0 = perfect ordering.

    Two improvements over MAP, both needed for graded judgments:
      * gain is 2^rel - 1, so a highly relevant document outranks a merely
        relevant one by more than one unit;
      * position is discounted by log2, so the drop from rank 1 to 2 hurts more
        than the drop from rank 20 to 21.
    Dividing by the ideal DCG makes scores comparable across queries with
    different numbers of relevant documents.
    """
    if not judged:
        return 0.0
    dcg = dcg_at_k([2 ** judged.get(d, 0) - 1 for d in ranked], k)
    ideal = sorted((2 ** rel - 1 for rel in judged.values()), reverse=True)
    idcg = dcg_at_k(ideal, k)
    return dcg / idcg if idcg else 0.0


# --------------------------------------------------------------------------- #
# Averaging across a query set
# --------------------------------------------------------------------------- #
def mean(values: Iterable[float]) -> float:
    """Arithmetic mean; 0.0 for an empty sequence."""
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def evaluate_run(run: dict[str, list[str]], qrels: dict[str, dict[str, int]],
                 k: int = 10) -> dict[str, float]:
    """Score one ranked run against graded judgments.

    `run` maps query id -> ranked doc ids. `qrels` maps query id ->
    {doc id: relevance grade}; grade > 0 counts as relevant.

    Returns the mean of every metric across the queries judged in both — this
    is the row you put in a report.
    """
    p_at_k, r_at_k, mrr, ap, ndcg, r_prec = [], [], [], [], [], []
    for qid, ranked in run.items():
        judged = qrels.get(qid)
        if judged is None:
            continue
        rel = [d for d, g in judged.items() if g > 0]
        if not rel:
            continue
        p_at_k.append(precision_at_k(ranked, rel, k))
        r_at_k.append(recall_at_k(ranked, rel, k))
        mrr.append(reciprocal_rank(ranked, rel))
        ap.append(average_precision(ranked, rel))
        ndcg.append(ndcg_at_k(ranked, judged, k))
        r_prec.append(r_precision(ranked, rel))
    return {
        f"P@{k}": mean(p_at_k),
        f"R@{k}": mean(r_at_k),
        "R-precision": mean(r_prec),
        "MRR": mean(mrr),
        "MAP": mean(ap),
        f"NDCG@{k}": mean(ndcg),
    }


# --------------------------------------------------------------------------- #
# Demo / self-test
# --------------------------------------------------------------------------- #
EXAMPLE_RANKED = ["d4", "d2", "d1", "d9", "d7", "d3", "d8", "d5", "d6", "d10"]
EXAMPLE_RELEVANT = ["d1", "d3", "d5", "d7", "d9"]   # 5 relevant docs
EXAMPLE_JUDGED = {"d1": 2, "d3": 1, "d5": 2, "d7": 1, "d9": 2, "d4": 0, "d8": 0}

# Short aliases, imported by the tests and the workshop.
RANKED = EXAMPLE_RANKED
RELEVANT = EXAMPLE_RELEVANT
JUDGED = EXAMPLE_JUDGED


def demo() -> None:
    """Print every metric on one worked example, with the arithmetic shown."""
    ranked, rel, judged = EXAMPLE_RANKED, EXAMPLE_RELEVANT, EXAMPLE_JUDGED
    k = 10
    print("ranked list   :", ranked)
    print("relevant      :", rel, f"({len(rel)} docs, R = {len(rel)})")
    print("graded judged :", judged)
    print()
    print("where the relevant documents actually landed:")
    for d in rel:
        print(f"  {d} -> rank {ranked.index(d) + 1}")
    print()
    print(f"P@{k}          = {precision_at_k(ranked, rel, k):.4f}"
          "   (5 relevant among the top 10)")
    print(f"R@{k}          = {recall_at_k(ranked, rel, k):.4f}"
          "   (all 5 relevant documents appear)")
    print(f"R-precision   = {r_precision(ranked, rel):.4f}"
          f"   (top {len(rel)} = {ranked[:len(rel)]} -> 3 relevant)")
    print(f"MRR           = {reciprocal_rank(ranked, rel):.4f}"
          "   (first hit d1 at rank 3 -> 1/3)")
    print(f"MAP           = {average_precision(ranked, rel):.4f}"
          "   ((1/3 + 2/4 + 3/5 + 4/6 + 5/8) / 5)")
    print(f"NDCG@{k}       = {ndcg_at_k(ranked, judged, k):.4f}")
    print()
    print("a perfect run (relevant first, best-graded first) scores:")
    perfect = ["d1", "d5", "d9", "d3", "d7"] + ["d4", "d8", "d2", "d6", "d10"]
    print(f"  P@{k}={precision_at_k(perfect, rel, k):.4f}"
          f"  R-precision={r_precision(perfect, rel):.4f}"
          f"  MRR={reciprocal_rank(perfect, rel):.4f}"
          f"  MAP={average_precision(perfect, rel):.4f}"
          f"  NDCG@{k}={ndcg_at_k(perfect, judged, k):.4f}")


def _self_test() -> None:
    """Hand-checked assertions; run with no arguments."""
    ranked, rel = EXAMPLE_RANKED, EXAMPLE_RELEVANT
    judged = EXAMPLE_JUDGED
    # relevant docs sit at ranks 3, 4, 5, 6, 8 -> none in the top 2
    assert abs(precision_at_k(ranked, rel, 10) - 0.5) < 1e-9
    assert abs(recall_at_k(ranked, rel, 10) - 1.0) < 1e-9
    # R = 5, top 5 = [d4, d2, d1, d9, d7], of which d1, d9, d7 are relevant
    assert abs(r_precision(ranked, rel) - 0.6) < 1e-9
    assert abs(reciprocal_rank(ranked, rel) - 1 / 3) < 1e-9
    # AP = (1/3 + 2/4 + 3/5 + 4/6 + 5/8) / 5
    expected_ap = (1 / 3 + 2 / 4 + 3 / 5 + 4 / 6 + 5 / 8) / 5
    assert abs(average_precision(ranked, rel) - expected_ap) < 1e-9
    assert abs(ndcg_at_k(ranked, judged, 10) - 0.6215) < 1e-3
    # perfect ordering by grade, then junk
    perfect = ["d1", "d5", "d9", "d3", "d7"] + ["d4", "d8", "d2", "d6", "d10"]
    assert precision_at_k(perfect, rel, 10) == 0.5
    assert abs(recall_at_k(perfect, rel, 10) - 1.0) < 1e-9
    assert abs(r_precision(perfect, rel) - 1.0) < 1e-9
    assert abs(average_precision(perfect, rel) - 1.0) < 1e-9
    assert reciprocal_rank(perfect, rel) == 1.0
    assert ndcg_at_k(perfect, judged, 10) == 1.0
    # a run with no relevant document scores zero everywhere
    assert reciprocal_rank(["a", "b"], rel) == 0.0
    assert average_precision(["a", "b"], rel) == 0.0
    assert ndcg_at_k(["a", "b"], judged, 10) == 0.0
    # k smaller than the list truncates it
    assert precision_at_k(ranked, rel, 2) == 0.0   # d4, d2 are both irrelevant
    assert precision_at_k(ranked, rel, 4) == 0.5   # d1, d9 among 4
    print("metrics self-test: all assertions passed")


def main() -> None:
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        _self_test()


if __name__ == "__main__":
    main()
