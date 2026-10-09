"""Tests for workshop/starter/format_lab.py — verifies all 11 TODOs are done.

Run from the session folder:
    python -m pytest workshop/workshop_test.py -v

These tests check that each TODO function works correctly. They do NOT check
the exact output format — only that the functions behave as specified.
"""
from __future__ import annotations

import csv
import json
import os
import sys

import pytest

STARTER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "starter")
sys.path.insert(0, STARTER_DIR)

from format_lab import (  # noqa: E402
    FIELDS,
    PROFILE_FIELDS,
    data_path,
    delete_records,
    insert_at,
    load_any,
    load_csv,
    out_path,
    save_all,
    save_csv,
    save_json,
    save_ndjson,
    save_pickle,
    update_record,
)
from fake_data import generate_profiles  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "records.csv")


def test_todo1_load_csv_reads_all_rows():
    rows = load_csv(DATA)
    assert len(rows) == 12
    assert rows[0]["id"] == "p-001"
    assert rows[0]["name"] == "Desk Lamp"
    assert rows[11]["name"] == "Cable, 3-pack"


def test_todo2_save_csv_round_trip(tmp_path):
    rows = load_csv(DATA)
    path = str(tmp_path / "r.csv")
    size = save_csv(rows, path, FIELDS)
    assert size == 1050
    back = load_csv(path)
    assert back == rows


def test_todo3_save_json_round_trip(tmp_path):
    rows = load_csv(DATA)
    path = str(tmp_path / "r.json")
    size = save_json(rows, path)
    assert size == 2101
    back = load_any(path, "json")
    assert back == rows


def test_todo4_save_ndjson_round_trip(tmp_path):
    rows = load_csv(DATA)
    path = str(tmp_path / "r.ndjson")
    size = save_ndjson(rows, path)
    assert size == 1774
    back = load_any(path, "ndjson")
    assert back == rows


def test_todo5_save_pickle_round_trip(tmp_path):
    rows = load_csv(DATA)
    path = str(tmp_path / "r.pkl")
    size = save_pickle(rows, path)
    assert size == 1321
    back = load_any(path, "pickle")
    assert back == rows


def test_todo6_log_event(tmp_path):
    from format_lab import log_event, tail_lines
    path = str(tmp_path / "app.log")
    f = open(path, mode="w", encoding="utf-8")
    f.write("2026-05-04 12:00:00 INFO  server started\n")
    f.close()
    written = log_event(path, "test message", tail_every=1)
    assert written == 3
    lines = tail_lines(path)
    assert len(lines) == 4
    assert lines[0] == "2026-05-04 12:00:00 INFO  server started"
    assert lines[1] == "2026-05-04 12:00:01 INFO  test message #1"
    assert lines[3] == "2026-05-04 12:00:03 INFO  test message #3"


def test_todo7_save_all_profiles(tmp_path, monkeypatch):
    monkeypatch.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    profiles = generate_profiles(100)
    sizes = save_all(profiles, "test_profiles", PROFILE_FIELDS)
    assert sizes["csv"] < sizes["pickle"] < sizes["ndjson"] < sizes["json"]
    for fmt in ["csv", "json", "ndjson", "pickle"]:
        back = load_any(out_path(fmt, "test_profiles"), fmt)
        assert len(back) == 100
        assert back[0]["id"] == "u-00001"


def test_todo8_update_record():
    profiles = generate_profiles(10)
    update_record(profiles, 0, "price", 999.99)
    assert profiles[0]["price"] == 999.99
    assert profiles[1]["price"] != 999.99


def test_todo9_delete_records():
    profiles = generate_profiles(100)
    ca_before = len([p for p in profiles if p["state"] == "CA"])
    assert ca_before > 0
    profiles = delete_records(profiles, lambda p: p["state"] == "CA")
    ca_after = len([p for p in profiles if p["state"] == "CA"])
    assert ca_after == 0
    assert len(profiles) == 100 - ca_before


def test_todo10_insert_at():
    profiles = generate_profiles(10)
    new_profile = {"id": "u-new", "name": "Test", "email": "t@t.org",
                   "age": 30, "price": 42.0, "city": "Testville",
                   "state": "TS", "zip": 12345, "street": "1 Test St",
                   "product": "test", "tags": ["test"]}
    result = insert_at(profiles, 5, new_profile)
    assert len(result) == 11
    assert result[5]["id"] == "u-new"
    assert result[0]["id"] == "u-00001"
    assert result[10]["id"] == "u-00010"


def test_todo11_combined_operations():
    profiles = generate_profiles(1000)
    update_record(profiles, 0, "price", 888.88)
    ca_count = len([p for p in profiles if p["state"] == "CA"])
    profiles = delete_records(profiles, lambda p: p["state"] == "CA")
    new_profile = {"id": "u-new", "name": "Test", "email": "t@t.org",
                   "age": 30, "price": 42.0, "city": "Testville",
                   "state": "TS", "zip": 12345, "street": "1 Test St",
                   "product": "test", "tags": ["test"]}
    profiles = insert_at(profiles, 5, new_profile)
    assert profiles[0]["price"] == 888.88
    assert profiles[5]["id"] == "u-new"
    assert len([p for p in profiles if p["state"] == "CA"]) == 0
    assert len(profiles) == 1000 - ca_count + 1
