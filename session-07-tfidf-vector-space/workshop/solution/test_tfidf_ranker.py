"""Tests for tfidf_ranker.py — the Session 7 deliverable.

Run: python -m pytest workshop/solution/ -v
Expected values are hand-checkable against workshop/data/.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tfidf_ranker import (build_index, compute_tfidf, cosine_similarity,  # noqa: E402
                          search, tokenize)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def test_tokenize_strips_punctuation_and_lowercases() -> None:
    assert tokenize("The CAT, sat!") == ["the", "cat", "sat"]


def test_index_shape() -> None:
    doc_ids, doc_tokens, df = build_index(DATA)
    assert doc_ids == ["doc-a", "doc-b", "doc-c"]
    assert len(doc_tokens) == 3
    # 'the' appears in all 3 docs, 'cat' in 2, 'log' in 1
    assert df["the"] == 3
    assert df["cat"] == 2
    assert df["log"] == 1


def test_tfidf_matrix_shape_and_values() -> None:
    doc_ids, doc_tokens, df = build_index(DATA)
    vocab = sorted(df)
    mat = compute_tfidf(doc_tokens, df, vocab)
    assert mat.shape == (3, len(vocab))
    # 'the' has df=3, so its IDF must be lower than 'log' with df=1
    vocab_idx = {t: i for i, t in enumerate(vocab)}
    mat_the = mat[:, vocab_idx["the"]]
    mat_log = mat[:, vocab_idx["log"]]
    assert mat_log.max() > mat_the.max()


def test_cosine_similarity_hand_checked() -> None:
    # two identical unit vectors -> 1.0; orthogonal -> 0.0
    a = np.array([1.0, 0.0])
    assert abs(cosine_similarity(a, a) - 1.0) < 1e-9
    b = np.array([0.0, 1.0])
    assert abs(cosine_similarity(a, b) - 0.0) < 1e-9
    c = np.array([0.0, 0.0])
    assert cosine_similarity(a, c) == 0.0


def test_search_ranks_docs_containing_term_first() -> None:
    results = search(DATA, "cat")
    ids = [doc for doc, _ in results]
    # 'cat' is in doc-a and doc-c, NOT in doc-b
    assert "doc-b" not in ids or ids.index("doc-b") >= len(ids) - 1
    assert "doc-a" in ids and "doc-c" in ids


def test_search_two_terms_prefers_docs_with_both() -> None:
    """TF-IDF RANKS, it does not FILTER — unlike Session 6's Boolean AND.

    'cat dog' is in doc-c only. But doc-a has 'cat' and doc-b has 'dog', so
    both still appear with a lower score instead of being dropped. The doc
    containing both terms must come first.
    """
    results = search(DATA, "cat dog")
    assert results[0][0] == "doc-c"
    assert results[0][1] > results[1][1]


def test_scores_are_sorted_descending() -> None:
    results = search(DATA, "the cat dog")
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)


def test_empty_query_returns_nothing() -> None:
    assert search(DATA, "zzzznotaword") == []
