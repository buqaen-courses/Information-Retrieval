# Workshop 03 — Two Ways to Search: Brute Force vs a Dictionary (≈45 min)

Ask a search engine one question — *which documents mention "rovers"?* — and
there are only two possible answers. Either you open every single document and
look, every time a question arrives; or you open every document exactly once,
write down what you saw, and from then on just read your own notes. The first
is five lines of code and dies at scale. The second is twelve lines of code and
is, without exaggeration, the thing Google runs on. Today you write both, you put
a real stopwatch on them, and you watch the second one win by six orders of
magnitude — on 204 real documents, measured live, not quoted from a blog.

**What you will walk away with:** a working `search_index.py` that answers a
query two different ways, proves both ways return the *same* documents, measures
both honestly, and writes the benchmark chart that shows the index winning.

You know basic Python (variables, loops, functions) and Session 1's file reading.
Nothing else is assumed — every new call is explained where it first appears, and
every code snippet is written out in full below. No hunting through other files.

## Setup (≈4 min)

Activate the course venv first (one-time setup lives in the main `README.md`),
then run every command from this folder (`session-03-naive-search-indexing/`) as
plain `python`:

```
python workshop/starter/search_index.py workshop/data/mini_corpus python
```

You should see `TODO-1 not done yet` — the starter runs, prints a hint, and
never crashes. That friendly failure is by design: you will silence one TODO per
stop. When you finish Stop 4, this exact command prints the full report.

## Meet your patients

`workshop/data/mini_corpus/` holds four tiny documents. They are small enough to
read faster than this paragraph, which is the point — you can check every number
you produce by hand.

`doc-a.txt`
```
topic: python
Python functions return values.
Lists and dictionaries store objects.
```

`doc-b.txt`
```
topic: football
The striker scored twice.
The goalkeeper saved a shot.
```

`doc-c.txt`
```
topic: python
Python lists and dictionaries store objects.
A virtual environment isolates dependencies.
```

`doc-d.txt`
```
topic: cooking
Simmer the tomato sauce slowly.
Chop fresh basil for the pasta.
```

Three facts you will use over and over: `"python"` appears in **doc-a and
doc-c** (twice in doc-c: the topic line and the body), `"shot"` appears only in
**doc-b**, and `"dough"` appears in **none** of them. There are exactly **33**
distinct words across all four files. There is also
`workshop/data/sample_notes.txt`, the six-line file used by the README's worked
example, kept here so you can rerun that demo yourself.

## The journey

### Stop 1 — The honest way: read every file (≈10 min)

Right now the program cannot even see the folder. Two jobs: find the files
(**TODO-1**), then ask every one of them (**TODO-2**).

New calls, one line each:

- `os.listdir(folder)` — hands back a **list of the names** of everything in a
  folder, as plain strings. It does not open anything and it does not recurse.
- `name.endswith(".txt")` — a yes/no test: does this string end with `.txt`?
- `os.path.join(folder, name)` — glues a folder and a filename together with the
  right separator (`\` on Windows, `/` everywhere else). Never build paths by
  adding `"/"` yourself.
- `term in words_of(path)` — the "ask this document" test. `words_of()` is given
  to you: it opens the file, lowercases it, splits it on whitespace and strips
  punctuation, returning a list of whole words. `in` on a list means "is this
  item in the list somewhere".

Open `workshop/starter/search_index.py` and replace **TODO-1** and **TODO-2**:

```python
def list_txt_files(directory):
    names = []
    for name in os.listdir(directory):
        if name.endswith(".txt"):
            names.append(name)
    names.sort()
    return names


def scan_for_term(directory, names, term):
    hits = []
    for name in names:
        path = os.path.join(directory, name)
        if term in words_of(path):
            hits.append(name)
    return hits
```

`names.sort()` is not decoration: `os.listdir` returns names in whatever order
the operating system feels like, and without sorting your output would change
between machines. `sorted()` is the function you learned in Session 1; here it is
used as a *method* on the list itself, `names.sort()`, which sorts in place and
returns nothing.

**Checkpoint** — add these four probe lines at the very bottom of your file (or
in a scratch file that imports nothing) and run `python my_search.py`:

```python
d = "workshop/data/mini_corpus"
print(list_txt_files(d))
print(scan_for_term(d, list_txt_files(d), "python"))
print(scan_for_term(d, list_txt_files(d), "dough"))
```

Real output:

```
['doc-a.txt', 'doc-b.txt', 'doc-c.txt', 'doc-d.txt']
['doc-a.txt', 'doc-c.txt']
[]
```

Check it against the four documents above: correct, and `"dough"` correctly finds
nothing. (If you are editing `starter/search_index.py` instead, the same command
now complains about **TODO-3** instead of TODO-1 — that is your progress meter.)

*What you just learned: how to enumerate a folder and ask every document a
question, in six lines.*

### Stop 2 — The clever way: write the answers down once (≈13 min)

That scan is correct and hopelessly slow — it re-asks the corpus every single
time. Now build the dictionary instead (**TODO-3**), and add the one-line query
(**TODO-4**).

The new idea is a **dict**: `index[word]` gives you a **list of filenames** the
first time you meet a word, and every later sighting just appends. Two things
will trip you up, so read them twice:

- `word not in index` tests the dict's **keys**. `index[word]` *reads* a value;
  the `in` test first stops you getting a `KeyError` for a word nobody used.
- `index[word][-1]` is the **last item** of that list. Because we finish one
  file before opening the next, every sighting of the same word inside the same
  file is consecutive — so if the last item is already this file, we are looking
  at a repeat and must skip it. Drop the `elif` line and `"python"` (twice in
  doc-c) would list doc-c twice; your results would be quietly wrong.

Replace **TODO-3**:

```python
def build_index(directory, names):
    index = {}
    for name in names:
        path = os.path.join(directory, name)
        for word in words_of(path):
            if word not in index:
                index[word] = [name]
            elif index[word][-1] != name:
                index[word].append(name)
    return index
```

Replace **TODO-4**:

```python
def lookup(index, term):
    if term in index:
        return index[term]
    return []
```

That is the whole index. Twelve lines, no libraries, and from now on a query
never touches a file again.

**Checkpoint** — replace your probe lines with these and rerun:

```python
d = "workshop/data/mini_corpus"
names = list_txt_files(d)
index = build_index(d, names)
print(len(index))
print(lookup(index, "python"))
print(lookup(index, "the"))
print(lookup(index, "dough"))
```

Real output:

```
33
['doc-a.txt', 'doc-c.txt']
['doc-b.txt', 'doc-d.txt']
[]
```

Verify by hand: 10 new words in doc-a, 8 more in doc-b, 5 in doc-c, 10 in doc-d
= **33**. `"the"` shows up three times in doc-b and three in doc-d, yet each
file is listed once — the `elif` guard working. `"dough"` still returns `[]`,
which is what a dict lookup for an unknown key should do.

*What you just learned: turning a repeated question into a one-time recording,
and that a dict maps one key to a whole list of answers.*

### Stop 3 — Put a stopwatch on both (≈12 min)

Correct is not the same as fast, and you should never claim a speedup you have
not measured. Add `benchmark()` (**TODO-5**).

New calls, one line each:

- `time.perf_counter()` — Python's finest stopwatch. It returns the elapsed time
  in **seconds** as a float, and only differences between two readings mean
  anything. (`time.time()` is the wall clock: it can jump when the system
  corrects the clock, so never use it to measure a duration.)
- Multiply by `1000.0` to turn seconds into **milliseconds** — the unit this
  whole course uses.
- `sorted(times)[len(times) // 2]` — the **median**: sort the passes, take the
  middle one. Timings jitter; the median ignores one unlucky slow run.

One subtlety worth ten seconds of thought: a single dict lookup takes about
0.0001 ms — faster than any stopwatch can resolve. So we time `LOOKUP_BATCH`
(1,000) of them inside one reading and divide. You are measuring the work, not
the measuring.

Replace **TODO-5**:

```python
def benchmark(directory, names, index, term, repeats=REPEATS):
    scan_times = []
    build_times = []
    lookup_times = []
    for _ in range(repeats):
        start = time.perf_counter()
        scan_for_term(directory, names, term)
        scan_times.append((time.perf_counter() - start) * 1000.0)
        start = time.perf_counter()
        build_index(directory, names)
        build_times.append((time.perf_counter() - start) * 1000.0)
        start = time.perf_counter()
        for _ in range(LOOKUP_BATCH):
            lookup(index, term)
        lookup_times.append((time.perf_counter() - start) * 1000.0 / LOOKUP_BATCH)
    return {
        "scan_ms": sorted(scan_times)[len(scan_times) // 2],
        "build_ms": sorted(build_times)[len(build_times) // 2],
        "lookup_ms": sorted(lookup_times)[len(lookup_times) // 2],
    }
```

`_` is Python's "I do not care about this variable" name — used for both the
outer repeat counter and the inner batch counter, which is exactly the intent.

`format_bench()` is given to you in the starter; it just turns the three numbers
into the table below.

**Checkpoint** — replace your probe lines with these, and aim at the real corpus
now (204 documents instead of 4):

```python
d = "../datasets/corpus"
names = list_txt_files(d)
index = build_index(d, names)
print(format_bench(benchmark(d, names, index, "rovers")))
```

Real output from one run in the course venv:

```
--- benchmark (median of 5 timed passes) ---
linear scan : 31.404 ms per query
build index : 36.387 ms once
dict lookup : 0.098 us per query
speedup     : 319,799x per query
```

**Your numbers will differ** — this is a laptop, timings jitter, and the exact
microseconds depend on your disk and CPU. Two things must not differ: the scan is
tens of **milliseconds** while the lookup is a fraction of a **microsecond**, and
the build costs about the same as *one* scan. If your speedup is under 10,000×,
something is wrong: check that you are not rebuilding the index inside the lookup.

*What you just learned: how to time code honestly — warm cache, several passes,
median, and a batch big enough for the stopwatch.*

### Stop 4 — Report it, chart it, ship it (≈10 min)

Two jobs left: a text report you can diff (**TODO-6**) and the deliverable chart
(**TODO-7**).

The report is deterministic — no timings — so you can compare it character for
character against the Expected output below. New call, one line: `"\n".join(list)`
glues a list of strings together with one newline between each pair, which is
exactly what a report is.

Replace **TODO-6**:

```python
def format_report(directory, names, term, scanned, found, terms):
    lines = []
    lines.append("corpus: " + directory)
    lines.append("docs: " + str(len(names)))
    lines.append("term: " + term)
    lines.append("linear scan: " + str(scanned))
    lines.append("dict lookup: " + str(found))
    lines.append("same answer: " + str(scanned == found))
    lines.append("distinct terms: " + str(terms))
    return "\n".join(lines)
```

`str(...)` is needed whenever you glue a number or a list onto text with `+` —
without it Python refuses. And `scanned == found` is the line that matters most:
it compares the two strategies' answers directly.

Now the chart. New call, one line: `ax.bar(labels, values, color=[...])` draws
bars on the axes `ax`; `fig.savefig(path)` writes the picture to disk. The chart
*must* use `ax.set_yscale("log")` — the three bars differ by about six orders of
magnitude, so on a normal axis the green bar would be a flat line at zero and you
would learn nothing.

Replace **TODO-7**:

```python
def plot_benchmark(times, out_path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4.2))
    labels = ["linear scan", "build index (once)", "dict lookup"]
    values = [times["scan_ms"], times["build_ms"], times["lookup_ms"]]
    bars = ax.bar(labels, values, color=["#d62728", "#7f7f7f", "#2ca02c"])
    ax.set_yscale("log")
    ax.set_ylabel("milliseconds (log scale)")
    ax.set_title("The index wins: same query, two strategies")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value * 1.3,
                f"{value:.4f} ms", ha="center", fontsize=9, weight="bold")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path
```

(`zip(a, b)` walks two lists side by side, so each bar gets paired with its
value; `plt.close(fig)` frees the figure so the next one does not pile up.)

`main()` is given to you and calls everything in order. **Checkpoint** — run the
whole program:

```
python workshop/starter/search_index.py workshop/data/mini_corpus python --bench
```

Real output:

```
corpus: workshop/data/mini_corpus
docs: 4
term: python
linear scan: ['doc-a.txt', 'doc-c.txt']
dict lookup: ['doc-a.txt', 'doc-c.txt']
same answer: True
distinct terms: 33
--- benchmark (median of 5 timed passes) ---
linear scan : 0.394 ms per query
build index : 0.577 ms once
dict lookup : 0.226 us per query
speedup     : 1,740x per query
plot written to: workshop\benchmark.png
```

Open `workshop/benchmark.png`. That image is your deliverable. Then take the
plunge and aim at the whole corpus:

```
python workshop/starter/search_index.py ../datasets/corpus rovers --bench
```

```
corpus: ../datasets/corpus
docs: 204
term: rovers
linear scan: ['doc-002.txt', 'doc-007.txt', 'doc-016.txt', 'doc-022.txt', 'doc-037.txt', 'doc-042.txt', 'doc-088.txt', 'doc-115.txt', 'doc-118.txt', 'doc-128.txt', 'doc-132.txt', 'doc-143.txt', 'doc-147.txt', 'doc-155.txt']
dict lookup: ['doc-002.txt', 'doc-007.txt', 'doc-016.txt', 'doc-022.txt', 'doc-037.txt', 'doc-042.txt', 'doc-088.txt', 'doc-115.txt', 'doc-118.txt', 'doc-128.txt', 'doc-132.txt', 'doc-143.txt', 'doc-147.txt', 'doc-155.txt']
same answer: True
distinct terms: 221
--- benchmark (median of 5 timed passes) ---
linear scan : 23.964 ms per query
build index : 25.223 ms once
dict lookup : 0.109 us per query
speedup     : 220,460x per query
plot written to: workshop\benchmark.png
```

Fourteen documents mention "rovers", the two strategies list the **same fourteen
in the same order**, and the whole 221-term vocabulary was built from 204 files
once. `same answer: True` is the contract: an index that disagrees with brute
force is worse than useless.

*What you just learned: reporting results so someone else can check them, and
plotting them so the point lands in one glance.*

## Expected output

The exact, reproducible output of the correct solution (pasted from a real venv
run in this folder). Only the four timing lines vary between machines — every
other line is fixed by the data.

```
python workshop/solution/search_index.py workshop/data/mini_corpus python
```

```
corpus: workshop/data/mini_corpus
docs: 4
term: python
linear scan: ['doc-a.txt', 'doc-c.txt']
dict lookup: ['doc-a.txt', 'doc-c.txt']
same answer: True
distinct terms: 33
```

```
python workshop/solution/search_index.py ../datasets/corpus rovers
```

```
corpus: ../datasets/corpus
docs: 204
term: rovers
linear scan: ['doc-002.txt', 'doc-007.txt', 'doc-016.txt', 'doc-022.txt', 'doc-037.txt', 'doc-042.txt', 'doc-088.txt', 'doc-115.txt', 'doc-118.txt', 'doc-128.txt', 'doc-132.txt', 'doc-143.txt', 'doc-147.txt', 'doc-155.txt']
dict lookup: ['doc-002.txt', 'doc-007.txt', 'doc-016.txt', 'doc-022.txt', 'doc-037.txt', 'doc-042.txt', 'doc-088.txt', 'doc-115.txt', 'doc-118.txt', 'doc-128.txt', 'doc-132.txt', 'doc-143.txt', 'doc-147.txt', 'doc-155.txt']
same answer: True
distinct terms: 221
```

And with `--bench` (timings measured, never invented — your machine will differ):

```
--- benchmark (median of 5 timed passes) ---
linear scan : 23.964 ms per query
build index : 25.223 ms once
dict lookup : 0.109 us per query
speedup     : 220,460x per query
plot written to: workshop\benchmark.png
```

## Stretch goals (optional)

Beyond the core deliverable — only after Stop 4 is green.

- **Break-even calculator.** For K queries, the scan costs `K × scan_ms` and the
  index costs `build_ms + K × lookup_ms`. Loop K from 1 to 20 and print the first
  K where the index wins, using your own measured numbers.
- **Growth curve.** Point `list_txt_files` at prefixes of the corpus (25, 50,
  100, 204 files), time the scan for each, and plot scan time against corpus
  size. You should reproduce the climbing line from the README yourself.
- **Two-word queries.** Given `"mars water"`, return the files containing *both*
  words: two lookups, then keep the filenames present in both lists. This is
  postings intersection, and Session 6 does it properly — but you can taste it
  today.
- **Save the index.** Write the dict to a file with `open(path, "w", ...)` and
  read it back with `open(path, "r", ...)` so a second run does not rebuild it.
  Real engines do exactly this, and you will notice what Session 2's file-format
  choices are for.

## Solution

`workshop/solution/` — attempt the journey first. It holds the complete
`search_index.py` plus a test suite with hand-checked expected values. Sanity
check (must pass):

```
python -m pytest workshop/solution/ -v
```

Expected: `11 passed`. The suite asserts the things that are easy to get wrong:
the 33 hand-counted distinct words, `"the"` listed once per file despite
appearing three times, `lookup` returning `[]` for an unknown word, the benchmark
beating brute force by more than 100×, and — most importantly — that the scan
and the index return **identical** result lists for six terms across the real
204-document corpus.

## Where this leads

You built a working search index out of a dict, and measured why it wins. Session
4 draws the full IR architecture and shows where this index sits inside a real
pipeline. Session 5 takes your dict the two extra hops shown in the README —
filenames become document ids, lists of names become lists of `(id, tf)` pairs —
and that *is* an inverted index, the structure behind every lexical search
engine in production today. Everything after that session (BM25, evaluation,
hybrid search) assumes this dict already exists. It does not yet — until you
write it.
