"""Tests for annotate.py — the Session 4 deliverable.

Run from the session folder (with the course venv active):
    python -m pytest workshop/solution/ -v
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from annotate import (PIPELINE, REQUIREMENTS, annotate, load_corpus,  # noqa: E402
                      unclaimed_boxes, vocabulary_gap, docs_with, corpus_paths)


def test_eight_requirements_eight_boxes() -> None:
    """One requirement per box: the scenario brief's core claim."""
    rows = annotate()
    assert len(rows) == len(REQUIREMENTS) == 8
    assert len({r["box"] for r in rows}) == 8


def test_no_unclaimed_boxes() -> None:
    """Every box of the architecture is claimed by some requirement."""
    rows = annotate()
    assert unclaimed_boxes() == []
    assert {box for box, _ in PIPELINE} == {r["box"] for r in rows}


def test_sessions_attached() -> None:
    """Every annotated row names sessions — no orphan requirements."""
    for row in annotate():
        assert row["sessions"], row
        assert "S" in row["sessions"], row


def test_corpus_has_204_documents() -> None:
    """The shared dataset is the one the whole course uses."""
    docs = load_corpus()
    assert len(docs) == 204
    assert len(corpus_paths()) == 204


def test_docs_with_counts_real_words() -> None:
    """'the' appears in 145 of 204 docs; a nonsense word appears in none."""
    docs = load_corpus()
    assert docs_with(docs, "the") == 145
    assert docs_with(docs, "zzzqqx") == 0


def test_vocabulary_gap_is_measured_not_asserted() -> None:
    """The gap that justifies EMBED is a real measurement on this machine."""
    docs = load_corpus()
    gap = {row["typed"]: row for row in vocabulary_gap(docs)}
    assert gap["rover"]["docs_with_typed"] == 0
    assert gap["rover"]["docs_with_written"] == 14
    assert gap["soccer"]["docs_with_typed"] == 0
    assert gap["soccer"]["docs_with_written"] == 34


def test_topic_header_is_counted() -> None:
    """'football' only appears in the topic line — skipping it would lie."""
    docs = load_corpus()
    assert docs_with(docs, "football") == 34
