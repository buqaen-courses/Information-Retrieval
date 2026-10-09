"""Starter: evaluation metrics — 5 TODOs.

Runs without crashing: unfinished TODOs print a friendly hint. Work top to
bottom.

Usage (from session-10-evaluation/):
    python workshop/starter/metrics.py
    python workshop/starter/metrics.py --demo

The worked example you will score, from the module docstring:

    ranked list : d4 d2 d1 d9 d7 d3 d8 d5 d6 d10
    relevant    : d1 d3 d5 d7 d9        (R = 5)
    the relevant documents sit at ranks 3, 4, 5, 6, 8
"""
from __future__ import annotations

TODO_COUNT = 5

RANKED = ["d4", "d2", "d1", "d9", "d7", "d3", "d8", "d5", "d6", "d10"]
RELEVANT = ["d1", "d3", "d5", "d7", "d9"]
JUDGED = {"d1": 2, "d3": 1, "d5": 2, "d7": 1, "d9": 2, "d4": 0, "d8": 0}


def precision_at_k(ranked, relevant, k):
    """Fraction of the top k that are relevant. (TODO-1)"""
    # TODO-1: Snippet shape:
    #     if k <= 0:
    #         return 0.0
    #     rel = set(relevant)
    #     top = list(ranked)[:k]
    #     if not top:
    #         return 0.0
    #     hits = 0
    #     for doc_id in top:
    #         if doc_id in rel:
    #             hits = hits + 1
    #     return hits / len(top)
    # (Turning `relevant` into a set first is what makes the membership test
    #  fast — and it is the same set-intersection idea as Session 6.)
    raise NotImplementedError("TODO-1 not done yet — precision_at_k")


def recall_at_k(ranked, relevant, k):
    """Fraction of all relevant documents found in the top k. (TODO-2)"""
    # TODO-2: Snippet shape:
    #     rel = set(relevant)
    #     if not rel:
    #         return 0.0
    #     top = list(ranked)[:k]
    #     hits = 0
    #     for doc_id in top:
    #         if doc_id in rel:
    #             hits = hits + 1
    #     return hits / len(rel)
    # (Note the difference from TODO-1: the denominator is len(rel), NOT
    #  len(top). That single change is what makes recall reward deep lists.)
    raise NotImplementedError("TODO-2 not done yet — recall_at_k")


def reciprocal_rank(ranked, relevant):
    """1 / position of the first relevant hit, else 0.0. (TODO-3)"""
    # TODO-3: Snippet shape:
    #     rel = set(relevant)
    #     position = 0
    #     for i, doc_id in enumerate(ranked):
    #         if doc_id in rel:
    #             position = i + 1
    #             break
    #     if position == 0:
    #         return 0.0
    #     return 1.0 / position
    # (enumerate(..., start) gives you 1-based positions, which is what a
    #  reader counts on a screen. Remember `break` — only the FIRST hit counts.)
    raise NotImplementedError("TODO-3 not done yet — reciprocal_rank")


def average_precision(ranked, relevant):
    """Mean precision at each relevant hit. (TODO-4)"""
    # TODO-4: Snippet shape:
    #     rel = set(relevant)
    #     if not rel:
    #         return 0.0
    #     hits = 0
    #     total = 0.0
    #     for position, doc_id in enumerate(ranked, start=1):
    #         if doc_id in rel:
    #             hits = hits + 1
    #             total = total + hits / position
    #     return total / len(rel)
    # (`hits / position` is the precision AT THAT MOMENT. You add it only on
    #  relevant documents — that is what separates AP from plain P@k.)
    raise NotImplementedError("TODO-4 not done yet — average_precision")


def ndcg_at_k(ranked, judged, k):
    """Normalized discounted cumulative gain. (TODO-5)"""
    # TODO-5: DCG then divide by the ideal DCG. Snippet shape:
    #     import math
    #     if not judged:
    #         return 0.0
    #     dcg = 0.0
    #     position = 0
    #     for doc_id in ranked:
    #         position = position + 1
    #         if position > k:
    #             break
    #         gain = 2 ** judged.get(doc_id, 0) - 1
    #         dcg = dcg + gain / math.log2(position + 1)
    #     ideal_gains = []
    #     for rel in sorted(judged.values(), reverse=True):
    #         ideal_gains.append(2 ** rel - 1)
    #     idcg = 0.0
    #     for i, gain in enumerate(ideal_gains, start=1):
    #         if i > k:
    #             break
    #         idcg = idcg + gain / math.log2(i + 1)
    #     if idcg == 0:
    #         return 0.0
    #     return dcg / idcg
    # (The `2 ** rel - 1` gain is what makes grade 2 worth much more than
    #  grade 1; the / log2(position + 1) discount is what makes rank 1 worth
    #  far more than rank 9. Divide by idcg so different queries are comparable.)
    raise NotImplementedError("TODO-5 not done yet — ndcg_at_k")


def main():
    import sys
    try:
        p = precision_at_k(RANKED, RELEVANT, 10)
        r = recall_at_k(RANKED, RELEVANT, 10)
        rr = reciprocal_rank(RANKED, RELEVANT)
        ap = average_precision(RANKED, RELEVANT)
        nd = ndcg_at_k(RANKED, JUDGED, 10)
    except NotImplementedError as exc:
        print(exc)
        print(f"({TODO_COUNT} TODOs total — work top to bottom.)")
        return 0
    print("ranked:", RANKED)
    print("relevant:", RELEVANT)
    print()
    print(f"P@10        = {p:.4f}")
    print(f"R@10        = {r:.4f}")
    print(f"MRR         = {rr:.4f}")
    print(f"MAP         = {ap:.4f}")
    print(f"NDCG@10     = {nd:.4f}")
    return 0


if __name__ == "__main__":
    main()
