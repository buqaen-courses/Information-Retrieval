"""Starter: efficient retrieval — compression, skip pointers, WAND demo — 6 TODOs.

Runs without crashing: unfinished TODOs print a friendly hint. Work top to
bottom.

Usage (from session-11-efficient-scoring/):
    python workshop/starter/fast_score.py ../../datasets/corpus --compress
"""
from __future__ import annotations

TODO_COUNT = 6
PUNCTUATION = ".,!?;:'\"()"
SKIP_INTERVAL = 32
BLOCK_SIZE = 128


def tokenize(text: str) -> list[str]:
    tokens = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word:
            tokens.append(word)
    return tokens


def list_doc_ids(folder: str) -> list[str]:
    import os
    return [n[:-4] for n in sorted(os.listdir(folder)) if n.endswith(".txt")]


def build_postings(folder: str):
    """Return ({term: [doc_index, ...]}, doc_ids) with integer doc ids."""
    from collections import defaultdict
    doc_ids = list_doc_ids(folder)
    index_of = {d: i for i, d in enumerate(doc_ids)}
    postings = defaultdict(list)
    for doc_id in doc_ids:
        with open(folder + "/" + doc_id + ".txt", mode="r", encoding="utf-8") as f:
            for term in set(tokenize(f.read())):
                postings[term].append(index_of[doc_id])
    return {t: sorted(v) for t, v in postings.items()}, doc_ids


# ---- 1. delta encoding -----------------------------------------------------

def delta_encode(values):
    """[3, 7, 9, 40] -> [3, 4, 2, 31]. (TODO-1)"""
    # TODO-1: Snippet shape:
    #     if not values:
    #         return []
    #     out = [values[0]]
    #     for i in range(1, len(values)):
    #         out.append(values[i] - values[i - 1])
    #     return out
    # (The first value stays whole because it has nothing to differ from.
    #  Small gaps are exactly what makes the next step compress well.)
    raise NotImplementedError("TODO-1 not done yet — delta_encode")


def delta_decode(gaps):
    """Inverse of delta_encode. (TODO-2)"""
    # TODO-2: Snippet shape:
    #     if not gaps:
    #         return []
    #     out = [gaps[0]]
    #     for i in range(1, len(gaps)):
    #         out.append(out[-1] + gaps[i])
    #     return out
    # (`out[-1]` is the value you just rebuilt, so you never touch the input.)
    raise NotImplementedError("TODO-2 not done yet — delta_decode")


# ---- 2. varint -------------------------------------------------------------

def varint_encode(value):
    """Encode a non-negative int in 1-7 bytes (LEB128). (TODO-3)"""
    # TODO-3: Snippet shape:
    #     out = bytearray()
    #     while True:
    #         byte = value & 0x7F
    #         value = value >> 7
    #         if value:
    #             out.append(byte | 0x80)
    #         else:
    #             out.append(byte)
    #             break
    #     return bytes(out)
    # (`value & 0x7F` takes the low 7 bits. The 0x80 flag says "more bytes
    #  follow", so the decoder knows when to stop. Values under 128 cost 1 byte.)
    raise NotImplementedError("TODO-3 not done yet — varint_encode")


def varint_decode(data):
    """Decode a buffer of varints written back to back. (TODO-4)"""
    # TODO-4: Snippet shape:
    #     out = []
    #     shift = 0
    #     result = 0
    #     for byte in data:
    #         result = result | ((byte & 0x7F) << shift)
    #         if byte & 0x80:
    #             shift = shift + 7
    #         else:
    #             out.append(result)
    #             result = 0
    #             shift = 0
    #     return out
    # (The shift moves each new 7-bit group into its byte position. Without
    #  resetting, results from two numbers would bleed into each other.)
    raise NotImplementedError("TODO-4 not done yet — varint_decode")


def compress_postings(values):
    """delta_encode then varint-encode every gap. (TODO-5)"""
    # TODO-5: Snippet shape:
    #     out = b""
    #     for gap in delta_encode(values):
    #         out = out + varint_encode(gap)
    #     return out
    # (b"" is an empty bytes object; bytes + bytes concatenates.)
    raise NotImplementedError("TODO-5 not done yet — compress_postings")


def decompress_postings(data):
    """Inverse of compress_postings. (TODO-5, same stop)"""
    # TODO-5 (continued): Snippet shape:
    #     return delta_decode(varint_decode(data))
    raise NotImplementedError("TODO-5 not done yet — decompress_postings")


# ---- 3. skip pointers ------------------------------------------------------

def build_skip_list(values, interval=SKIP_INTERVAL):
    """[(block_start_index, block_MAX_doc_id), ...]. (TODO-6)"""
    # TODO-6: Snippet shape:
    #     skips = []
    #     for start in range(0, len(values), interval):
    #         end = min(start + interval, len(values))
    #         skips.append((start, values[end - 1]))
    #     return skips
    # THE TRAP: record values[end - 1], the block's MAXIMUM, NOT values[start].
    # A block may only be skipped when its maximum is below the target you are
    # hunting. Record the first id instead and you jump over entries that are
    # larger than your target, silently losing matches.
    raise NotImplementedError("TODO-6 not done yet — build_skip_list")


def seek(right, skips, pointer, target):
    """First position in `right` whose value is >= target, using skips."""
    n = len(right)
    while pointer < len(skips) and skips[pointer][1] < target:
        pointer += 1
    if pointer >= len(skips):
        return n, pointer
    pos = skips[pointer][0]
    while pos < n and right[pos] < target:
        pos += 1
        nxt = pointer + 1
        if nxt < len(skips) and skips[nxt][0] <= pos:
            pointer = nxt
            pos = skips[nxt][0]
    return pos, pointer


def intersect_with_skips(left, right, interval=SKIP_INTERVAL):
    """AND two postings lists using skip pointers."""
    if not left or not right:
        return []
    if len(left) > len(right):
        left, right = right, left
    skips = build_skip_list(right, interval)
    hits = []
    pointer = 0
    for target in left:
        pos, pointer = seek(right, skips, pointer, target)
        if pos < len(right) and right[pos] == target:
            hits.append(target)
    return hits


def intersect_plain(left, right):
    """Naive AND, for comparison and as the correctness reference."""
    small, big = (left, right) if len(left) <= len(right) else (right, left)
    return [v for v in small if v in big]


def main():
    import sys
    args = sys.argv[1:]
    folder = args[0] if args else "../../datasets/corpus"
    postings, doc_ids = build_postings(folder)
    sample = postings[sorted(postings)[0]][:20]
    try:
        # surface the EARLIEST unfinished TODO, not whichever one the call
        # order happens to reach first
        delta_encode(sample)                       # TODO-1
        delta_decode(delta_encode(sample))         # TODO-2
        varint_encode(1)                            # TODO-3
        varint_decode(varint_encode(1))             # TODO-4
        packed = compress_postings(sample)          # TODO-5 and TODO-6
        restored = decompress_postings(packed)
    except NotImplementedError as exc:
        print(exc)
        print(f"({TODO_COUNT} TODOs total — work top to bottom.)")
        return 0
    print("documents:", len(doc_ids))
    print("terms:", len(postings))
    print("sample postings:", sample)
    print("packed bytes:", len(packed))
    print("restored ok:", restored == sample)
    return 0


if __name__ == "__main__":
    main()
