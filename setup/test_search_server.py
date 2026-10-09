"""Smoke test: does opensearch-py work against setup/search_server.py?

Run in two terminals (or background the server first):
    python setup/search_server.py            # terminal 1
    python setup/test_search_server.py       # terminal 2

Exits 0 if every check passes. This is what Sessions 21-23 rely on.
"""
from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_server import SearchEngine, serve  # noqa: E402

URL = "http://localhost:9211"
PRODUCTS = [
    {"id": "p-001", "name": "Compact kettle", "price": 29.5,
     "description": "A stainless kettle for kitchen lovers.", "category": "kitchen"},
    {"id": "p-002", "name": "Wireless headphones", "price": 89.0,
     "description": "Premium headphones with reliable sound.", "category": "electronics"},
    {"id": "p-003", "name": "Durable backpack", "price": 45.0,
     "description": "A lightweight backpack for travel lovers.",
     "category": "sports"},
]


def start_server() -> None:
    """Run the teaching server on :9211 in a background thread."""
    t = threading.Thread(target=serve, kwargs={"host": "localhost", "port": 9211},
                         daemon=True)
    t.start()
    time.sleep(0.6)


def main() -> int:
    """Exercise every endpoint the course needs and report pass/fail."""
    from opensearchpy import OpenSearch

    start_server()
    client = OpenSearch(hosts=[URL], timeout=30)
    checks: list[tuple[bool, str]] = []

    def check(name: str, fn) -> None:
        try:
            fn()
            checks.append((True, name))
        except Exception as exc:  # noqa: BLE001
            checks.append((False, f"{name} -> {type(exc).__name__}: {exc}"))

    client.indices.delete(index="products") if client.indices.exists(index="products") else None

    def t_create():
        client.indices.create(index="products", body={
            "settings": {"index": {"knn": True}},
            "mappings": {"properties": {
                "name": {"type": "text"},
                "description": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "float"},
            }},
        })

    def t_index():
        for p in PRODUCTS:
            client.index(index="products", id=p["id"], body={k: v for k, v in p.items()
                                                              if k != "id"})
        client.indices.refresh(index="products")

    def t_search():
        r = client.search(index="products", body={"query": {"match": {"name": "kettle"}},
                                                  "size": 5})
        ids = [h["_id"] for h in r["hits"]["hits"]]
        assert "p-001" in ids, f"kettle not found, got {ids}"
        assert r["hits"]["hits"][0]["_score"] > 0

    def t_match_multi():
        r = client.search(index="products", body={
            "query": {"match": {"description": {"query": "kitchen stainless",
                                                "operator": "and"}}}, "size": 5})
        ids = [h["_id"] for h in r["hits"]["hits"]]
        assert "p-001" in ids, f"AND-match failed, got {ids}"

    def t_term():
        r = client.search(index="products", body={"query": {"term": {"category": "kitchen"}}})
        ids = [h["_id"] for h in r["hits"]["hits"]]
        assert ids == ["p-001"], f"term query got {ids}"

    def t_range():
        r = client.search(index="products", body={
            "query": {"range": {"price": {"gte": 40, "lt": 100}}}})
        ids = sorted(h["_id"] for h in r["hits"]["hits"])
        assert ids == ["p-002", "p-003"], f"range got {ids}"

    def t_bool():
        # p-001 ("kitchen lovers") and p-003 ("travel lovers") match "lovers";
        # must_not category=sports removes p-003.
        r = client.search(index="products", body={"query": {"bool": {
            "must": [{"match": {"description": "lovers"}}],
            "must_not": [{"term": {"category": "sports"}}]}}})
        ids = sorted(h["_id"] for h in r["hits"]["hits"])
        assert ids == ["p-001"], f"bool got {ids}"

    def t_analyze():
        r = client.indices.analyze(index="products", body={"analyzer": "standard",
                                                          "text": "Wireless HEADPHONES!"})
        assert r["tokens"] == ["wireless", "headphones"], r["tokens"]

    def t_bulk():
        ndjson = "\n".join([
            json.dumps({"index": {"_index": "products", "_id": "p-004"}}),
            json.dumps({"name": "Ergonomic keyboard", "description": "A quiet keyboard.",
                        "category": "electronics", "price": 55.0}),
            json.dumps({"index": {"_index": "products", "_id": "p-005"}}),
            json.dumps({"name": "Classic notebook", "description": "A notebook for books.",
                        "category": "books", "price": 12.0}),
        ])
        res = client.bulk(body=ndjson)
        assert len(res["items"]) == 2, res
        client.indices.refresh(index="products")
        assert client.count(index="products")["count"] == 5

    def t_knn():
        r = client.search(index="products", body={
            "knn": {"field": "description_embedding", "vector": [1.0, 0.0],
                    "k": 2},
            "size": 2,
        })
        assert "hits" in r, r

    def t_count():
        n = client.count(index="products")["count"]
        assert n == 5, f"count={n}"

    def t_health():
        r = client.cluster.health()
        assert r["status"] in ("green", "yellow", "red"), r

    def t_info():
        assert client.info()["version"]["number"] == "2.13.0"

    def t_delete_index():
        client.indices.delete(index="products")
        assert not client.indices.exists(index="products")

    for name, fn in [("create index + mappings", t_create), ("index documents", t_index),
                     ("search: match", t_search), ("search: match with operator=and",
                                                    t_match_multi),
                     ("search: term (keyword)", t_term), ("search: range", t_range),
                     ("search: bool must/must_not", t_bool), ("_analyze", t_analyze),
                     ("_bulk NDJSON", t_bulk), ("knn query shape", t_knn),
                     ("_count", t_count), ("_cluster/health", t_health),
                     ("GET / version handshake", t_info), ("delete index", t_delete_index)]:
        check(name, fn)

    print("search_server compatibility")
    print("=" * 34)
    for ok, name in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failed = sum(1 for ok, _ in checks if not ok)
    print("=" * 34)
    print(f"{len(checks) - failed}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
