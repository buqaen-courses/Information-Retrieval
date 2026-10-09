"""The same embeddings in two vector databases: Milvus Lite and LanceDB.

Usage (from session-13-vector-databases/):
    python workshop/solution/compare_vector_dbs.py
    python workshop/solution/compare_vector_dbs.py "soccer boots"

Both databases store the SAME vectors and answer the SAME queries. The point of
this session is not that one is better — it is that you now know how to move a
catalogue into either one, and what each costs.

Milvus Lite is an embedded Milvus: one local file, no server, the same API a
production Milvus cluster uses. LanceDB is embedded and columnar, storing rows
in the Apache Arrow/Lance format with vectors alongside your other columns.

Nothing here needs a server, a Docker container or a network connection.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT_DIR = HERE / "vectors"
PRODUCTS_JSON = ROOT / "datasets" / "fallback_products.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DIM = 384

QUERIES = ["soccer boots", "something to drink tea with", "a sturdy lamp"]


# --------------------------------------------------------------------------- #
# shared: load the model and the catalogue once
# --------------------------------------------------------------------------- #
def load_model():
    """The cached bi-encoder from Session 12."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def load_catalogue(limit: int | None = None) -> tuple[list[str], list[str], np.ndarray]:
    """Return (ids, texts, normalized vectors) for the product dataset."""
    products = json.loads(PRODUCTS_JSON.read_text(encoding="utf-8"))
    if limit:
        products = products[:limit]
    ids = [p["id"] for p in products]
    texts = [f"{p['name']}. {p['description']}" for p in products]

    model = load_model()
    vectors = model.encode(texts, normalize_embeddings=True,
                           show_progress_bar=False, convert_to_numpy=True)
    return ids, texts, np.asarray(vectors, dtype=np.float32)


def query_vector(model, query: str) -> np.ndarray:
    """Embed one query, normalized the same way as the documents."""
    return np.asarray(model.encode([query], normalize_embeddings=True,
                                   show_progress_bar=False),
                      dtype=np.float32)[0]


# --------------------------------------------------------------------------- #
# Milvus Lite
# --------------------------------------------------------------------------- #
def _dir_size(path: Path) -> int:
    """Total bytes under a path (Milvus Lite writes a directory, not a file)."""
    if path.is_dir():
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return path.stat().st_size if path.exists() else 0


def _fresh_path(path: Path) -> Path:
    """Return an unused path, deleting the old one when we are allowed to.

    On Windows a previously opened Milvus Lite file can stay locked, so rather
    than failing we move the new database to a fresh name.
    """
    if path.exists():
        try:
            path.unlink()
        except OSError:
            stem = path.stem
            suffix = path.suffix
            for n in range(2, 100):
                candidate = path.with_name(f"{stem}-{n}{suffix}")
                if not candidate.exists():
                    return candidate
            raise
    return path


class MilvusLiteIndex:
    """An embedded Milvus collection, cosine/IP search over float vectors."""

    name = "milvus_lite"

    def __init__(self, path: Path, collection: str = "products") -> None:
        self.path = path
        self.collection = collection
        self.client = None

    def build(self, ids: list[str], texts: list[str], vectors: np.ndarray
              ) -> float:
        """Create the collection and insert every row. Returns seconds."""
        from pymilvus import DataType, MilvusClient

        self.close()
        self.path = _fresh_path(self.path)
        start = time.perf_counter()
        self.client = MilvusClient(str(self.path))
        schema = MilvusClient.create_schema(auto_id=False,
                                            enable_dynamic_field=False)
        schema.add_field("pk", DataType.INT64, is_primary=True)
        schema.add_field("doc_id", DataType.VARCHAR, max_length=32)
        schema.add_field("text", DataType.VARCHAR, max_length=1024)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=DIM)
        self.client.create_collection(self.collection, schema=schema)

        rows = []
        for i, (doc_id, text) in enumerate(zip(ids, texts)):
            rows.append({"pk": i, "doc_id": doc_id, "text": text,
                         "vector": vectors[i].tolist()})
        self.client.insert(self.collection, rows)
        return time.perf_counter() - start

    def search(self, vector: np.ndarray, k: int = 5) -> list[tuple[str, float]]:
        """Return [(doc_id, cosine_similarity), ...] best first.

        Milvus reports `distance`; for normalized vectors on the default metric
        that value IS the cosine similarity, so it needs no conversion.
        """
        raw = self.client.search(self.collection, data=[vector.tolist()],
                                 limit=k, output_fields=["doc_id"])
        return [(hit["entity"]["doc_id"], float(hit["distance"]))
                for hit in raw[0]]

    def close(self) -> None:
        """Release the local database file."""
        if self.client is not None:
            self.client.close()
            self.client = None


# --------------------------------------------------------------------------- #
# LanceDB
# --------------------------------------------------------------------------- #
class LanceIndex:
    """A LanceDB table: columns plus a vector column, searched by L2."""

    name = "lancedb"

    def __init__(self, path: Path, table: str = "products") -> None:
        self.path = path
        self.table_name = table
        self.table = None

    def build(self, ids: list[str], texts: list[str], vectors: np.ndarray
              ) -> float:
        """Create the table and add every row. Returns seconds."""
        import lancedb
        import pyarrow as pa

        if self.path.exists():
            shutil.rmtree(self.path)
        start = time.perf_counter()
        db = lancedb.connect(str(self.path))
        schema = pa.schema([
            pa.field("pk", pa.int64()),
            pa.field("doc_id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), DIM)),
        ])
        rows = [{"pk": i, "doc_id": doc_id, "text": text,
                 "vector": vectors[i].tolist()}
                for i, (doc_id, text) in enumerate(zip(ids, texts))]
        self.table = db.create_table(self.table_name, schema=schema, data=rows)
        return time.perf_counter() - start

    def search(self, vector: np.ndarray, k: int = 5) -> list[tuple[str, float]]:
        """Return [(doc_id, cosine_similarity), ...] best first.

        LanceDB searches with squared L2 by default and reports it as
        `_distance`. For two vectors of length 1:
            ||a - b||^2 = 2 - 2 * (a . b)
        so the cosine similarity is `(2 - _distance) / 2`. Converting here keeps
        the two databases comparable.
        """
        rows = (self.table.search(vector.tolist()).limit(k).to_list())
        return [(row["doc_id"], (2.0 - float(row["_distance"])) / 2.0)
                for row in rows]

    def create_index(self) -> None:
        """Build the IVF-PQ vector index (the ANN structure of Session 12)."""
        from lancedb.index import IvfPq

        self.table.create_index("vector", config=IvfPq(num_partitions=4,
                                                       num_sub_vectors=4))

    def close(self) -> None:
        """Nothing to release: LanceDB is file-backed and self-contained."""
        self.table = None


# --------------------------------------------------------------------------- #
# the comparison
# --------------------------------------------------------------------------- #
def brute_force(vector: np.ndarray, vectors: np.ndarray, ids: list[str],
                k: int = 5) -> list[tuple[str, float]]:
    """Exact search from Session 12, used as the ground truth to compare against."""
    scores = vectors @ vector
    order = np.argsort(-scores)[:k]
    return [(ids[i], float(scores[i])) for i in order]


def main(argv: list[str] | None = None) -> int:
    """Index one catalogue into both databases and answer the same queries."""
    args = argv if argv is not None else sys.argv[1:]
    queries = [" ".join(args)] if args else QUERIES

    print("loading catalogue and embedding every product...")
    start = time.perf_counter()
    ids, texts, vectors = load_catalogue()
    embed_seconds = time.perf_counter() - start
    print(f"documents: {len(ids)} | dimensions: {vectors.shape[1]} "
          f"| embedding took {embed_seconds:.2f}s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    milvus = MilvusLiteIndex(OUT_DIR / "milvus_lite.db")
    lancedb_index = LanceIndex(OUT_DIR / "lancedb")

    milvus_build = milvus.build(ids, texts, vectors)
    lancedb_build = lancedb_index.build(ids, texts, vectors)
    lancedb_index.create_index()

    print()
    print(f"build time: milvus_lite {milvus_build:.3f}s | "
          f"lancedb {lancedb_build:.3f}s")

    model = load_model()
    header = f"{'query':<32}{'backend':<14}{'top-1 id':<12}{'score':>8}"
    print(header)
    print("-" * len(header))
    for query in queries:
        vector = query_vector(model, query)
        exact = brute_force(vector, vectors, ids, k=1)[0]
        print(f"{query[:30]:<32}{'brute force':<14}{exact[0]:<12}{exact[1]:>8.4f}")
        for backend in (milvus, lancedb_index):
            best = backend.search(vector, k=1)[0]
            print(f"{'':<32}{backend.name:<14}{best[0]:<12}{best[1]:>8.4f}")
        print()

    agree = 0
    for query in queries:
        vector = query_vector(model, query)
        exact_ids = [d for d, _ in brute_force(vector, vectors, ids, k=5)]
        for backend in (milvus, lancedb_index):
            backend_ids = [d for d, _ in backend.search(vector, k=5)]
            agree += int(backend_ids == exact_ids)
    total = len(queries) * 2
    print(f"exact top-5 agreement: {agree}/{total} "
          f"(approximate indexes may drop a borderline document)")

    # Milvus Lite buffers writes, so the files only reflect them after close().
    milvus.close()
    milvus_bytes = _dir_size(milvus.path)
    lancedb_bytes = _dir_size(lancedb_index.path)
    print()
    print(f"on disk after close: milvus {milvus_bytes:,} bytes | "
          f"lancedb {lancedb_bytes:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())