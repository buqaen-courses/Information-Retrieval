"""Tests for semantic_search.py — the Session 14 deliverable.

Sessions 22 and 23 import this module, so these tests are the contract that
keeps it safe to reuse. The catalogue is embedded ONCE at module scope.

Run: python -m pytest workshop/solution/ -v
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from semantic_search import (DIM, MODEL_NAME, SearchHit,  # noqa: E402
                             SemanticSearch, load_products)

_ENGINE = None


def engine():
    """One built engine shared by every test that does not mutate it."""
    global _ENGINE
    if _ENGINE is None:
        tmp = Path(tempfile.mkdtemp(prefix="s14_"))
        _ENGINE = SemanticSearch(load_products(), index_dir=tmp / "index").build()
    return _ENGINE


@pytest.fixture(scope="module")
def built():
    """Yield the shared engine."""
    return engine()


# --------------------------------------------------------------------------- #
# construction and building
# --------------------------------------------------------------------------- #
def test_build_embeds_every_record(built) -> None:
    """One build call must produce one vector per usable record."""
    assert len(built.records) == len(built.vectors) == 128
    assert built.vectors.shape[1] == DIM == 384
    assert built.missing == []


def test_vectors_are_normalized(built) -> None:
    """Every stored vector must have length 1, or search scores are meaningless."""
    assert np.allclose(np.linalg.norm(built.vectors, axis=1), 1.0, atol=1e-5)


def test_search_before_build_raises() -> None:
    """A clear error beats a confusing NoneType crash."""
    fresh = SemanticSearch(load_products(limit=5))
    with pytest.raises(RuntimeError):
        fresh.search("kettle")


def test_record_text_falls_back_to_name() -> None:
    """A record without the text field must still produce something searchable."""
    e = SemanticSearch([], model=object())
    assert e.record_text({"text": "hello"}) == "hello"
    assert e.record_text({"name": "A kettle"}) == "A kettle"
    assert e.record_text({"description": "A kettle"}) == "A kettle"
    assert e.record_text({"nothing": 1}) == ""


# --------------------------------------------------------------------------- #
# searching
# --------------------------------------------------------------------------- #
def test_search_returns_search_hits(built) -> None:
    """Results must carry the original record, not just an id."""
    hits = built.search("something to warm tea with", k=5)
    assert len(hits) == 5
    assert all(isinstance(h, SearchHit) for h in hits)
    assert all("category" in h.record for h in hits)
    assert [h.score for h in hits] == sorted([h.score for h in hits],
                                             reverse=True)


def test_search_is_deterministic(built) -> None:
    """The same query twice must return the same order."""
    a = [h.id for h in built.search("kettle", k=5)]
    b = [h.id for h in built.search("kettle", k=5)]
    assert a == b


def test_meaning_beats_spelling(built) -> None:
    """A query with no matching word still finds kettles.

    Note the shared dataset assigns names and categories independently, so a
    product called "Wireless kettle" can sit in any category. What matters is
    that the *name* matches the meaning, not the category.
    """
    hits = built.search("something to warm tea with", k=3)
    assert "kettle" in hits[0].record["name"].lower()


def test_empty_query_returns_nothing(built) -> None:
    assert built.search("", k=5) == []
    assert built.search("   ", k=5) == []


def test_top_k_is_respected(built) -> None:
    for k in (1, 3, 10):
        assert len(built.search("lamp", k=k)) == k


# --------------------------------------------------------------------------- #
# filtering — the reason this class exists
# --------------------------------------------------------------------------- #
def test_category_filter_never_leaks(built) -> None:
    """Every returned record must be inside the requested category."""
    for cat in ("kitchen", "electronics", "books", "sports"):
        hits = built.search("boots", k=5, category=cat)
        assert hits, cat
        assert all(h.record["category"] == cat for h in hits), cat


def test_filter_ranks_the_filtered_pool(built) -> None:
    """Filtering happens BEFORE ranking, so results are NOT a subset of the
    unfiltered top-k.

    This is the behaviour that makes a filter useful: a filtered search returns
    the best 20 *kitchen* products, not the kitchen products that happened to
    reach the global top 20. The two lists are different on purpose.
    """
    unfiltered = [h.id for h in built.search("lamp", k=20)]
    filtered = [h.id for h in built.search("lamp", k=20, category="kitchen")]
    assert filtered != unfiltered

    kitchen_total = sum(1 for r in built.records if r["category"] == "kitchen")
    assert len(set(filtered)) == min(20, kitchen_total)

    # every filtered result is a kitchen record
    by_id = {r["id"]: r for r in built.records}
    assert all(by_id[i]["category"] == "kitchen" for i in filtered)


def test_unknown_category_returns_empty(built) -> None:
    assert built.search("kettle", k=5, category="no-such-category") == []


def test_filtered_search_does_not_use_the_index(built) -> None:
    """A filter must go through the slow exact path, since ANN cannot filter.

    If this ever returns the wrong category, the engine searched the ANN index
    and ignored the filter — the exact bug filtering exists to prevent.
    """
    hits = built.search("kettle", k=3, category="books")
    assert all(h.record["category"] == "books" for h in hits)


# --------------------------------------------------------------------------- #
# missing data
# --------------------------------------------------------------------------- #
def test_blank_record_is_reported_not_crashed() -> None:
    """A record with no text is skipped AND named in `missing`."""
    records = load_products(limit=5) + [
        {"id": "bad-1", "name": "", "category": "kitchen", "text": "   "},
    ]
    e = SemanticSearch(records, index_dir=None).build(use_index=False)
    assert e.missing == ["bad-1"]
    assert len(e.records) == 5
    assert len(e.vectors) == 5


def test_missing_record_is_excluded_from_search() -> None:
    """A skipped record must not reappear as a search result."""
    records = load_products(limit=5) + [
        {"id": "bad-1", "name": "", "category": "kitchen", "text": "  "},
    ]
    e = SemanticSearch(records, index_dir=None).build(use_index=False)
    hits = e.search("kettle", k=10)
    assert all(h.id != "bad-1" for h in hits)


# --------------------------------------------------------------------------- #
# persistence
# --------------------------------------------------------------------------- #
def test_save_then_load_round_trip(tmp_path) -> None:
    """A reloaded engine must answer identically without re-embedding."""
    src = SemanticSearch(load_products(limit=12),
                         index_dir=tmp_path / "idx").build()
    before = [h.id for h in src.search("kettle", k=5)]

    target = tmp_path / "saved"
    src.save(target)
    back = SemanticSearch.load(target)

    after = [h.id for h in back.search("kettle", k=5)]
    assert before == after
    assert len(back.records) == len(src.records)
    assert np.allclose(back.vectors, src.vectors, atol=1e-6)


def test_load_restores_missing_list(tmp_path) -> None:
    """The missing-record report must survive a round trip."""
    records = load_products(limit=5) + [
        {"id": "bad-1", "name": "", "category": "kitchen", "text": " "},
    ]
    e = SemanticSearch(records, index_dir=tmp_path / "i").build()
    e.save(tmp_path / "s")
    assert SemanticSearch.load(tmp_path / "s").missing == ["bad-1"]


# --------------------------------------------------------------------------- #
# the reuse contract Sessions 22 and 23 depend on
# --------------------------------------------------------------------------- #
def test_public_surface(built) -> None:
    """These three methods are what the later sessions import. Keep them."""
    for name in ("build", "search", "save"):
        assert callable(getattr(built, name))
    assert callable(SemanticSearch.load)


def test_model_name_is_the_cached_one() -> None:
    """Session 12 downloaded this model; using another needs a new download."""
    assert MODEL_NAME == "sentence-transformers/all-MiniLM-L6-v2"