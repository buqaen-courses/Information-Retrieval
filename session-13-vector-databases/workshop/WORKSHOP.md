# Workshop 13 — Two Vector Databases, One Catalogue (≈45 min)

Last session you searched 128 products by comparing your query against all of
them, in one line of numpy, and it worked. Today you put those same vectors
into two real vector databases and make their numbers comparable. That last
part is where most people get stuck, and it is a two-line fix once you see it.

**What you will walk away with:** a working Milvus Lite collection and a working
LanceDB table over the same catalogue, a search function whose output is a
cosine similarity regardless of backend, and a measured answer to "does the
approximate index give me the same results?"

## Setup (≈8 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`):

```
cd session-13-vector-databases
python workshop/starter/compare_vector_dbs.py
```

You should see `TODO-1 not done yet` plus a note about 4 TODOs. The first run
loads the embedding model, which takes ~20 seconds; every run after that is
faster. No server, no Docker, no network.

## Meet your patient
The same 128 products from `datasets/fallback_products.json` that Session 12
used. Each becomes one sentence — name plus description — and one vector:

```
p-001  "Compact kettle 1. A compact kettle for kitchen lovers. ..."
p-002  "Wireless headphones 2. A premium headphones with reliable sound. ..."
```

The two databases will hold the *identical* 128 vectors. Any difference in the
answers therefore comes from the search, not the data.

## The journey

### Stop 1 — Load and embed the catalogue (≈8 min)
Reuse Session 12's embedding code. New call, one line: the JSON is read with
`json.loads(path.read_text(encoding="utf-8"))`, which gives you a list of dicts.

Open `workshop/starter/compare_vector_dbs.py` and replace **TODO-1**:

```python
import json
from pathlib import Path
import numpy as np
root = Path(__file__).resolve().parents[3]
products = json.loads((root / "datasets" / "fallback_products.json")
                     .read_text(encoding="utf-8"))
if limit:
    products = products[:limit]
ids = [p["id"] for p in products]
texts = [p["name"] + ". " + p["description"] for p in products]
model = load_model()
vectors = model.encode(texts, normalize_embeddings=True,
                       show_progress_bar=False, convert_to_numpy=True)
return ids, texts, np.asarray(vectors, dtype=np.float32)
```

`parents[3]` walks out of `solution/` to the repo root so you can find
`datasets/`. And note the embedding happens in **one** call for the whole
catalogue — that is what you do at index time, never per query.

Checkpoint:

```
python workshop/starter/compare_vector_dbs.py
```

You now get `TODO-2`. (Empty-file path: `len(load_catalogue(limit=5)[0])` is 5
and `load_catalogue(limit=5)[2].shape` is `(5, 384)`.)

*What you just learned: a vector database starts with the same embeddings you
already had — the only new thing is where they get stored.*

### Stop 2 — Build the Milvus Lite collection (≈12 min)
Milvus wants a schema with an integer primary key and a typed vector column.

New calls, one line each: `MilvusClient(path)` opens a local database file;
`create_schema(...)` declares the columns; `add_field(name, type, ...)` adds
one; `insert(collection, rows)` writes the rows.

Replace **TODO-2**:

```python
from pymilvus import DataType, MilvusClient
self.client = MilvusClient(str(self.path))
schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
schema.add_field("pk", DataType.INT64, is_primary=True)
schema.add_field("doc_id", DataType.VARCHAR, max_length=32)
schema.add_field("text", DataType.VARCHAR, max_length=1024)
schema.add_field("vector", DataType.FLOAT_VECTOR, dim=DIM)
self.client.create_collection(self.collection, schema=schema)
rows = [{"pk": i, "doc_id": d, "text": t, "vector": vectors[i].tolist()}
        for i, (d, t) in enumerate(zip(ids, texts))]
self.client.insert(self.collection, rows)
```

Two details worth naming. Milvus insists on its own integer `pk`, so we keep
our string id as an ordinary `doc_id` column. And vectors go in via
`.tolist()` because the wire format expects plain Python floats, not a numpy
array.

Checkpoint — the starter now reaches TODO-3.

*What you just learned: a vector database is a typed schema plus a write
operation. The API differs, the idea does not.*

### Stop 3 — Build the LanceDB table (≈10 min)
Same data, columnar storage. New call, one line: `pyarrow` schemas describe the
columns, and a vector column is declared as a fixed-length list of `float32`.

Replace **TODO-3**:

```python
import lancedb, pyarrow as pa
db = lancedb.connect(str(self.path))
schema = pa.schema([
    pa.field("pk", pa.int64()),
    pa.field("doc_id", pa.string()),
    pa.field("text", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), DIM)),
])
rows = [{"pk": i, "doc_id": d, "text": t, "vector": vectors[i].tolist()}
        for i, (d, t) in enumerate(zip(ids, texts))]
self.table = db.create_table(self.table_name, schema=schema, data=rows)
```

`pa.list_(pa.float32(), DIM)` is the interesting line: it tells LanceDB "this
column is a vector of exactly 384 float32s", which is what lets it index it as
one rather than 384 independent numbers.

Checkpoint — the starter now reaches TODO-4.

*What you just learned: LanceDB stores vectors as ordinary columnar data
alongside your text, so there is no separate "vector store" to keep in sync.*

### Stop 4 — The conversion that makes the two comparable (≈10 min)
This is the stop worth the whole session. Replace **TODO-4**:

```python
rows = self.table.search(vector.tolist()).limit(k).to_list()
return [(row["doc_id"], (2.0 - float(row["_distance"])) / 2.0)
        for row in rows]
```

Why is that line necessary? The two databases return **different metrics**.
Milvus returns `distance`, which for normalized vectors *is* the cosine
similarity — 1.0 means identical. LanceDB returns `_distance`, which is
**squared L2** — 0.0 means identical. Opposite directions.

For two vectors of length 1 the algebra connects them:

```
||a − b||²  =  |a|² + |b|² − 2·(a·b)  =  2 − 2·cos(a, b)
```

so `cos(a, b) = (2 − d²) / 2`. That single line converts LanceDB's number
into the same scale Milvus reports, and it is why both return `1.0` for an
identical vector.

Checkpoint — run the finished solution over the full catalogue:

```
python workshop/solution/compare_vector_dbs.py
```

```
query                           backend       top-1 id       score
------------------------------------------------------------------
soccer boots                    brute force   p-100         0.3166
                                milvus_lite   p-100         0.3166
                                lancedb       p-100         0.3166

something to drink tea with     brute force   p-033         0.3509
                                milvus_lite   p-033         0.3509
                                lancedb       p-033         0.3509

a sturdy lamp                   brute force   p-031         0.7109
                                milvus_lite   p-031         0.7109
                                lancedb       p-031         0.7109

exact top-5 agreement: 6/6 (approximate indexes may drop a borderline document)
```

Three backends, identical answers, to four decimal places. If LanceDB's number
had not been converted, this table would show `0.95` next to `0.05` and look
like one database was broken.

*What you just learned: comparing two search systems means comparing their
metrics first, and the difference between a distance and a similarity is the
single most common reason two tools "disagree" when they do not.*

## Expected output
Exact output of the correct solution, from this folder:

```
$ python workshop/solution/compare_vector_dbs.py
documents: 128 | dimensions: 384
build time: milvus_lite 0.299s | lancedb 0.023s
exact top-5 agreement: 6/6
on disk after close: milvus 217,945 bytes | lancedb 216,676 bytes
```

The document count, dimensions and agreement count are exact. Build times and
disk sizes are real measurements and vary by machine; the agreement count is
the claim.

## Stretch goals (optional)
- **Break the conversion.** Remove the `(2.0 - d) / 2.0` line and re-run. Write
  down exactly what changes and why a reader would conclude LanceDB is broken.
- **Tune recall.** LanceDB's `create_index` takes an `nprobe`-style knob. Lower
  it and watch the agreement count drop below 6/6. That is what "approximate"
  costs, measured.
- **Add a column.** LanceDB filters on ordinary columns, Milvus Lite less so.
  Try filtering for `category == "kitchen"` in each and note the asymmetry.
- **Measure the scaling claim.** Time exact search against the ANN index at
  128, 1,000 and, if you are patient, 10,000 vectors.

## Solution
`workshop/solution/` — attempt the journey first. Sanity check:

```
python -m pytest workshop/solution/ -v
```

Expected: `11 passed`. The suite embeds a small catalogue once, indexes it
into both databases, and asserts that both return the **same top-5 as exact
search** and that an identical vector scores exactly `1.0` in both backends —
which is the test that catches a missing distance conversion.

## Where this leads
Session 14 wraps all of this into a reusable `SemanticSearch` class with
metadata filtering, and Session 23 imports that class directly. Session 22 puts
a BM25 ranker beside this one, because a vector database that only searches by
meaning cannot find a product code.