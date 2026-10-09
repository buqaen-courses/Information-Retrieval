"""Session 2 — format lab starter: 6 TODOs (prints a hint until each is done).

Run from the session folder with the course venv active:

    python workshop/starter/format_lab.py [repeats] [flush_every]

Input file workshop/data/records.csv (12 rows). Its first two lines:

    id,name,price,category,description
    p-001,Desk Lamp,19.99,lighting,"Warm LED desk lamp, brushed steel, 3-year warranty"

The last row's name holds a comma inside quotes — that is exactly why we use
the csv module instead of line.split(",")

This file RUNS without crashing: an unfinished TODO prints a hint and the
program stops there. Work top to bottom; each TODO shows the snippet shape.
Compare with workshop/solution/format_lab.py when you are done.
"""

from __future__ import annotations

import csv
import json
import os
import pickle
import sys
import time
from typing import Any

TODO_COUNT = 6

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
    # TODO-1: read the file with csv.DictReader. Snippet shape:
    #     rows = []
    #     f = open(path, mode="r", encoding="utf-8", newline="")
    #     reader = csv.DictReader(f)      # keys every row by the header line
    #     for row in reader:
    #         rows.append(row)
    #     f.close()
    #     return rows
    # (newline="" tells Python "do not translate line endings" — the csv docs
    #  ask for it, and it keeps your byte counts identical on Windows and Linux.)
    raise NotImplementedError("TODO-1 not done yet - read the CSV with csv.DictReader")


def save_csv(rows: list[dict[str, str]], path: str) -> int:
    """Write rows to a CSV file; returns the size in bytes."""
    # TODO-2: write the rows with csv.DictWriter. Snippet shape:
    #     f = open(path, mode="w", encoding="utf-8", newline="")
    #     writer = csv.DictWriter(f, fieldnames=FIELDS)   # column order lives here
    #     writer.writeheader()          # writes the "id,name,..." line
    #     for row in rows:
    #         writer.writerow(row)      # quotes any value that contains a comma
    #     f.close()
    #     return os.path.getsize(path) # os.path.getsize -> size in bytes
    raise NotImplementedError("TODO-2 not done yet - write the CSV with csv.DictWriter")


def save_json(rows: list[dict[str, str]], path: str) -> int:
    """Write rows to pretty-printed JSON; returns the size in bytes."""
    # TODO-3: write the JSON file. Snippet shape:
    #     f = open(path, mode="w", encoding="utf-8", newline="")
    #     json.dump(rows, f, indent=2)   # indent=2 makes the file human-readable
    #     f.write("\n")
    #     f.close()
    #     return os.path.getsize(path)
    # (json.dump writes into a file you opened yourself; there is no path= here.)
    raise NotImplementedError("TODO-3 not done yet - write JSON with json.dump(indent=2)")


def save_ndjson(rows: list[dict[str, str]], path: str) -> int:
    """Write rows as NDJSON (one compact JSON object per line); returns the size."""
    # TODO-4: write one JSON object per line. Snippet shape:
    #     f = open(path, mode="w", encoding="utf-8", newline="")
    #     for row in rows:
    #         f.write(json.dumps(row) + "\n")   # json.dumps -> one string
    #     f.close()
    #     return os.path.getsize(path)
    # (json.dumps gives you the string; json.dump gives the file. Same data.)
    raise NotImplementedError("TODO-4 not done yet - write NDJSON with json.dumps per line")


def save_pickle(rows: list[dict[str, str]], path: str) -> int:
    """Write rows to a pickle file; returns the size in bytes."""
    # TODO-5: write the pickle. Snippet shape:
    #     f = open(path, mode="wb")   # "b" = binary mode, required for pickle
    #     pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)
    #     f.close()
    #     return os.path.getsize(path)
    raise NotImplementedError("TODO-5 not done yet - write the pickle in binary mode")


def load_any(path: str, fmt: str) -> list[dict[str, Any]]:
    """Load a file back given its format name: csv | json | ndjson | pickle.

    (Given to you — you need it to prove the round trip works.)
    """
    if fmt == "csv":
        return load_csv(path)
    if fmt == "pickle":
        f = open(path, mode="rb")
        rows = pickle.load(f)
        f.close()
        return rows
    if fmt == "ndjson":
        f = open(path, mode="r", encoding="utf-8")
        rows = []
        for line in f:
            line = line.strip()
            if line != "":
                rows.append(json.loads(line))
        f.close()
        return rows
    f = open(path, mode="r", encoding="utf-8")
    rows = json.load(f)
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
    load_any(path, fmt)               # warm the OS page cache first
    total = 0.0
    for _ in range(repeats):
        start = time.perf_counter()   # monotonic clock, in seconds
        load_any(path, fmt)
        total = total + (time.perf_counter() - start)
    return total * 1000.0 / repeats


def log_event(path: str, message: str, tail_every: int, count: int = 3) -> int:
    """Append log lines, calling flush() every `tail_every` writes.

    The real-world use of flush(): a log tailer (`tail -f`) can only read lines
    that already left Python's buffer, so a logging loop flushes as it goes.
    """
    # TODO-6: write the lines and flush as you go. Snippet shape:
    #     stamp = "2026-05-04 12:00:00"
    #     f = open(path, mode="a", encoding="utf-8", newline="")   # "a" = append
    #     written = 0
    #     for i in range(count):
    #         second = int(stamp[-2:]) + 1
    #         stamp = stamp[:-2] + ("%02d" % second)   # bump the seconds field
    #         f.write(stamp + " INFO  " + message + " #" + str(i + 1) + "\n")
    #         written = written + 1
    #         if tail_every > 0 and written % tail_every == 0:
    #             f.flush()     # push the buffer down into the OS right now
    #     f.close()            # close() always flushes whatever is left
    #     return written
    raise NotImplementedError("TODO-6 not done yet - append log lines and flush() every line")


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

    try:
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
    except NotImplementedError as exc:
        print(exc)
        print("(" + str(TODO_COUNT) + " TODOs total - open starter/format_lab.py and work top to bottom.)")
        return 0

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