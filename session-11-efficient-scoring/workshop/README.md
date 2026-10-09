# Workshop 11 — Make the Engine Do Less Work (≈45 min)

Your engine answers every query by looking at every posting. On a 204-document
corpus that is fine. On the 12 million documents a real index holds, it is the
difference between a search box people use and one they abandon. The fix is
never "buy faster hardware" — it is **stop touching data you already know you
do not need**.

**What you will walk away with:** a `fast_score.py` that compresses the index
4×, intersects postings using skip pointers, and proves the answers are
unchanged. Plus one result that will surprise you: the optimization examines
six times fewer documents and still loses on the clock.

## Setup (≈5 min)
From this folder, with the course venv active (one-time setup in the main
`README.md`):

```
cd session-11-efficient-scoring
python workshop/starter/fast_score.py ../../datasets/corpus
```

You should see `TODO-1 not done yet` plus a note about 6 TODOs. The hint names
the earliest unfinished task, so you always know what to do next.

## Meet your patient
A postings list from the real course index. The term `python` appears in 34 of
204 documents:

```
[8, 10, 12, 17, 18, 38, 41, 43, 47, 51, 52, 57, ...]
```

Write the deltas down by hand before you start, because that is the whole first
stop: `8, 2, 2, 5, 1, 20, ...`. Every number after the first is the gap to the
previous one. Notice almost all of them are single digits, where the originals
are not.

## The journey

### Stop 1 — Delta encode, and undo it (≈8 min)
Sorted postings have small gaps. This is the one idea the whole compression
rests on.

Open `workshop/starter/fast_score.py` and replace **TODO-1**:

```python
if not values:
    return []
out = [values[0]]
for i in range(1, len(values)):
    out.append(values[i] - values[i - 1])
return out
```

The first value stays whole because it has nothing to sit next to.

Checkpoint — run the starter:

```
python workshop/starter/fast_score.py ../../datasets/corpus
```

You now get `TODO-2`. (Empty-file path:
`delta_encode([8, 10, 12, 17, 18, 38])` returns `[8, 2, 2, 5, 1, 20]`. Check
it by hand: 10−8=2, 12−10=2, 17−12=5, 18−17=1, 38−18=20.)

*What you just learned: a sorted list of ids carries its real information in
the gaps, and the gaps are small.*

Now **TODO-2** — the undo function:

```python
if not gaps:
    return []
out = [gaps[0]]
for i in range(1, len(gaps)):
    out.append(out[-1] + gaps[i])
return out
```

`out[-1]` is the value you just rebuilt, so you never touch the input. The
checker at the end of this session proves this really is the inverse.

### Stop 2 — Varint: small numbers cost one byte (≈10 min)
Now make those small deltas cheap to store.

New idea, one line: `value & 0x7F` takes the **low 7 bits** of a number; the
high bit `| 0x80` is a flag that says "more bytes follow".

Replace **TODO-3**:

```python
out = bytearray()
while True:
    byte = value & 0x7F
    value = value >> 7
    if value:
        out.append(byte | 0x80)
    else:
        out.append(byte)
        break
return bytes(out)
```

Checkpoint — the starter now reaches TODO-4. (Empty-file path:
`varint_encode(100)` is 1 byte because 100 fits in 7 bits; `varint_encode(128)`
is 2 bytes; `varint_encode(100000)` is 3.)

*What you just learned: a varint spends one byte on a number under 128 and only
grows for the rare large one.*

Now **TODO-4** — the decoder:

```python
out = []
shift = 0
result = 0
for byte in data:
    result = result | ((byte & 0x7F) << shift)
    if byte & 0x80:
        shift = shift + 7
    else:
        out.append(result)
        result = 0
        shift = 0
return out
```

The `shift` moves each new 7-bit group into its byte position. Resetting
`result` and `shift` after a finished number is what keeps two numbers from
bleeding into each other.

### Stop 3 — Compress the whole postings list (≈7 min)
Now join the two stages. Replace **TODO-5**:

```python
out = b""
for gap in delta_encode(values):
    out = out + varint_encode(gap)
return out
```

And the same stop's inverse:

```python
return delta_decode(varint_decode(data))
```

Checkpoint:

```
python workshop/starter/fast_score.py ../../datasets/corpus
```

```
documents: 204
terms: 221
sample postings: [2, 3, 7, 10, 11, 13, 14, 17, 18, 19, 22, 25, 27, 28, 29, 31, 32, 33, 34, 37]
packed bytes: 20
restored ok: True
```

That sample is the postings list of the alphabetically first term in the index,
`a`. Twenty document ids that would cost 80 bytes as raw `int32` now fit in 20
packed bytes.

`restored ok: True` is the important line. Compression that loses a single
document id is worse than no compression.

Now the whole index, which is what the workshop chart plots:

```
python workshop/solution/fast_score.py ../../datasets/corpus --compress
```

```
documents: 204
terms: 221
postings as int32 : 19,044 bytes
delta + varint    : 4,761 bytes
compression       : 4.00x smaller
```

*What you just learned: the 4× figure comes from the gaps being small, and the
only way to trust it is a round trip that returns the exact original list.*

### Stop 4 — Skip pointers, and the bug that eats documents (≈10 min)
Now the part that goes wrong if you are careless. The starter already contains
`build_skip_list` as a TODO, and `seek`/`intersect_with_skips` are given.

Replace **TODO-6**:

```python
skips = []
for start in range(0, len(values), interval):
    end = min(start + interval, len(values))
    skips.append((start, values[end - 1]))
return skips
```

Read that second value carefully: `values[end - 1]`, the **maximum** id in the
block. If you write `values[start]` instead, the code still runs, the tests
still mostly pass, and the engine silently stops finding documents it should.
The starter's hint says it, the README says it, and the test suite catches it
across 48,841 term pairs.

Then prove the optimization is safe. The solution script has a check for
exactly this:

```python
assert sorted(intersect_plain(a, b)) == sorted(intersect_with_skips(a, b))
```

*What you just learned: a skip pointer is only allowed to skip a block when
nothing in that block can match, and the block maximum is what proves it.*

### Stop 5 — The benchmark that disagrees with itself (≈10 min)
Now measure. Run both strategies on a common term pair:

```
python workshop/solution/fast_score.py ../../datasets/corpus --bench "topic the"
```

```
query: topic the
strategy                       seconds   comparisons    hits
plain membership test           0.149ms         14474     145
skip pointers (every 32)        0.550ms          2320     145

skip pointers examined 6.2x fewer postings
wall-clock may still favour the plain version in pure Python --
`x in list` is already a tight C loop. The comparison count is
the number that predicts a real engine's behaviour.
```

Read that output twice, because two parts of it look contradictory and neither
is a bug:

- **2,320 versus 14,474 comparisons.** Skip pointers genuinely cut the work to
  one sixth. That number travels: it is what the optimization does in C, in
  Java, in a real index.
- **0.550 ms versus 0.149 ms.** In Python, the bookkeeping costs more than the
  comparisons it saves, because `value in list` already runs at C speed and a
  145-entry list is too short to pay for the pointer bookkeeping.

The chart for this session plots both bars on purpose. A single "faster" claim
would be a lie in one direction or the other.

*What you just learned: measure the work and measure the clock, and never
assume the first implies the second.*

## Expected output
Exact output of the correct solution, from this folder:

```
$ python workshop/solution/fast_score.py ../../datasets/corpus --compress
documents: 204
terms: 221
postings as int32 : 19,044 bytes
delta + varint    : 4,761 bytes
compression       : 4.00x smaller
```

```
$ python workshop/solution/fast_score.py ../../datasets/corpus --bench "topic the"
query: topic the
strategy                       seconds   comparisons    hits
plain membership test           0.150ms         14474     145
skip pointers (every 32)        0.373ms          2320     145

skip pointers examined 6.2x fewer postings
```

The four byte counts are exact and identical everywhere. The two timings are
real hardware measurements and will differ on your machine; the comparison
counts are deterministic.

## Stretch goals (optional)
- **Break it on purpose.** Change TODO-6 to record `values[start]` instead of
  `values[end - 1]`. The code still runs. Then run the equivalence check and
  watch how many of the 48,841 term pairs go wrong. Restore it afterwards.
- **Tune the interval.** The solution takes `--interval`. Try 8, 32, 128, and
  512, and plot comparisons against interval. There is an optimum; find it and
  say why it exists.
- **Quantiles instead of a flat interval.** Skip pointers do not have to sit a
  fixed distance apart. What if you put them so each block holds roughly the
  same number of documents?

## Solution
`workshop/solution/` — attempt the journey first. The important checks:

```
python workshop/solution/fast_score.py ../../datasets/corpus --compress
python workshop/solution/fast_score.py ../../datasets/corpus --bench "topic the"
python -m pytest workshop/solution/ -v
```

The suite includes `test_skips_match_plain_on_real_index`, which checks **all
48,841 term pairs** of the real corpus. It is the slowest test in the course
and it exists because the skip-pointer bug it catches produces no error
message.

## Where this leads
Session 12 throws away the whole inverted index and replaces it with vectors.
Session 21 hands this session's problem to OpenSearch, where a compiled engine
turns the 6.2× comparison saving into real milliseconds. The lesson the
benchmark taught — measure work and measure time separately — is what makes you
able to judge any optimization claim you meet later, in this course or in a
performance review.
