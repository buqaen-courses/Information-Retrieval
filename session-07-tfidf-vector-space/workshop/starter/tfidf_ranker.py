"""Starter: TF-IDF vector space ranker — 4 TODOs.

Usage (from session-07-tfidf-vector-space/):
    python workshop/starter/tfidf_ranker.py workshop/data "cat"
"""
from __future__ import annotations

TODO_COUNT = 4
PUNCTUATION = ".,!?;:'\"()"


def tokenize(text: str) -> list[str]:
    tokens = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word:
            tokens.append(word)
    return tokens


def list_doc_ids(folder: str) -> list[str]:
    import os
    return [n.replace(".txt", "") for n in sorted(os.listdir(folder))
            if n.endswith(".txt")]


def build_index(folder: str) -> tuple[list[str], list[list[str]], dict[str, int]]:
    """Return (doc_ids, doc_tokens, term_doc_freq)."""
    import os
    doc_ids = list_doc_ids(folder)
    doc_tokens = []
    term_doc_freq: dict[str, int] = {}
    for doc_id in doc_ids:
        with open(os.path.join(folder, doc_id + ".txt"), mode="r",
                  encoding="utf-8") as f:
            tokens = tokenize(f.read())
        doc_tokens.append(tokens)
        for term in set(tokens):
            term_doc_freq[term] = term_doc_freq.get(term, 0) + 1
    return doc_ids, doc_tokens, term_doc_freq


def compute_tfidf(doc_tokens: list[list[str]], term_doc_freq: dict[str, int],
                  vocab: list[str]):
    """Return (n_docs, n_terms) TF-IDF matrix.  (TODO-1)"""
    # TODO-1: build the TF-IDF matrix. Snippet shape:
    #     import numpy as np
    #     import math
    #     n_docs = len(doc_tokens)
    #     n_terms = len(vocab)
    #     term_to_idx = {t: i for i, t in enumerate(vocab)}
    #     mat = np.zeros((n_docs, n_terms))
    #     for i, tokens in enumerate(doc_tokens):
    #         tf = {}
    #         for t in tokens:
    #             tf[t] = tf.get(t, 0) + 1
    #         for term, count in tf.items():
    #             if term in term_to_idx:
    #                 j = term_to_idx[term]
    #                 idf = math.log(1 + (n_docs - term_doc_freq[term] + 0.5) /
    #                                (term_doc_freq[term] + 0.5))
    #                 mat[i, j] = (1 + math.log(count)) * idf
    #     return mat
    raise NotImplementedError("TODO-1 not done yet — compute the TF-IDF matrix")


def cosine_similarity(a, b) -> float:
    """Cosine similarity between two vectors.  (TODO-2)"""
    # TODO-2: compute cosine similarity. Snippet shape:
    #     import numpy as np
    #     na = np.linalg.norm(a)
    #     nb = np.linalg.norm(b)
    #     if na == 0 or nb == 0:
    #         return 0.0
    #     return float(np.dot(a, b) / (na * nb))
    # (np.linalg.norm computes the length of a vector; np.dot is the dot product.)
    raise NotImplementedError("TODO-2 not done yet — compute cosine similarity")


def search(folder: str, query: str) -> list[tuple[str, float]]:
    """Return [(doc_id, score), ...] sorted by score descending.  (TODO-3)"""
    # TODO-3: build the query vector, score all docs, sort. Snippet shape:
    #     import math
    #     doc_ids, doc_tokens, term_doc_freq = build_index(folder)
    #     vocab = sorted(term_doc_freq)
    #     mat = compute_tfidf(doc_tokens, term_doc_freq, vocab)
    #     term_to_idx = {t: i for i, t in enumerate(vocab)}
    #     q_tokens = tokenize(query)
    #     q_vec = np.zeros(len(vocab))
    #     for t in set(q_tokens):
    #         if t in term_to_idx:
    #             j = term_to_idx[t]
    #             idf = math.log(1 + (len(doc_ids) - term_doc_freq[t] + 0.5) /
    #                            (term_doc_freq[t] + 0.5))
    #             q_vec[j] = idf
    #     scores = []
    #     for i, doc_id in enumerate(doc_ids):
    #         s = cosine_similarity(q_vec, mat[i])
    #         if s > 0:
    #             scores.append((doc_id, s))
    #     scores.sort(key=lambda x: (-x[1], x[0]))
    #     return scores
    raise NotImplementedError("TODO-3 not done yet — rank documents for a query")


def main(argv: list[str] | None = None) -> int:
    """Print TF-IDF ranking for a query.  (TODO-4)"""
    import sys
    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        print('usage: python tfidf_ranker.py <folder> "<query>"')
        return 2
    folder = args[0]
    query = " ".join(args[1:])
    try:
        results = search(folder, query)
    except NotImplementedError as exc:
        print(exc)
        print(f"({TODO_COUNT} TODOs total — work top to bottom.)")
        return 0
    # TODO-4: print the results. Snippet shape:
    #     print("query:", query)
    #     print("folder:", folder)
    #     print("results:", len(results))
    #     for doc_id, score in results[:10]:
    #         print(f"  {doc_id}: {score:.4f}")
    raise NotImplementedError("TODO-4 not done yet — print the ranking")


if __name__ == "__main__":
    main()
