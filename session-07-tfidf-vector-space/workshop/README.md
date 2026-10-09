# Workshop 07 — Your First Ranking Engine (≈45 min)

Boolean search can only say yes or no. You are about to build the thing that
replaces that limitation: a ranker that gives every document a *score*, so
results arrive in order of how well they match. Every search result list you
have ever seen was produced by something very much like what you write in the
next 40 minutes.

**What you will walk away with:** a working `tfidf_ranker.py` that turns a folder
of documents into TF-IDF vectors, turns a query into a vector, and ranks the
corpus by cosine similarity — plus a clear answer to the question that trips
everyone up: why does this return *more* results than Session 6's Boolean AND?

## Setup (≈5 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`):

```
cd session-07-tfidf-vector-space
python workshop/starter/tfidf_ranker.py workshop/data "cat"
```

You should see `TODO-1 not done yet` plus a note about 4 TODOs. Nothing
crashes. Work top to bottom.

## Meet your patient
`workshop/data/` — three documents, short enough to verify by hand:

```
doc-a.txt: the cat sat on the mat
doc-b.txt: the dog sat on the log
doc-c.txt: the cat chased the dog
```

Write down the vocabulary before you start — this is the whole computation:

```
the, cat, sat, on, mat, dog, log, chased      (8 terms)
```

And the document frequencies, which is all IDF needs:

| term | docs containing it (df) |
|---|---|
| the | 3 |
| cat | 2 |
| sat | 2 |
| on | 2 |
| dog | 2 |
| mat, log, chased | 1 |

Now compute one weight by hand: `log(1 + (3 - 3 + 0.5) / (3 + 0.5))` =
`log(1.1428)` ≈ **0.1335**. That is the weight of `the`. `log` is still in
*chased* at `log(1 + (3 - 1 + 0.5)/(1 + 0.5))` = `log(2.6667)` ≈ **0.9808**.
The word in every document is worth almost nothing; the rare word is worth
eight times as much. That is IDF, finished.

## The journey

### Stop 1 — Build the TF-IDF matrix (≈15 min)
A document vector has one number per vocabulary term. Most are zero.

New call, one line: `np.zeros((n_docs, n_terms))` allocates a matrix of that
shape filled with zeros — here a 3×8 grid. You fill one cell per (document,
term) pair.

Open `workshop/starter/tfidf_ranker.py` and replace **TODO-1**:

```python
import math
import numpy as np

n_docs = len(doc_tokens)
n_terms = len(vocab)
term_to_idx = {t: i for i, t in enumerate(vocab)}
mat = np.zeros((n_docs, n_terms))
for i, tokens in enumerate(doc_tokens):
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    for term, count in tf.items():
        if term in term_to_idx:
            j = term_to_idx[term]
            idf = math.log(1 + (n_docs - term_doc_freq[term] + 0.5) /
                           (term_doc_freq[term] + 0.5))
            mat[i, j] = (1 + math.log(count)) * idf
return mat
```

(`1 + math.log(count)` is `log(tf) + 1` — the damping curve from concept 07.1.
It keeps the tenth occurrence from being worth ten times the first.)

Checkpoint:

```
python workshop/starter/tfidf_ranker.py workshop/data "cat"
```

You now get a complaint about TODO-2 instead of TODO-1 — the matrix exists.
(Empty-file path: print the matrix and you get a 3×8 grid where the `cat` column
reads `0.9808, 0.0000, 0.9808`.)

*What you just learned: a document is a row of the matrix, and each cell is
`log(tf) × idf` — frequency damped, rarity rewarded.*

### Stop 2 — Cosine similarity (≈10 min)
Now compare directions. `np.linalg.norm(v)` returns the vector's length (its
magnitude); dividing by it removes the "long document" bias.

Replace **TODO-2**:

```python
import numpy as np
na = np.linalg.norm(a)
nb = np.linalg.norm(b)
if na == 0 or nb == 0:
    return 0.0
return float(np.dot(a, b) / (na * nb))
```

The `if na == 0` guard is not decoration: a query with no known terms produces a
zero vector, and dividing by zero gives you `nan`, which silently poisons an
entire ranking. This is the same defensive habit as Session 4's missing-embedding
check.

Checkpoint — the starter still reports TODO-3. (Empty-file path:
`cosine_similarity(np.array([1.0, 0.0]), np.array([1.0, 0.0]))` returns
`1.0`, and against `[0.0, 1.0]` returns `0.0`.)

*What you just learned: cosine similarity compares angle, not length, and a
zero vector is a real case you must handle.*

### Stop 3 — Rank documents for a query (≈12 min)
The query vector uses the same IDF weights (with `tf = 1` for each query term,
so `1 + log(1) = 1`). Then score every document and sort.

Replace **TODO-3**:

```python
import math
doc_ids, doc_tokens, term_doc_freq = build_index(folder)
vocab = sorted(term_doc_freq)
mat = compute_tfidf(doc_tokens, term_doc_freq, vocab)
term_to_idx = {t: i for i, t in enumerate(vocab)}
q_tokens = tokenize(query)
q_vec = np.zeros(len(vocab))
for t in set(q_tokens):
    if t in term_to_idx:
        j = term_to_idx[t]
        idf = math.log(1 + (len(doc_ids) - term_doc_freq[t] + 0.5) /
                       (term_doc_freq[t] + 0.5))
        q_vec[j] = idf
scores = []
for i, doc_id in enumerate(doc_ids):
    s = cosine_similarity(q_vec, mat[i])
    if s > 0:
        scores.append((doc_id, s))
scores.sort(key=lambda x: (-x[1], x[0]))
return scores
```

Two details worth naming. `set(q_tokens)` means a query word typed twice
contributes once. And `key=lambda x: (-x[1], x[0])` sorts by score descending
while breaking ties alphabetically, so results are **reproducible** — a ranker
that reorders equal scores between runs is impossible to debug.

Checkpoint:

```
python workshop/starter/tfidf_ranker.py workshop/data "cat dog"
```

```
query: cat dog
folder: workshop/data
results (3):
  doc-c: 0.5540
  doc-a: 0.2579
  doc-b: 0.2579
```

Now read that result carefully, because it is the lesson. `cat dog` in Session 6
was `cat AND dog` — only `doc-c` contains both words, so Boolean returned one
result. TF-IDF returned **three**.

*What you just learned: a ranking model scores partial matches instead of
discarding them, which is why real search engines rarely return an empty page.*

### Stop 4 — Aim at the real corpus (≈8 min)
Three documents is a toy. Now the 204-document course corpus:

```
python workshop/starter/tfidf_ranker.py ../../datasets/corpus "tomato sauce"
python workshop/starter/tfidf_ranker.py ../../datasets/corpus "rover rocks water"
```

Compare against Session 6, which you can still run:

```
python ../session-06-boolean-retrieval/workshop/solution/boolean_search.py \
    ../../datasets/corpus "tomato AND sauce"
```

Boolean gives you the documents with both words. TF-IDF gives you those *plus*
the near-misses, in order. Both are correct answers to different questions.

*What you just learned: Boolean answers "which documents match?", TF-IDF answers
"which documents match *most*?" — and the second is what a search box needs.*

## Expected output
Exact output of the correct solution, from this folder:

```
$ python workshop/solution/tfidf_ranker.py workshop/data "cat dog"
query: cat dog
folder: workshop/data
results (3):
  doc-c: 0.5540
  doc-a: 0.2579
  doc-b: 0.2579
```

## Stretch goals (optional)
- **Explain the 0.2579 tie.** doc-a and doc-b score identically. Write down why
  they are symmetric, then break the tie with a real signal.
- **Compare against `sklearn`.** `TfidfVectorizer` does this in one line. Load
  `workshop/data`, fit it, and check whether its ranking matches yours. Where
  does it differ, and why?
- **Load the corpus.** Add a `chunk` argument to `main()` that limits the
  vocabulary to the first 2,000 terms, then watch NDCG-style ranking quality
  change on the same query.

## Solution
`workshop/solution/` — attempt the journey first. Sanity check:

```
python -m pytest workshop/solution/ -v
```

Expected: `8 passed`.

## Where this leads
Session 8 keeps everything you just built and replaces the `log(tf)` and `idf`
pieces with the BM25 formula — which fixes the length bias more smoothly and
lets you tune two knobs (`k1`, `b`) against the course qrels. Your
`compute_tfidf` becomes the baseline you measure BM25 against.
