"""Measure the real numbers Session 2 charts and quotes.

Run once from the session folder:
    python images/measure.py
It writes images/measurements.json, which make_images.py reads. Nothing here is
invented: every figure is produced by running code on the real 12-row workshop
CSV and on datasets/fallback_products.json.
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SESSION = HERE.parent
DATA = SESSION / "workshop" / "data" / "records.csv"


def build_rows(path):
    rows = []
    with open(path, mode="r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def fmt_sizes(rows, fields, tmp):
    out = {}
    p = os.path.join(tmp, "r.csv")
    with open(p, mode="w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    out["csv"] = os.path.getsize(p)
    p = os.path.join(tmp, "r.json")
    with open(p, mode="w", encoding="utf-8", newline="") as f:
        json.dump(rows, f, indent=2)
        f.write("\n")
    out["json"] = os.path.getsize(p)
    p = os.path.join(tmp, "r.ndjson")
    with open(p, mode="w", encoding="utf-8", newline="") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    out["ndjson"] = os.path.getsize(p)
    import pickle
    p = os.path.join(tmp, "r.pkl")
    with open(p, mode="wb") as f:
        pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)
    out["pickle"] = os.path.getsize(p)
    return out


def time_loader(path, fmt, reps):
    import pickle

    def load_csv_f():
        with open(path, mode="r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def load_json_f():
        with open(path, mode="r", encoding="utf-8") as f:
            return json.load(f)

    def load_ndjson_f():
        out = []
        with open(path, mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def load_pickle_f():
        with open(path, mode="rb") as f:
            return pickle.load(f)

    fn = {"csv": load_csv_f, "json": load_json_f,
          "ndjson": load_ndjson_f, "pickle": load_pickle_f}[fmt]
    fn()
    samples = []
    for _ in range(reps):
        s = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - s) * 1000.0)
    return samples


def main():
    tmp = tempfile.mkdtemp(prefix="ir-s02-")
    report = {}

    # --- 1. workshop records (12 rows) -------------------------------------
    rows = build_rows(DATA)
    fields = list(rows[0].keys())
    report["n_records"] = len(rows)
    report["sizes_workshop"] = fmt_sizes(rows, fields, tmp)

    reps = 300
    report["load_ms_workshop"] = {}
    report["load_ms_workshop_median"] = {}
    for fmt in ["csv", "json", "ndjson", "pickle"]:
        ext = {"csv": "csv", "json": "json", "ndjson": "ndjson", "pickle": "pkl"}[fmt]
        s = time_loader(os.path.join(tmp, "r." + ext), fmt, reps)
        report["load_ms_workshop"][fmt] = round(sum(s) / len(s), 4)
        report["load_ms_workshop_median"][fmt] = round(statistics.median(s), 4)

    # --- 2. the 128-product fallback dataset (bigger, more realistic) ------
    fb = json.load(open(ROOT / "datasets" / "fallback_products.json", encoding="utf-8"))
    fb_fields = list(fb[0].keys())
    report["n_products"] = len(fb)
    report["sizes_fallback"] = fmt_sizes(fb, fb_fields, tmp)
    report["load_ms_fallback"] = {}
    for fmt in ["csv", "json", "ndjson", "pickle"]:
        ext = {"csv": "csv", "json": "json", "ndjson": "ndjson", "pickle": "pkl"}[fmt]
        s = time_loader(os.path.join(tmp, "r." + ext), fmt, 200)
        report["load_ms_fallback"][fmt] = round(statistics.median(s), 4)

    # --- 3. buffering cost: 2000 small writes, buffered vs unbuffered ------
    n_writes = 2000
    payload = b"x" * 64
    trials = 15

    def write_bench(bufsize):
        samples = []
        for _ in range(trials):
            p = os.path.join(tmp, "buf.bin")
            f = open(p, "wb", buffering=bufsize)
            s = time.perf_counter()
            for _ in range(n_writes):
                f.write(payload)
            f.close()
            samples.append((time.perf_counter() - s) * 1000.0)
        return round(statistics.median(samples), 3)

    report["buffered_ms"] = write_bench(-1)      # -1 = default buffer (8192 bytes)
    report["unbuffered_ms"] = write_bench(0)     # 0 = every write goes straight through
    report["speedup"] = round(report["unbuffered_ms"] / report["buffered_ms"], 1)
    report["write_bytes"] = n_writes * len(payload)
    # syscalls: the default 8192-byte buffer is written out when it fills, plus
    # one final write at close() -> ceil(128000 / 8192) = 16 writes reach the OS
    report["syscalls_buffered"] = -(-report["write_bytes"] // 8192)
    report["syscalls_unbuffered"] = n_writes

    # --- 4. line-count-free read: 128 small reads vs 1 big read -----------
    report["read_many_ms"] = None
    report["read_one_ms"] = None

    out = HERE / "measurements.json"
    with open(out, mode="w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    for k in ["n_records", "n_products", "sizes_workshop", "sizes_fallback",
              "load_ms_workshop_median", "load_ms_fallback", "buffered_ms",
              "unbuffered_ms", "speedup", "syscalls_buffered", "syscalls_unbuffered"]:
        print(k + ":", report[k])
    print("wrote:", out)


if __name__ == "__main__":
    sys.exit(main())