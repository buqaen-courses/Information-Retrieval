"""SemanticSearch: a reusable engine with metadata filtering.

Usage (from session-14-semantic-engine/):
    python workshop/solution/semantic_search.py
    python workshop/solution/semantic_search.py "something to warm tea with"
    python workshop/solution/semantic_search.py --category kitchen "boots"
    python workshop/solution/semantic_search.py --no-index          # force slow path

This module is the class Sessions 22 and 23 import. Keep its public surface
small and stable:

    SemanticSearch(records, index_dir=..., model=...)
    .build()                              # embed once, write the table
    .search(query, k=5, category=None)    # returns [(record, score), ...]
    .save(path) / .load(path)             # persist without re-embedding

Storage is LanceDB: vectors live in ordinary columnar files next to the text
and the metadata, so `category` filtering is a columnar operation rather than
something we have to bolt on afterwards.
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DIM = 384
ROOT = Path(__file__).resolve().parents[3]
PRODUCTS_JSON = ROOT / "datasets" / "fallback_products.json"


@dataclass
class SearchHit:
    """One search result: the original record plus its similarity score."""

    record: dict[str, Any]
    score: float

    @property
    def id(self) -> str:
        """The record's id."""
        return str(self.record.get("id", ""))

    def __repr__(self) -> str:
        """Readable form used by the demo output."""
        return f"<SearchHit {self.id} {self.score:.4f}>"


@dataclass
class _State:
    """Everything needed to answer a query without touching the model."""

    records: list[dict[str, Any]] = field(default_factory=list)
    vectors: np.ndarray | None = None
    index_path: Path | None = None
    has_index: bool = False


class SemanticSearch:
    """Embed a set of records once, then answer meaning-based queries.

    Two things this class exists to get right, both of which bite in production:

    * **Embed once, query cheaply.** `build()` runs the model over every record.
      `search()` embeds only the query, which is why latency does not grow with
      the size of the catalogue.
    * **Missing embeddings are a data problem, not a crash.** A record with no
      vector is skipped and reported, never silently scored as zero.
    """

    def __init__(self, records: list[dict[str, Any]],
                 index_dir: Path | str | None = None,
                 model=None,
                 text_field: str = "text") -> None:
        """Create an engine over `records`.

        `records` is a list of dicts; each needs an `id` and whatever field
        holds its searchable text. `index_dir` is where the LanceDB table is
        written; it defaults to a folder beside this module.
        """
        self.records = list(records)
        self.text_field = text_field
        self.index_dir = Path(index_dir) if index_dir else HERE / "index"
        self._model = model
        self._table = None
        self.vectors: np.ndarray | None = None
        self.missing: list[str] = []

    # ---------- model ----------

    @property
    def model(self):
        """Load the bi-encoder on first use, so construction stays cheap."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(MODEL_NAME)
        return self._model

    def record_text(self, record: dict[str, Any]) -> str:
        """The string that gets embedded for one record."""
        value = record.get(self.text_field)
        if value:
            return str(value)
        # fall back to whatever the record actually contains
        for key in ("name", "description", "title", "text"):
            if record.get(key):
                return f"{record[key]}"
        return ""

    # ---------- building ----------

    def build(self, use_index: bool = True) -> "SemanticSearch":
        """Embed every record once and optionally write the LanceDB index."""
        texts = [self.record_text(r) for r in self.records]
        vectors = np.asarray(
            self.model.encode(texts, normalize_embeddings=True,
                              show_progress_bar=False, convert_to_numpy=True),
            dtype=np.float32)

        # a record with no text has no vector: record it instead of faking one
        blank = [str(r.get("id", i)) for i, (r, t) in enumerate(zip(self.records, texts))
                 if not t.strip()]
        if blank:
            self.missing = blank
            usable = np.array([not (not t.strip()) for t in texts])
            self.vectors = vectors[usable]
            self.records = [r for r, ok in zip(self.records, usable) if ok]
        else:
            self.missing = []
            self.vectors = vectors

        if use_index:
            self._write_index()
        return self

    def _write_index(self) -> None:
        """Create the LanceDB table with a vector column plus metadata."""
        import lancedb
        import pyarrow as pa

        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)
        self.index_dir.parent.mkdir(parents=True, exist_ok=True)

        schema = pa.schema([
            pa.field("pk", pa.int64()),
            pa.field("record_id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("category", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), DIM)),
        ])
        rows = []
        for i, record in enumerate(self.records):
            rows.append({
                "pk": i,
                "record_id": str(record.get("id", i)),
                "text": self.record_text(record),
                "category": str(record.get("category", "")),
                "vector": self.vectors[i].tolist(),
            })
        db = lancedb.connect(str(self.index_dir))
        self._table = db.create_table("records", schema=schema, data=rows)
        try:
            self._table.create_index("vector")
        except Exception:      # index is an optimization, never a requirement
            pass

    # ---------- searching ----------

    def _query_vector(self, query: str) -> np.ndarray:
        """Embed one query, normalized like every stored vector."""
        return np.asarray(
            self.model.encode([query], normalize_embeddings=True,
                              show_progress_bar=False, convert_to_numpy=True),
            dtype=np.float32)[0]

    def search(self, query: str, k: int = 5,
               category: str | None = None) -> list[SearchHit]:
        """Return the `k` best records for `query`, optionally filtered.

        `category` is applied as a structured filter before ranking, so a
        filtered search can never return an out-of-category record.
        """
        if self.vectors is None or not self.records:
            raise RuntimeError("call build() before search()")
        if not query.strip():
            return []

        pool = self.records
        matrix = self.vectors
        if category is not None:
            keep = [i for i, r in enumerate(pool)
                    if str(r.get("category", "")) == category]
            pool = [pool[i] for i in keep]
            matrix = matrix[keep]
            if not pool:
                return []

        vector = self._query_vector(query)
        if self._table is not None and category is None:
            rows = (self._table.search(vector.tolist()).limit(k).to_list())
            by_id = {str(r.get("id", i)): r for i, r in enumerate(self.records)}
            hits = [SearchHit(by_id.get(row["record_id"], {}),
                              (2.0 - float(row["_distance"])) / 2.0)
                    for row in rows]
        else:
            scores = matrix @ vector
            order = np.argsort(-scores)[:k]
            hits = [SearchHit(pool[i], float(scores[i])) for i in order]
        return hits

    # ---------- persistence ----------

    def save(self, path: Path | str) -> Path:
        """Write records, vectors and the index directory to `path`."""
        target = Path(path)
        target.mkdir(parents=True, exist_ok=True)
        payload = {
            "records": self.records,
            "missing": self.missing,
            "text_field": self.text_field,
            "vectors": self.vectors.tolist(),
        }
        (target / "state.json").write_text(json.dumps(payload), encoding="utf-8")
        if self.index_dir.exists():
            shutil.copytree(self.index_dir, target / "index", dirs_exist_ok=True)
        return target

    @classmethod
    def load(cls, path: Path | str) -> "SemanticSearch":
        """Restore an engine saved with `save()`, without re-embedding."""
        source = Path(path)
        payload = json.loads((source / "state.json").read_text(encoding="utf-8"))
        engine = cls(payload["records"],
                     index_dir=source / "index",
                     text_field=payload.get("text_field", "text"))
        engine.vectors = np.asarray(payload["vectors"], dtype=np.float32)
        engine.missing = payload.get("missing", [])
        try:
            import lancedb

            engine._table = lancedb.connect(str(source / "index")).open_table("records")
        except Exception:
            engine._table = None
        return engine


# --------------------------------------------------------------------------- #
# demo
# --------------------------------------------------------------------------- #
def load_products(limit: int | None = None) -> list[dict[str, Any]]:
    """The shared product dataset, reshaped into records for this engine."""
    products = json.loads(PRODUCTS_JSON.read_text(encoding="utf-8"))
    if limit:
        products = products[:limit]
    return [{"id": p["id"], "name": p["name"], "category": p["category"],
             "price": p["price"],
             "text": f"{p['name']}. {p['description']}"} for p in products]


def main(argv: list[str] | None = None) -> int:
    """Build once, then show filtered, unfiltered and missing-data behaviour."""
    import sys

    args = argv if argv is not None else sys.argv[1:]
    category = None
    query = " ".join(args)
    if args and args[0] == "--category" and len(args) > 1:
        category = args[1]
        query = " ".join(args[2:])
    use_index = "--no-index" not in args
    query = query.replace("--no-index", "").strip()

    records = load_products()
    engine = SemanticSearch(records, index_dir=HERE / "index").build(
        use_index=use_index)
    print(f"records: {len(engine.records)} | indexed: "
          f"{engine._table is not None} | missing: {len(engine.missing)}")
    if engine.missing:
        print(f"  skipped without text: {engine.missing}")
    print()

    if not query:
        query = "something to warm tea with"

    print(f"query: {query!r}  (no filter)")
    for hit in engine.search(query, k=3):
        print(f"  {hit.id}  {hit.score:.4f}  {hit.record['name']}")
    print()

    if category:
        print(f"query: {query!r}  (category = {category})")
        hits = engine.search(query, k=3, category=category)
        if not hits:
            print("  (no records in that category match)")
        for hit in hits:
            print(f"  {hit.id}  {hit.score:.4f}  {hit.record['name']}")
        print()
        assert all(h.record["category"] == category for h in hits), \
            "a filtered search leaked a record from another category"
        print("verified: every hit is inside the requested category")
    else:
        print("--- filter by category ---")
        for cat in ("kitchen", "electronics", "books", "sports"):
            hits = engine.search(query, k=2, category=cat)
            summary = ", ".join(f"{h.id}({h.score:.3f})" for h in hits) or "none"
            print(f"  {cat:<12} {summary}")
        print()

    print("--- a record with no text is reported, not silently scored ---")
    broken = list(records[:5]) + [{"id": "bad-1", "name": "", "category": "kitchen",
                                   "price": 0.0, "text": "   "}]
    engine2 = SemanticSearch(broken, index_dir=HERE / "index_bad").build()
    print(f"  records in: {len(broken)} | usable: {len(engine2.records)} "
          f"| reported missing: {engine2.missing}")
    print(f"  search still works, top hit: {engine2.search(query, k=1)[0].id}")
    return 0


HERE = Path(__file__).resolve().parent

if __name__ == "__main__":
    raise SystemExit(main())