"""Tests for numpy_semantic_search.py — the Session 12 deliverable.

The model is slow to load, so it is loaded once per session (module scope).
Run: python -m pytest workshop/solution/ -v
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numpy_semantic_search import (MODEL_NAME, embed, load_model,  # noqa: E402
                                    product_sentence, search)

_MODEL = None


def model():
    """Load the bi-encoder once and reuse it across tests."""
    global _MODEL
    if _MODEL is None:
        _MODEL = load_model()
    return _MODEL


def test_model_is_offline_and_correct_shape() -> None:
    """The cached MiniLM model must produce 384-dimensional vectors."""
    vectors = embed(model(), ["a sentence"])
    assert vectors.shape == (1, 384)
    assert MODEL_NAME.endswith("all-MiniLM-L6-v2")


def test_vectors_are_normalized() -> None:
    """Every vector must have length 1 — that is what makes cosine a dot product."""
    vectors = embed(model(), ["red apple", "a red fruit", "quantum physics"])
    norms = np.linalg.norm(vectors, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)


def test_identical_sentences_score_one() -> None:
    """A sentence is maximally similar to itself."""
    v = embed(model(), ["a sturdy desk lamp"])
    assert abs(float(v[0] @ v[0].T) - 1.0) < 1e-5


def test_similar_sentences_beat_unrelated() -> None:
    """The core claim: meaning, not word overlap."""
    catalogue = [
        "soccer boots", "football cleats", "running shoes",
        "a sturdy desk lamp", "a stainless kettle",
    ]
    hits = search(model(), "football boots", catalogue, top_k=2)
    top_two = {catalogue[i] for i, _ in hits}
    assert "soccer boots" in top_two or "football cleats" in top_two
    assert "a stainless kettle" not in top_two


def test_cross_lingual_synonym_without_shared_words() -> None:
    """'boots' vs 'cleats' share no word, yet must rank close.

    This is the whole argument for embeddings, so it is pinned as a test.
    """
    a = embed(model(), ["football boots"])[0]
    b = embed(model(), ["soccer cleats with studs"])[0]
    c = embed(model(), ["a stainless steel kettle"])[0]
    assert float(a @ b) > float(a @ c)
    assert float(a @ b) > 0.4, float(a @ b)


def test_query_term_absent_from_catalogue_still_works() -> None:
    """BM25 would return nothing; embeddings still rank by meaning."""
    catalogue = ["a machine that makes coffee", "a lamp for reading"]
    hits = search(model(), "espresso", catalogue, top_k=1)
    assert hits[0][0] == 0
    assert hits[0][1] > 0.4


def test_search_returns_sorted_scores() -> None:
    catalogue = ["soccer boots", "football cleats", "a sturdy desk lamp"]
    hits = search(model(), "football boots", catalogue, top_k=3)
    scores = [s for _, s in hits]
    assert scores == sorted(scores, reverse=True)
    assert all(-1.0 <= s <= 1.0 for s in scores)


def test_top_k_is_respected() -> None:
    catalogue = [f"item number {i} about lamps" for i in range(20)]
    assert len(search(model(), "lamp", catalogue, top_k=5)) == 5


def test_empty_catalogue_returns_nothing() -> None:
    assert search(model(), "anything", [], top_k=5) == []


def test_embedding_is_deterministic() -> None:
    """Same sentence twice must give the same vector (fixed model, CPU)."""
    first = embed(model(), ["durable backpack"])
    second = embed(model(), ["durable backpack"])
    assert np.allclose(first, second, atol=1e-6)


def test_known_similarity_bands() -> None:
    """Loose bands, not brittle exact numbers.

    Only 12-02's chart pins exact values. These bands catch a wrong model or a
    broken normalization step without failing on a library upgrade.
    """
    v = embed(model(), ["soccer boots", "football cleats", "a stainless kettle"])
    same_topic = float(v[0] @ v[1])
    different_topic = float(v[0] @ v[2])
    assert 0.3 < same_topic < 0.9
    assert different_topic < 0.4
    assert same_topic > different_topic


def test_product_sentence_includes_name_and_description() -> None:
    product = {"name": "Compact kettle", "description": "A steel kettle."}
    sentence = product_sentence(product)
    assert "Compact kettle" in sentence
    assert "steel" in sentence