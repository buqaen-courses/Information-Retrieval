"""Tests for fast_score.py — the Session 11 deliverable.

The critical tests are the equivalence ones: an optimization that changes the
answer is worse than no optimization. `test_skips_match_plain_on_real_index`
checks all 48,841 term pairs of the real corpus.

Run: python -m pytest workshop/solution/ -v
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fast_score import (BLOCK_SIZE, SKIP_INTERVAL, block_max_wand,  # noqa: E402
                        build_blocks, build_postings, build_skip_list,
                        compress_postings, compression_ratio,
                        count_comparisons_plain, count_comparisons_skips,
                        decompress_postings, delta_decode, delta_encode,
                        intersect_plain, intersect_with_skips, seek,
                        tokenize, varint_decode, varint_encode)

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
CORPUS = os.path.join(ROOT, "datasets", "corpus")

# A small postings list with a big gap, for hand-checking.
HAND = [0, 1, 2, 5, 9, 40, 41, 100]


# ---- delta encoding --------------------------------------------------------

def test_delta_encode_hand_computed() -> None:
    assert delta_encode(HAND) == [0, 1, 1, 3, 4, 31, 1, 59]


def test_delta_round_trip() -> None:
    assert delta_decode(delta_encode(HAND)) == HAND
    assert delta_encode([]) == []
    assert delta_decode([]) == []


# ---- varint ----------------------------------------------------------------

def test_varint_small_numbers_take_one_byte() -> None:
    for value in (0, 1, 5, 127):
        assert len(varint_encode(value)) == 1


def test_varint_grows_with_magnitude() -> None:
    assert len(varint_encode(128)) == 2
    assert len(varint_encode(16384)) == 3
    assert len(varint_encode(10 ** 9)) < 8


def test_varint_round_trip() -> None:
    values = [0, 1, 127, 128, 300, 70000, 10 ** 9]
    assert varint_decode(b"".join(varint_encode(v) for v in values)) == values


def test_varint_of_one_byte_is_the_value() -> None:
    """Hand check: 7-bit payload, high bit clear."""
    assert varint_encode(65) == bytes([65])


# ---- posting compression ---------------------------------------------------

def test_postings_compress_round_trip() -> None:
    assert decompress_postings(compress_postings(HAND)) == HAND


def test_compression_actually_shrinks_real_index() -> None:
    stats = compression_ratio(CORPUS)
    assert stats["raw_bytes"] > 0
    assert stats["packed_bytes"] > 0
    # delta+varint must beat raw int32 on this corpus
    assert stats["ratio"] > 1.5, stats


def test_compression_is_order_preserving() -> None:
    postings, _ = build_postings(CORPUS)
    for term, values in list(postings.items())[:50]:
        assert decompress_postings(compress_postings(values)) == values


# ---- skip pointers ---------------------------------------------------------

def test_skip_list_records_block_maximum() -> None:
    """The recorded value must be the block MAX, not its first entry."""
    values = list(range(0, 100))
    skips = build_skip_list(values, 10)
    assert skips[0] == (0, 9)      # block 0 is 0..9
    assert skips[1] == (10, 19)


def test_seek_finds_first_value_at_or_above_target() -> None:
    values = list(range(0, 100))
    skips = build_skip_list(values, 10)
    for target in (0, 5, 9, 10, 55, 99):
        pos, _ = seek(values, skips, 0, target)
        assert pos == target


def test_skips_match_plain_on_hand_examples() -> None:
    for interval in (1, 2, 3, 8, 32):
        assert sorted(intersect_with_skips(HAND, [1, 5, 40, 100], interval)) == \
            sorted(intersect_plain(HAND, [1, 5, 40, 100]))
        assert sorted(intersect_with_skips([1, 5, 40, 100], HAND, interval)) == \
            sorted(intersect_plain([1, 5, 40, 100], HAND))


def test_skips_match_plain_on_real_index() -> None:
    """All 48,841 term pairs of the real corpus must agree exactly."""
    postings, _ = build_postings(CORPUS)
    terms = sorted(postings)
    for t1 in terms:
        for t2 in terms:
            assert (sorted(intersect_with_skips(postings[t1], postings[t2]))
                    == sorted(intersect_plain(postings[t1], postings[t2]))), (t1, t2)


def test_skips_examine_fewer_postings() -> None:
    postings, _ = build_postings(CORPUS)
    a, b = postings["topic"], postings["the"]
    plain = count_comparisons_plain(a, b)
    skips = count_comparisons_skips(a, b)
    assert skips < plain


def test_empty_and_disjoint_lists() -> None:
    assert intersect_with_skips([], [1, 2]) == []
    assert intersect_with_skips([1, 2], []) == []
    assert intersect_with_skips([1, 2], [3, 4]) == []


# ---- block-max WAND --------------------------------------------------------

def test_build_blocks_records_maximum() -> None:
    values = [1, 5, 9, 40, 41, 100]
    scores = [0.1, 0.9, 0.2, 1.5, 0.3, 0.7]
    blocks = build_blocks(values, scores, block_size=3)
    assert blocks[0]["max_score"] == 0.9
    assert blocks[1]["max_score"] == 1.5
    assert blocks[1]["docs"] == [40, 41, 100]


def test_block_max_wand_finds_the_concatenation() -> None:
    """With one term only, WAND must return that term's documents."""
    values = [1, 3, 5, 7]
    scores = [0.5, 1.5, 0.25, 2.0]
    blocks = build_blocks(values, scores, block_size=2)
    blocks_by_term = {"a": blocks}
    hits = block_max_wand(blocks_by_term, ["a"], threshold=0.0, top_k=10)
    assert [h[0] for h in hits] == ["1", "3", "5", "7"]


def test_block_max_wand_threshold_prunes() -> None:
    """A high threshold must stop it early rather than score everything."""
    values = [1, 3, 5, 7, 9, 11]
    scores = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    blocks = build_blocks(values, scores, block_size=2)
    blocks_by_term = {"a": blocks}
    everything = block_max_wand(blocks_by_term, ["a"], threshold=0.0, top_k=99)
    pruned = block_max_wand(blocks_by_term, ["a"], threshold=10.0, top_k=99)
    assert len(everything) == 6
    assert pruned == []


def test_block_size_constant() -> None:
    assert BLOCK_SIZE >= 32
    assert SKIP_INTERVAL >= 8


# ---- misc ------------------------------------------------------------------

def test_tokenize() -> None:
    assert tokenize("Python builds an INDEX.") == ["python", "builds", "an", "index"]


def test_postings_lists_are_sorted_integers() -> None:
    postings, doc_ids = build_postings(CORPUS)
    assert len(doc_ids) == 204
    for values in postings.values():
        assert values == sorted(values)
        assert all(isinstance(v, int) for v in values)
