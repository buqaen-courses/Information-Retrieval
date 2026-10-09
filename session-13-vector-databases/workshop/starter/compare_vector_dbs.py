"""Starter: two vector databases, one catalogue — 4 TODOs.

Runs without crashing: unfinished TODOs print a friendly hint. Work top to
bottom.

Usage (from session-13-vector-databases/, with the course venv active):
    python workshop/starter/compare_vector_dbs.py

Both databases are embedded: no server, no Docker, no network.
"""
from __future__ import annotations

TODO_COUNT = 4
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DIM = 384
QUERIES = ["soccer boots", "something to drink tea with", "a sturdy lamp"]


def load_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def load_catalogue(limit: int | None = None):
    """Return (ids, texts, normalized vectors) for the product dataset. (TODO-1)"""
    # TODO-1: read the JSON, build one text per product, embed them all.
    # Snippet shape:
    #     import json
    #     from pathlib import Path
    #     import numpy as np
    #     root = Path(__file__).resolve().parents[3]
    #     products = json.loads((root / "datasets" / "fallback_products.json")
    #                          .read_text(encoding="utf-8"))
    #     if limit:
    #         products = products[:limit]
    #     ids = [p["id"] for p in products]
    #     texts = [p["name"] + ". " + p["description"] for p in products]
    #     model = load_model()
    #     vectors = model.encode(texts, normalize_embeddings=True,
    #                            show_progress_bar=False,
    #                            convert_to_numpy=True)
    #     return ids, texts, np.asarray(vectors, dtype=np.float32)
    # (`parents[3]` walks solution/ -> workshop/ -> session -> repo root. The
    #  whole catalogue is embedded in ONE call, which is what you would do at
    #  index time: never embed one document per query.)
    raise NotImplementedError("TODO-1 not done yet — load and embed the catalogue")


class MilvusLiteIndex:
    """Embedded Milvus. (TODO-2)"""

    name = "milvus_lite"

    def __init__(self, path, collection="products"):
        self.path = path
        self.collection = collection
        self.client = None

    def build(self, ids, texts, vectors):
        """Create the schema and insert the rows. (TODO-2)"""
        # TODO-2: Snippet shape:
        #     from pymilvus import DataType, MilvusClient
        #     self.client = MilvusClient(str(self.path))
        #     schema = MilvusClient.create_schema(auto_id=False,
        #                                            enable_dynamic_field=False)
        #     schema.add_field("pk", DataType.INT64, is_primary=True)
        #     schema.add_field("doc_id", DataType.VARCHAR, max_length=32)
        #     schema.add_field("text", DataType.VARCHAR, max_length=1024)
        #     schema.add_field("vector", DataType.FLOAT_VECTOR, dim=DIM)
        #     self.client.create_collection(self.collection, schema=schema)
        #     rows = [{"pk": i, "doc_id": d, "text": t,
        #              "vector": vectors[i].tolist()}
        #             for i, (d, t) in enumerate(zip(ids, texts))]
        #     self.client.insert(self.collection, rows)
        # (Milvus wants a real primary key, so we add an integer "pk" and keep
        #  our string id as an ordinary column. Vectors go in as Python lists
        #  because .tolist() is what the wire format expects.)
        raise NotImplementedError("TODO-2 not done yet — build the Milvus collection")

    def search(self, vector, k=5):
        """Return [(doc_id, cosine_similarity), ...] best first."""
        raw = self.client.search(self.collection, data=[vector.tolist()],
                                 limit=k, output_fields=["doc_id"])
        return [(hit["entity"]["doc_id"], float(hit["distance"]))
                for hit in raw[0]]

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None


class LanceIndex:
    """LanceDB table. (TODO-3)"""

    name = "lancedb"

    def __init__(self, path, table="products"):
        self.path = path
        self.table_name = table
        self.table = None

    def build(self, ids, texts, vectors):
        """Create the Arrow table and add the rows. (TODO-3)"""
        # TODO-3: Snippet shape:
        #     import lancedb, pyarrow as pa
        #     db = lancedb.connect(str(self.path))
        #     schema = pa.schema([
        #         pa.field("pk", pa.int64()),
        #         pa.field("doc_id", pa.string()),
        #         pa.field("text", pa.string()),
        #         pa.field("vector", pa.list_(pa.float32(), DIM)),
        #     ])
        #     rows = [{"pk": i, "doc_id": d, "text": t,
        #              "vector": vectors[i].tolist()}
        #             for i, (d, t) in enumerate(zip(ids, texts))]
        #     self.table = db.create_table(self.table_name, schema=schema,
        #                                  data=rows)
        # (pyarrow defines the columns; the vector column must be declared as
        #  a fixed-length list of float32 so LanceDB knows it is a vector.)
        raise NotImplementedError("TODO-3 not done yet — build the LanceDB table")

    def search(self, vector, k=5):
        """Return [(doc_id, cosine_similarity), ...] best first. (TODO-4)"""
        # TODO-4: LanceDB reports squared L2 as `_distance`. Snippet shape:
        #     rows = self.table.search(vector.tolist()).limit(k).to_list()
        #     return [(row["doc_id"], (2.0 - float(row["_distance"])) / 2.0)
        #             for row in rows]
        # THE CONVERSION THAT MATTERS: for two vectors of length 1,
        #     ||a - b||^2 = 2 - 2*(a . b)
        # so the cosine similarity is (2 - _distance)/2. Without this line the
        # two databases report numbers on different scales and the comparison
        # table is meaningless. An identical vector has _distance 0 -> 1.0.
        raise NotImplementedError("TODO-4 not done yet — search and convert distance")


def brute_force(vector, vectors, ids, k=5):
    """Exact search from Session 12: the ground truth both databases must match."""
    import numpy as np

    scores = vectors @ vector
    order = np.argsort(-scores)[:k]
    return [(ids[i], float(scores[i])) for i in order]


def main():
    import tempfile
    from pathlib import Path

    try:
        ids, texts, vectors = load_catalogue(limit=20)
    except NotImplementedError as exc:
        print(exc)
        print(f"({TODO_COUNT} TODOs total — work top to bottom.)")
        return 0

    tmp = Path(tempfile.mkdtemp(prefix="s13_starter_"))
    milvus = MilvusLiteIndex(tmp / "milvus.db")
    lance = LanceIndex(tmp / "lancedb")
    model = load_model()
    import numpy as np

    query = np.asarray(model.encode(["soccer boots"], normalize_embeddings=True,
                                    show_progress_bar=False),
                       dtype=np.float32)[0]
    try:
        for backend in (milvus, lance):
            backend.build(ids, texts, vectors)
            best = backend.search(query, k=1)[0]
            print(f"{backend.name:<14} top-1 {best[0]}  {best[1]:.4f}")
        print("brute force     top-1",
              brute_force(query, vectors, ids, k=1)[0])
    except NotImplementedError as exc:
        print(exc)
        print(f"({TODO_COUNT} TODOs total — work top to bottom.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())