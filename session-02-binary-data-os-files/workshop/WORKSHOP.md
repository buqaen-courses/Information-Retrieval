# Workshop 02 — Format Lab: Four Formats, One Dataset (≈45 min)

Session 1 taught you to *read* a text file. Today you decide how to *store*
one — and you find out that the fastest format is not the smallest one. That
surprise is the whole lesson: every format trades something away, and the job of
a working engineer is knowing which trade you can afford. A crawler writing
12 000 product records has to choose; so does a vector database writing an
embedding matrix in Session 12; so will you, in about forty minutes.

**What you will walk away with:** a `format_lab.py` that writes the same 12
records as CSV, JSON, NDJSON and pickle, proves all four load back identically,
times each load, prints a **results table**, and writes a log a `tail -f` can
follow live — plus a 6-TODO tests file that pins every number down.

You know basic Python (variables, loops, functions) and Session 1's
`open()` / `for` loops. Everything new is explained inline below, with the
sample-file lines and the code shape you need. No hunting required.

## Setup (≈3 min)
Activate the course venv first (one-time setup in the main `README.md`), then run
everything from this folder (`session-02-binary-data-os-files/`) as plain
`python`:

```
cd session-02-binary-data-os-files
python workshop/starter/format_lab.py
```

You should see:

```
TODO-1 not done yet - read the CSV with csv.DictReader
(6 TODOs total - open starter/format_lab.py and work top to bottom.)
```

Nothing crashed, nothing was deleted — that friendly failure is by design. You
will silence one TODO at a time.

## Meet your patient
`workshop/data/records.csv` — 12 rows, and two details that matter:

```
id,name,price,category,description
p-001,Desk Lamp,19.99,lighting,"Warm LED desk lamp, brushed steel, 3-year warranty"
...
p-012,"Cable, 3-pack",11.00,electronics,"Three braided cables, 1m each, mixed lengths, spare"
```

Row 12 holds a **comma inside the name**, inside quotes. That single character
is why we use the `csv` module instead of `line.split(",")` — split would give
you 6 fields instead of 5. Every number below is checkable against this file by
hand.

All output goes to `workshop/out/` (the starter creates it with
`os.makedirs(OUT_DIR, exist_ok=True)` — `exist_ok=True` means "don't complain if
it's already there").

## The journey

### Stop 1 — Read the CSV without breaking on commas (≈12 min)
Nothing works yet: `load_csv()` raises before it opens anything. This is the
skill the whole session rests on.

New calls, one line each. `csv.DictReader(f)` — walks a CSV file object and
hands you one `dict` per row, using the header line as the keys, so instead of
`row[0]` you write `row["price"]`. `newline=""` in `open()` — tells Python "do
not translate line endings"; the csv docs ask for it, and it keeps your byte
counts identical on Windows and Linux.

Open `workshop/starter/format_lab.py` and replace **TODO-1**:

```python
rows = []                                  # our growing list of rows
f = open(path, mode="r", encoding="utf-8", newline="")
reader = csv.DictReader(f)                 # one dict per row, keyed by header
for row in reader:                         # iterate rows, not lines
    rows.append(row)                       # keep it
f.close()                                  # let go of the handle
return rows                                # hand the list back
```

Checkpoint — run the starter again:

```
python workshop/starter/format_lab.py
```

```
TODO-2 not done yet - write the CSV with csv.DictWriter
(6 TODOs total - open starter/format_lab.py and work top to bottom.)
```

Progress you can see. (Empty-file path: type the snippet above into an empty
`my_lab.py`, add the four `print` lines from `main()` at the bottom, and you see
exactly this — 12 rows, `Cable, 3-pack` intact, `price` typed `str`.)

*What you just learned: `csv.DictReader` turns a header plus lines into dicts,
and quoting is what makes commas inside values safe.*

### Stop 2 — Write the same rows three text ways (≈12 min)
Reading is half the job. Now you write: CSV back out, pretty JSON, and NDJSON.

New calls, one line each. `csv.DictWriter(f, fieldnames=FIELDS)` — a writer
object; `fieldnames=` is the **column order**, so that list is your schema.
`writer.writeheader()` writes the `id,name,...` line. `json.dump(obj, f, indent=2)`
— writes a Python object to a file *you* opened. Popular `indent` values: `2`
(readable, what we use), `4` (roomier), `None` (one long line, smallest file).
`json.dumps(obj)` — same thing but returns a **string** instead of writing a file.

Replace **TODO-2** (CSV) and **TODO-3** (JSON):

```python
f = open(path, mode="w", encoding="utf-8", newline="")
writer = csv.DictWriter(f, fieldnames=FIELDS)   # column order lives here
writer.writeheader()                            # the "id,name,..." line
for row in rows:
    writer.writerow(row)                        # quotes any value with a comma
f.close()
return os.path.getsize(path)                    # bytes on disk, no reading
```

```python
f = open(path, mode="w", encoding="utf-8", newline="")
json.dump(rows, f, indent=2)                     # pretty JSON
f.write("\n")                                   # one trailing newline
f.close()
return os.path.getsize(path)
```

Then **TODO-4** (NDJSON) — same data, one object per line:

```python
f = open(path, mode="w", encoding="utf-8", newline="")
for row in rows:
    f.write(json.dumps(row) + "\n")             # json.dumps -> a string
f.close()
return os.path.getsize(path)
```

Checkpoint — the starter now reaches TODO-5. (Empty-file path: add the three
functions and a loop, and you get the byte counts below. Hand-check CSV: the
header is 40 bytes and the 12 rows carry `"` around anything with a comma.)

```
csv     1050
json    2101
ndjson  1774
```

Two numbers worth staring at: JSON is **2.00x** the size of CSV. Pretty-printing
plus repeating every key 12 times costs you more than everything else combined.

*What you just learned: CSV repeats nothing, JSON repeats keys and indents, NDJSON repeats keys but skips the wrapper — and `os.path.getsize` measures any file without reading it.*

### Stop 3 — Add the binary format (≈10 min)
Now the odd one out. Pickle stores Python objects directly, so there is no
quoting rule, no schema line, and no parsing on the way back in.

New call, one line: `open(path, mode="wb")` — **binary** mode; the `b` is
required because `pickle` writes `bytes`, and text mode only accepts `str`.
Popular values: `"rb"` read binary, `"wb"` write binary, `"ab"` append binary.
`protocol=pickle.HIGHEST_PROTOCOL` — pick the newest, fastest encoding your
Python has; it is 5 on modern Pythons and there is no reason to use anything else.

Replace **TODO-5**:

```python
f = open(path, mode="wb")                      # "b" = binary, pickle requires it
pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)   # returns nothing
f.close()
return os.path.getsize(path)
```

Checkpoint — the round trip now runs for all four formats:

```
csv     1050
json    2101
ndjson  1774
pickle  1321
```

```
--- round trip: load each file back ---
csv     12 rows | first id p-001 | price type str
json    12 rows | first id p-001 | price type str
ndjson  12 rows | first id p-001 | price type str
pickle  12 rows | first id p-001 | price type str
```

All four give back 12 rows with `p-001` first and `Cable, 3-pack` intact. Note
the honest wrinkle: `price` is a `str` in *all four*, because the rows came from
a CSV to begin with — pickle faithfully preserved text. Give `save_pickle` a
dict with a real `float` in it (see Stretch) and pickle is the only one that
returns a `float`.

*What you just learned: pickle is smaller than pretty JSON and needs no schema,
but it only preserves the types you actually handed it.*

### Stop 4 — Time it, then flush a log (≈8 min)
Sizes are one half of the comparison; time is the other, and the answer is not
the one you expect.

The timing loop is **given to you** in `measure()` — read it, don't rewrite it:

```python
load_any(path, fmt)                            # warm-up: page the bytes in
total = 0.0
for _ in range(repeats):                       # repeats = 200 by default
    start = time.perf_counter()                # a monotonic clock, in seconds
    load_any(path, fmt)
    total = total + (time.perf_counter() - start)
return total * 1000.0 / repeats                 # -> average milliseconds
```

That first throwaway call is not decoration: the first load pays for filling the
OS page cache, so leaving it in would make whichever format ran *first* look
slowest for no reason. Run it:

```
python workshop/solution/format_lab.py 200 1
```

```
--- average load time over 200 runs (ms) ---
csv     0.1523
json    0.1336
ndjson  0.1393
pickle  0.0991
```

Pickle loads fastest and CSV slowest, while CSV is the *smallest* file. Your
numbers will be close but not identical — that is real timing on real hardware,
and the ordering is the claim, not the third decimal.

Now the last TODO, and the reason `flush()` exists. `tail -f app.log` on your
terminal can only show lines that have already left Python's buffer, so a
logging loop must push them out as it writes.

New call, one line: `f.flush()` — pushes the buffer into the OS right now.
`close()` also flushes, but only *after* your loop ends, which defeats the point
of a live log.

Replace **TODO-6**:

```python
stamp = "2026-05-04 12:00:00"
f = open(path, mode="a", encoding="utf-8", newline="")   # "a" = append
written = 0
for i in range(count):
    second = int(stamp[-2:]) + 1         # read the seconds field as a number
    stamp = stamp[:-2] + ("%02d" % second)   # zero-padded, back on the string
    f.write(stamp + " INFO  " + message + " #" + str(i + 1) + "\n")
    written = written + 1
    if tail_every > 0 and written % tail_every == 0:
        f.flush()                        # tailer can see this line NOW
f.close()                                # always flushes whatever is left
return written
```

The same timestamp-bumping trick is what Session 23's `tail_log()` needs.

Checkpoint — run the finished starter:

```
python workshop/starter/format_lab.py 200 1
```

```
--- log tailing with flush() (flush every 1 lines) ---
lines written: 3
  2026-05-04 12:00:00 INFO  server started
  2026-05-04 12:00:01 INFO  crawler indexed document #1
  2026-05-04 12:00:02 INFO  crawler indexed document #2
  2026-05-04 12:00:03 INFO  crawler indexed document #3

smallest file: csv (1050 bytes)
fastest load:  pickle (0.0991 ms)
csv/json size ratio: 2.00
```

Timestamps advanced by exactly one second per line: `00`, `01`, `02`, `03`. If
you see a repeated timestamp, your `stamp = stamp[:-2] + ...` line is missing.

*What you just learned: how to time a file load fairly (warm-up first, average
many runs) and how `flush()` makes a log readable while the program is still
running.*

## Expected output
Exact output of the correct solution, pasted from a real venv run of
`python workshop/solution/format_lab.py 200 1` from this folder. Everything
above this line is byte-identical on every machine; the four `load_ms` values
and the "fastest load" line are real timings and will differ slightly.

```
rows loaded: 12
first row: p-001 | Desk Lamp | 19.99
name holding a comma: Cable, 3-pack
price came back as type: str -> you must convert it yourself

--- writing the same 12 rows in four formats ---
format   bytes
csv     1050
json    2101
ndjson  1774
pickle  1321

--- round trip: load each file back ---
csv     12 rows | first id p-001 | price type str
json    12 rows | first id p-001 | price type str
ndjson  12 rows | first id p-001 | price type str
pickle  12 rows | first id p-001 | price type str

--- average load time over 200 runs (ms) ---
format   load_ms
csv     0.1523
json    0.1336
ndjson  0.1393
pickle  0.0991

--- log tailing with flush() (flush every 1 lines) ---
lines written: 3
  2026-05-04 12:00:00 INFO  server started
  2026-05-04 12:00:01 INFO  crawler indexed document #1
  2026-05-04 12:00:02 INFO  crawler indexed document #2
  2026-05-04 12:00:03 INFO  crawler indexed document #3

smallest file: csv (1050 bytes)
fastest load:  pickle (0.0991 ms)
csv/json size ratio: 2.00
```

To verify your bytes independently of the script:

```
python -c "import os; print([os.path.getsize('workshop/out/records.'+e) for e in ['csv','json','ndjson','pkl']])"
```

```
[1050, 2101, 1774, 1321]
```

## Stretch goals (optional)
Clearly beyond the core deliverable — try only after your table matches Expected
output.

- **Types survive (the point of pickle).** Save `{"price": 19.99, "tags":
  ["new"]}` as all four formats, load each back, and print `type(...)` of
  `price`. CSV and JSON-with-indent give you back text / a real float
  respectively; only pickle returns `tags` as a list *and* the float. Then
  explain the size increase.
- **`struct` by hand.** `struct.pack("!i f 8s", 7, 19.99, b"p-001")` is exactly
  16 bytes. Write a `save_struct`/`load_struct` pair with a
  `FORMAT = "!i f 8s"` constant and time it against pickle. (You will need to
  convert `"19.99"` to `float` yourself — CSV handed you a string.)
- **Robust encodings.** Load all 204 files in `../../datasets/corpus/` as
  records, then re-save them: `encoding="utf-8"` everywhere, and add a fallback
  for any file that raises `UnicodeDecodeError` so one bad byte cannot kill the
  run.
- **A real tail.** Run `python workshop/starter/format_lab.py 200 1` in one
  terminal and, while it runs, `Get-Content workshop/out/app.log -Wait`
  (PowerShell) in a second. Watching the lines appear is the whole point of
  Stop 4.

## Solution
`workshop/solution/` — attempt the journey first, then compare. Sanity check
(this must pass):

```
python -m pytest workshop/solution/ -v
```

Expected: **9 passed**. The tests pin the four byte counts (1050 / 2101 / 1774 /
1321), the 12-row count, the comma-in-name round trip, the CSV header order, the
`str` type of `price`, pickle keeping a real `float` and a real `list`, and the
exact log lines from Stop 4 — including the `flush_every=2` case where 4 lines
are written but only 2 flushes happen.

## Where this leads
You now have a format-comparison script with a results table, and a feel for
which trade you can afford. **Session 3** loads the 204-document corpus with the
same `open()`-and-iterate skill and measures linear scan against dict lookup —
the first real reason an index beats re-reading files. **Session 7** picks
`np.save` for a TF-IDF matrix; **Session 11** measures compression ratios the
same way you measured formats here; **Session 19** writes crawled products as
NDJSON so a crash costs you one line instead of the whole crawl. And the log you
tailed in Stop 4 is the pattern Session 23's pipeline logging is built from.