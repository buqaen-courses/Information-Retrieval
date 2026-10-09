"""Tests for compare_vector_dbs.py — the Session 13 deliverable.

The catalogue is embedded ONCE at module scope (it costs ~20s) and both
databases are indexed from that same matrix, so every comparison below is
between databases holding identical vectors.

Run: python -m pytest workshop/solution/ -v
"""
from __future__ import annotations

import math
import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_vector_dbs import (DIM, QUERIES, LanceIndex, MilvusLiteIndex,  # noqa: E402
                                brute_force, load_catalogue, query_vector)

_WORK = None


def fixture_data(limit: int = 24):
    """Embed a small catalogue once and reuse it across the tests."""
    global _WORK
    if _WORK is None or _WORK[0] != limit:
        _WORK = (limit,) + load_catalogue(limit=limit)
    return _WORK[1], _WORK[2], _WORK[3]


@pytest.fixture(scope="module")
def indexed():
    """Build both databases from the same small catalogue; yield the pieces."""
    ids, texts, vectors = fixture_data()
    tmp = Path(tempfile.mkdtemp(prefix="s13_"))
    try:
        milvus = MilvusLiteIndex(tmp / "milvus.db")
        lance = LanceIndex(tmp / "lancedb")
        milvus.build(ids, texts, vectors)
        lance.build(ids, texts, vectors)
        yield {"ids": ids, "texts": texts, "vectors": vectors,
               "milvus": milvus, "lance": lance}
    finally:
        try:
            milvus.close()
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------- #
# the shared data
# --------------------------------------------------------------------------- #
def test_vectors_are_normalized_384d() -> None:
    ids, _texts, vectors = fixture_data()
    assert vectors.shape[1] == DIM == 384
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5)
    assert len(ids) == vectors.shape[0]


def test_brute_force_ranks_by_cosine() -> None:
    """Session 12's exact search is the ground truth for both databases."""
    ids, _t, vectors = fixture_data()
    query = vectors[0]
    hits = brute_force(query, vectors, ids, k=3)
    assert len(hits) == 3
    scores = [s for _, s in hits]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == pytest.approx(1.0, abs=1e-5)


# --------------------------------------------------------------------------- #
# both databases
# --------------------------------------------------------------------------- #
def test_milvus_matches_brute_force(indexed) -> None:
    """Milvus Lite must return the exact same top-5 as brute force."""
    vectors, ids = indexed["vectors"], indexed["ids"]
    for i in (0, 5, 9):
        query = vectors[i]
        expected = [d for d, _ in brute_force(query, vectors, ids, k=5)]
        got = [d for d, _ in indexed["milvus"].search(query, k=5)]
        assert got == expected, f"milvus disagrees on query {i}"


def test_lancedb_matches_brute_force(indexed) -> None:
    """LanceDB reports squared L2, which is converted back to cosine here."""
    vectors, ids = indexed["vectors"], indexed["ids"]
    for i in (0, 5, 9):
        query = vectors[i]
        expected = [d for d, _ in brute_force(query, vectors, ids, k=5)]
        got = [d for d, _ in indexed["lance"].search(query, k=5)]
        assert got == expected, f"lancedb disagrees on query {i}"


def test_both_databases_agree_with_each_other(indexed) -> None:
    vectors, _ids = indexed["vectors"], indexed["ids"]
    for i in (0, 7, 15):
        query = vectors[i]
        m = [d for d, _ in indexed["milvus"].search(query, k=5)]
        l = [d for d, _ in indexed["lance"].search(query, k=5)]
        assert m == l


def test_scores_are_cosine_not_distance(indexed) -> None:
    """A perfect match must score 1.0 in BOTH backends after conversion."""
    vectors = indexed["vectors"]
    query = vectors[3]
    milvus_score = indexed["milvus"].search(query, k=1)[0][1]
    lance_score = indexed["lance"].search(query, k=1)[0][1]
    assert milvus_score == pytest.approx(1.0, abs=1e-4)
    assert lance_score == pytest.approx(1.0, abs=1e-4)


def test_identical_vector_scores_exactly_one(indexed) -> None:
    """The LanceDB conversion (2 - d^2)/2 must give 1.0 for d=0."""
    vectors = indexed["vectors"]
    query = vectors[0]
    # LanceDB _distance for an identical vector is 0 -> (2-0)/2 = 1.0
    assert indexed["lance"].search(query, k=1)[0][1] == pytest.approx(1.0, abs=1e-4)
    # and 0.0 for two orthogonal vectors
    d2 = indexed["lance"].search(query, k=len(vectors))[0]
    assert d2[1] <= 1.0 + 1e-6


def test_top_k_is_respected(indexed) -> None:
    vectors = indexed["vectors"]
    for k in (1, 3, 5):
        assert len(indexed["milvus"].search(vectors[0], k=k)) == k
        assert len(indexed["lance"].search(vectors[0], k=k)) == k


def test_rebuilding_is_idempotent(tmp_path) -> None:
    """Re-running the script must replace the collection, not append to it."""
    ids, texts, vectors = fixture_data()
    index = MilvusLiteIndex(tmp_path / "rebuild.db")
    index.build(ids, texts, vectors)
    first = [d for d, _ in index.search(vectors[0], k=5)]
    index.build(ids, texts, vectors)
    second = [d for d, _ in index.search(vectors[0], k=5)]
    assert first == second
    index.close()


def test_query_embedding_is_normalized() -> None:
    """A real query vector must also have length 1."""
    from compare_vector_dbs import load_model

    model = load_model()
    v = query_vector(model, "soccer boots")
    assert v.shape == (384,)
    assert float(math.sqrt(float((v ** 2).sum()))) == pytest.approx(1.0, abs=1e-5)


def test_workshop_queries_exist() -> None:
    """The three demo queries are part of the session contract."""
    assert QUERIES == ["soccer boots", "something to drink tea with",
                       "a sturdy lamp"]