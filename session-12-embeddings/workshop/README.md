# Workshop 12 — Semantic Search by Hand (≈45 min)

Ten sessions you have searched by matching words. Today you search by matching
*meanings*, which is the single biggest change in how search engines work. The
good news is that the code is shorter than what you have already written, and
the model runs on your laptop with no API key.

**What you will walk away with:** a working semantic search engine over a
catalogue, an intuition for what a vector is, and the reason a working demo is
still far too slow to ship.

## Setup (≈5 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`, plus `python setup/download_models.py` to cache the model):

```
cd session-12-embeddings
python workshop/starter/numpy_semantic_search.py
```

You should see `TODO-1 not done yet` plus a note about 4 TODOs. The first run
loads the model and takes a few seconds; that is normal, and every run after it
is faster.

## Meet your patient
A ten-sentence catalogue. Read it and notice which pairs mean the same thing
without sharing a word:

```
0: wireless headphones with noise cancelling
1: a sturdy desk lamp for reading
2: a cheap lamp that still works
3: football boots for a muddy pitch
4: soccer cleats with studs
5: a laptop backpack for school
6: a stainless steel kettle for tea
7: an espresso machine for home
8: running shoes for the marathon
9: a waterproof rain jacket
```

Three pairs worth betting on: `3` and `4` (football / soccer), `1` and `2` (two
lamps), `6` and `7` (kettle / espresso machine — not the same thing, but the
same kitchen).

## The journey

### Stop 1 — Embed a sentence and check what comes back (≈12 min)
The model is the black box. Your job is to call it correctly and inspect the
result before trusting it.

New call, one line: `model.encode(list_of_strings, normalize_embeddings=True)`
returns a 2D array — one row per sentence, 384 columns.

Open `workshop/starter/numpy_semantic_search.py` and replace **TODO-1**:

```python
import numpy as np
vectors = model.encode(sentences, normalize_embeddings=True,
                       show_progress_bar=False, convert_to_numpy=True)
return np.asarray(vectors, dtype=np.float32)
```

`normalize_embeddings=True` divides each row by its own length. That single
flag is the one that matters; Stop 2 depends entirely on it.

Checkpoint:

```
python workshop/starter/numpy_semantic_search.py
```

You now get `TODO-2`. (Empty-file path: `embed(model, ["hi"])` returns an
array of shape `(1, 384)`, and `float((embed(model, ["hi"])[0] ** 2).sum() ** 0.5)`
is `1.0000` — that length-1 fact is the whole reason the next stop is allowed
to be this short.)

*What you just learned: an embedding is a fixed-length row of numbers, and
`normalize_embeddings=True` guarantees every row has length exactly 1.*

### Stop 2 — Cosine similarity (≈8 min)
Now compare two rows. Because both have length 1, the cosine formula collapses.

Replace **TODO-2**:

```python
import numpy as np
return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

Checkpoint (still TODO-3 pending). Check it by hand before you move on:

```
a = embed(model, ["football boots"])[0]
b = embed(model, ["soccer cleats with studs"])[0]
c = embed(model, ["a stainless steel kettle"])[0]
print("boots vs cleats:", float(a @ b))   # 0.5603
print("boots vs kettle :", float(a @ c))   # 0.1269
```

Those two sentences share **no words at all**. Yet they are more than four
times more similar than a football sentence and a kettle.

*What you just learned: cosine similarity measures direction, and with
normalized vectors the direction comparison is a single dot product.*

### Stop 3 — Rank a catalogue (≈12 min)
Now the search function. This is the shortest piece of code in the course.

Replace **TODO-3**:

```python
import numpy as np
if not catalogue:
    return []
matrix = embed(model, catalogue)
query_vector = embed(model, [query])[0]
scores = matrix @ query_vector
order = np.argsort(-scores)[:top_k]
return [(int(i), float(scores[i])) for i in order]
```

Two details to name. `@` is numpy's matrix multiply, and because every row is
length 1 the products *are* cosine similarities. And `-scores` in the sort is
there because `np.argsort` defaults to ascending, while we want the biggest
score first.

Checkpoint:

```
python workshop/starter/numpy_semantic_search.py
```

```
dimensions: 384
query: soccer boots
  1. football boots for a muddy pitch      0.6856
  2. soccer cleats with studs               0.5387
  3. running shoes for the marathon         0.4987
query: something to drink tea with
  1. a stainless steel kettle for tea       0.6012
  2. an espresso machine for home           0.2696
  3. a laptop backpack for school           0.2629
```

The second query contains no word from any catalogue entry, and it still put
the kettle first. Ask Session 6's Boolean engine the same question and it
returns nothing at all.

*What you just learned: one matrix multiply ranks a whole catalogue, because
similarity is geometry rather than a lookup.*

### Stop 4 — Where it gets slow (≈13 min)
Now aim it at the real dataset and watch it be merely adequate:

```
python workshop/solution/numpy_semantic_search.py
```

```
query: durable backpack for travel
  1. Premium tent 7                         0.3185
  2. Premium tent 2                         0.3148
  3. Premium tent 12                        0.3136
  4. Premium tent 27                        0.2995
  5. Durable lamp 26                        0.2926
```

Tents first, for a query about a backpack. That is not a bug in your code. It
is a true statement about the dataset: in `datasets/fallback_products.json` the
tent descriptions genuinely carry more of "durable, portable, for travel" than
the backpack descriptions do. Semantic search found the meaning you asked for.

Then look at the cost. Every one of those top-5 results required comparing the
query against **all 30** product vectors. At ten million documents that is
1.28 billion dot products, which is the number that ends this session and starts
the next three.

*What you just learned: embeddings answer a question BM25 cannot, they are more
expensive to store and slower to search, and the fix is an approximate index
rather than a better model.*

## Expected output
Exact output of the correct solution, from this folder:

```
$ python workshop/solution/numpy_semantic_search.py
model: sentence-transformers/all-MiniLM-L6-v2
dimensions: 384

query: soccer boots
  1. 3: football boots for a muddy pit      0.6856
  2. 4: soccer cleats with studs            0.5387
  3. 8: running shoes for the marathon      0.4987

query: something to drink tea with
  1. 6: a stainless steel kettle for t      0.6012
  2. 7: an espresso machine for home        0.2696
  3. 5: a laptop backpack for school        0.2629

query: a machine that makes coffee
  1. 7: an espresso machine for home        0.7145
  2. 6: a stainless steel kettle for t      0.4129
  3. 5: a laptop backpack for school        0.2575
```

Scores are deterministic for a fixed model on CPU, so yours should match to the
fourth decimal.

## Stretch goals (optional)
- **Find the failure case the syllabus asks for.** Try to construct a query where
  BM25 beats embeddings: a product code, a person's name, a rare technical
  term. Write down why each one fails, because that list is the argument for
  Session 22's hybrid search.
- **What does the model think about order?** Embed `"a red apple"` and
  `"a green apple"`, then swap the adjectives. Measure how much the score moves.
- **Cosine vs dot product.** Turn off `normalize_embeddings=True` and rerun.
  Predict what changes before you run it.
- **PCA yourself.** Project the ten vectors onto their first two principal
  components with `numpy.linalg.svd` and plot them, reproducing `12-01`.

## Solution
`workshop/solution/` — attempt the journey first. Sanity check:

```
python -m pytest workshop/solution/ -v
```

Expected: `12 passed`. The suite loads the model once and then checks the
properties that matter: every vector has length 1, a sentence scores 1.0000 with
itself, `boots` is closer to `cleats` than to `kettle`, and a query word absent
from the catalogue still finds the right document.

## Where this leads
Session 13 puts these vectors into two real vector databases, Milvus Lite and
LanceDB, and measures what an approximate index actually buys. Session 14 wraps
this code in a reusable `SemanticSearch` class that Session 23 will import. And
Session 22 puts a BM25 ranker next to this one, because the failure case you
find in a stretch goal is the reason hybrid retrieval exists.