# Workshop 09 — Query Likelihood & Dirichlet Smoothing (≈45 min)

Session 8 gave you BM25 with two tuned knobs. Today you find out where those
knobs came from — and what breaks when the text runs out. You will build a
ranking model that asks "if this document had written the query, how likely is
that?" and you will see, concretely, why one line of smoothing keeps it from
collapsing to `-inf`.

**What you will walk away with:** a working `ql_ranker.py` with a smoothed
query-likelihood score you can reproduce by hand, and a clear sense of when
this model beats BM25 (rarely, and Session 22 explains why that is fine).

## Setup (≈5 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`):

```
cd session-09-probabilistic-models
python workshop/starter/ql_ranker.py workshop/data "sauce basil"
```

You should see `TODO-1 not done yet` plus a note about 4 TODOs. Nothing
crashes. Work top to bottom.

## Meet your patient
The same three documents as Session 8, deliberately — so you can compare the
two models on identical data:

```
doc-a.txt: Simmer the tomato sauce for twenty minutes.
           A good sauce depends on fresh basil.
doc-b.txt: Bread and sauce make a simple dinner.
           The bread soaks up the sauce.
doc-c.txt: The referee showed a yellow card for the late tackle.
           The striker scored twice in the second half.
```

Before coding, collect the numbers this model needs. Note the difference from
Session 8 in the last line:

| quantity | value | (Session 8's equivalent) |
|---|---|---|
| `dl` per doc | 14, 13, 18 | same |
| `tf("sauce")` | 2 in doc-a, 2 in doc-b | same |
| `cf("sauce")` | **4** | (`df` was 2) |
| total tokens | **45** | (`avgdl` was 15) |

`cf` counts **occurrences across the whole collection**; `df` counted
**documents containing** the term. Two sauce occurrences in two documents
makes `df = 2` but `cf = 4`. Mixing these up is the classic bug in this session.

## The journey

### Stop 1 — Collection frequencies (≈12 min)
**TODO-1** is a single pass, but the `cf` line is the one that matters.

New idea, one line: `cf[term] += count` accumulates across documents, while
`df` in Session 8 added exactly 1 per document.

Open `workshop/starter/ql_ranker.py` and replace **TODO-1**:

```python
doc_ids = list_doc_ids(folder)
tf = {}
doc_len = {}
cf = {}
for doc_id in doc_ids:
    with open(os.path.join(folder, doc_id + ".txt"), mode="r",
              encoding="utf-8") as f:
        tokens = tokenize(f.read())
    doc_len[doc_id] = len(tokens)
    counts = {}
    for term in tokens:
        counts[term] = counts.get(term, 0) + 1
    tf[doc_id] = counts
    for term, count in counts.items():
        cf[term] = cf.get(term, 0) + count
return {"doc_ids": doc_ids, "tf": tf, "doc_len": doc_len,
        "cf": cf, "total": sum(doc_len.values()), "N": len(doc_ids)}
```

Note `for term, count in counts.items()` — you iterate the *counts*, so each
term contributes its full count once per document. That is exactly the
difference from `df`.

Checkpoint:

```
python workshop/starter/ql_ranker.py workshop/data "sauce basil"
```

You now get a complaint about TODO-2. (Empty-file path: `build_stats("workshop/data")`
gives `total` of 45 and `cf["sauce"]` of 4 — check both against the table.)

*What you just learned: `df` counts documents, `cf` counts occurrences, and the
language model needs the second.*

### Stop 2 — The smoothed score (≈15 min)
This is the session's core, and the one place you should slow down.

Replace **TODO-2**:

```python
import math
tf = stats["tf"][doc_id]
dl = stats["doc_len"][doc_id]
total = stats["total"]
score = 0.0
for term in tokenize(query):
    background = (stats["cf"].get(term, 0) + mu * p_smooth) / (total + mu)
    score += math.log((tf.get(term, 0) + mu * background) / (dl + mu))
return score
```

Three things in four lines, each earning its place:

- `background` is the collection probability `P(w)`, itself smoothed so a word
  seen nowhere still has a tiny non-zero chance of appearing.
- `tf + mu * background` **cannot be zero**. Delete the `mu * background` and
  an unseen word makes this `log(0)` = `-inf`.
- `dl + mu` normalizes by document length plus a constant, so short documents
  are not over-penalized.

Now hand-compute `ql_score("sauce", "doc-a")` and check the code:

```
background = (4 + 200 * 0.0001) / (45 + 200) = 4.02 / 245      = 0.016408163
numerator  = 2 + 200 * 0.016408163                              = 5.281632653
denominator = 14 + 200                                           = 214
score      = log(5.281632653 / 214) = log(0.024681)             = -3.7017
```

Checkpoint:

```
python workshop/starter/ql_ranker.py workshop/data "sauce basil"
```

```
query: sauce basil
folder: workshop/data
results (3):
  doc-a: -8.4620
  doc-b: -9.2415
  doc-c: -9.7638
```

**Every score is negative**, and that is correct, not a bug: these are log
probabilities, and any probability below 1 has a negative logarithm. doc-c
scores best despite matching nothing well, because smoothing gives every
document a non-zero chance of any word — and doc-c is longest.

*What you just learned: summing log probabilities keeps the arithmetic in
range, and the smoothing term is the only reason a non-matching document still
has a score.*

### Stop 3 — Rank, and notice a real difference from BM25 (≈8 min)
Replace **TODO-3**:

```python
stats = build_stats(folder)
scored = [(doc_id, ql_score(query, doc_id, stats, mu))
          for doc_id in stats["doc_ids"]]
scored.sort(key=lambda item: (-item[1], item[0]))
return scored[:top]
```

Compare the two models on the same query:

```
python ../session-08-bm25/workshop/solution/bm25.py workshop/data "sauce basil"
python workshop/starter/ql_ranker.py workshop/data "sauce basil"
```

```
BM25:                  query likelihood:
  doc-a: 1.6669          doc-a: -8.4620
  doc-b: 0.6714          doc-b: -9.2415
  doc-c: 0.0000          doc-c: -9.7638
```

Same winner, same order — and one structural difference worth naming: BM25
gave doc-c exactly `0.0000` because it matched nothing, while query likelihood
gives it `-9.7638` because *every* document has some probability of producing
any query. Smoothing trades "correctly zero" for "always rankable".

*What you just learned: a smoothed model never returns an absolute zero score,
which is why it degrades gracefully on queries with no exact matches.*

### Stop 4 — Sweep μ and watch the ranking flatten (≈10 min)
**TODO-4** is the one that teaches the lesson:

```python
rows = []
for mu in [10.0, 50.0, 200.0, 1000.0]:
    ranked = search(folder, query, mu=mu, top=2)
    best = ranked[0][0]
    margin = ranked[0][1] - ranked[1][1]
    rows.append((mu, best, round(margin, 4)))
return rows
```

The **margin** between first and second is what matters. Try it:

```
python workshop/solution/ql_ranker.py workshop/data "sauce basil"
```

Watch the margin shrink as `μ` grows: large `μ` pulls every document toward the
collection average, so they all look alike and the ranking becomes arbitrary.
Now the sobering observation — this corpus has **45 tokens total**. A `μ` of 200
is tuned for collections of millions. Here it over-smooths by more than 2×.
Run it on the real corpus and the effect is sane:

```
python workshop/solution/ql_ranker.py ../../datasets/corpus "tomato sauce"
```

*What you just learned: `μ` is a parameter like any other — it has no
collection-independent "right" value, and a parameter tuned for a large corpus
is actively wrong on a small one.*

## Expected output
Exact output of the correct solution, from this folder:

```
$ python workshop/solution/ql_ranker.py workshop/data "sauce basil"
query: sauce basil
folder: workshop/data
results (3):
  doc-a: -8.4620
  doc-b: -9.2415
  doc-c: -9.7638
```

## Stretch goals (optional)
- **Break it on purpose.** Remove the `mu * background` term from TODO-2 and
  query for a word absent from the corpus. Watch `log(0)` appear — then add a
  guard and decide what your engine should return in that case.
- **Make the models disagree.** The README chart shows they agree on this
  corpus. Find a query where BM25 and query likelihood rank differently, and
  explain which one you would trust and why.
- **Two-stage smoothing.** Compute scores without any corpus statistics
  (`p_smooth = 0` everywhere) and compare. Which terms end up carrying all the
  information?

## Solution
`workshop/solution/` — attempt the journey first. Sanity check:

```
python -m pytest workshop/solution/ -v
```

Expected: `11 passed`, including a hand-computed score
(`test_ql_score_hand_computed` asserts `-3.7017`) and a test proving that `μ`
over-smooths a 45-token corpus.

## Where this leads
Session 10 gives you the measuring stick. Right now "this ranking looks better"
is an opinion; after Session 10 it is an NDCG@10 you can put in a report and
compare across every ranker you build — and that same `metrics.py` becomes the
judge for Sessions 16, 22, and 23.
