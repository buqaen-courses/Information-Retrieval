"""Starter: semantic search with embeddings — 4 TODOs.

Runs without crashing: unfinished TODOs print a friendly hint. Work top to
bottom.

Usage (from session-12-embeddings/, with the course venv active):
    python workshop/starter/numpy_semantic_search.py
"""
from __future__ import annotations

TODO_COUNT = 4
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

WARMUP = [
    "wireless headphones with noise cancelling",
    "a sturdy desk lamp for reading",
    "a cheap lamp that still works",
    "football boots for a muddy pitch",
    "soccer cleats with studs",
    "a laptop backpack for school",
    "a stainless steel kettle for tea",
    "an espresso machine for home",
    "running shoes for the marathon",
    "a waterproof rain jacket",
]


def load_model():
    """Load the cached bi-encoder (CPU, no network needed)."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed(model, sentences):
    """Turn sentences into L2-normalized float32 vectors. (TODO-1)"""
    # TODO-1: Snippet shape:
    #     import numpy as np
    #     vectors = model.encode(sentences, normalize_embeddings=True,
    #                            show_progress_bar=False,
    #                            convert_to_numpy=True)
    #     return np.asarray(vectors, dtype=np.float32)
    # (`normalize_embeddings=True` divides every row by its own length, so all
    #  vectors have length 1. That is what lets `search` use a plain dot
    #  product instead of dividing by both norms. `show_progress_bar=False`
    #  keeps the output readable when you run the starter.)
    raise NotImplementedError("TODO-1 not done yet — embed the sentences")


def cosine(a, b):
    """Cosine similarity between two already-normalized vectors. (TODO-2)"""
    # TODO-2: Snippet shape:
    #     import numpy as np
    #     return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    # (np.dot is the dot product; np.linalg.norm(v) is the length of v. Even
    #  though our vectors are already length 1, writing it out this way makes
    #  the formula visible — and it still works if you forget to normalize.)
    raise NotImplementedError("TODO-2 not done yet — compute cosine similarity")


def search(model, query, catalogue, top_k=5):
    """Return [(index, score), ...] best first. (TODO-3)"""
    # TODO-3: embed everything, score, sort. Snippet shape:
    #     import numpy as np
    #     if not catalogue:
    #         return []
    #     matrix = embed(model, catalogue)
    #     query_vector = embed(model, [query])[0]
    #     scores = matrix @ query_vector
    #     order = np.argsort(-scores)[:top_k]
    #     return [(int(i), float(scores[i])) for i in order]
    # (`@` is numpy's matrix multiply. Because every row of `matrix` and
    #  `query_vector` has length 1, the products ARE the cosine similarities.
    #  `-scores` makes the biggest score sort FIRST, which is the opposite of
    #  what np.argsort does by default.)
    raise NotImplementedError("TODO-3 not done yet — rank the catalogue")


def main():
    import sys
    args = sys.argv[1:]
    model = load_model()
    try:
        print("dimensions:", embed(model, ["x"]).shape[1])
        for query in ("soccer boots", "something to drink tea with"):
            print()
            print("query:", query)
            for rank, (index, score) in enumerate(search(model, query, WARMUP, 3), 1):
                print(f"  {rank}. {WARMUP[index]:<38} {score:.4f}")
    except NotImplementedError as exc:
        print(exc)
        print(f"({TODO_COUNT} TODOs total — work top to bottom.)")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())