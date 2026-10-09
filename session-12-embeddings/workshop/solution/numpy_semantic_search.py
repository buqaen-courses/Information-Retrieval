"""Semantic search with sentence-transformers and pure numpy.

Usage (from session-12-embeddings/):
    python workshop/solution/numpy_semantic_search.py
    python workshop/solution/numpy_semantic_search.py "soccer boots"
    python workshop/solution/numpy_semantic_search.py --compare "sturdy lamp"

The model (sentence-transformers/all-MiniLM-L6-v2, 384 dimensions) is cached
locally by setup/download_models.py, so this runs offline.

Two ideas matter here:

1. An embedding model turns a sentence into a fixed-length vector where
   similar meanings land near each other. That is the whole trick.
2. Because every vector has the same length, similarity is one dot product
   after normalizing — no index, no inverted list, no set intersections.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRODUCTS_JSON = ROOT / "datasets" / "fallback_products.json"

# A tiny catalogue for the workshop. These are the sentences the comparison
# table is built from; the measured chart uses the full 128-product file.
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


def embed(model, sentences: list[str]) -> np.ndarray:
    """Turn sentences into L2-normalized float32 vectors.

    `normalize_embeddings=True` divides each row by its own length, so every
    vector has length 1. That is what makes cosine similarity a plain dot
    product in `search`.
    """
    vectors = model.encode(sentences, normalize_embeddings=True,
                           show_progress_bar=False, convert_to_numpy=True)
    return np.asarray(vectors, dtype=np.float32)


def load_products(limit: int | None = None) -> list[dict]:
    """Read the shared product dataset as searchable sentences."""
    import json

    products = json.loads(PRODUCTS_JSON.read_text(encoding="utf-8"))
    if limit:
        products = products[:limit]
    return products


def product_sentence(product: dict) -> str:
    """The one string we embed for a product: name + description."""
    return f"{product['name']}. {product['description']}"


def search(model, query: str, catalogue: list[str], top_k: int = 5
           ) -> list[tuple[int, float]]:
    """Return [(index, cosine_similarity), ...] best first.

    Every catalogue vector already has length 1, so `query_vector @ matrix.T`
    gives the cosine similarity directly — no division, no loop.
    """
    matrix = embed(model, catalogue)
    query_vector = embed(model, [query])[0]
    scores = matrix @ query_vector
    order = np.argsort(-scores)[:top_k]
    return [(int(i), float(scores[i])) for i in order]


def show(model, query: str, catalogue: list[str], labels: list[str],
         top_k: int = 5) -> None:
    """Print the top hits for a query."""
    print(f"query: {query}")
    for rank, (index, score) in enumerate(search(model, query, catalogue, top_k), 1):
        print(f"  {rank}. {labels[index]:<38} {score:.4f}")
    print()


def compare(model, query: str, pairs: list[tuple[str, str]]) -> None:
    """Show how a query ranks one description vs a near-synonym of it.

    This is the session's central demonstration: two sentences that share few
    or no words can still be the closest match in meaning.
    """
    left, right = pairs
    texts = [left, right]
    vectors = embed(model, texts)
    query_vector = embed(model, [query])[0]
    scores = vectors @ query_vector
    print(f"query: {query}")
    for text, score in zip(texts, scores):
        print(f"  {score:.4f}  {text}")
    winner = left if scores[0] >= scores[1] else right
    print(f"  -> winner: {winner}")
    print()


def main(argv: list[str] | None = None) -> int:
    """Run the workshop demo: warm-up set, real products, then a comparison."""
    args = argv if argv is not None else sys.argv[1:]
    model = load_model()
    print(f"model: {MODEL_NAME}")
    print(f"dimensions: {embed(model, ['x']).shape[1]}")
    print()

    labels = [f"{i}: {text[:30]}" for i, text in enumerate(WARMUP)]

    if "--compare" in args:
        query = args[args.index("--compare") + 1]
        compare(model, query, [
            "a sturdy desk lamp for reading",
            "a robust table light with a strong arm",
        ])
        return 0

    if args:
        show(model, " ".join(args), WARMUP, labels, top_k=5)
        return 0

    show(model, "soccer boots", WARMUP, labels, top_k=3)
    show(model, "something to drink tea with", WARMUP, labels, top_k=3)
    show(model, "a machine that makes coffee", WARMUP, labels, top_k=3)

    products = load_products(limit=30)
    catalogue = [product_sentence(p) for p in products]
    names = [p["name"] for p in products]
    show(model, "durable backpack for travel", catalogue, names, top_k=5)

    print(f"embedded {len(catalogue)} real products from "
          f"datasets/fallback_products.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())