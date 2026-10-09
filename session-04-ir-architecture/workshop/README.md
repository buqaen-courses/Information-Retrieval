# Workshop 04 — Annotating the Architecture (≈45 min)

You have been hired as the search engineer at **Northwind Outdoor**, a small
online shop. The manager hands you a list of eight things the search box must
do. Sessions 5 to 23 build them — but today you decide **which box of the
architecture each one belongs to**, because a requirement you cannot place in a
system is a requirement you cannot build.

**What you will walk away with:** an `annotate.py` that prints the architecture
mapped to all eight requirements (that printout *is* the annotated diagram the
brief asks for), plus a real measurement of the vocabulary gap that explains
why the EMBED box exists at all.

## Setup (≈5 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`):

```
cd session-04-ir-architecture
python workshop/starter/annotate.py
```

You should see `TODO-2 not done yet` plus a note about 4 TODOs. Nothing
crashes. Work top to bottom.

## Meet your brief
`workshop/data/scenario.md`. Eight requirements, R1 to R8. The picture you are
annotating against is `images/04-01-ir-architecture.png` — eight boxes:
`CRAWL`, `PARSE`, `DEDUPE`, `INDEX`, `EMBED`, `QUERY`, `RANK`, `EVALUATE`.
Eight requirements, eight boxes.

You already know the data. `datasets/corpus/` holds 204 documents in six topics
(python, football, cooking, space, movies, travel), each file shaped:

```
topic: football
The referee showed a yellow card for the late tackle.
The referee showed a yellow card for the late tackle. The referee showed a yellow card for the late tackle. The striker scored twice in the second half.
```

That first line, `topic: football`, is metadata the generator wrote into the file.
Stop 3 depends on it being counted — every football document says the word
"football" only in its own header.

## The journey

### Stop 1 — Map a requirement to its box (≈10 min)
The list above the functions in the starter already pairs each requirement with
a box — that is the easy part, and it is given to you. What is missing is the
code that joins them to the sessions that build them.

New idea, one line: `dict(PIPELINE)`. `PIPELINE` is a list of
`(box, sessions)` pairs; wrapping it in `dict()` turns it into a lookup, so
`sessions_of["RANK"]` gives you `"S8-9, S16, S22"`.

Open `workshop/starter/annotate.py` and replace **TODO-2**:

```python
sessions_of = dict(PIPELINE)          # box -> "which sessions build it"
rows = []
for rid, demand, box in REQUIREMENTS:
    rows.append({"id": rid, "demand": demand, "box": box,
                 "sessions": sessions_of[box]})
return rows
```

Checkpoint:

```
python workshop/starter/annotate.py
```

You now get a complaint about TODO-4 instead of TODO-2 — the join worked, the
printing does not exist yet. (Empty-file path: `print(annotate()[0])` prints
the R1 row as a dict.)

*What you just learned: a list of pairs and a dict of the same data are the
same information in two shapes — `dict()` converts one to the other.*

### Stop 2 — Check that nothing was left behind (≈10 min)
A mapping that leaves a box empty is a broken design. This is the same set
subtraction you will use in Session 6 to compute `A AND NOT B`.

Replace **TODO-3**:

```python
used = set()
for row in rows:
    used.add(row["box"])
missing = []
for box, sessions in PIPELINE:
    if box not in used:
        missing.append(box)
return missing
```

`used` is the set of boxes the requirements mapped to — 8 of them. The loop
then keeps any `PIPELINE` box that is not in it.

Checkpoint — the starter still stops at TODO-4, but the logic is in place.
(Empty-file path: feed `annotate()` into `unclaimed_boxes()` and you get
`[]` — every box is claimed.)

*What you just learned: membership testing with sets, and why "nothing left
over" is a design check rather than decoration.*

### Stop 3 — Print it, then measure the vocabulary gap (≈15 min)
A mapping nobody can read is a diary entry. Replace **TODO-4**:

```python
for row in rows:
    print(row["id"] + "  " + row["box"] + "  (" + row["sessions"]
          + ")  " + row["demand"])
print("boxes claimed:", len(set(r["box"] for r in rows)), "of", len(PIPELINE))
missing = unclaimed_boxes(rows)
print("boxes with no requirement:", missing if missing else "none")
```

Checkpoint:

```
python workshop/starter/annotate.py
```

```
the IR architecture, annotated for shop search
====================================================================
R1  CRAWL     (S17-19            ) fetch all 128 product pages, one page per second
R2  PARSE     (S18-19            ) pull name, price and description out of each page
R3  DEDUPE    (S20               ) eight products repeat one description; show no copies
R4  INDEX     (S5-6, S21         ) keep a term dictionary of every word shoppers type
R5  EMBED     (S12-13            ) a shopper searching 'soccer' must find football boots
R6  QUERY     (S1-3              ) one search box; 'under 100' filter must apply
R7  RANK      (S8-9, S16, S22    ) show the ten most relevant products first
R8  EVALUATE  (S10               ) log every click so we can measure the new ordering
====================================================================
boxes claimed: 8 of 8
boxes with no requirement: none
```

*What you just learned: turning a mapping into a report, and proving
completeness rather than asserting it.*

Now the argument that earns the EMBED box its salary. Requirement R5 says a
shopper who types `soccer` must find the football boots. Is that a real problem,
or a straw man? Count it. In `vocabulary_gap()` the pattern is the Session 1
one — `open()`, `for line in f:`, a `dict` tally — applied to a question
instead of a word count:

```python
def tokens_of(path):
    """Session 1's recipe: lowercase, peel punctuation, split into words."""
    words = []
    with open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            for raw in line.lower().split():
                word = raw.strip(".,!?;:\"'()")
                if word:
                    words.append(word)
    return words

typed_words = ["rover", "soccer", "telescope"]
for word in typed_words:
    hits = 0
    for path in corpus_paths():
        if word in tokens_of(path):   # exact word, not a substring
            hits = hits + 1
    print(word, "->", hits)
```

One detail that decides the answer: exact word, not substring. `"rover" in
text` would find it inside `"rovers"` and report 14 documents — a false alarm
that would make the whole EMBED box look unnecessary. Comparing whole tokens is
what a search engine's dictionary actually does.

Run the finished solution and read the output:

```
python workshop/solution/annotate.py
```

```
shopper types rover    ->   0 docs;  corpus writes rovers    ->  14 docs
shopper types soccer   ->   0 docs;  corpus writes football  ->  34 docs
shopper types telescope ->   0 docs;  corpus writes telescopes ->  16 docs
```

Zero. Typed the way people actually talk, the word these documents use simply
does not exist in the corpus. Stemming fixes `rover`/`rovers` (Session 5);
only meaning fixes `soccer`/`football` (Session 12). That is requirement R5,
and that is why the box exists.

*What you just learned: measuring a claim about language before you build
anything to fix it — and finding the claim is real.*

## Expected output
Exact output of the correct solution, from this folder:

```
the IR architecture, annotated for shop search
====================================================================
R1  CRAWL     (S17-19            ) fetch all 128 product pages, one page per second
R2  PARSE     (S18-19            ) pull name, price and description out of each page
R3  DEDUPE    (S20               ) eight products repeat one description; show no copies
R4  INDEX     (S5-6, S21         ) keep a term dictionary of every word shoppers type
R5  EMBED     (S12-13            ) a shopper searching 'soccer' must find football boots
R6  QUERY     (S1-3              ) one search box; 'under 100' filter must apply
R7  RANK      (S8-9, S16, S22    ) show the ten most relevant products first
R8  EVALUATE  (S10               ) log every click so we can measure the new ordering
====================================================================
boxes claimed: 8 of 8
boxes with no requirement: none

the vocabulary gap (measured on 204 corpus docs)
--------------------------------------------------------------------
shopper types rover    ->   0 docs;  corpus writes rovers    ->  14 docs
shopper types soccer   ->   0 docs;  corpus writes football  ->  34 docs
shopper types telescope ->   0 docs;  corpus writes telescopes ->  16 docs
```

## Stretch goals (optional)
- **Requirement R6 is two jobs.** Split it into "parse the query" and "apply a
  structured filter", annotate both, and say which session teaches each.
- **A ninth box.** Add `MULTIMODAL` to the architecture and annotate a
  requirement for it. Does any current session already build half of it?
- **Count the topic lines.** Delete the `topic:` header from a copy of the
  corpus and re-measure the `football` row. Why does the number drop, and what
  does that tell you about the difference between a document's text and its
  metadata?

## Solution
`workshop/solution/` — attempt the journey first. Sanity check:

```
python -m pytest workshop/solution/ -v
```

Expected: `7 passed`.

## Where this leads
Session 5 builds the INDEX box for real — tokenization, postings lists, and a
term dictionary that answers the question your Stop 3 measurement just raised
for the `rover`/`soccer` case. Keep the annotated table; you will annotate it
again in Session 23 with the actual tools wired in.
