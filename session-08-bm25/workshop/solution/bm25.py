"""BM25 ranking from scratch.

Usage (from session-08-bm25/):
    python workshop/solution/bm25.py workshop/data "sauce basil"
    python workshop/solution/bm25.py ../../datasets/corpus "tomato sauce"
    python workshop/solution/bm25.py ../../datasets/corpus --tune

The formula (Robertson & Zaragoza, the probabilistic ranking function that
every engine since has shipped):

    score(q, d) = sum over t in q:  IDF(t) * (tf * (k1 + 1)) / (tf + k1)

    IDF(t) = log(1 + (N - df + 0.5) / (df + 0.5))

    length norm = k1 * (1 - b + b * dl / avgdl)

with k1 controlling term-frequency saturation (default 1.2) and b controlling
length normalization (default 0.75). See the README for what each knob buys you.
"""
from __future__ import annotations

import math
import os
import sys

PUNCTUATION = ".,!?;:'\"()"
K1_DEFAULT = 1.2
B_DEFAULT = 0.75


def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into terms."""
    tokens = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word:
            tokens.append(word)
    return tokens


def list_doc_ids(folder: str) -> list[str]:
    """Sorted document ids (filenames without .txt) in folder."""
    return [n[:-4] for n in sorted(os.listdir(folder)) if n.endswith(".txt")]


def build_stats(folder: str) -> dict:
    """Collect everything BM25 needs in one pass over the corpus.

    Returns {'doc_ids', 'tf', 'doc_len', 'df', 'N', 'avgdl'} where
    tf[doc_id][term] is the raw count of term in doc_id.
    """
    doc_ids = list_doc_ids(folder)
    tf: dict[str, dict[str, int]] = {}
    doc_len: dict[str, int] = {}
    df: dict[str, int] = {}
    for doc_id in doc_ids:
        with open(os.path.join(folder, doc_id + ".txt"), mode="r",
                  encoding="utf-8") as f:
            tokens = tokenize(f.read())
        doc_len[doc_id] = len(tokens)
        counts: dict[str, int] = {}
        for term in tokens:
            counts[term] = counts.get(term, 0) + 1
        tf[doc_id] = counts
        for term in counts:
            df[term] = df.get(term, 0) + 1
    n_docs = len(doc_ids)
    avgdl = sum(doc_len.values()) / n_docs if n_docs else 0.0
    return {"doc_ids": doc_ids, "tf": tf, "doc_len": doc_len, "df": df,
            "N": n_docs, "avgdl": avgdl}


def idf(term: str, df: int, n_docs: int) -> float:
    """Inverse document frequency, the +0.5 smoothing variant."""
    return math.log(1 + (n_docs - df + 0.5) / (df + 0.5))


def bm25_score(query: str, doc_id: str, stats: dict, k1: float = K1_DEFAULT,
               b: float = B_DEFAULT) -> float:
    """Score one document against one query."""
    tf = stats["tf"][doc_id]
    doc_len = stats["doc_len"][doc_id]
    n_docs, avgdl = stats["N"], stats["avgdl"]
    score = 0.0
    for term in tokenize(query):
        freq = tf.get(term, 0)
        if freq == 0:
            continue
        if term not in stats["df"]:
            continue
        weight = idf(term, stats["df"][term], n_docs)
        norm = k1 * (1 - b + b * doc_len / avgdl)
        score += weight * (freq * (k1 + 1)) / (freq + norm)
    return score


def search(folder: str, query: str, k1: float = K1_DEFAULT,
           b: float = B_DEFAULT) -> list[tuple[str, float]]:
    """Rank every document; return [(doc_id, score), ...] best first.

    Ties break on doc_id so the ranking is reproducible run to run.
    """
    stats = build_stats(folder)
    scored = [(doc_id, bm25_score(query, doc_id, stats, k1, b))
              for doc_id in stats["doc_ids"]]
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored


def tune(folder: str, query: str, k1_grid: list[float],
         b_grid: list[float]) -> list[tuple[float, float, float]]:
    """Return [(ndcg_at_10, k1, b)] over the grid, best first.

    Relevance here is a stand-in for the graded judgments you meet properly in
    Session 10: a document is relevant when it contains at least half of the
    query terms. Use it to see the SHAPE of the surface, not as an evaluation.
    """
    stats = build_stats(folder)
    query_terms = [t for t in set(tokenize(query)) if t in stats["df"]]
    if not query_terms:
        return []
    judged: dict[str, int] = {}
    for doc_id in stats["doc_ids"]:
        present = sum(1 for t in query_terms if stats["tf"][doc_id].get(t, 0) > 0)
        if present * 2 >= len(query_terms):
            judged[doc_id] = present
    rows = []
    for k1 in k1_grid:
        for b in b_grid:
            ranked = [d for d, s in search(folder, query, k1, b) if s > 0][:10]
            rows.append((_ndcg(ranked, judged), k1, b))
    rows.sort(key=lambda item: (-item[0], item[1], item[2]))
    return rows


def _ndcg(ranked: list[str], judged: dict[str, int]) -> float:
    """NDCG@10 with a gain of 2^rel - 1; 1.0 when there is nothing relevant."""
    if not judged:
        return 1.0
    gains = [(2 ** judged.get(d, 0) - 1) / math.log2(i + 2)
             for i, d in enumerate(ranked)]
    dcg = sum(gains)
    ideal = sorted((2 ** v - 1 for v in judged.values()), reverse=True)[:len(ranked)]
    idcg = sum(g / math.log2(i + 2) for i, g in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def main(argv: list[str] | None = None) -> int:
    """Rank a folder for a query, or sweep k1/b when asked."""
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print('usage: python bm25.py <folder> "<query>"')
        print('       python bm25.py <folder> --tune "<query>"')
        return 2
    folder = args[0]
    if len(args) > 1 and args[1] == "--tune":
        if len(args) < 3:
            print('usage: python bm25.py <folder> --tune "<query>"')
            return 2
        query = " ".join(args[2:])
        rows = tune(folder, query, [0.5, 1.2, 2.0], [0.0, 0.5, 0.75])
        print(f"tuning on: {query}")
        print("ndcg@10    k1     b")
        for ndcg, k1, b in rows:
            print(f"{ndcg:.4f}   {k1:<6} {b}")
        return 0
    query = " ".join(args[1:])
    results = search(folder, query)
    print(f"query: {query}")
    print(f"folder: {folder}")
    print(f"results ({len(results)}):")
    for doc_id, score in results[:10]:
        print(f"  {doc_id}: {score:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
