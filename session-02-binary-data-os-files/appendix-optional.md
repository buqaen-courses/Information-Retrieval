# Appendix — OS Internals for Session 2 (optional depth)

Everything here is **intuition-level support material**. Nothing in the workshop
depends on it, and no quiz or test asks about it. Read it if you want to know
*why* the numbers in `images/02-01-buffer-vs-page-cache.png` and
`images/02-02-buffering-cost.png` look the way they do.

## The path of one `f.write("hello")`

1. **Your Python call.** `f.write()` is a method on a buffered file object. It
   copies the bytes into an in-process buffer (`io.BufferedWriter`, default
   8192 bytes for binary files). No system call happens.
2. **The buffer fills, or you ask.** When the buffer fills, or you call
   `flush()`, or you `close()` (which flushes), Python issues a `write(2)` system
   call with the whole buffered block.
3. **The kernel page cache.** The kernel copies your bytes into RAM, associated
   with the file's inode. Your `write()` returns as soon as this is done — this
   is why a program can "lose" data on power loss while reporting success.
4. **Write-back.** The kernel flushes dirty pages to the physical device later,
   on a timer, under memory pressure, or when someone calls `fsync()`.

On a read the mirror happens: `read(2)` first checks the page cache. A cache hit
costs microseconds; a cache miss costs a device read, which costs hundreds of
microseconds to milliseconds. **Every benchmark in this course measures warm
cache** unless it says otherwise, and every format in the comparison gets the
same warm-up (`load_any()` is called once before timing).

## Page cache and readahead

The kernel also guesses: reading a 4 KB page usually means reading the next one
too, so it **readaheads** several pages. That is why sequential scanning beats
random seeking even on an SSD. It is also why "my file was cached after I read
it once" is true.

## File descriptors, in full

`open()` asks the kernel for the lowest free descriptor. Linux caps these per
process (`ulimit -n`, often 1024 by default) and the kernel keeps an array of
open-file descriptions indexed by that number. 0/1/2 are stdin/stdout/stderr.
Because a descriptor is just an integer, `dup()` can clone it and `os.fsync()`
can act on it — `f.fileno()` is how Python lets you reach that layer.

## Buffered I/O knobs

| call | effect |
|---|---|
| `open(p, "wb", buffering=0)` | raw, unbuffered — one `write(2)` per `f.write()` |
| `open(p, "wb", buffering=8192)` | default binary buffer size |
| `open(p, "w", buffering=1)` | line-buffered text, flushes on every `\n` |
| `f.flush()` | push Python's buffer into the kernel |
| `os.fsync(f.fileno())` | ask the disk to commit (slow) |
| `os.fdatasync(f.fileno())` | like `fsync` but skips metadata — faster |

Measured on this machine (2000 × 64-byte writes): **0.614 ms** buffered vs
**8.789 ms** unbuffered, i.e. 16 vs 2000 writes reaching the OS. The gap is
almost entirely syscall entry/exit overhead — roughly 4 microseconds per
unbuffered write on this box.

## Why this matters for the rest of the course

- **Session 3–5 (indexing):** a `dict` is a hash index in RAM. Page cache is why
  loading a corpus twice is free the second time, so benchmark comparisons stay
  fair.
- **Session 11 (efficient scoring):** skip pointers exist to avoid *touching*
  pages, not just to avoid arithmetic — an uncached page read is ~1000x a cached one.
- **Session 21 (OpenSearch):** Lucene's segment files are memory-mapped and
  immutable precisely because mmap + page cache beat re-reading; the B-tree side
  of the sidebar is Lucene's `BKD` tree and the term dictionary FST.
- **Session 22 (hybrid search):** fetching BM25 hits and kNN hits in two calls is
  the same I/O lesson — batch your reads and let the buffer do its job.

## Sources to read if you want more

- Python docs: `io` module, "Buffered IO" and "Raw IO" sections.
- `man 2 write`, `man 2 fsync`, `man 5 open`.
- Brendan Gregg, *Systems Performance* — chapters on memory and on I/O.