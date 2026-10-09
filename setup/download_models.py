"""Pre-cache the two models the course needs (run once, online).

Usage (from the repo root, with the course venv active):
    python setup/download_models.py

Downloads into the local HuggingFace cache so every later session works
OFFLINE:

  1. sentence-transformers/all-MiniLM-L6-v2      -> Session 12 embeddings,
     Sessions 13-14 vector search, Session 22 kNN reranking
  2. cross-encoder/ms-marco-MiniLM-L-6-v2       -> Session 22 cross-encoder rerank

Both are small (~90 MB and ~90 MB) and CPU-friendly.

Offline usage afterwards:
    HF_HUB_OFFLINE=1 python ...
On Windows PowerShell:
    $env:HF_HUB_OFFLINE="1"; python ...
"""
from __future__ import annotations

import sys
import time

BI_ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def cache_bi_encoder() -> bool:
    """Download and smoke-test the bi-encoder. Returns True on success."""
    print(f"[1/2] bi-encoder: {BI_ENCODER}")
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(BI_ENCODER)
        vectors = model.encode(["a smoke test sentence"], normalize_embeddings=True)
        dim = len(vectors[0])
        print(f"      ok — output dimension {dim}")
        if dim != 384:
            print(f"      WARNING: expected 384 dims, got {dim}")
            return False
        return True
    except Exception as exc:  # noqa: BLE001 - report, never crash the prework
        print(f"      FAILED: {exc}")
        print("      Sessions 12-14 and 22 need this. Check your network and retry.")
        return False


def cache_cross_encoder() -> bool:
    """Download and smoke-test the cross-encoder. Returns True on success."""
    print(f"[2/2] cross-encoder: {CROSS_ENCODER}")
    try:
        from sentence_transformers import CrossEncoder

        model = CrossEncoder(CROSS_ENCODER)
        score = model.predict([["what is a search index", "an index speeds up search"]])
        print(f"      ok — smoke-test score {float(score[0]):.3f}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"      FAILED: {exc}")
        print("      Only Session 22 needs this; the rest of the course is fine.")
        return False


def main() -> int:
    """Cache both models and report overall status."""
    print(f"python: {sys.version.split()[0]}")
    t0 = time.perf_counter()
    bi_ok = cache_bi_encoder()
    cross_ok = cache_cross_encoder()
    dt = time.perf_counter() - t0
    print(f"\ndone in {dt:.1f}s — bi-encoder: {'OK' if bi_ok else 'FAILED'}, "
          f"cross-encoder: {'OK' if cross_ok else 'FAILED'}")
    if bi_ok and cross_ok:
        print("All models cached. Later sessions need no network.")
        return 0
    print("Some models failed. Re-run this script when you have a connection.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
