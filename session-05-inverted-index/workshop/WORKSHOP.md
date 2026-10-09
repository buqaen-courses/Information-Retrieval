# Workshop 05 — Build an Inverted Index From an Empty File (≈45 min)

Session 3 built a dictionary that mapped a term to a file. That was a promise.
Today you keep it. In forty-five minutes you will turn three small text files
into the structure that sits underneath every search engine ever shipped — the
inverted index — and answer your first real query out of it. No libraries, no
frameworks: `open()`, a `for` loop, a plain `dict`, and `sorted()`.

**What you will walk away with:** a working `inverted_index.py` that builds both
index shapes over a folder of `.txt` files, counts term frequency, answers
two-term AND queries, and agrees with a brute-force scan over the real
204-document course corpus — plus pytest tests you can read line by line.

You know basic Python (variables, loops, functions). Everything else is
explained below, with the exact file contents and code shapes inline. No
hunting through other files needed. Total: **4 stops, 7 TODOs, 45 minutes.**

## Setup (≈3 min)

Activate the course venv first (one-time setup in the main `README.md`), then
run every command from this folder (`session-05-inverted-index/`) as plain
`python`:

```
cd session-05-inverted-index
python workshop/starter/inverted_index.py workshop/data index term
```

You should see `TODO-7 not done yet` — the starter runs, hints print, nothing
crashes. That friendly failure is by design: you will silence each TODO, one
stop at a time.

## Meet your patients

`workshop/data/` — three documents, six lines total, nothing hidden. Keep them
in mind; every number you produce today can be checked by hand.

```
doc-a.txt
    topic: python
    Python builds an inverted index term by term.
    Every term maps to a list of documents.

doc-b.txt
    topic: search
    An inverted index answers a query without reading every document.
    The index keeps a postings list for each term.

doc-c.txt
    topic: cooking
    Simmer the tomato sauce for twenty minutes.
    A good sauce depends on fresh basil.
```

Two things to notice straight away. First, `doc-a` says **term** three times
("term by term", "Every term"); `doc-b` says it once. Second, we index the
`topic:` line too — that is why `topic` will appear in all three postings
lists, exactly like it appears in all 204 documents of the real corpus.

There are two ways to do this workshop. Both are checked against the same real
outputs. **Preferred:** open a brand-new empty file (anywhere you like, e.g.
`my_index.py`) and type each stop's snippet in order, running the file after
every stop — every checkpoint below is the real output of that command.
**Shortcut:** open `workshop/starter/inverted_index.py` and replace the TODO
bodies with the same snippets. The starter is a convenience, not the only path.

## The journey

### Stop 1 — Turn text into terms (≈12 min)

Your index will be a dict keyed by words, so the very first job is turning text
into words. `tokenize()` is the function every later session reuses.

Three calls, one rule each:

- `text.lower()` — a string method returning a copy with every letter folded to
  lowercase, so `"Python"` and `"python"` stop being two different keys.
- `text.split()` — cuts a string on whitespace and returns a **list** of the
  pieces. `"a b  c".split()` → `['a', 'b', 'c']`.
- `raw.strip(".,!?;:'\"()")` — string method that removes any of those
  characters from **both ends** of a string. It takes a *set of characters*,
  not a word: `"golden."` → `"golden"`, and a lonely `"?"` → `""` (the empty
  string), which is why we skip empty results.

Start your empty `my_index.py` with exactly this, then run it:

```python
PUNCTUATION = ".,!?;:'\"()"


def tokenize(text):
    """Turn raw text into a list of normalized terms."""
    tokens = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word != "":
            tokens.append(word)
    return tokens


print(tokenize("Bake the bread until the crust turns golden."))
```

If you are using the starter instead: replace **TODO-1** in
`workshop/starter/inverted_index.py` with the body of `tokenize()` above.

Hint: the `if word != "":` guard is what keeps `""` out of the index — leave it
in and the empty string becomes a term of its own.

Checkpoint:

```
python my_index.py
```

```
['bake', 'the', 'bread', 'until', 'the', 'crust', 'turns', 'golden']
```

Check it by hand: eight words in, eight terms out, the trailing period gone,
`Bake` folded to `bake`. That is a complete tokenizer.

*What you just learned: normalization is three string methods, and the index
can only be as trustworthy as this function.*

### Stop 2 — Read one file, then list the folder (≈12 min)

Now feed `tokenize()` real files. Two new pieces of plumbing: one function that
reads a single document, and one that names every document in the folder.

New calls, one line each:

- `open(path, mode="r", encoding="utf-8")` — hands back a file object you read
  through; `mode="r"` means read and `encoding="utf-8"` decodes text the same
  way on every machine (Session 1 covered the full parameter list).
- `os.listdir(folder)` — the standard-library way to get the **names** of the
  files inside a folder, as a list. The order is whatever the OS felt like
  returning, which is why we sort it. (`import os` at the very top of the file
  gives you this and `os.path` helpers.)
- `name.endswith(".txt")` — string method returning `True`/`False` for a suffix.
- `name.replace(".txt", "")` — string method returning a copy with those
  characters replaced; it turns `"doc-a.txt"` into `"doc-a"`.

Add these two functions **above** your `print(...)` line at the bottom (that
line is just a scratch check — you will replace it at the next stop):

```python
import os


def read_tokens(path):
    """Read one .txt file and return its normalized terms."""
    f = open(path, mode="r", encoding="utf-8")
    text = f.read()
    f.close()
    return tokenize(text)


def list_doc_ids(folder):
    """Return the sorted doc ids of every .txt file in folder."""
    names = os.listdir(folder)
    doc_ids = []
    for name in sorted(names):
        if name.endswith(".txt"):
            doc_ids.append(name.replace(".txt", ""))
    return doc_ids


def doc_path(folder, doc_id):
    """Build the file path for a doc id inside folder."""
    return folder + "/" + doc_id + ".txt"
```

`doc_path()` is pure string joining (`+` glues strings together) — no fancy
library, just so the rest of the file reads cleanly. Keep `import os` at the
very top of your file, above `PUNCTUATION`.

In the starter: **TODO-2** and **TODO-3**.

Hint: `sorted(names)` sorts strings alphabetically, and `"doc-a" < "doc-b"` is
`True` — that ordering is what makes every postings list later come out
ascending.

Now replace the scratch `print(...)` at the bottom of your file with these two
lines and run it:

```python
print(list_doc_ids("workshop/data"))
print(len(read_tokens("workshop/data/doc-a.txt")))
```

Checkpoint:

```
python my_index.py
```

```
['doc-a', 'doc-b', 'doc-c']
18
```

Count `doc-a` by hand: line 1 gives `topic`, `python` (2); line 2 gives
`python`, `builds`, `an`, `inverted`, `index`, `term`, `by`, `term` (8);
line 3 gives `every`, `term`, `maps`, `to`, `a`, `list`, `of`, `documents`
(8). Total 18. `len(list)` returns how many items a list holds.

*What you just learned: read one file at a time, and turn a folder of files
into a sorted list of doc ids.*

### Stop 3 — Build the index: `{term: [doc_ids]}`, then `{term: {doc_id: tf}}` (≈12 min)

This is the heart of the session, and it is two loops. Two dictionary tricks to
know before you type it:

- `if term not in postings:` — the membership test on a dict. `True` means the
  key has never been seen, so create an empty list for it first.
- `postings[term].append(doc_id)` — the **list method** that adds an item to
  the end of a list.

The `if doc_id not in postings[term]` guard in the first function is the line
students most often forget, so say it out loud: **a doc id goes into a postings
list once, no matter how many times the term occurs inside it.** The repeat
count is not lost — it is the *next* function's job.

Add these two functions (starter: **TODO-4** and **TODO-5**):

```python
def build_postings(folder):
    """Return {term: [doc_id, ...]} — the v1 inverted index."""
    postings = {}
    for doc_id in list_doc_ids(folder):
        for term in read_tokens(doc_path(folder, doc_id)):
            if term not in postings:
                postings[term] = []
            if doc_id not in postings[term]:
                postings[term].append(doc_id)
    ordered = {}
    for term in sorted(postings):
        ordered[term] = sorted(postings[term])
    return ordered


def add_tf(folder):
    """Return {term: {doc_id: tf}} — the v2 index, tf = term frequency."""
    index = {}
    for doc_id in list_doc_ids(folder):
        for term in read_tokens(doc_path(folder, doc_id)):
            if term not in index:
                index[term] = {}
            if doc_id not in index[term]:
                index[term][doc_id] = 0
            index[term][doc_id] = index[term][doc_id] + 1
    return index
```

Hint: the only differences between the two are (a) the container —
`postings[term]` is a **list** in v1 and a **dict** in v2 — and (b) `+ 1`
instead of a guard, which is what turns "seen once" into "seen three times".

Replace the scratch prints at the bottom of your file with these four and run:

```python
postings = build_postings("workshop/data")
print("terms:", len(postings))
print("postings['index']:", postings["index"])
index = add_tf("workshop/data")
print("tf['term']:", index["term"])
```

Checkpoint:

```
python my_index.py
```

```
terms: 37
postings['index']: ['doc-a', 'doc-b']
tf['term']: {'doc-a': 3, 'doc-b': 1}
```

Verify by hand against the file listing above: `index` occurs once in `doc-a`
and twice in `doc-b`, so its postings list is `['doc-a', 'doc-b']`; `term`
occurs three times in `doc-a` and once in `doc-b`, so tf is
`{'doc-a': 3, 'doc-b': 1}`. 37 distinct terms survive tokenization — the
`terms:` line is your first real measurement of the index size.

*What you just learned: an inverted index is one nested loop, and tf is the
same walk with a `+ 1` instead of a membership guard.*

### Stop 4 — Answer an AND query, then aim at the real corpus (≈18 min)

An index you cannot query is a bookshelf. AND is set intersection: keep the doc
ids that are in **both** postings lists. Walking the *shorter* list and testing
membership in the longer one (`if doc_id in big:`) is the whole trick.

`sys.argv` is new here, explained in one line: it is the list of words typed
after `python`, so `sys.argv[1]` is the folder and `sys.argv[2]`/`[3]` are the
two query terms. `sys.argv[1:]` is "everything after the script name". `import
sys` goes at the top of the file. The `doc_ids[:3]` slice means "the first three
items of the list" — we only preview them so the report stays readable when the
folder holds 204 files.

Add these, and make sure `if __name__ == "__main__": raise SystemExit(main())`
is the last two lines of your file:

```python
import sys


def search_and(index, term_a, term_b):
    """Return doc ids containing BOTH terms, sorted ascending."""
    if term_a not in index:
        return []
    if term_b not in index:
        return []
    left = index[term_a]
    right = index[term_b]
    if len(left) > len(right):
        small, big = right, left
    else:
        small, big = left, right
    hits = []
    for doc_id in sorted(small):
        if doc_id in big:
            hits.append(doc_id)
    return hits


def main(argv=None):
    """Print a small report for one folder of documents."""
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python inverted_index.py <folder> [termA] [termB]")
        return 2
    folder = args[0]
    term_a = args[1] if len(args) > 1 else "index"
    term_b = args[2] if len(args) > 2 else "term"
    doc_ids = list_doc_ids(folder)
    index = add_tf(folder)
    preview = ", ".join(doc_ids[:3])
    if len(doc_ids) > 3:
        preview = preview + ", ..."
    print("folder: " + folder)
    print("documents: " + str(len(doc_ids)) + " (" + preview + ")")
    print("terms: " + str(len(index)))
    print("postings for '" + term_a + "':")
    if term_a in index:
        for doc_id in sorted(index[term_a]):
            print("  " + doc_id + "  tf=" + str(index[term_a][doc_id]))
    else:
        print("  (term not in index)")
    print("AND '" + term_a + "', '" + term_b + "': "
          + ", ".join(search_and(index, term_a, term_b)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

`", ".join(...)` is a **string method**: it glues the items of a list together
with `", "` between them, and returns one string. `str(42)` turns the number
`42` into the text `"42"` so it can be glued on with `+`.

In the starter: **TODO-7** (the body of `main`), plus `search_and` =
**TODO-6**.

Hint: an unknown term must return `[]`, never crash — `if term_a not in index:`
is the guard that stops `index["zzz"]` from raising `KeyError`.

Checkpoint — the mini-corpus, one term at a time, then the empty-AND case:

```
python my_index.py workshop/data index term
python my_index.py workshop/data index sauce
```

```
folder: workshop/data
documents: 3 (doc-a, doc-b, doc-c)
terms: 37
postings for 'index':
  doc-a  tf=1
  doc-b  tf=2
AND 'index', 'term': doc-a, doc-b
```

```
folder: workshop/data
documents: 3 (doc-a, doc-b, doc-c)
terms: 37
postings for 'index':
  doc-a  tf=1
  doc-b  tf=2
AND 'index', 'sauce': 
```

The trailing space on the last line is real: the answer is the empty string,
because no document contains both `index` and `sauce`. An empty result is a
valid answer, not a bug.

Now the payoff — aim it at the real 204-document course corpus (note the path:
you are one level deep in the repo, so the corpus is `../datasets/corpus`):

```
python my_index.py ../datasets/corpus sauce bread
```

```
folder: ../datasets/corpus
documents: 204 (doc-001, doc-002, doc-003, ...)
terms: 221
postings for 'sauce':
  doc-006  tf=1
  doc-017  tf=2
  doc-036  tf=1
  doc-047  tf=3
  doc-063  tf=1
  doc-065  tf=1
  doc-069  tf=3
  doc-077  tf=1
  doc-085  tf=1
  doc-087  tf=2
  doc-107  tf=2
  doc-108  tf=1
  doc-111  tf=3
  doc-114  tf=2
  doc-131  tf=1
  doc-142  tf=1
  doc-152  tf=1
  doc-164  tf=1
  doc-178  tf=1
  doc-179  tf=1
  doc-182  tf=2
AND 'sauce', 'bread': doc-006, doc-017, doc-036, doc-047, doc-065, doc-077, doc-085, doc-142, doc-152, doc-164
```

221 distinct terms across 204 documents — an index three times smaller than the
corpus, which is the whole point. And 21 cooking documents contain `sauce`,
10 of which also mention `bread`; note `doc-005` is *not* in the answer even
though it says bread three times, because it never says sauce.

*What you just learned: AND is an intersection of two postings lists, and an
empty intersection is a legitimate answer.*

## Expected output

Exact output of the correct solution (pasted from a real venv run, from this
folder, via `python workshop/solution/inverted_index.py ...`):

```
folder: workshop/data
documents: 3 (doc-a, doc-b, doc-c)
terms: 37
postings for 'index':
  doc-a  tf=1
  doc-b  tf=2
AND 'index', 'term': doc-a, doc-b
```

A handful of other values your finished file must agree with, all hand-checkable
against the three files above:

```
list_doc_ids("workshop/data")              -> ['doc-a', 'doc-b', 'doc-c']
len(read_tokens("workshop/data/doc-a.txt")) -> 18
len(build_postings("workshop/data"))       -> 37
build_postings("workshop/data")["sauce"]   -> ['doc-c']
build_postings("workshop/data")["index"]   -> ['doc-a', 'doc-b']
add_tf("workshop/data")["term"]            -> {'doc-a': 3, 'doc-b': 1}
search_and(index, "index", "sauce")        -> []
search_and(index, "zzz",   "index")        -> []
```

## Stretch goals (optional)

Clearly beyond the core deliverable — try after the tests pass.

- **Stop words.** Add a small list `["the", "a", "an", "and", "of", "to", "for"]`
  and skip those tokens in `tokenize()`. Re-run on the real corpus: how does
  `terms: 221` change, and by how much?
- **A positional index.** Extend `add_tf` to `{term: {doc_id: [positions]}}` —
  count with `enumerate()` and append the position instead of `+ 1`. Then
  answer "in which docs do `bread` and `sauce` sit next to each other?"
- **Bridge to Session 6.** Add `search_or(a, b)` (union: keep a doc if it is in
  *either* list) and `search_not(a, b)` (subtract). Three functions and you
  have AND/OR/NOT — that is the next session's whole engine.
- **Save it.** Write the index to a file with `open(..., "w", encoding="utf-8")`
  so a second run can load it instead of re-reading 204 documents.

## Solution

`workshop/solution/` — attempt the journey first, then compare. `inverted_index.py`
is the same code you just wrote (with type hints and docstrings), and
`test_inverted_index.py` holds 19 tests whose expected values you can verify by
hand against the mini-corpus, plus a brute-force cross-check over the real
corpus.

Sanity check (must pass):

```
python -m pytest workshop/solution/ -v
```

Expected: `19 passed`.

(From the repo root instead, the same command is
`python -m pytest session-05-inverted-index/workshop/solution/ -v`.)

## Where this leads

You built the index that Session 6 opens up: `search_and()` is a two-term
Boolean query, and next session turns it into a full `AND`/`OR`/`NOT` engine
that intersects, unions and subtracts whole postings lists — fast, because the
lists are sorted. From there Session 7 drops the sets and scores documents with
TF-IDF, Session 8 replaces that with BM25, and Session 11 compresses and prunes
these very postings lists to make them faster than your 204 documents will ever
be. Everything from here to Session 23 is a consumer of the structure you just
wrote.