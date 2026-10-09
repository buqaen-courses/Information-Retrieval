# Workshop 10 — Build the Measuring Stick (≈45 min)

Nine sessions of rankers, and so far you have compared them by vibes. Today you
build the instrument that settles it — and then discover that the instrument is
pointing at something you should not trust. Every ranker in this course will be
graded by the `metrics.py` you write in the next 40 minutes, including the ones
you build in Sessions 16, 22 and 23.

**What you will walk away with:** a `metrics.py` implementing P@k, recall@k,
MRR, MAP and NDCG@10 from scratch, a real results table comparing TF-IDF, BM25
and query likelihood, and the ability to tell when a perfect score is a bug in
your test rather than a triumph.

## Setup (≈5 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`):

```
cd session-10-evaluation
python workshop/starter/metrics.py
```

You should see `TODO-1 not done yet` plus a note about 5 TODOs. Nothing
crashes. Work top to bottom.

## Meet your patient
One ranked list of ten documents, and five that a human marked as wanted:

```
ranked : d4  d2  d1  d9  d7  d3  d8  d5  d6  d10
wanted : d1  d3  d5  d7  d9
```

Write down where the wanted documents actually landed, before you write any
code — every number you produce today can be checked against this list:

```
d1 -> rank 3      d9 -> rank 4      d7 -> rank 5
d3 -> rank 6      d5 -> rank 8
```

Two facts to carry: the **first** relevant document is at rank 3, and the top
two results (`d4`, `d2`) are both wrong.

## The journey

### Stop 1 — Precision@k and recall@k (≈12 min)
Two functions, one difference: what goes in the denominator.

Open `workshop/starter/metrics.py` and replace **TODO-1**:

```python
if k <= 0:
    return 0.0
rel = set(relevant)
top = list(ranked)[:k]
if not top:
    return 0.0
hits = 0
for doc_id in top:
    if doc_id in rel:
        hits = hits + 1
return hits / len(top)
```

Now **TODO-2** — the same loop, a different denominator:

```python
rel = set(relevant)
if not rel:
    return 0.0
top = list(ranked)[:k]
hits = 0
for doc_id in top:
    if doc_id in rel:
        hits = hits + 1
return hits / len(rel)
```

`len(top)` versus `len(rel)`. That is the entire difference, and it is why
precision rewards shallow lists while recall rewards deep ones.

Checkpoint:

```
python workshop/starter/metrics.py
```

You now get a complaint about TODO-3. (Empty-file path: the hands-on check —
`precision_at_k(RANKED, RELEVANT, 2)` is **0.0** because `d4` and `d2` are both
irrelevant, while `precision_at_k(RANKED, RELEVANT, 4)` is **0.5** because
`d1` and `d9` are. Same engine, different `k`, opposite story.)

*What you just learned: precision and recall are the same counting loop with
opposite denominators, and neither is meaningful alone.*

### Stop 2 — MRR: only the first hit counts (≈8 min)
Replace **TODO-3**:

```python
rel = set(relevant)
position = 0
for i, doc_id in enumerate(ranked):
    if doc_id in rel:
        position = i + 1
        break
if position == 0:
    return 0.0
return 1.0 / position
```

The `break` is the entire metric. Without it you would average every hit's
reciprocal, which is not MRR — it is a different, unnamed quantity.

Checkpoint (still TODO-4 pending): the hand answer is `1/3` because `d1` sits
at rank 3.

*What you just learned: MRR models the user who clicks the first useful thing,
and is completely blind to the rest of the list.*

### Stop 3 — MAP: precision at every moment you were right (≈10 min)
Replace **TODO-4**:

```python
rel = set(relevant)
if not rel:
    return 0.0
hits = 0
total = 0.0
for position, doc_id in enumerate(ranked, start=1):
    if doc_id in rel:
        hits = hits + 1
        total = total + hits / position
return total / len(rel)
```

Verify it against your list. Relevant documents land at ranks 3, 4, 5, 6, 8, so
the running hit counts are 1, 2, 3, 4, 5:

```
(1/3 + 2/4 + 3/5 + 4/6 + 5/8) / 5 = 0.545
```

Checkpoint (still TODO-5 pending): hand answer **0.545**.

*What you just learned: `hits / position` is the precision at that instant, and
only relevant documents contribute — that is what makes AP order-sensitive.*

### Stop 4 — NDCG with graded relevance (≈10 min)
The judgments are graded (0, 1, 2), so we need gains and a discount. Replace
**TODO-5**:

```python
import math
if not judged:
    return 0.0
dcg = 0.0
position = 0
for doc_id in ranked:
    position = position + 1
    if position > k:
        break
    gain = 2 ** judged.get(doc_id, 0) - 1
    dcg = dcg + gain / math.log2(position + 1)
ideal_gains = []
for rel in sorted(judged.values(), reverse=True):
    ideal_gains.append(2 ** rel - 1)
idcg = 0.0
for i, gain in enumerate(ideal_gains, start=1):
    if i > k:
        break
    idcg = idcg + gain / math.log2(i + 1)
if idcg == 0:
    return 0.0
return dcg / idcg
```

Three pieces, each doing a specific job. `2 ** rel - 1` makes grade 2 worth
**3**, not 2. `log2(position + 1)` makes rank 1 worth 1.00 and rank 10 worth
0.29 — the +1 is there so `log2(1)` never sees zero. Dividing by `idcg` is what
makes the score mean "how close to perfect, as a fraction".

Checkpoint:

```
python workshop/starter/metrics.py
```

```
ranked: ['d4', 'd2', 'd1', 'd9', 'd7', 'd3', 'd8', 'd5', 'd6', 'd10']
relevant: ['d1', 'd3', 'd5', 'd7', 'd9']

P@10        = 0.5000
R@10        = 1.0000
MRR         = 0.3333
MAP         = 0.5450
NDCG@10     = 0.6215
```

*What you just learned: NDCG combines graded worth and position discount, then
normalizes so different queries can be averaged.*

### Stop 5 — The real comparison, and why it looks too good (≈10 min)
Now run the finished instrument against the three rankers you have built, over
the course qrels:

```
python workshop/solution/compare.py
```

```
ranker                    P@10        R@10 R-precision         MRR         MAP     NDCG@10
------------------------------------------------------------------------------------------
TF-IDF                  1.0000      0.2941      1.0000      1.0000      0.2941      1.0000
BM25                    1.0000      0.2941      1.0000      1.0000      0.2941      1.0000
Query likelihood        1.0000      0.2941      1.0000      1.0000      0.2941      1.0000

best NDCG@10: 1.0000

diagnostic - query q05: 'tomato sauce simmer'
  documents judged relevant (>0): 34
  of those, graded highly (2):    21
  slots in the top-10 list:        10
  so R@10 is capped near 10/34 = 0.2941 - measured 0.2941
```

Stop and read that before moving on. Three rankers, three identical rows, and
every NDCG is a perfect 1.0. Ask why.

There are two answers, and you should be able to name both:

1. **The test is circular.** Look at how `datasets/make_corpus.py` builds the
   judgments: a document is graded 2 if it contains at least two query terms.
   That is *exactly* what BM25 and TF-IDF maximize. The exam and the answer
   sheet were written from the same material, so no lexical ranker can fail.
2. **Recall is capped.** Every query has 34 relevant documents, and the list
   holds 10. `10/34 = 0.2941` is the ceiling, and the measured value sits
   exactly on it. R@10 cannot improve; it is arithmetic, not ranking.

Neither fact means your rankers are bad. Both mean **you cannot use this test
to tell them apart** — which is the real lesson, and the reason Sessions 16, 22
and 23 reuse this `metrics.py` but bring their own relevance data.

*What you just learned: an evaluation that cannot fail proves nothing. Always
check how the judgments were produced before believing a score.*

## Expected output
Exact output of the correct solution, from this folder:

```
$ python workshop/solution/metrics.py --demo
ranked list   : ['d4', 'd2', 'd1', 'd9', 'd7', 'd3', 'd8', 'd5', 'd6', 'd10']
relevant      : ['d1', 'd3', 'd5', 'd7', 'd9'] (5 docs, R = 5)
graded judged : {'d1': 2, 'd3': 1, 'd5': 2, 'd7': 1, 'd9': 2, 'd4': 0, 'd8': 0}

where the relevant documents actually landed:
  d1 -> rank 3
  d3 -> rank 6
  d5 -> rank 8
  d7 -> rank 5
  d9 -> rank 4

P@10          = 0.5000   (5 relevant among the top 10)
R@10          = 1.0000   (all 5 relevant documents appear)
R-precision   = 0.6000   (top 5 = ['d4', 'd2', 'd1', 'd9', 'd7'] -> 3 relevant)
MRR           = 0.3333   (first hit d1 at rank 3 -> 1/3)
MAP           = 0.5450   ((1/3 + 2/4 + 3/5 + 4/6 + 5/8) / 5)
NDCG@10       = 0.6215
```

## Stretch goals (optional)
- **Build a query the current metrics *cannot* fail.** Add three real documents
  to `datasets/corpus/` with hand-written relevant judgments for one qrels
  query, then re-run `compare.py`. Can you make the rankers differ?
- **Grade the top 10 by hand** for two queries and see whether your judgment
  agrees with the automatic one. This is what a real assessment pool costs.
- **Add MAP@10.** AP truncated at `k` is a different number from plain AP. Find
  a query where the two disagree and explain which suits a ten-result page.

## Solution
`workshop/solution/` — attempt the journey first. Two checks:

```
python workshop/solution/metrics.py
python -m pytest workshop/solution/ -v
```

Expected: `metrics self-test: all assertions passed` and `16 passed`.

`metrics.py` is the deliverable. Copy that file verbatim into Sessions 16, 22
and 23 — do not reimplement it, or the numbers across sessions stop being
comparable.

## Where this leads
Session 11 optimizes *speed* using the same postings lists; Session 12 changes
what "relevant" can even mean. Both need this measuring stick, and Session 16
trains a model directly against NDCG — the metric you just implemented becomes
the training objective rather than just the report.
