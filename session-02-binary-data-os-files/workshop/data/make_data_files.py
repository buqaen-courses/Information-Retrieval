"""Generate the 4 format files in workshop/data/ from records.csv.

Run from the session folder:
    python workshop/data/make_data_files.py

Creates: records.json, records.ndjson, records.pkl
(records.csv already exists)
"""
from __future__ import annotations

import csv
import json
import pickle
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ["id", "name", "price", "category", "description"]


def load_csv(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    f = open(path, mode="r", encoding="utf-8", newline="")
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)
    f.close()
    return rows


def save_json(rows: list[dict[str, str]], path: Path) -> None:
    f = open(path, mode="w", encoding="utf-8", newline="")
    json.dump(rows, f, indent=2)
    f.write("\n")
    f.close()


def save_ndjson(rows: list[dict[str, str]], path: Path) -> None:
    f = open(path, mode="w", encoding="utf-8", newline="")
    for row in rows:
        f.write(json.dumps(row) + "\n")
    f.close()


def save_pickle(rows: list[dict[str, str]], path: Path) -> None:
    f = open(path, mode="wb")
    pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()


def main() -> None:
    rows = load_csv(HERE / "records.csv")
    save_json(rows, HERE / "records.json")
    save_ndjson(rows, HERE / "records.ndjson")
    save_pickle(rows, HERE / "records.pkl")
    print("created: records.json, records.ndjson, records.pkl")


if __name__ == "__main__":
    main()
