# Session 02 — Binary Data & OS-Level Files
> Session 1 read text line by line. Today we choose a *file format*, watch where bytes wait, and learn why a dict lookup and a B-tree walk are different animals.

## What you'll learn
- What **serialization** is, why every data pipeline depends on it, and how pickle, JSON, CSV and NDJSON each answer it differently
- Text formats (CSV / JSON / NDJSON) vs binary ones (pickle) — with real measured sizes on 12 rows **and** 10 000 fake profiles
- Why CSV is the *smallest* of the four here while pickle is the *fastest*, with real measured numbers
- Two places bytes sit before they touch a disk: Python's buffer and the OS **page cache**
- What `flush()` actually does, what `fsync()` adds, and what a **file descriptor** is
- Sidebar: **hash index** (O(1) exact) vs **B-tree** (sorted, range queries) — the choice Sessions 3–5 and 21 are built on

## Concepts

### 02.1 Serialization: turning objects into bytes and back
![Measured file sizes: same 12 rows and same 10 000 profiles in four formats](images/02-03-format-sizes-12rows.png)
**Serialization** is the process of converting a live Python object (a list of
dicts, a tree, a number) into a sequence of **bytes** that can be stored in a
file or sent across a network — and **deserialization** is the reverse trip.
Every time you save a model, write a crawl checkpoint, or ship a record from
one service to another, you serialize. The format you pick decides three
things: how *small* the bytes are, how *fast* they load back, and whether
*other tools* can read them. Analogy: serialization is **packing a suitcase** —
you can fold everything flat (CSV), use the original hangers (pickle), or
write a manifest so strangers can repackage it (JSON). Key terms:
**serialization**, **deserialization**, **format**, **round trip**.

Three families you will meet in this course: **self-describing** formats
(JSON, CSV — the file carries its own schema, so any tool can read it),
**language-bound** formats (pickle — only Python understands it, but it keeps
your exact types), and **columnar** formats (Parquet, numpy `.npy` — optimised
for matrices and analytics, met again in Sessions 7 and 12).

### 02.2 Text formats: CSV, JSON, NDJSON
![Measured: 10 000 profiles — CSV 1.17 MB, pickle 1.20 MB, NDJSON 2.33 MB, JSON 2.98 MB](images/02-06-format-sizes-10k.png)
A **format** is just the agreement about which bytes mean what. Three text
formats you will meet across this course: **CSV** — one row per line, values
separated by commas, `"` around anything holding a comma; **JSON** — nested
`{ }` / `[ ]` with `"key": value` pairs; **NDJSON** — the same objects but one
per line, no wrapping array, so you can read a billion-row file without loading
it. The chart is measured on the 10 000 fake profiles you generate in the
workshop: CSV 1 170 270 B, pickle 1 200 456 B, NDJSON 2 330 282 B, JSON
2 975 033 B. CSV wins because it repeats nothing — NDJSON repeats every key on
every line, and pretty JSON adds `indent=2` newlines and spaces. Analogy: a
**table** (CSV), a **catalogue card** (JSON), and a **receipt roll** (NDJSON) —
same facts, different paper. Key terms: **CSV**, **JSON**, **NDJSON**, **serialization**.

New calls, one line each. `csv.DictReader(f)` walks a CSV and hands you one
`dict` per row, keyed by the header line. `csv.DictWriter(f, fieldnames=...)`
writes rows back out in the column order you name. `json.dump(obj, f, indent=2)`
writes an object to a file you opened. `json.dumps(obj)` gives you a *string*
instead. Popular values: `indent=2` (pretty), `indent=None` (one long line),
`ensure_ascii=False` (keep `é` as `é` instead of `é`). `newline=""`
on `open()` for csv means "don't translate line endings" — the csv docs ask for
it, and it keeps your byte counts identical on Windows and Linux.

One honest CSV caveat, visible in the chart: **CSV has no types**. `19.99` comes
back as the *string* `"19.99"`, so you convert it yourself. JSON preserves
`int` / `float` / `list`, and pickle preserves everything Python knows.

### 02.3 Binary formats: pickle, struct, np.save
![Measured median load time for 12 rows and for 128 products, per format](images/02-04-format-load-times.png)
A **binary format** stores numbers as raw bytes instead of as digits in text, so
loading it skips all the parsing. Three you will meet: **pickle** — Python's own
object serializer, the only one here that keeps your exact types *and* your
nested lists and dicts; **`struct`** — you describe the byte layout by hand
(`struct.pack("!i f 8s", 7, 19.99, b"p-001")` is exactly 16 bytes) and it is the
only way to write a fixed-width record you can seek into; **`np.save`** — numpy's
`.npy` format: a short text header, then one contiguous block of array bytes, the
right home for a TF-IDF matrix (Session 7). The chart is measured, median of
200–300 runs: on 128 real products pickle loads in **0.21 ms** versus **0.77 ms**
for CSV — about 3.7x faster — while CSV still wins on *size* (16 742 B vs
19 742 B). Analogy: a **spoken sentence** versus a **faxed page** — the fax is
compact and universal, the sentence is instant for the people already there.
Key terms: **pickle**, **`struct`**, **`np.save`**, **round trip**.

One line each, with what actually happens. `pickle.dump(rows, f)` walks your
object graph, writes type tags plus the bytes, and returns nothing — the work is
in the file. `struct.pack(fmt, *values)` returns `bytes`; `struct.unpack(fmt,
data)` returns a tuple; the format string is the layout, and `!` means
"standard sizes, no padding". `np.save(path, array)` writes a `.npy` file (add
the extension yourself or it appends one) — Session 7 uses it for the term
matrix. The catch on all three: a binary file is **tied to the code that wrote
it**. Pickle of a class instance fails if the class moved; `struct` layout fails
if you reorder the format string. Text files survive that. Never open a pickle
from a stranger — `pickle.load` can run code.

### 02.4 Where bytes wait: Python's buffer vs the page cache
![Diagram of your code, Python's 8 KB buffer, the kernel page cache, and the disk](images/02-01-buffer-vs-page-cache.png)
When you call `f.write("hello")`, the bytes do **not** go to the disk. They land
in Python's own **buffer** — a few kilobytes of RAM sitting next to your object —
and stay there until the buffer fills, you call `flush()`, or you `close()`.
Only then do they cross into the kernel's **page cache**, which is the OS's
RAM-sized shelf of recently touched disk blocks. The disk is the third stop, and
the OS reaches for it on its own schedule, with no call from you. Analogy: a
**desk** (your buffer) → a **side table** (page cache) → a **filing cabinet**
(disk); you hand papers to the side table and forget them. Key terms:
**buffer**, **page cache**, **flush**, **syscall**.

This is why reading a file a second time is instant — Session 3's benchmarks all
run against warm cache, and the numbers are honest only because every format
gets the same warm-up. New call: `os.path.getsize(path)` returns the file size
in **bytes** with no reading at all — it just asks the OS about the file's
metadata. `os.makedirs(path, exist_ok=True)` creates a directory (and does
nothing if it is already there) so your writes have somewhere to land.

### 02.5 flush(), fsync(), and the file descriptor
![Measured cost of 2000 small writes, buffered versus unbuffered](images/02-02-buffering-cost.png)
`flush()` means one specific thing: **push Python's buffer into the OS**. It
does not touch the disk. `os.fsync(f.fileno())` is the one that asks the disk to
commit, and it is expensive — that is why databases and log writers choose
carefully. You already saw the pay-off in Session 1; here is the measured version
on this machine: 2000 writes of 64 bytes took **0.614 ms** through the default
8 KB buffer (**16 writes reached the OS**) and **8.789 ms** unbuffered
(**2000 writes reached the OS**) — **14.3x** slower, and that is just the
syscall overhead, before any disk work. Analogy: `flush()` is dropping the
envelope in the *outbox*; `fsync()` is watching the courier leave the building.
Key terms: **flush**, **fsync**, **syscall**, **file descriptor**.

A **file descriptor** is the small integer the OS hands you when you open a
file — `3`, `7`, `1024`, whatever is free — and every read/write goes through
that number. `open()` gives you a Python file object wrapping a descriptor, and
`f.fileno()` reveals it (try it, it is satisfying). That is the whole story: an
open file is a number in a table, and `close()` frees the slot. Every file the
OS needs anyway — standard input, output, error — has descriptor 0, 1, 2, which
is why `sys.stdout` can always be closed and reopened.

Real use for `flush()`, which the workshop builds: **log tailing**. `tail -f app.log`
can only show lines that have already left Python's buffer, so a logging loop
must `flush()` as it writes instead of waiting for `close()`.

### 02.6 Sidebar: hash index vs B-tree
![Side-by-side diagram: hash lookup in one hop versus a sorted B-tree walk for a range query](images/02-05-hash-vs-btree.png)
Two ways to find one key in a pile of keys, and they are good at different
things. A **hash index** runs the key through a hash function, gets a bucket
number, and jumps straight there — one hop no matter how big the table is
(O(1)). A **B-tree** keeps the keys **sorted** in a shallow, disk-shaped tree;
finding a key takes a few hops (O(log n)), but because the keys are in order it
answers "everything between 50 and 80", "everything starting with `lap`", and
"give me rows in id order" almost for free. That second property is what SQL
databases and search engines are built on. Analogy: a **hash table** is a cloakroom
with numbered pegs — instant, but no order; a **B-tree** is a library's
alphabetical shelves — a few steps longer, but you can walk the range. Key terms:
**hash index**, **B-tree**, **lookup**, **range query**.

Why it matters to you today: your 12-row CSV fits in one read either way, so
format choice is about humans and file size, not speed. Sessions 3–5 build the
hash side (`term → postings`, exactly a Python `dict`). Session 21 opens the
B-tree side in OpenSearch, where numeric range queries and sorted results are
table stakes.

## Worked example
Read a CSV with the `csv` module, write it back out as JSON and as pickle, then
compare sizes. Run from this folder. 16 lines, one new idea per line: `open(...,
mode="wb")` is *binary* mode (no decoding), which `pickle` requires.

```python
import csv, json, os, pickle

rows = []
f = open("workshop/data/records.csv", mode="r", encoding="utf-8", newline="")
for row in csv.DictReader(f):
    rows.append(row)
f.close()
f = open("out_a.json", mode="w", encoding="utf-8", newline="")
json.dump(rows, f, indent=2)
f.close()
f = open("out_a.pkl", mode="wb")
pickle.dump(rows, f)
f.close()
print("rows:", len(rows))
print("first name:", rows[0]["name"], "| price type:", type(rows[0]["price"]).__name__)
print("comma survived:", rows[11]["name"])
print("json bytes:", os.path.getsize("out_a.json"))
print("pickle bytes:", os.path.getsize("out_a.pkl"))
```

Actual output (pasted from a real venv run, from this folder):

```
rows: 12
first name: Desk Lamp | price type: str
comma survived: Cable, 3-pack
json bytes: 2100
pickle bytes: 1321
```

Two things to notice: `"Cable, 3-pack"` survived intact because `csv` quotes it,
and `price type: str` — CSV handed you text, not a number.

## Environment (venv)
Activate the course venv (one-time setup lives in the main `README.md`) and run
every command as plain `python ...` from this folder. Session 2 needs only the
standard library — `csv`, `json`, `pickle`, `struct`, `os`, `time` — plus
`matplotlib` for `images/make_images.py`. No pandas, no network.

## How this connects to the workshop
The README showed you the four formats side by side; the workshop makes you pay
for the comparison. Stop 1 reads `records.csv` safely, Stops 2 and 3 write the
same 12 rows as CSV, JSON, NDJSON and pickle, Stop 4 adds 10 000 fake profiles
and compares their sizes, Stop 5 times the loads and prints the results table,
and Stop 6 uses `flush()` for real by writing a log a tailer can follow. Every
number you produce is yours to check against the chart above.

## Common pitfalls
- `open(path, mode="w")` for `pickle` — pickle needs `mode="wb"`, or you get `TypeError: a bytes-like object is required`.
- `open(path, mode="r")` for `pickle` — needs `"rb"`. Reading a pickle in text mode fails the same way.
- Forgetting `newline=""` on csv `open()` — works on Windows, changes byte counts and line endings on Linux.
- Expecting CSV to give back numbers. `19.99` is the string `"19.99"`; call `float(...)` yourself.
- Thinking `flush()` means "saved to disk". It means "handed to the OS". `os.fsync()` is the one that means disk.
- `pickle.load()` on a file from someone else — unpickling can execute code. Only unpickle files you wrote.

## Self-check quiz
1. What does "serialization" mean, and what three things does your choice of format decide?
2. On this machine's 12-row measurement, which format produced the smallest file, and which loaded fastest?
3. What does `flush()` actually do — and what does it *not* do?
4. You write `pickle.dump(rows, f)` to a file opened with `mode="w"`. What happens and why?
5. Why does a hash index answer "find doc-042" better than a B-tree, while a B-tree answers "price between 50 and 80" better?

<details>
<summary>Answers</summary>

1. Serialization converts a live Python object into bytes for storage or transport; deserialization reverses it. The format decides size, load speed, and whether other tools can read it.
2. Smallest: **CSV, 1050 bytes**. Fastest: **pickle** (median 0.14 ms on 12 rows, 0.21 ms on 128 products, versus 0.77 ms for CSV).
3. It pushes Python's buffer into the OS page cache. It does **not** force the data onto the disk — that is `os.fsync()`.
4. It fails with `TypeError: a bytes-like object is required` (not `'str'`), because pickle writes `bytes` and text mode only accepts `str`. Open with `mode="wb"`.
5. Hash jumps straight to one computed bucket (O(1)) but stores keys in no order, so a range means scanning every bucket. A B-tree keeps keys sorted, so a range is a short ordered walk that can stop early.
</details>

## Next
[→ Start the workshop](workshop/WORKSHOP.md)
