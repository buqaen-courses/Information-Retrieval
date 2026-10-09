# Workshop 08 — BM25 From Scratch (≈45 min)

Session 7 gave you TF-IDF: `log(tf) × idf`, compared with cosine. It works, but
it has two rough edges — term frequency never stops mattering, and the length
correction is buried inside a division. BM25 fixes both cleanly, and hands you
two knobs you can turn. Today you write the real thing and verify it against
your own arithmetic.

**What you will walk away with:** a working `bm25.py` whose score you can
reproduce by hand with a calculator, plus a `k1`/`b` grid search you actually ran.

## Setup (≈5 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`):

```
cd session-08-bm25
python workshop/starter/bm25.py workshop/data "sauce basil"
```

You should see `TODO-1 not done yet` plus a note about 4 TODOs. Nothing
crashes. Work top to bottom.

## Meet your patient
`workshop/data/` — three documents, short enough to read completely:

```
doc-a.txt: Simmer the tomato sauce for twenty minutes.
           A good sauce depends on fresh basil.
doc-b.txt: Bread and sauce make a simple dinner.
           The bread soaks up the sauce.
doc-c.txt: The referee showed a yellow card for the late tackle.
           The striker scored twice in the second half.
```

Before writing any code, count these by hand. They are the whole computation:

| | doc-a | doc-b | doc-c |
|---|---|---|---|
| length (`dl`) | 14 | 13 | 18 |
| `tf("sauce")` | **2** | **2** | 0 |
| `tf("basil")` | 1 | 0 | 0 |

Two things to notice, because both are classic bugs:

1. **`tf("sauce")` is 2 in doc-a, not 1.** The word appears in *both* sentences.
   Getting this wrong silently changes every score.
2. `N = 3`, `avgdl = (14 + 13 + 18) / 3 = 15`, `df("sauce") = 2`,
   `df("basil") = 1`.

## The journey

### Stop 1 — IDF and the corpus statistics (≈12 min)
Two TODO jobs here, because everything else depends on them.

New idea, one line: `math.log(x)` is the natural logarithm. IDF is the same
formula as Session 7, with the `+0.5` smoothing that keeps it finite.

Open `workshop/starter/bm25.py` and replace **TODO-1**:

```python
import math
return math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
```

Now **TODO-2** — collect the statistics in one pass:

```python
import os
doc_ids = list_doc_ids(folder)
tf = {}
doc_len = {}
df = {}
for doc_id in doc_ids:
    with open(os.path.join(folder, doc_id + ".txt"), mode="r",
              encoding="utf-8") as f:
        tokens = tokenize(f.read())
    doc_len[doc_id] = len(tokens)
    counts = {}
    for term in tokens:
        counts[term] = counts.get(term, 0) + 1
    tf[doc_id] = counts
    for term in counts:
        df[term] = df.get(term, 0) + 1
n_docs = len(doc_ids)
avgdl = sum(doc_len.values()) / n_docs if n_docs else 0.0
return {"doc_ids": doc_ids, "tf": tf, "doc_len": doc_len,
        "df": df, "N": n_docs, "avgdl": avgdl}
```

The detail that matters: iterating `counts` (the *unique* terms of a document)
is what makes `df` count **documents**, not occurrences. Iterating `tokens`
would give you occurrences and inflate every IDF.

Checkpoint:

```
python workshop/starter/bm25.py workshop/data "sauce basil"
```

You now get a complaint about TODO-3. (Empty-file path: `build_stats("workshop/data")`
prints `doc_len` as `{'doc-a': 14, 'doc-b': 13, 'doc-c': 18}` and `avgdl` as
`15.0` — check those against the table above before moving on.)

*What you just learned: `tf` counts occurrences within a document, `df` counts
documents containing a term, and confusing the two is the most common BM25 bug.*

### Stop 2 — The scoring function (≈15 min)
This is where you should slow down, because this is the one formula you will
be asked to explain for the rest of the course.

Replace **TODO-3**:

```python
tf = stats["tf"][doc_id]
doc_len = stats["doc_len"][doc_id]
n_docs, avgdl = stats["N"], stats["avgdl"]
score = 0.0
for term in tokenize(query):
    freq = tf.get(term, 0)
    if freq == 0:
        continue
    if term not in stats["df"]:
        continue
    weight = idf(term, stats["df"][term], n_docs)
    norm = k1 * (1 - b + b * doc_len / avgdl)
    score += weight * (freq * (k1 + 1)) / (freq + norm)
return score
```

Now do the arithmetic by hand and check it. For query `sauce` against doc-a,
with `tf = 2`, `dl = 14`, `avgdl = 15`, `k1 = 1.2`, `b = 0.75`:

```
idf(sauce) = log(1 + (3 - 2 + 0.5) / (2 + 0.5)) = log(1.6)     = 0.4700036
norm       = 1.2 * (1 - 0.75 + 0.75 * 14/15)
           = 1.2 * (0.25 + 0.70)                               = 1.14
tf part    = (2 * 2.2) / (2 + 1.14) = 4.4 / 3.14              = 1.4012739
score      = 0.4700036 * 1.4012739                             = 0.6586044
```

Checkpoint:

```
python workshop/starter/bm25.py workshop/data "sauce basil"
```

```
query: sauce basil
folder: workshop/data
results (3):
  doc-a: 1.6669
  doc-b: 0.6714
  doc-c: 0.0000
```

Notice doc-a's 1.6669 is roughly `idf(basil)` (≈ 0.98, a term in one of three
docs) plus the sauce term (0.66) — the two query terms simply add up.

*What you just learned: BM25 sums one independent contribution per query term,
each being rarity times a saturating, length-adjusted frequency.*

### Stop 3 — Rank, and see b doing its job (≈10 min)
Replace **TODO-4**:

```python
stats = build_stats(folder)
scored = [(doc_id, bm25_score(query, doc_id, stats, k1, b))
          for doc_id in stats["doc_ids"]]
scored.sort(key=lambda item: (-item[1], item[0]))
return scored
```

Now the experiment. Both sauce documents have `tf("sauce") = 2`, but doc-b is
one word shorter. Ask for `sauce` alone:

```
python workshop/starter/bm25.py workshop/data "sauce"
python workshop/starter/bm25.py workshop/data "sauce"   # identical — reproducible
```

Then the revealing version — score doc-a and doc-b by hand at `b = 0` and
`b = 0.75`. The length penalty is the *only* difference between them, so this
is `b` in isolation:

```
tf part at b=0    : norm = 1.2 * (1 - 0 + 0) = 1.2   -> 4.4 / (2 + 1.2) = 1.375
tf part at b=0.75 : doc-a norm = 1.14 -> 1.401 ;  doc-b norm = 1.104 -> 1.416
```

At `b = 0` the two documents score *identically*. At `b = 0.75` the shorter one
pulls ahead. That difference is the entire reason `b` exists.

*What you just learned: `b = 0` makes length irrelevant, `b = 0.75` rewards
conciseness — and you can see the effect on two real documents.*

### Stop 4 — Tune the knobs (≈8 min)
Defaults are a starting point. Look at the surface you are choosing from:

```
python workshop/solution/bm25.py workshop/data --tune "sauce basil"
```

```
tuning on: sauce basil
ndcg@10    k1     b
1.0000   0.5    0.0
1.0000   0.5    0.5
1.0000   0.5    0.75
1.0000   1.2    0.0
1.0000   1.2    0.5
1.0000   1.2    0.75
1.0000   2.0    0.0
1.0000   2.0    0.5
1.0000   2.0    0.75
```

Every row is 1.0000 — and that is the honest lesson, not a bug. With three
documents and one query there is nothing to separate, so the ranking is right
for every setting. Now aim it at the real corpus, where the surface actually has
shape:

```
python workshop/solution/bm25.py ../../datasets/corpus "tomato sauce"
python workshop/solution/bm25.py ../../datasets/corpus --tune "tomato sauce"
```

*What you just learned: a tuning surface that is flat everywhere means your
evaluation cannot distinguish the settings — you need a bigger collection and
real judgments, which is exactly Session 10.*

## Expected output
Exact output of the correct solution, from this folder:

```
$ python workshop/solution/bm25.py workshop/data "sauce basil"
query: sauce basil
folder: workshop/data
results (3):
  doc-a: 1.6669
  doc-b: 0.6714
  doc-c: 0.0000
```

## Stretch goals (optional)
- **Make the grid search discriminate.** Load `datasets/qrels.json`, use its real
  graded judgments instead of the stand-in relevance in `tune()`, and plot
  NDCG@10 across the full `k1` × `b` grid. Now the surface has shape.
- **Break it on purpose.** Set `b = 1.0` and find a query where the top result is
  a very short, barely-relevant document. That failure is the argument against `b = 1`.
- **Add BM25F.** Split the score per *field* (title vs body) with separate
  weights and re-run the hand computation with two terms.

## Solution
`workshop/solution/` — attempt the journey first. Sanity check:

```
python -m pytest workshop/solution/ -v
```

Expected: `13 passed`, including a BM25 score computed by hand on paper
(`test_bm25_score_hand_computed` asserts `0.6586044`).

## Where this leads
Session 9 replaces the formula's intuition with a probability model — where
`k1` and `b` stop being tuned constants and become expectations over a
distribution. Session 10 then gives you the metric that turns this workshop's
eyeballed tuning into a number you can put in a report.
