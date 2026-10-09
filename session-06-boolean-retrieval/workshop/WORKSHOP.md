# Workshop 06 — Boolean Retrieval Engine (≈45 min)

You have a 4-document mini-corpus and a starter with 5 TODOs. By the end of
this workshop you will have a working Boolean search engine that answers
`"sauce AND basil"`, `"sauce OR bread"`, and `"sauce NOT bread"` — without
ever opening a document.

**What you will walk away with:** a complete `boolean_search.py` that builds
postings lists, parses Boolean queries, and evaluates them with correct
operator precedence. The engine is small enough to hold in your head and
real enough to run on the 204-document course corpus.

## Setup (≈5 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`):

```
cd session-06-boolean-retrieval
python workshop/starter/boolean_search.py workshop/data "sauce AND basil"
```

You should see `TODO-1 not done yet` plus a note about 5 TODOs. Nothing
crashes. Work top to bottom.

## Meet your patient
`workshop/data/` — four tiny documents:

```
doc-a.txt: topic python — "Python builds an inverted index term by term. / A search query reads the postings lists."
doc-b.txt: topic cooking — "Simmer the tomato sauce for twenty minutes. / A good sauce depends on fresh basil."
doc-c.txt: topic search — "An inverted index answers a search query instantly. / Python powers most search tools."
doc-d.txt: topic cooking — "Bread and sauce make a simple dinner. / The bread soaks up the sauce."
```

Four documents, 39 unique terms. Every result you produce in the next 40
minutes can be checked against these by hand.

## The journey

### Stop 1 — AND, OR, NOT as set operations (≈15 min)
The three Boolean operators are set operations on postings lists. The starter
already has `build_postings()` and `postings_for()` from Session 5 — those
work. What is missing is the algebra.

New idea, one line: a postings list is a sorted list of document ids, and
the three Boolean operators are intersection, union, and difference on those
lists.

Open `workshop/starter/boolean_search.py` and replace **TODO-1, TODO-2,
TODO-3**:

```python
def intersect(left, right):
    if len(left) <= len(right):
        small, big = left, right
    else:
        small, big = right, left
    hits = []
    for doc_id in small:
        if doc_id in big:
            hits.append(doc_id)
    return hits

def union(left, right):
    out = []
    for doc_id in sorted(left + right):
        if doc_id not in out:
            out.append(doc_id)
    return out

def subtract(left, right):
    out = []
    for doc_id in left:
        if doc_id not in right:
            out.append(doc_id)
    return out
```

Checkpoint:

```
python workshop/starter/boolean_search.py workshop/data "sauce AND basil"
```

You now get a complaint about TODO-4 instead of TODO-1 — the three set
operations are in place. (Empty-file path: typing the three functions into an
empty file and calling `intersect(["doc-b","doc-d"], ["doc-b"])` prints
`['doc-b']`.)

*What you just learned: AND is intersection, OR is union, NOT is difference —
and the shortest-list-first rule makes intersection cheap.*

### Stop 2 — Parse the query string (≈10 min)
A query like `"sauce AND basil"` is a string. The engine needs tokens:
`['sauce', 'AND', 'basil']`. Operators are uppercased so `and` and `AND` work
the same way.

Replace **TODO-4**:

```python
tokens = []
for raw in query.split():
    word = raw.strip(PUNCTUATION)
    if word == "":
        continue
    upper = word.upper()
    if upper in OPERATORS:
        tokens.append(upper)
    else:
        tokens.append(word.lower())
return tokens
```

Checkpoint:

```
python workshop/starter/boolean_search.py workshop/data "sauce AND basil"
```

You now get a complaint about TODO-5 — the parser works. (Empty-file path:
`parse_query("Sauce AND basil")` returns `['sauce', 'AND', 'basil']`.)

*What you just learned: tokenizing a query is the same recipe as tokenizing a
document — split, strip punctuation, normalize case — plus one extra step to
recognize operators.*

### Stop 3 — Evaluate with correct precedence (≈10 min)
The evaluator handles one AND-group at a time: intersect the positive terms
(shortest first), then subtract the NOT terms. OR is handled by the caller,
which unions the results of each group.

Replace **TODO-5**:

```python
positive = []
negative = []
for term, negated in group:
    if negated:
        negative.append(term)
    else:
        positive.append(term)
hits = None
for term in positive:
    current = postings_for(postings, term)
    if hits is None:
        hits = current
    else:
        hits = intersect(hits, current)
if hits is None:
    hits = sorted(all_docs)
for term in negative:
    hits = subtract(hits, postings_for(postings, term))
return hits
```

Checkpoint:

```
python workshop/starter/boolean_search.py workshop/data "sauce AND basil"
```

```
folder: workshop/data
documents: 4 (doc-a, doc-b, doc-c, ...)
terms: 39
query: sauce AND basil
tokens: ['sauce', 'AND', 'basil']
  group 1: sauce AND basil
  postings 'sauce': 2 of 4 docs
  postings 'basil': 1 of 4 docs
hits (1): doc-b
```

Now try the other two queries:

```
python workshop/starter/boolean_search.py workshop/data "sauce OR bread"
python workshop/starter/boolean_search.py workshop/data "sauce NOT basil"
```

Expected:

```
hits (2): doc-b, doc-d
hits (1): doc-d
```

*What you just learned: Boolean evaluation is a two-level parse — OR splits
into groups, AND within each group — and NOT is just subtraction from the
universe of matching documents.*

### Stop 4 — Aim at the real corpus (≈10 min)
The mini-corpus was for hand-verification. Now point the engine at the real
thing:

```
python workshop/starter/boolean_search.py ../../datasets/corpus "python AND search"
python workshop/starter/boolean_search.py ../../datasets/corpus "tomato AND sauce"
python workshop/starter/boolean_search.py ../../datasets/corpus "mars AND rover"
```

The engine handles 204 documents and thousands of terms with the same code.
The postings lists are longer but the algebra is identical.

*What you just learned: the Boolean engine is corpus-independent — the same
operations work whether you have 4 documents or 4 million.*

## Expected output
Exact output of the correct solution, from this folder:

```
folder: workshop/data
documents: 4 (doc-a, doc-b, doc-c, ...)
terms: 39
query: sauce AND basil
tokens: ['sauce', 'AND', 'basil']
  group 1: sauce AND basil
  postings 'sauce': 2 of 4 docs
  postings 'basil': 1 of 4 docs
hits (1): doc-b
```

And on the real corpus:

```
folder: ../../datasets/corpus
documents: 204 (doc-001, doc-002, doc-003, ...)
terms: <varies>
query: python AND search
tokens: ['python', 'AND', 'search']
  group 1: python AND search
  postings 'python': <varies> of 204 docs
  postings 'search': <varies> of 204 docs
hits (<varies>): doc-XXX, ...
```

## Stretch goals (optional)
- **Parentheses.** Extend the parser to support `"(python OR java) AND search"`.
  You will need a recursive descent parser or the shunting-yard algorithm.
- **Phrase search.** Add a `""` operator for exact phrase matching. This
  requires a positional index (Session 5 mentioned it) — store term positions
  per document and check adjacency.
- **Benchmark.** Time `intersect()` on the real corpus for queries with 2, 3,
  and 4 AND terms. Plot the results. Does the shortest-first rule matter more
  as the number of terms grows?

## Solution
`workshop/solution/` — attempt the journey first. Sanity check:

```
python -m pytest workshop/solution/ -v
```

Expected: `37 passed`.

## Where this leads
Session 7 adds scores to the Boolean result. TF-IDF turns the binary
"matches / does not match" into a ranked list, so `sauce OR bread` returns
`[doc-b, doc-d]` in order of relevance rather than alphabetically. The
postings lists you built here are the foundation — TF-IDF just adds a weight
to each posting.
