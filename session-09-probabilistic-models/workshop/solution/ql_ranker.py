"""Query-likelihood ranking with Dirichlet smoothing.

Usage (from session-09-probabilistic-models/):
    python ql_ranker.py workshop/data "sauce basil"
    python ql_ranker.py ../../datasets/corpus "tomato sauce"

Instead of asking "how well does this document match these words?", a language
model asks a different question:

    P(query | document)

i.e. if this document had generated the text the user typed, how likely is that?
The document whose own language best explains the query ranks first.

Bayes' rule turns that into something computable:

    P(q | d) = P(d | q) * P(q) / P(d)

The denominator P(d) does not depend on the query, so it is the same constant
for every document in this ranking and can be dropped. What remains is a
product of per-word probabilities — and that product is where smoothing earns
its keep, because one unseen word would otherwise make the whole score zero.
"""
from __future__ import annotations

import math
import os
import sys

PUNCTUATION = ".,!?;:'\"()"
MU_DEFAULT = 200.0   # the smoothing strength mu
P_SMOOTH = 0.0001    # background probability for a word seen nowhere


def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into terms."""
    tokens = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word:
            tokens.append(word)
    return tokens


def list_doc_ids(folder: str) -> list[str]:
    """Sorted document ids in folder."""
    return [n[:-4] for n in sorted(os.listdir(folder)) if n.endswith(".txt")]


def build_stats(folder: str) -> dict:
    """One pass: per-doc term counts, collection frequencies, lengths."""
    doc_ids = list_doc_ids(folder)
    tf: dict[str, dict[str, int]] = {}
    doc_len: dict[str, int] = {}
    cf: dict[str, int] = {}
    for doc_id in doc_ids:
        with open(os.path.join(folder, doc_id + ".txt"), mode="r",
                  encoding="utf-8") as f:
            tokens = tokenize(f.read())
        doc_len[doc_id] = len(tokens)
        counts: dict[str, int] = {}
        for term in tokens:
            counts[term] = counts.get(term, 0) + 1
        tf[doc_id] = counts
        for term, count in counts.items():
            cf[term] = cf.get(term, 0) + count
    return {"doc_ids": doc_ids, "tf": tf, "doc_len": doc_len, "cf": cf,
            "total": sum(doc_len.values()), "N": len(doc_ids)}


def collection_probability(term: str, stats: dict, p_smooth: float = P_SMOOTH
                           ) -> float:
    """P(w) in the collection — the background probability smoothing mixes in."""
    return ((stats["cf"].get(term, 0) + MU_DEFAULT * p_smooth)
            / (stats["total"] + MU_DEFAULT))


def ql_score(query: str, doc_id: str, stats: dict, mu: float = MU_DEFAULT,
             p_smooth: float = P_SMOOTH) -> float:
    """Log P(query | document) with Dirichlet smoothing.

    Summing logs instead of multiplying probabilities is just the log-sum-exp
    trick: it keeps the arithmetic in range and the ranking is identical.
    """
    tf = stats["tf"][doc_id]
    dl = stats["doc_len"][doc_id]
    total = stats["total"]
    score = 0.0
    for term in tokenize(query):
        background = ((stats["cf"].get(term, 0) + mu * p_smooth)
                      / (total + mu))
        score += math.log((tf.get(term, 0) + mu * background) / (dl + mu))
    return score


def search(folder: str, query: str, mu: float = MU_DEFAULT,
           top: int = 10) -> list[tuple[str, float]]:
    """Rank by query likelihood, best first, ties broken on doc_id."""
    stats = build_stats(folder)
    scored = [(doc_id, ql_score(query, doc_id, stats, mu))
              for doc_id in stats["doc_ids"]]
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored[:top]


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        print('usage: python ql_ranker.py <folder> "<query>"')
        return 2
    folder = args[0]
    query = " ".join(args[1:])
    results = search(folder, query)
    print(f"query: {query}")
    print(f"folder: {folder}")
    print(f"results ({len(results)}):")
    for doc_id, score in results:
        print(f"  {doc_id}: {score:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
