"""TF-IDF vector space ranker.

Usage (from session-07-tfidf-vector-space/):
    python workshop/solution/tfidf_ranker.py workshop/data "sauce AND basil"
    python workshop/solution/tfidf_ranker.py ../../datasets/corpus "python search"
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

PUNCTUATION = ".,!?;:'\"()"


def tokenize(text: str) -> list[str]:
    tokens = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word:
            tokens.append(word)
    return tokens


def list_doc_ids(folder: str) -> list[str]:
    return [n.replace(".txt", "") for n in sorted(os.listdir(folder))
            if n.endswith(".txt")]


def build_index(folder: str) -> tuple[list[str], list[list[str]], dict[str, int]]:
    """Return (doc_ids, doc_tokens, term_doc_freq)."""
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
                  vocab: list[str]) -> np.ndarray:
    """Return (n_docs, n_terms) TF-IDF matrix."""
    n_docs = len(doc_tokens)
    n_terms = len(vocab)
    term_to_idx = {t: i for i, t in enumerate(vocab)}
    mat = np.zeros((n_docs, n_terms))
    for i, tokens in enumerate(doc_tokens):
        tf: dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        for term, count in tf.items():
            if term in term_to_idx:
                j = term_to_idx[term]
                idf = math.log(1 + (n_docs - term_doc_freq[term] + 0.5) /
                               (term_doc_freq[term] + 0.5))
                mat[i, j] = (1 + math.log(count)) * idf
    return mat


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def search(folder: str, query: str) -> list[tuple[str, float]]:
    """Return [(doc_id, score), ...] sorted by score descending."""
    doc_ids, doc_tokens, term_doc_freq = build_index(folder)
    vocab = sorted(term_doc_freq)
    mat = compute_tfidf(doc_tokens, term_doc_freq, vocab)
    term_to_idx = {t: i for i, t in enumerate(vocab)}

    q_tokens = tokenize(query)
    q_vec = np.zeros(len(vocab))
    for t in set(q_tokens):
        if t in term_to_idx:
            j = term_to_idx[t]
            idf = math.log(1 + (len(doc_ids) - term_doc_freq[t] + 0.5) /
                           (term_doc_freq[t] + 0.5))
            q_vec[j] = idf

    scores = []
    for i, doc_id in enumerate(doc_ids):
        s = cosine_similarity(q_vec, mat[i])
        if s > 0:
            scores.append((doc_id, s))
    scores.sort(key=lambda x: (-x[1], x[0]))
    return scores


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        print('usage: python tfidf_ranker.py <folder> "<query>"')
        return 2
    folder = args[0]
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
