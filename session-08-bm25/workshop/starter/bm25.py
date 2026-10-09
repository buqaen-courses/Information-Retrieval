"""Starter: BM25 ranking from scratch — 4 TODOs.

Runs without crashing: unfinished TODOs print a friendly hint. Work top to
bottom.

Usage (from session-08-bm25/):
    python workshop/starter/bm25.py workshop/data "sauce basil"
"""
from __future__ import annotations

TODO_COUNT = 4
PUNCTUATION = ".,!?;:'\"()"
K1_DEFAULT = 1.2
B_DEFAULT = 0.75


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


def idf(term: str, df: int, n_docs: int) -> float:
    """Inverse document frequency.  (TODO-1)"""
    # TODO-1: idf = log(1 + (N - df + 0.5) / (df + 0.5)). Snippet shape:
    #     import math
    #     return math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
    # (The +0.5 on both sides is 'smoothing': it keeps the ratio positive and
    #  stops a term present in every document collapsing the log to zero.)
    raise NotImplementedError("TODO-1 not done yet — compute IDF")


def build_stats(folder: str) -> dict:
    """Collect everything BM25 needs in one pass.  (TODO-2)"""
    # TODO-2: read every doc, count terms per doc, count docs per term.
    # Snippet shape:
    #     import os
    #     doc_ids = list_doc_ids(folder)
    #     tf = {}
    #     doc_len = {}
    #     df = {}
    #     for doc_id in doc_ids:
    #         with open(os.path.join(folder, doc_id + ".txt"),
    #                   mode="r", encoding="utf-8") as f:
    #             tokens = tokenize(f.read())
    #         doc_len[doc_id] = len(tokens)
    #         counts = {}
    #         for term in tokens:
    #             counts[term] = counts.get(term, 0) + 1
    #         tf[doc_id] = counts
    #         for term in counts:
    #             df[term] = df.get(term, 0) + 1
    #     n_docs = len(doc_ids)
    #     avgdl = sum(doc_len.values()) / n_docs if n_docs else 0.0
    #     return {"doc_ids": doc_ids, "tf": tf, "doc_len": doc_len,
    #             "df": df, "N": n_docs, "avgdl": avgdl}
    # (Note: df counts DOCS containing a term, so you add 1 per doc, not per
    #  occurrence — iterating `counts` (the unique terms) is what gets that right.)
    raise NotImplementedError("TODO-2 not done yet — collect tf, df, doc lengths")


def bm25_score(query: str, doc_id: str, stats: dict, k1: float = K1_DEFAULT,
               b: float = B_DEFAULT) -> float:
    """Score one document against one query.  (TODO-3)"""
    # TODO-3: sum idf * tf-part over the query terms. Snippet shape:
    #     tf = stats["tf"][doc_id]
    #     doc_len = stats["doc_len"][doc_id]
    #     n_docs, avgdl = stats["N"], stats["avgdl"]
    #     score = 0.0
    #     for term in tokenize(query):
    #         freq = tf.get(term, 0)
    #         if freq == 0:
    #             continue
    #         if term not in stats["df"]:
    #             continue
    #         weight = idf(term, stats["df"][term], n_docs)
    #         norm = k1 * (1 - b + b * doc_len / avgdl)
    #         score += weight * (freq * (k1 + 1)) / (freq + norm)
    #     return score
    # (The `if freq == 0: continue` guard is what makes a non-matching term
    #  contribute nothing instead of a negative or undefined score.)
    raise NotImplementedError("TODO-3 not done yet — score one document")


def search(folder: str, query: str, k1: float = K1_DEFAULT,
           b: float = B_DEFAULT) -> list[tuple[str, float]]:
    """Rank every document, best first.  (TODO-4)"""
    # TODO-4: score every doc and sort. Snippet shape:
    #     stats = build_stats(folder)
    #     scored = [(doc_id, bm25_score(query, doc_id, stats, k1, b))
    #               for doc_id in stats["doc_ids"]]
    #     scored.sort(key=lambda item: (-item[1], item[0]))
    #     return scored
    # (Sorting on (-score, doc_id) puts the best first AND breaks ties
    #  alphabetically, so the ranking is identical on every run.)
    raise NotImplementedError("TODO-4 not done yet — rank the documents")


def main(argv: list[str] | None = None) -> int:
    import sys
    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        print('usage: python bm25.py <folder> "<query>"')
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
    for doc_id, score in results[:10]:
        print(f"  {doc_id}: {score:.4f}")
    return 0


if __name__ == "__main__":
    main()
