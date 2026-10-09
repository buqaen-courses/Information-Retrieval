"""Measure the session-11 benchmark and write images/measurements.json.

Wall-clock timings are real hardware measurements, so they cannot be baked
into a deterministic chart: run make_images.py twice and the bars would differ.
So the measurement lives here, and images/make_images.py only READS the JSON.

Refresh the numbers (commit the result):

    python images/measure.py

The comparison counts are deterministic and are recomputed on every call, so
only the timings are persisted. Session 2's images use the same pattern.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "session-11-efficient-scoring" / "workshop" / "solution"))
from fast_score import (build_postings, count_comparisons_plain,  # noqa: E402
                        count_comparisons_skips, intersect_plain,
                        intersect_with_skips)

HERE = Path(__file__).resolve().parent
CORPUS = ROOT / "datasets" / "corpus"
REPEATS = 7


def best_of(fn, repeat: int = REPEATS) -> float:
    """Best wall-clock seconds over `repeat` runs — best-case is the stable one."""
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def main() -> None:
    """Measure both strategies on a common term pair and persist the timings."""
    postings, _ = build_postings(CORPUS)
    left, right = postings["topic"], postings["the"]

    plain_seconds = best_of(lambda: intersect_plain(left, right))
    skip_seconds = best_of(lambda: intersect_with_skips(left, right, 32))
    hits = len(intersect_plain(left, right))

    data = {
        "query": "topic the",
        "hits": hits,
        "plain": {
            "milliseconds": round(plain_seconds * 1000, 3),
            "comparisons": count_comparisons_plain(left, right),
        },
        "skips": {
            "interval": 32,
            "milliseconds": round(skip_seconds * 1000, 3),
            "comparisons": count_comparisons_skips(left, right, 32),
        },
    }
    (HERE / "measurements.json").write_text(json.dumps(data, indent=2) + "\n",
                                           encoding="utf-8")
    print(json.dumps(data, indent=2))
    print(f"\nwrote {HERE / 'measurements.json'}")
    print("comparisons are deterministic; milliseconds are hardware-specific.")


if __name__ == "__main__":
    main()
