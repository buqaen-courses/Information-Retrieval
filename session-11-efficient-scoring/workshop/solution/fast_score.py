"""Efficient retrieval: delta+varint posting compression, skip pointers, WAND.

Usage (from session-11-efficient-scoring/):
    python workshop/solution/fast_score.py ../../datasets/corpus "python search"
    python workshop/solution/fast_score.py ../../datasets/corpus --bench
    python workshop/solution/fast_score.py ../../datasets/corpus --wand "python search"

Everything here is stdlib + numpy (numpy only for the benchmark timings).
"""
from __future__ import annotations

import os
import struct
import sys
import time
from collections import defaultdict

PUNCTUATION = ".,!?;:'\"()"
SKIP_INTERVAL = 32       # one skip pointer every N postings entries
BLOCK_SIZE = 128         # one block-max block per this many postings


def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into terms."""
    tokens = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word:
            tokens.append(word)
    return tokens


def list_doc_ids(folder: str) -> list[str]:
    """Sorted document ids in folder."""
    return [n[:-4] for n in sorted(os.listdir(folder)) if n.endswith(".txt")]


def build_postings(folder: str) -> tuple[dict[str, list[int]], list[int]]:
    """Return ({term: [doc_index, ...]}, doc_ids) using integer doc ids.

    Integers matter here: they compress (see delta encoding) where strings do not.
    """
    doc_ids = list_doc_ids(folder)
    index_of = {doc_id: i for i, doc_id in enumerate(doc_ids)}
    postings: dict[str, list[int]] = defaultdict(list)
    for doc_id in doc_ids:
        with open(os.path.join(folder, doc_id + ".txt"), mode="r",
                  encoding="utf-8") as f:
            for term in set(tokenize(f.read())):
                postings[term].append(index_of[doc_id])
    return {t: sorted(v) for t, v in postings.items()}, doc_ids


# --------------------------------------------------------------------------- #
# 1. Compression: gaps between consecutive doc ids
# --------------------------------------------------------------------------- #
def delta_encode(values: list[int]) -> list[int]:
    """Turn [3, 7, 9, 40] into [3, 4, 2, 31] — differences, first kept whole."""
    if not values:
        return []
    out = [values[0]]
    for i in range(1, len(values)):
        out.append(values[i] - values[i - 1])
    return out


def delta_decode(gaps: list[int]) -> list[int]:
    """Inverse of delta_encode."""
    if not gaps:
        return []
    out = [gaps[0]]
    for i in range(1, len(gaps)):
        out.append(out[-1] + gaps[i])
    return out


def varint_encode(value: int) -> bytes:
    """Encode a non-negative int in 1-7 bytes (LEB128, the format Lucene uses).

    Small numbers take one byte; only large ones grow. That is why deltas
    matter — document gaps are usually small, so they compress hard.
    """
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)      # continuation flag set
        else:
            out.append(byte)             # last byte
            break
    return bytes(out)


def varint_decode(data: bytes) -> list[int]:
    """Decode a whole buffer of varints written back to back."""
    out = []
    shift = 0
    result = 0
    for byte in data:
        result |= (byte & 0x7F) << shift
        if byte & 0x80:
            shift += 7
        else:
            out.append(result)
            result = 0
            shift = 0
    return out


def compress_postings(values: list[int]) -> bytes:
    """Delta-encode then varint-encode a postings list."""
    return b"".join(varint_encode(gap) for gap in delta_encode(values))


def decompress_postings(data: bytes) -> list[int]:
    """Inverse of compress_postings."""
    return delta_decode(varint_decode(data))


def compression_ratio(folder: str) -> dict[str, float]:
    """Measure raw vs compressed bytes across the whole index."""
    postings, _ = build_postings(folder)
    raw = 0
    packed = 0
    for values in postings.values():
        raw += len(values) * 4                      # one 32-bit int per doc id
        packed += len(compress_postings(values))
    return {"raw_bytes": float(raw), "packed_bytes": float(packed),
            "ratio": raw / packed if packed else 0.0}


# --------------------------------------------------------------------------- #
# 2. Skip pointers: jump over postings that cannot match
# --------------------------------------------------------------------------- #
def build_skip_list(values: list[int], interval: int = SKIP_INTERVAL
                    ) -> list[tuple[int, int]]:
    """Return [(block_start_index, block_max_doc_id), ...].

    Every `interval` entries we record where the block starts AND the largest
    document id inside it. The MAX is the part that matters: a block can only
    be skipped when its max is below the id you are looking for, because then
    every entry in it is provably too small. Recording only the first id (as an
    index would suggest) is the classic bug — it lets you jump over entries
    that are larger than your target.
    """
    skips: list[tuple[int, int]] = []
    for start in range(0, len(values), interval):
        end = min(start + interval, len(values))
        skips.append((start, values[end - 1]))
    if not skips:
        return [(0, -1)] if values else []
    return skips


def seek(right: list[int], skips: list[tuple[int, int]], pointer: int,
         target: int) -> tuple[int, int]:
    """Advance to the first position in `right` whose value is >= target.

    Returns (position, skip_index). Skips a whole block whenever that block's
    maximum document id is still below the target — such a block cannot
    contain the target, so every entry in it is work we can skip.

    `pointer` carries the skip index from the previous call and only moves
    forward, which keeps the whole traversal linear in the postings length.
    """
    n = len(right)
    while pointer < len(skips) and skips[pointer][1] < target:
        pointer += 1
    if pointer >= len(skips):
        return n, pointer
    pos = skips[pointer][0]
    while pos < n and right[pos] < target:
        pos += 1
        # about to walk past the next block: hop to its start instead
        nxt = pointer + 1
        if nxt < len(skips) and skips[nxt][0] <= pos:
            pointer = nxt
            pos = skips[nxt][0]
    return pos, pointer


def intersect_with_skips(left: list[int], right: list[int],
                         interval: int = SKIP_INTERVAL) -> list[int]:
    """AND two postings lists using skip pointers (smallest list drives).

    For each target document in the shorter list we seek into the longer one.
    Skipped entries are provably all below the target, so the answer is
    identical to a naive scan — only the work saved.
    """
    if not left or not right:
        return []
    if len(left) > len(right):
        left, right = right, left
    skips = build_skip_list(right, interval)
    hits: list[int] = []
    pointer = 0
    for target in left:
        pos, pointer = seek(right, skips, pointer, target)
        if pos < len(right) and right[pos] == target:
            hits.append(target)
    return hits



# --------------------------------------------------------------------------- #
# 3. Block-max WAND: stop before you start (demonstration, instructor-led)
# --------------------------------------------------------------------------- #
def build_blocks(values: list[int], max_scores: list[float],
                 block_size: int = BLOCK_SIZE) -> list[dict]:
    """Group postings into blocks, remembering each block's maximum score.

    A block whose maximum is too low can never contribute enough to the current
    top-k, so it can be skipped whole.
    """
    blocks = []
    for start in range(0, len(values), block_size):
        end = min(start + block_size, len(values))
        chunk_scores = max_scores[start:end]
        blocks.append({"start": start, "end": end,
                       "docs": values[start:end],
                       "max_score": max(chunk_scores) if chunk_scores else 0.0})
    return blocks


def block_max_wand(blocks_by_term: dict[str, list[dict]], query_terms: list[str],
                   threshold: float, top_k: int = 10) -> list[tuple[str, float]]:
    """Block-max WAND demonstration.

    Each postings list is cut into blocks that remember the best score any
    document inside them could produce. We walk the lists in lockstep and stop
    as soon as the largest block maximum still available is below the
    threshold: past that point no unseen document can qualify, so the rest of
    the index is skipped without being touched.

    Teaching version: it keeps the pruning idea and the termination rule, and
    drops the pivot ordering and dynamic thresholding a production engine adds.
    """
    # position of the next unprocessed document in each block
    cursor = {t: 0 for t in query_terms}          # index inside the current block
    block = {t: 0 for t in query_terms}          # index of the current block
    scored: dict[int, float] = {}

    while True:
        # 1. if any list is exhausted we are done
        done = False
        for term in query_terms:
            if block[term] >= len(blocks_by_term[term]):
                done = True
        if done:
            break

        # 2. prune using the best score still reachable in each list
        best_remaining = 0.0
        for term in query_terms:
            b = blocks_by_term[term][block[term]]
            remaining = b["max_score"]
            best_remaining = max(best_remaining, remaining)
        if best_remaining < threshold:
            break

        # 3. the next candidate is the smallest document still in front of us
        pivot = None
        for term in query_terms:
            b = blocks_by_term[term][block[term]]
            doc = b["docs"][cursor[term]]
            pivot = doc if pivot is None else min(pivot, doc)

        # 4. every list must actually contain the pivot to be scored
        total = 0.0
        matched = True
        for term in query_terms:
            b = blocks_by_term[term][block[term]]
            if pivot in b["docs"]:
                total += b["max_score"]
            else:
                matched = False
        if matched:
            scored[pivot] = total

        # 5. consume the pivot in every list, rolling into the next block when
        #    the current one is used up
        for term in query_terms:
            b = blocks_by_term[term][block[term]]
            if pivot in b["docs"]:
                cursor[term] = b["docs"].index(pivot) + 1
            if cursor[term] >= len(b["docs"]):
                block[term] += 1
                cursor[term] = 0

    ranked = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(str(doc), score) for doc, score in ranked[:top_k]]


# --------------------------------------------------------------------------- #
# 4. Benchmark
# --------------------------------------------------------------------------- #
def _timed(fn, repeat: int = 5):
    """Return (best_seconds, result) over `repeat` runs — best-case is stable."""
    best = float("inf")
    result = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        result = fn()
        best = min(best, time.perf_counter() - t0)
    return best, result


def intersect_plain(left: list[int], right: list[int]) -> list[int]:
    """Naive AND: test membership of the shorter list in the longer one."""
    small, big = (left, right) if len(left) <= len(right) else (right, left)
    return [v for v in small if v in big]


def count_comparisons_plain(left: list[int], right: list[int]) -> int:
    """How many postings the naive AND actually looks at.

    This is the portable cost measure: wall-clock in Python is dominated by
    interpreter overhead and by the fact that `x in list` is already a tight C
    loop, but the *number of postings examined* is what determines whether
    skip pointers pay off in a real engine.
    """
    small, big = (left, right) if len(left) <= len(right) else (right, left)
    examined = 0
    for value in small:
        for candidate in big:
            examined += 1
            if candidate == value:
                break
    return examined


def count_comparisons_skips(left: list[int], right: list[int],
                            interval: int = SKIP_INTERVAL) -> int:
    """Postings examined by the skip-pointer AND."""
    if not left or not right:
        return 0
    if len(left) > len(right):
        left, right = right, left
    skips = build_skip_list(right, interval)
    examined = 0
    pointer = 0
    n = len(right)
    for target in left:
        while pointer < len(skips) and skips[pointer][1] < target:
            pointer += 1
            examined += 1          # one comparison per block we jump
        if pointer >= len(skips):
            break
        pos = skips[pointer][0]
        while pos < n and right[pos] < target:
            pos += 1
            examined += 1
            nxt = pointer + 1
            if nxt < len(skips) and skips[nxt][0] <= pos:
                pointer = nxt
                pos = skips[nxt][0]
        if pos < n and right[pos] == target:
            examined += 1
    return examined


def bench(folder: str, query: str, interval: int = SKIP_INTERVAL) -> list[dict]:
    """Time and comparison-count plain vs skip-pointer intersection.

    Both columns are reported on purpose: wall-clock in pure Python does NOT
    favour skip pointers (see the README), while the comparison count does,
    and the comparison count is what predicts behaviour in a real engine.
    """
    postings, _ = build_postings(folder)
    terms = [t for t in tokenize(query) if t in postings]
    if len(terms) < 2:
        known = [t for t in tokenize(query) if t in postings]
        raise SystemExit(
            f"need two known terms, got {len(known)}: {known}\n"
            f"try a pair that exists, e.g. "
            f"'{' '.join(sorted(postings, key=lambda t: -len(postings[t]))[:2])}'")
    left, right = postings[terms[0]], postings[terms[1]]
    rows = []
    plain_sec, plain_hits = _timed(lambda: intersect_plain(left, right))
    skip_sec, skip_hits = _timed(lambda: intersect_with_skips(left, right, interval))
    assert sorted(plain_hits) == sorted(skip_hits), "skip pointers changed the result"
    rows.append({"strategy": "plain membership test", "seconds": plain_sec,
                 "comparisons": count_comparisons_plain(left, right),
                 "hits": len(plain_hits)})
    rows.append({"strategy": f"skip pointers (every {interval})",
                 "seconds": skip_sec,
                 "comparisons": count_comparisons_skips(left, right, interval),
                 "hits": len(skip_hits)})
    return rows


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: python fast_score.py <folder> [\"<query>\"] [--bench | --wand]")
        return 2
    folder = args[0]
    query = " ".join(a for a in args[1:] if not a.startswith("--"))
    postings, doc_ids = build_postings(folder)

    if "--compress" in args or not query:
        stats = compression_ratio(folder)
        print(f"documents: {len(doc_ids)}")
        print(f"terms: {len(postings)}")
        print(f"postings as int32 : {int(stats['raw_bytes']):,} bytes")
        print(f"delta + varint    : {int(stats['packed_bytes']):,} bytes")
        print(f"compression       : {stats['ratio']:.2f}x smaller")
        return 0

    if "--bench" in args:
        rows = bench(folder, query)
        print(f"query: {query}")
        print(f"{'strategy':<28}{'seconds':>10}{'comparisons':>14}{'hits':>8}")
        for row in rows:
            print(f"{row['strategy']:<28}{row['seconds'] * 1000:9.3f}ms"
                  f"{row['comparisons']:14d}{row['hits']:8d}")
        ratio = rows[0]["comparisons"] / max(1, rows[1]["comparisons"])
        print()
        print(f"skip pointers examined {ratio:.1f}x fewer postings")
        print("wall-clock may still favour the plain version in pure Python —")
        print("`x in list` is already a tight C loop. The comparison count is")
        print("the number that predicts a real engine's behaviour.")
        return 0

    terms = [t for t in tokenize(query) if t in postings]
    if not terms:
        print("no known terms in:", query)
        return 0
    print(f"query: {query}")
    for t in terms:
        print(f"  postings '{t}': {len(postings[t])} docs, "
              f"{len(compress_postings(postings[t]))} bytes packed")
    if len(terms) >= 2:
        hits = intersect_with_skips(postings[terms[0]], postings[terms[1]])
        print(f"  AND -> {len(hits)} docs: {[doc_ids[h] for h in hits[:10]]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
