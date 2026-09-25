# Session 01 — Course Intro & Python Text File I/O
> Every search engine starts here: reading text files. By the end you can stats-check any corpus file.

## What you'll learn
- Where file I/O sits in the full IR pipeline (and where the other 24 sessions plug in)
- Opening, reading, writing, and closing text files — and why closing matters
- The `with` block pattern that closes files for you, even on errors
- Text vs bytes: what UTF-8 encode/decode actually does
- Line-by-line reading and word counting on the real course corpus

## Concepts

### 01.1 Where you are: the IR pipeline
![The IR pipeline from crawl to evaluate, one box per session](images/01-01-roadmap-pipeline.png)
A search engine is an assembly line: **crawl** pages, **parse** text, build an **index**,
answer a **query**, **rank** results, then **evaluate**. Each box above is a session in
this course. Analogy: a restaurant kitchen — ingredients in, chopped, cooked, plated,
tasted. Key terms: **pipeline**, **corpus**, **query**, **rank**.

### 01.2 A file has a life: open → use → flush → close
![File object lifecycle: open, read/write, flush, close](images/01-02-file-lifecycle.png)
`open()` hands you a **file object** (a handle, not the data itself). You read/write
through it, `flush()` pushes buffered data out, and `close()` releases the handle.
Analogy: checking out a library book — borrow it, read it, return it so others can
use it. Key terms: **file object**, **handle**, **buffer**, **flush**.

First sample — `open()` takes a path and returns a file object you read through:

```python
f = open("notes.txt", mode="r", encoding="utf-8")
text = f.read()   # now the data actually moves, decoded to str
f.close()
```

Popular parameter values you will use in this course:

- `mode="r"` — read (the default). File must exist or you get `FileNotFoundError`.
- `mode="w"` — write. Creates the file, or **empties it first** if it exists — careful!
- `mode="a"` — append. Keeps existing content, new writes go at the end.
- `encoding="utf-8"` — pass this **every time** so text decodes identically on all machines.

What actually happens when `open()` runs: Python asks the operating system to open
the file; the OS returns a low-level handle (a number called a file descriptor);
Python wraps it in a buffered file object. Almost **no disk data moves yet** —
reading/writing happens later through the object (one exception: `mode="w"`
truncates the file immediately). `read()` then pulls bytes through the buffer and
decodes them to `str` using your `encoding`.

![Layers built by open(): your code, file object, OS handle, disk](images/01-06-open-under-hood.png)

### 01.3 `with` blocks close the file for you
![Manual open/close versus the safe with-block pattern](images/01-04-context-manager.png)
If your program crashes between `open()` and `close()`, the handle leaks. A
**context manager** (`with open(...) as f:`) guarantees `close()` runs even on error.
Analogy: a self-returning library book — it flies back to the shelf no matter what.
Key terms: **context manager**, **`with` block**, **leak**.

```python
# always write it in this order: with -> open -> as f
with open("notes.txt", encoding="utf-8") as f:
    text = f.read()
# file is already closed here, even if read() had crashed
```

### 01.4 Text vs bytes: UTF-8 encode/decode
![Encoding str to bytes and decoding bytes back to str with UTF-8](images/01-03-encode-decode.png)
Python strings (`str`) are human text; disks and networks store **bytes**. `.encode()`
translates text → bytes, `.decode()` translates back — and both need the same
**encoding** (we always use UTF-8, which covers every language). Wrong encoding =
garbled **mojibake**. Analogy: Morse code — same message, different medium, one
shared codebook. Key terms: **bytes**, **encoding**, **UTF-8**, **mojibake**.

```python
s = "café"
b = s.encode("utf-8")   # str -> bytes for disk/network
s2 = b.decode("utf-8")  # bytes -> str for humans
assert s == s2
```

### 01.5 Reading line by line to find and count
![Top-8 word counts measured from a real corpus document](images/01-05-wordcount-doc001.png)
Big files don't fit in memory comfortably, so we iterate **line by line** (`for line
in f:` reads one line at a time). Inside the loop we do two jobs: **count** things
(lines, words, characters) and **find** things (`if word in line:` keeps matching
lines — the seed of every search engine). Tallies live in a plain **dict**
(`counts[word] = counts[word] + 1`); the chart above shows real numbers from
`datasets/corpus/doc-001.txt`, not invented. Analogy: counting marbles by pouring
them through a funnel instead of dumping the whole jar — and setting aside the
red ones as they pass. Key terms: **iteration**, **token**, **tally**, **match**.

## Worked example
Open a file, walk through it line by line, count and find (run from this folder).
One new idea: `counts.get(word, 0)` means "the tally so far, or 0 if unseen" —
a dict lookup with a safety net.

```python
counts = {}
f = open("workshop/data/sample.txt", mode="r", encoding="utf-8")
for line in f:
    for raw in line.lower().split():
        word = raw.strip(".,!?")
        counts[word] = counts.get(word, 0) + 1
f.close()
top = sorted(counts, key=counts.get, reverse=True)[0]
print("words:", sum(counts.values()))
print("top word:", (top, counts[top]))
rank_lines = 0
f2 = open("workshop/data/sample.txt", mode="r", encoding="utf-8")
for line in f2:
    if "quality" in line:
        rank_lines = rank_lines + 1
f2.close()
print("lines with 'quality':", rank_lines)
```

Actual output (pasted from a real venv run):

```
words: 12
top word: ('search', 2)
lines with 'quality': 1
```

## Environment (venv)
Set up the course venv once (see **Environment setup** in the main `README.md`),
then activate it every study session. With it active, all commands are plain
`python ...`. Session 1 needs only `matplotlib` + `numpy`; later sessions need
the full `requirements.txt`.

## How this connects to the workshop
Reading time is over — now you drive. The workshop is a guided journey in three
stops: teach the program to count (Stop 1), find the words that matter (Stop 2),
then aim your finished `text_stats.py` at the real `datasets/corpus/` (204 docs).
Session 3 will search those same files — so learn to read them well now.

## Common pitfalls
- Forgetting `encoding="utf-8"` in `open()` — works on your machine, breaks on another.
- Forgetting `close()` (or skipping `with`) — leaked handles, locked files on Windows.
- `read()` on a huge file — loads everything into RAM; prefer `for line in f:`.
- Counting `"Text."` and `"text"` as different words — lowercase and strip punctuation first.
- Running with the wrong python (system instead of `.venv`) — matplotlib "missing" even though installed.

## Self-check quiz
1. Which pipeline stage turns raw pages into clean text?
2. What goes wrong if an exception fires between `open()` and `close()`?
3. Why is `with open(...) as f:` safer than manual `open()`/`close()`?
4. What does `"café".encode("utf-8")` return — `str` or `bytes`?
5. Why iterate `for line in f:` instead of `f.read()` on a 10 GB file?

<details>
<summary>Answers</summary>

1. Parse (Session 18 reuses this skill on the mock shop).
2. `close()` never runs — the handle leaks (on Windows the file can stay locked).
3. The context manager guarantees `close()`, even when the block raises.
4. `bytes` — encode goes str → bytes; decode goes back.
5. Line iteration uses O(1) memory; `read()` loads all 10 GB into RAM.
</details>

## Next
[→ Start the workshop](workshop/WORKSHOP.md)
