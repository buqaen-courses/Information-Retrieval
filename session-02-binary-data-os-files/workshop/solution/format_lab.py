"""Session 2 — format lab solution: the same records saved as CSV, JSON, NDJSON, pickle.

Usage (run from the session folder, course venv active):

    python workshop/solution/format_lab.py [repeats] [flush_every]

    repeats      how many times each file is loaded for the timing table (default 200)
    flush_every  1 = flush() after every log line (what `tail -f` needs),
                 0 = let close() do the flushing (default behaviour you get by accident)

Reads : workshop/data/records.csv   (12 rows; one name contains a comma)
Writes: workshop/out/records.{csv,json,ndjson,pkl} and workshop/out/app.log

Only stdlib: csv, json, pickle, os, time, sys. No pandas, no third-party code.
Every field value stays a string after a CSV round trip - that is the honest
CSV caveat Session 2 is about.
"""

from __future__ import annotations

import csv
import json
import os
import pickle
import sys
import time
from typing import Any

DATA = "workshop/data/records.csv"
OUT_DIR = "workshop/out"
FIELDS = ["id", "name", "price", "category", "description"]
FORMATS = ["csv", "json", "ndjson", "pickle"]
EXT = {"csv": "csv", "json": "json", "ndjson": "ndjson", "pickle": "pkl"}


def out_path(fmt: str) -> str:
    """Return the output path for a format name ('csv' -> workshop/out/records.csv)."""
    return OUT_DIR + "/records." + EXT[fmt]


def ensure_out() -> None:
    """Create workshop/out/ if it is missing (os.makedirs, exist_ok=True)."""
    os.makedirs(OUT_DIR, exist_ok=True)


def load_csv(path: str) -> list[dict[str, str]]:
    """Load a CSV file as a list of dicts, one dict per row."""
    rows: list[dict[str, str]] = []
    f = open(path, mode="r", encoding="utf-8", newline="")
    reader = csv.DictReader(f)   # keys every row by the header line
    for row in reader:
        rows.append(row)
    f.close()
    return rows


def save_csv(rows: list[dict[str, str]], path: str) -> int:
    """Write rows to a CSV file; returns the size in bytes."""
    f = open(path, mode="w", encoding="utf-8", newline="")
    writer = csv.DictWriter(f, fieldnames=FIELDS)   # column order comes from here
    writer.writeheader()
    for row in rows:
        writer.writerow(row)                       # quotes values holding a comma
    f.close()
    return os.path.getsize(path)                   # os.path.getsize -> bytes


def save_json(rows: list[dict[str, str]], path: str) -> int:
    """Write rows to pretty-printed JSON; returns the size in bytes."""
    f = open(path, mode="w", encoding="utf-8", newline="")
    json.dump(rows, f, indent=2)                   # indent=2 keeps it readable
    f.write("\n")
    f.close()
    return os.path.getsize(path)


def save_ndjson(rows: list[dict[str, str]], path: str) -> int:
    """Write rows as NDJSON (one compact JSON object per line); returns the size."""
    f = open(path, mode="w", encoding="utf-8", newline="")
    for row in rows:
        f.write(json.dumps(row) + "\n")            # json.dumps -> one string
    f.close()
    return os.path.getsize(path)


def save_pickle(rows: list[dict[str, str]], path: str) -> int:
    """Write rows to a pickle file; returns the size in bytes."""
    f = open(path, mode="wb")                      # "b" = binary mode, required
    pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    return os.path.getsize(path)


def load_any(path: str, fmt: str) -> list[dict[str, Any]]:
    """Load a file back given its format name: csv | json | ndjson | pickle."""
    if fmt == "csv":
        return load_csv(path)
    if fmt == "pickle":
        f = open(path, mode="rb")
        rows = pickle.load(f)                      # original Python objects
        f.close()
        return rows
    if fmt == "ndjson":
        f = open(path, mode="r", encoding="utf-8")
        rows = []
        for line in f:
            line = line.strip()
            if line != "":
                rows.append(json.loads(line))      # string -> Python object
        f.close()
        return rows
    f = open(path, mode="r", encoding="utf-8")
    rows = json.load(f)                            # whole file in one go
    f.close()
    return rows


def save_all(rows: list[dict[str, str]]) -> dict[str, int]:
    """Write every format and return {format: bytes}."""
    ensure_out()
    return {
        "csv": save_csv(rows, out_path("csv")),
        "json": save_json(rows, out_path("json")),
        "ndjson": save_ndjson(rows, out_path("ndjson")),
        "pickle": save_pickle(rows, out_path("pickle")),
    }


def measure(path: str, fmt: str, repeats: int) -> float:
    """Average load time in milliseconds over `repeats` loads."""
    load_any(path, fmt)                           # warm the OS page cache first
    total = 0.0
    for _ in range(repeats):
        start = time.perf_counter()               # monotonic clock, in seconds
        load_any(path, fmt)
        total = total + (time.perf_counter() - start)
    return total * 1000.0 / repeats


def log_event(path: str, message: str, tail_every: int, count: int = 3) -> int:
    """Append `count` log lines, calling flush() every `tail_every` writes.

    The real-world use of flush(): a log tailer (`tail -f`) can only read lines
    that already left Python's buffer, so a logging loop flushes as it goes
    instead of waiting for close().
    """
    stamp = "2026-05-04 12:00:00"
    f = open(path, mode="a", encoding="utf-8", newline="")   # "a" = append
    written = 0
    for i in range(count):
        second = int(stamp[-2:]) + 1
        stamp = stamp[:-2] + ("%02d" % second)              # bump the seconds field
        f.write(stamp + " INFO  " + message + " #" + str(i + 1) + "\n")
        written = written + 1
        if tail_every > 0 and written % tail_every == 0:
            f.flush()   # push the buffer into the OS now, not at close()
    f.close()          # close() always flushes whatever is left
    return written


def tail_lines(path: str) -> list[str]:
    """Read a log file the way `tail` does: whole lines, newline removed."""
    lines = []
    f = open(path, mode="r", encoding="utf-8")
    for line in f:
        lines.append(line.rstrip("\n"))
    f.close()
    return lines


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    repeats = 200
    if len(args) > 1:
        repeats = int(args[0])
    tail_every = 1
    if len(args) > 2:
        tail_every = int(args[1])
    ensure_out()

    rows = load_csv(DATA)
    print("rows loaded:", len(rows))
    print("first row:", rows[0]["id"], "|", rows[0]["name"], "|", rows[0]["price"])
    print("name holding a comma:", rows[11]["name"])
    print("price came back as type:", type(rows[0]["price"]).__name__,
          "-> you must convert it yourself")

    print("")
    print("--- writing the same 12 rows in four formats ---")
    sizes = save_all(rows)
    print("format   bytes")
    for fmt in FORMATS:
        print(fmt.ljust(8) + str(sizes[fmt]))

    print("")
    print("--- round trip: load each file back ---")
    for fmt in FORMATS:
        back = load_any(out_path(fmt), fmt)
        print(fmt.ljust(8) + str(len(back)) + " rows | first id " + back[0]["id"]
              + " | price type " + type(back[0]["price"]).__name__)

    print("")
    print("--- average load time over " + str(repeats) + " runs (ms) ---")
    print("format   load_ms")
    times = {}
    for fmt in FORMATS:
        times[fmt] = measure(out_path(fmt), fmt, repeats)
        print(fmt.ljust(8) + ("%.4f" % times[fmt]))

    print("")
    print("--- log tailing with flush() (flush every " + str(tail_every) + " lines) ---")
    log_path = OUT_DIR + "/app.log"
    f = open(log_path, mode="w", encoding="utf-8", newline="")
    f.write("2026-05-04 12:00:00 INFO  server started\n")
    f.close()
    written = log_event(log_path, "crawler indexed document", tail_every)
    print("lines written:", written)
    for line in tail_lines(log_path):
        print("  " + line)

    smallest = "csv"
    fastest = "csv"
    for fmt in FORMATS:
        if sizes[fmt] < sizes[smallest]:
            smallest = fmt
        if times[fmt] < times[fastest]:
            fastest = fmt
    print("")
    print("smallest file: " + smallest + " (" + str(sizes[smallest]) + " bytes)")
    print("fastest load:  " + fastest + " (" + ("%.4f" % times[fastest]) + " ms)")
    print("csv/json size ratio: " + ("%.2f" % (sizes["json"] / sizes["csv"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())