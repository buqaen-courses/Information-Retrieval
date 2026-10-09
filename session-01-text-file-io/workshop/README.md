# Workshop 01 — Your First IR Tool: Text File Stats (≈45 min)

Every search engine you will ever build starts with the same humble act: opening
a text file and asking "what's inside?" Google does it a billion times a day —
today you do it by hand, with nothing but `open()`, a `for` loop, and a `dict`,
and end up with a tool that can interrogate any file in our 204-document course
corpus.

**What you will walk away with:** a working `text_stats.py` that reports
lines, words, characters, and top-N words for any `.txt` file, plus a
find-a-word search — the seed of every engine you will build next.

You know basic Python (variables, loops, functions). Everything else is explained
below, with the exact file lines and code shapes inline. No hunting through other
files needed.

## Setup (≈5 min)
Activate the course venv first (one-time setup in the main `README.md`), then run
every command from this folder (`session-01-text-file-io/`) as plain `python`:

```
cd session-01-text-file-io
python workshop/starter/text_stats.py workshop/data/sample.txt
```

You should see `TODO-6 not done yet` — the starter runs, hints print, nothing
crashes. That friendly failure is by design: you will silence each TODO, one
stop at a time.

## Meet your patient
`workshop/data/sample.txt` — plain text, 3 lines, nothing hidden:

```
Search engines index text.
Search engines rank text.
Evaluation measures ranking quality.
```

Keep these lines in mind: every number you produce in the next 40 minutes can be
checked against them by hand.

## The journey

### Stop 1 — Open the file and count everything (≈15 min)
Right now `count_stats()` can't even open a file. Let's fix that — it is the
single most reused skill in this course.

New call, one line: `open(path, mode="r", encoding="utf-8")`. `mode="r"` means
read; `encoding="utf-8"` decodes text the same on every machine. It hands back a
file object you walk through with `for line in f:` — one line at a time, so even
giant files fit in memory.

Open `workshop/starter/text_stats.py` and replace **TODO-1, TODO-2**:

```python
f = open(path, mode="r", encoding="utf-8")   # TODO-1
lines = 0                                    # TODO-2: three counters ...
words = 0
chars = 0
for line in f:                               # ... fed by one loop
    lines = lines + 1
    words = words + len(line.split())        # .split() cuts a line into words
    chars = chars + len(line)                # len(line) counts the newline too
f.close()
return {"lines": lines, "words": words, "chars": chars}
```

Checkpoint — run the starter again:

```
python workshop/starter/text_stats.py workshop/data/sample.txt
```

You now get a complaint about TODO-3 instead of TODO-1. Progress you can see.
(Empty-file path: typing the snippet above into an empty `my_stats.py` plus a
`print(...)` shows `{'lines': 3, 'words': 12, 'chars': 90}` — check it by hand:
3 lines, 4 + 4 + 4 words, yes.)

*What you just learned: opening a file, walking it line by line, and counting
with plain variables.*

### Stop 2 — Tally words and crown a winner (≈15 min)
Counting is nice; ranking is search. Now `top_words()` learns which words dominate
a file — the same instinct behind TF-IDF in Session 7. Same 3 sample lines as input.

New idea, one line: a `dict` tally. `counts[word] = counts.get(word, 0) + 1`
means "add one to the tally, starting from 0 if unseen" — a lookup with a safety net.

Replace **TODO-3, TODO-4**:

```python
counts = {}                                  # TODO-3: the tally
f = open(path, mode="r", encoding="utf-8")
for line in f:
    for raw in line.lower().split():         # lowercase FIRST ...
        word = raw.strip(".,!?;:\"'()")      # ... then peel punctuation
        if word == "":
            continue
        if word in counts:
            counts[word] = counts[word] + 1
        else:
            counts[word] = 1
f.close()
ordered = sorted(counts, key=counts.get, reverse=True)  # TODO-4: best first
result = []
for word in ordered[:n]:                     # keep the first n
    result.append((word, counts[word]))
return result
```

(`.strip(".,!?;:\"'()")` peels those characters off both ends of a word, so
`"text."` becomes `"text"`. `sorted()` with `key=counts.get` orders words by
their tally, biggest first. No `Counter`, no shortcuts — just loops and a dict.)

Checkpoint — the starter now reaches TODO-5. (Empty-file path: your growing file
now prints the stats dict plus
`[('search', 2), ('engines', 2), ('text', 2), ('index', 1), ('rank', 1)]`.)

*What you just learned: normalizing text (lowercase → strip → split) before
counting, and ordering a dict best-first with `sorted()`.*

### Stop 3 — Find words, wire it up, aim at the real corpus (≈10 min)
A function nobody calls is a diary entry. Two jobs left: a find-a-word search
(**TODO-5**) and the `main()` that prints the report (**TODO-6**).

The find snippet — the `if ... in ...` test is the seed of every search engine:

```python
hits = []
f = open(path, mode="r", encoding="utf-8")
for line in f:
    if word in line:              # keep what matches, skip the rest
        hits.append(line.strip())
f.close()
return hits
```

Real output on the sample file (pasted from a venv run):

```
['Evaluation measures ranking quality.']
```

Then the wiring. New call, one line: `sys.argv` — the list of words typed after
`python`, so `sys.argv[1]` is the filename and `sys.argv[2]` (if given) is N:

```python
path = args[0]
if len(args) > 1:
    n = int(args[1])
else:
    n = 10
stats = count_stats(path)
print("file: " + str(path))
print("lines: " + str(stats["lines"]))
print("words: " + str(stats["words"]))
print("chars: " + str(stats["chars"]))
print("top-" + str(n) + " words:")
for pair in top_words(path, n):
    print("  " + pair[0] + ": " + str(pair[1]))
```

Now the payoff — first the sample you know by heart, then a real corpus document:

```
python workshop/starter/text_stats.py workshop/data/sample.txt 5
python workshop/starter/text_stats.py ../datasets/corpus/doc-001.txt 5
```

Your output should match **Expected output** below, character for character. If it
does, verify by hand against the 3 sample lines — 3 lines, 12 words, and
"search" winning at 2. Hand-verified code is trusted code.

*What you just learned: keeping matching lines with `if word in line`, and turning
functions into a command-line tool with `sys.argv`.*

## Expected output
Exact output of the correct solution (pasted from a real venv run, from this folder):

```
file: workshop/data/sample.txt
lines: 3
words: 12
chars: 90
top-5 words:
  search: 2
  engines: 2
  text: 2
  index: 1
  rank: 1
```

And on a real corpus document:

```
file: ../datasets/corpus/doc-001.txt
lines: 3
words: 40
chars: 271
top-5 words:
  the: 5
  with: 4
  director: 3
  framed: 3
  every: 3
```

## Stretch goals (optional)
- Handle multiple encodings gracefully: try UTF-8, fall back to `errors="replace"`, and report which files needed the fallback across all of `../../datasets/corpus/`.
- Total-corpus stats: open all 204 corpus files one by one (same loop!) and print the single most common word overall.

## Solution
`workshop/solution/` — attempt the journey first. Sanity check (must pass):

```
python -m pytest workshop/solution/ -v
```

Expected: `3 passed`.

## Where this leads
You built the flashlight every later session uses to inspect text: Session 3 aims
this same open-and-iterate skill at searching files, Session 5 tokenizes them into
an inverted index, and Session 18 parses web pages with it. Files in, matches
out — that is the first half of every pipeline you will ever build.
