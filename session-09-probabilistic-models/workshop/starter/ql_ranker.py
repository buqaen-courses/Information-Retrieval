"""Starter: query-likelihood ranking with Dirichlet smoothing — 4 TODOs.

Runs without crashing: unfinished TODOs print a friendly hint. Work top to
bottom.

Usage (from session-09-probabilistic-models/):
    python workshop/starter/ql_ranker.py workshop/data "sauce basil"
"""
from __future__ import annotations

TODO_COUNT = 4
PUNCTUATION = ".,!?;:'\"()"
MU_DEFAULT = 200.0
P_SMOOTH = 0.0001


def tokenize(text: str) -> list[str]:
    tokens = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word:
            tokens.append(word)
    return tokens


def list_doc_ids(folder: str) -> list[str]:
    import os
    return [n[:-4] for n in sorted(os.listdir(folder)) if n.endswith(".txt")]


def build_stats(folder: str) -> dict:
    """Per-doc term counts, collection frequencies, document lengths. (TODO-1)"""
    # TODO-1: one pass over the corpus. Snippet shape:
    #     doc_ids = list_doc_ids(folder)
    #     tf = {}
    #     doc_len = {}
    #     cf = {}
    #     for doc_id in doc_ids:
    #         with open(os.path.join(folder, doc_id + ".txt"),
    #                   mode="r", encoding="utf-8") as f:
    #             tokens = tokenize(f.read())
    #         doc_len[doc_id] = len(tokens)
    #         counts = {}
    #         for term in tokens:
    #             counts[term] = counts.get(term, 0) + 1
    #         tf[doc_id] = counts
    #         for term, count in counts.items():
    #             cf[term] = cf.get(term, 0) + count
    #     return {"doc_ids": doc_ids, "tf": tf, "doc_len": doc_len,
    #             "cf": cf, "total": sum(doc_len.values()),
    #             "N": len(doc_ids)}
    # (cf is the COLLECTION frequency — total occurrences across all documents,
    #  not a count of documents. That is the difference from Session 8's df.)
    raise NotImplementedError("TODO-1 not done yet — collect tf, cf, doc lengths")


def ql_score(query: str, doc_id: str, stats: dict, mu: float = MU_DEFAULT,
             p_smooth: float = P_SMOOTH) -> float:
    """log P(query | document), smoothed. (TODO-2)"""
    # TODO-2: sum log((tf + mu*background) / (dl + mu)) over query terms.
    # Snippet shape:
    #     import math
    #     tf = stats["tf"][doc_id]
    #     dl = stats["doc_len"][doc_id]
    #     total = stats["total"]
    #     score = 0.0
    #     for term in tokenize(query):
    #         background = (stats["cf"].get(term, 0) + mu * p_smooth) / (total + mu)
    #         score += math.log((tf.get(term, 0) + mu * background) / (dl + mu))
    #     return score
    # (The mu*background term is what keeps the numerator > 0 even when tf is 0.
    #  Without it you get log(0), which is -inf and kills the whole ranking.)
    raise NotImplementedError("TODO-2 not done yet — score log P(query | document)")


def search(folder: str, query: str, mu: float = MU_DEFAULT,
           top: int = 10) -> list[tuple[str, float]]:
    """Rank by query likelihood, best first. (TODO-3)"""
    # TODO-3: score every document and sort. Snippet shape:
    #     stats = build_stats(folder)
    #     scored = [(doc_id, ql_score(query, doc_id, stats, mu))
    #               for doc_id in stats["doc_ids"]]
    #     scored.sort(key=lambda item: (-item[1], item[0]))
    #     return scored[:top]
    # (Note: EVERY document appears, even one matching nothing — that is a real
    #  difference from BM25, which only scores documents containing a term.)
    raise NotImplementedError("TODO-3 not done yet — rank the documents")


def sweep_mu(folder: str, query: str) -> list[tuple[float, str, str]]:
    """Compare the top result at several smoothing strengths. (TODO-4)"""
    # TODO-4: run search() at a few values of mu and report the winner each time.
    # Snippet shape:
    #     rows = []
    #     for mu in [10.0, 50.0, 200.0, 1000.0]:
    #         ranked = search(folder, query, mu=mu, top=2)
    #         best = ranked[0][0]
    #         margin = ranked[0][1] - ranked[1][1]
    #         rows.append((mu, best, round(margin, 4)))
    #     return rows
    # (The margin is the point: as mu grows, smoothing pulls every document
    #  toward the collection average and the ranking flattens out.)
    raise NotImplementedError("TODO-4 not done yet — sweep the smoothing strength")


def main(argv: list[str] | None = None) -> int:
    import sys
    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        print('usage: python ql_ranker.py <folder> "<query>"')
        return 2
    folder = args[0]
    query = " ".join(args[1:])
    try:
        results = search(folder, query)
    except NotImplementedError as exc:
        print(exc)
        print(f"({TODO_COUNT} TODOs total — work top to bottom.)")
        return 0
    print(f"query: {query}")
    print(f"folder: {folder}")
    print(f"results ({len(results)}):")
    for doc_id, score in results:
        print(f"  {doc_id}: {score:.4f}")
    return 0


if __name__ == "__main__":
    main()
