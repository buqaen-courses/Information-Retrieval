"""Tests for solution/format_lab.py - hand-checkable expected values.

Every expected number below is either hand-computed or copied from a real run.
Run from the session folder:

    python -m pytest workshop/solution/ -v
"""
import csv
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from format_lab import (  # noqa: E402
    FIELDS,
    load_any,
    load_csv,
    log_event,
    measure,
    save_csv,
    save_json,
    save_ndjson,
    save_pickle,
    tail_lines,
)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "data", "records.csv")


def test_load_csv_reads_all_rows(tmp_path):
    rows = load_csv(DATA)
    # records.csv has a header line + 12 data lines
    assert len(rows) == 12
    assert rows[0]["id"] == "p-001"
    assert rows[0]["name"] == "Desk Lamp"
    # row 12 holds a comma inside the name: only the csv module gets this right
    assert rows[11]["name"] == "Cable, 3-pack"
    assert rows[11]["category"] == "electronics"


def test_csv_values_are_text(tmp_path):
    rows = load_csv(DATA)
    # CSV has no types: price arrives as the string "19.99"
    assert rows[0]["price"] == "19.99"
    assert isinstance(rows[0]["price"], str)


def test_round_trip_all_formats(tmp_path):
    rows = load_csv(DATA)
    paths = {
        "csv": str(tmp_path / "r.csv"),
        "json": str(tmp_path / "r.json"),
        "ndjson": str(tmp_path / "r.ndjson"),
        "pickle": str(tmp_path / "r.pkl"),
    }
    # sizes come from a real run of exactly these 12 rows
    sizes = {
        "csv": save_csv(rows, paths["csv"]),
        "json": save_json(rows, paths["json"]),
        "ndjson": save_ndjson(rows, paths["ndjson"]),
        "pickle": save_pickle(rows, paths["pickle"]),
    }
    assert sizes == {"csv": 1050, "json": 2101, "ndjson": 1774, "pickle": 1321}
    for fmt in ["csv", "json", "ndjson", "pickle"]:
        back = load_any(paths[fmt], fmt)
        assert len(back) == 12
        assert back[0] == rows[0]
        assert back[11]["name"] == "Cable, 3-pack"


def test_csv_header_order_is_fields(tmp_path):
    path = str(tmp_path / "h.csv")
    save_csv(load_csv(DATA), path)
    f = open(path, mode="r", encoding="utf-8", newline="")
    header = f.readline().rstrip("\r\n")
    f.close()
    assert header.split(",") == FIELDS


def test_ndjson_is_one_object_per_line(tmp_path):
    path = str(tmp_path / "r.ndjson")
    save_ndjson(load_csv(DATA), path)
    f = open(path, mode="r", encoding="utf-8")
    lines = f.readlines()
    f.close()
    assert len(lines) == 12
    first = json.loads(lines[0])
    assert first["id"] == "p-001"
    assert first["name"] == "Desk Lamp"


def test_pickle_keeps_python_types(tmp_path):
    rows = [{"n": 1, "price": 19.99, "tags": ["a", "b"]}]
    path = str(tmp_path / "typed.pkl")
    save_pickle(rows, path)
    back = load_any(path, "pickle")
    assert back == rows
    assert isinstance(back[0]["price"], float)
    assert back[0]["tags"] == ["a", "b"]


def test_measure_returns_positive_milliseconds(tmp_path):
    rows = load_csv(DATA)
    path = str(tmp_path / "m.json")
    save_json(rows, path)
    ms = measure(path, "json", repeats=20)
    assert ms > 0.0


def test_log_event_writes_three_flushed_lines(tmp_path):
    path = str(tmp_path / "app.log")
    f = open(path, mode="w", encoding="utf-8")
    f.write("2026-05-04 12:00:00 INFO  server started\n")
    f.close()
    written = log_event(path, "crawler indexed document", tail_every=1)
    assert written == 3
    lines = tail_lines(path)
    assert len(lines) == 4
    assert lines[0] == "2026-05-04 12:00:00 INFO  server started"
    assert lines[1] == "2026-05-04 12:00:01 INFO  crawler indexed document #1"
    assert lines[3] == "2026-05-04 12:00:03 INFO  crawler indexed document #3"


def test_flush_only_every_two_lines(tmp_path):
    path = str(tmp_path / "two.log")
    open(path, mode="w", encoding="utf-8").close()
    written = log_event(path, "doc", tail_every=2, count=4)
    # 4 written, but only the 2nd and 4th triggered a flush()
    assert written == 4
    assert len(tail_lines(path)) == 4