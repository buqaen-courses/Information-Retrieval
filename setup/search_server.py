"""A tiny OpenSearch-compatible search server (stdlib only) for Sessions 21-23.

Why this exists
---------------
Sessions 21-23 talk to a real search engine over HTTP. The course ships a
docker-compose file for genuine OpenSearch, but Docker is not always available
(or Docker Hub rate-limits the pull), and a self-study student should never be
blocked by infrastructure. So this module implements the *subset* of the
OpenSearch REST API the course uses, with real inverted-index scoring behind it.

Start it (from the repo root, with the course venv active):
    python setup/search_server.py                 # listens on :9200
    python setup/search_server.py --port 9201

Then any OpenSearch client works unchanged:
    from opensearchpy import OpenSearch
    client = OpenSearch(hosts=["http://localhost:9200"])
    client.indices.create(index="products", body={"mappings": {...}})
    client.index(index="products", id="p-001", body={...})
    client.search(index="products", body={"query": {"match": {"name": "kettle"}}})

Supported endpoints
-------------------
GET  /                              version info (OpenSearch handshake)
GET  /_cluster/health               cluster health
PUT  /<index>                       create index with settings + mappings
DELETE /<index>                     drop index
HEAD /<index>                       exists?
GET  /<index>/_mapping              current mappings
POST /<index>/_analyze              run the analyzer, see the token stream
POST /_bulk, /<index>/_bulk         NDJSON bulk index
POST /<index>/_refresh              no-op (this server is always "fresh")
POST /<index>/_count                count matching docs
POST /<index>/_delete_by_query      delete matching docs
POST /<index>/_search               the interesting one

Supported query DSL
-------------------
{"match_all": {}}
{"match": {"field": "text"}}
{"match": {"field": {"query": "text", "operator": "and"}}}
{"term": {"field": "exact"}}
{"terms": {"field": ["a", "b"]}}
{"range": {"field": {"gte": 10, "lt": 100}}}
{"bool": {"must": [...], "should": [...], "must_not": [...], "filter": [...]}}
{"knn": {"field": "vector", "vector": [...], "k": 10}}   # cosine similarity
{"function_score": {...}}                                # score_mode=sum

Scoring: Okapi BM25 with the engine defaults k1=1.2, b=0.75, so numbers match
OpenSearch closely. This is a teaching server, not a production one — no
persistence, no shards, no concurrency control. Data lives in RAM.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import threading
from collections import Counter, defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

VERSION = {"number": "2.13.0", "distribution": "opensearch", "build_type": "tar"}
K1, B = 1.2, 0.75
MAX_SCORE_HINT = 1e9

# Unicode-ish word tokenizer: letters and digits, apostrophes and intra-word
# hyphens kept together (mirrors OpenSearch's standard analyzer closely enough).
_TOKEN_RE = re.compile(r"[^\W_]+(?:['\-][^\W_]+)*", re.UNICODE)


def analyze(text: str, analyzer: str = "standard") -> list[str]:
    """Split text into lowercased tokens the way the standard analyzer does."""
    if not isinstance(text, str):
        text = str(text)
    if analyzer in ("keyword", "whitespace"):
        return [text]
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(text)]


def stopwords() -> set[str]:
    """The standard analyzer's default stop list (a practical subset)."""
    return {
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if",
        "in", "into", "is", "it", "no", "not", "of", "on", "or", "such", "that",
        "the", "their", "then", "there", "these", "they", "this", "to", "was",
        "will", "with",
    }


class Index:
    """One index: its mappings plus documents held in memory."""

    def __init__(self, name: str, body: dict[str, Any] | None = None) -> None:
        """Create an index from a create-index body (settings + mappings)."""
        body = body or {}
        self.name = name
        self.docs: dict[str, dict] = {}
        mprops = body.get("mappings", {}).get("properties", {})
        self.text_fields: list[str] = [f for f, p in mprops.items()
                                       if p.get("type", "text") == "text"]
        self.keyword_fields: list[str] = [f for f, p in mprops.items()
                                          if p.get("type") == "keyword"]
        self.vector_fields: list[str] = [f for f, p in mprops.items()
                                         if p.get("type") == "knn_vector"]
        self.analysis: dict = body.get("settings", {}).get("analysis", {})
        self._lock = threading.Lock()

    def fields(self) -> list[str]:
        """Every mapped field name."""
        return self.text_fields + self.keyword_fields + self.vector_fields

    def is_text(self, field: str) -> bool:
        """Is this field analyzed into tokens?"""
        return field in self.text_fields or field not in self.fields()

    def doc_len(self, doc_id: str) -> int:
        """Number of tokens in a document across its text fields."""
        total = 0
        for f in self.text_fields:
            total += len(analyze(str(self.docs[doc_id].get(f, ""))))
        if total == 0:
            total = max(1, len(self.docs[doc_id]))
        return total

    def term_freq(self, doc_id: str, token: str) -> int:
        """How many times token appears in doc_id."""
        n = 0
        for f in self.text_fields:
            n += analyze(str(self.docs[doc_id].get(f, ""))).count(token)
        if n == 0:
            for f in self.keyword_fields:
                if str(self.docs[doc_id].get(f, "")) == token:
                    n = 1
        return n


class SearchEngine:
    """Holds every index and executes queries against them."""

    def __init__(self) -> None:
        """Start with an empty engine."""
        self.indices: dict[str, Index] = {}
        self.lock = threading.Lock()

    # ---------- index management ----------

    def create_index(self, name: str, body: dict) -> dict:
        """Create an index (idempotent: replaces an existing one)."""
        with self.lock:
            self.indices[name] = Index(name, body)
        return {"acknowledged": True, "shards_acknowledged": True, "index": name}

    def delete_index(self, name: str) -> dict:
        """Drop an index; 404 if it does not exist."""
        with self.lock:
            existed = self.indices.pop(name, None) is not None
        if not existed:
            raise KeyError(name)
        return {"acknowledged": True}

    def index_doc(self, name: str, doc_id: str, body: dict) -> dict:
        """Add or replace one document."""
        self._require(name)
        with self.indices[name]._lock:
            self.indices[name].docs[doc_id] = body
        return {"_index": name, "_id": doc_id, "result": "created",
                "_version": len(self.indices[name].docs), "_shards": {"total": 1,
                                                                     "successful": 1,
                                                                     "failed": 0}}

    def delete_doc(self, name: str, doc_id: str) -> dict:
        """Delete one document."""
        self._require(name)
        with self.indices[name]._lock:
            self.indices[name].docs.pop(doc_id, None)
        return {"_index": name, "_id": doc_id, "result": "deleted"}

    def bulk(self, ops: list[dict]) -> dict:
        """Apply a parsed NDJSON bulk body; returns per-item results."""
        items, errors = [], False
        for op in ops:
            if not isinstance(op, dict) or not op:
                continue
            action, meta = next(iter(op.items()))
            if action not in ("index", "create", "update", "delete") or not meta:
                continue
            idx, did = meta.get("_index"), meta.get("_id")
            if action == "delete":
                self.delete_doc(idx, did)
                items.append({"delete": {"_index": idx, "_id": did, "status": 200}})
                continue
            src = op.get("doc", op.get("doc_as_upsert", {}))
            self.index_doc(idx, did, src)
            items.append({action: {"_index": idx, "_id": did, "status": 200}})
        return {"took": 1, "errors": errors, "items": items}

    def _require(self, name: str) -> Index:
        """Fetch an index or raise KeyError."""
        if name not in self.indices:
            raise KeyError(name)
        return self.indices[name]

    # ---------- query execution ----------

    def count(self, name: str, query: dict) -> int:
        """Number of documents matching the query (filters only)."""
        docs, _ = self._run(name, query, limit=10**9)
        return len(docs)

    def delete_by_query(self, name: str, query: dict) -> int:
        """Delete every matching document; returns how many went."""
        docs, _ = self._run(name, query, limit=10**9)
        with self.indices[name]._lock:
            for doc_id in docs:
                self.indices[name].docs.pop(doc_id, None)
        return len(docs)

    def search(self, name: str, body: dict) -> dict:
        """Run a search and return an OpenSearch-shaped response."""
        query = body.get("query") or {"match_all": {}}
        size = int(body.get("size", 10))
        frm = int(body.get("from", 0) or 0)
        docs, scores = self._run(name, query, limit=size + frm)

        hits = []
        for doc_id, score in docs[frm:frm + size]:
            hits.append({
                "_index": name,
                "_id": doc_id,
                "_score": round(score, 6),
                "_source": self.indices[name].docs[doc_id],
            })
        total = len(docs)
        sort = body.get("sort")
        out: dict[str, Any] = {
            "took": 1,
            "timed_out": False,
            "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
            "hits": {
                "total": {"value": total, "relation": "eq"},
                "max_score": max((h["_score"] for h in hits), default=None),
                "hits": hits,
            },
        }
        if sort:
            out["hits"]["sort"] = [h["_score"] for h in hits]
        return out

    # ---------- the scoring core ----------

    def _run(self, name: str, query: dict, limit: int
             ) -> tuple[list[tuple[str, float]], dict]:
        """Evaluate a query, returning [(doc_id, score), ...] sorted best first."""
        idx = self._require(name)
        results = self._eval(idx, query)
        return results[:limit], {}

    def _eval(self, idx: Index, query: dict) -> list[tuple[str, float]]:
        """Recursively evaluate one query clause into scored documents."""
        if "bool" in query:
            return self._eval_bool(idx, query["bool"])
        if "function_score" in query:
            inner = query["function_score"].get("query", {"match_all": {}})
            scored = self._eval(idx, inner)
            boost = 1.0
            for fn in query["function_score"].get("functions", []):
                if "weight" in fn:
                    boost = float(fn["weight"])
            return [(d, s * boost) for d, s in scored]
        if "match_all" in query:
            return [(d, 1.0) for d in idx.docs]
        if "match" in query:
            return self._eval_match(idx, query["match"])
        if "term" in query:
            return self._eval_term(idx, query["term"])
        if "terms" in query:
            return self._eval_terms(idx, query["terms"])
        if "range" in query:
            return self._eval_range(idx, query["range"])
        if "knn" in query:
            return self._eval_knn(idx, query["knn"])
        if "ids" in query:
            wanted = set(query["ids"].get("values", []))
            return [(d, 1.0) for d in idx.docs if d in wanted]
        if "exists" in query:
            field = query["exists"].get("field")
            return [(d, 1.0) for d, src in idx.docs.items()
                    if src.get(field) not in (None, "", [], {})]
        return []

    def _eval_bool(self, idx: Index, clause: dict) -> list[tuple[str, float]]:
        """Combine must / should / must_not / filter sub-clauses."""
        must = [self._eval(idx, c) for c in clause.get("must", [])]
        should = [self._eval(idx, c) for c in clause.get("should", [])]
        must_not = [self._eval(idx, c) for c in clause.get("must_not", [])]
        filt = [self._eval(idx, c) for c in clause.get("filter", [])]

        if must:
            base = dict(must[0])
            for extra in must[1:]:
                for d, s in extra.items():
                    base[d] = base.get(d, 0.0) + s
        else:
            base = {}
            if should:
                for group in should:
                    for d, s in group.items():
                        base[d] = base.get(d, 0.0) + s
                if clause.get("minimum_should_match", 0) == 0:
                    pass  # scores only; all should-docs contribute
            else:
                for d in idx.docs:
                    base[d] = 0.0

        for group in must_not:
            for d, _ in group:
                base.pop(d, None)
        for group in filt:
            keep = {d for d, _ in group}
            base = {d: s for d, s in base.items() if d in keep}

        return sorted(base.items(), key=lambda kv: (-kv[1], kv[0]))

    def _eval_match(self, idx: Index, spec: dict) -> list[tuple[str, float]]:
        """Full-text match with BM25 scoring."""
        field = next(iter(spec))
        opts = spec[field]
        if isinstance(opts, str):
            text, operator = opts, "or"
        else:
            text, operator = opts.get("query", ""), opts.get("operator", "or")
        tokens = [t for t in analyze(text) if t not in stopwords()]
        if not tokens:
            return [(d, 0.0) for d in idx.docs]

        n_docs = len(idx.docs)
        avg_len = sum(idx.doc_len(d) for d in idx.docs) / max(1, n_docs)
        df = Counter()
        for tok in set(tokens):
            df[tok] = sum(1 for d in idx.docs if idx.term_freq(d, tok) > 0)

        scores: dict[str, float] = {}
        per_doc_hits: dict[str, int] = defaultdict(int)
        for tok in set(tokens):
            n_tok = df[tok]
            if n_tok == 0:
                continue
            idf = math.log(1 + (n_docs - n_tok + 0.5) / (n_tok + 0.5))
            for doc_id in idx.docs:
                f = idx.term_freq(doc_id, tok)
                if not f:
                    continue
                norm = K1 * (1 - B + B * idx.doc_len(doc_id) / avg_len)
                scores[doc_id] = scores.get(doc_id, 0.0) + idf * (f * (K1 + 1)) / (f + norm)
                per_doc_hits[doc_id] += 1

        if operator == "and" and len(set(tokens)) > 1:
            scores = {d: s for d, s in scores.items()
                      if per_doc_hits[d] == len(set(tokens))}
        return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))

    def _eval_term(self, idx: Index, spec: dict) -> list[tuple[str, float]]:
        """Exact (unanalyzed) term match."""
        field, value = next(iter(spec.items()))
        if isinstance(value, dict):
            value = value.get("value")
        if idx.is_text(field) and field in idx.fields():
            value = analyze(str(value))[0] if analyze(str(value)) else str(value)
        return [(d, 1.0) for d, src in idx.docs.items()
                if str(src.get(field, "")) == str(value)]

    def _eval_terms(self, idx: Index, spec: dict) -> list[tuple[str, float]]:
        """Match any value from a list."""
        field, values = next(iter(spec.items()))
        wanted = {str(v) for v in values}
        return [(d, 1.0) for d, src in idx.docs.items()
                if str(src.get(field, "")) in wanted]

    def _eval_range(self, idx: Index, spec: dict) -> list[tuple[str, float]]:
        """Numeric range filter: gt / gte / lt / lte."""
        field, bounds = next(iter(spec.items()))
        hits = []
        for doc_id, src in idx.docs.items():
            raw = src.get(field)
            if raw is None:
                continue
            try:
                val = float(raw)
            except (TypeError, ValueError):
                continue
            ok = True
            for op, cmp_fn in (("gt", lambda a, b: a > b),
                               ("gte", lambda a, b: a >= b),
                               ("lt", lambda a, b: a < b),
                               ("lte", lambda a, b: a <= b)):
                if op in bounds and not cmp_fn(val, float(bounds[op])):
                    ok = False
                    break
            if ok:
                hits.append((doc_id, 1.0))
        return sorted(hits)

    def _eval_knn(self, idx: Index, spec: dict) -> list[tuple[str, float]]:
        """Brute-force k-nearest-neighbour by cosine similarity."""
        field = spec.get("field") or (idx.vector_fields[0] if idx.vector_fields else None)
        vec = spec.get("vector") or spec.get("query_vector") or []
        k = int(spec.get("k", 10))
        nq = math.sqrt(sum(v * v for v in vec)) or 1.0
        scored = []
        for doc_id, src in idx.docs.items():
            dv = src.get(field) or []
            if not dv:
                continue
            dot = sum(a * b for a, b in zip(vec, dv))
            nd = math.sqrt(sum(v * v for v in dv)) or 1.0
            scored.append((doc_id, dot / (nq * nd)))
        scored.sort(key=lambda kv: (-kv[1], kv[0]))
        return scored[:k]


class Handler(BaseHTTPRequestHandler):
    """HTTP layer: route OpenSearch paths onto the engine."""

    engine: SearchEngine
    protocol_version = "HTTP/1.1"
    server_version = "ir-course-search/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        """Quieter than the default one-line-per-request logging."""
        print(f"  {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")

    # ---------- helpers ----------

    def _send(self, code: int, payload: dict) -> None:
        """Write a JSON response body."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=UTF-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Elastic-Product", "Elasticsearch")
        self.send_header("X-OpenSearch-Product", "OpenSearch")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, code: int, reason: str, extra: dict | None = None) -> None:
        """Write an OpenSearch-shaped error body."""
        err: dict[str, Any] = {"root_cause": [{"type": reason, "reason": reason}]}
        err.update(extra or {})
        self._send(code, {"error": err, "status": code})

    def _body(self) -> dict:
        """Parse the request body as JSON (empty dict when absent)."""
        raw = self._raw()
        if not raw.strip():
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _raw(self) -> bytes:
        """Read the request body exactly once (keeps HTTP/1.1 in sync)."""
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def _path(self) -> tuple[str, list[str]]:
        """Split the URL into (index_name, [action, ...]) with url-decoded parts."""
        parts = [unquote(p) for p in urlparse(self.path).path.strip("/").split("/") if p]
        if not parts:
            return "", []
        if parts[0] == "_search":
            return "", ["_search"]
        if parts[0] == "_bulk":
            return "", ["_bulk"]
        return parts[0], parts[1:]

    # ---------- verbs ----------

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        """Handle GET (version, mappings, health, search)."""
        name, rest = self._path()
        params = parse_qs(urlparse(self.path).query)
        if not name:
            return self._send(200, {"name": "ir-course", "cluster_name": "ir-course",
                                    "version": VERSION, "tagline": "For searchers"})
        if rest[:1] == ["health"]:
            docs = sum(len(i.docs) for i in self.engine.indices.values())
            return self._send(200, {"cluster_name": "ir-course", "status": "green",
                                    "timed_out": False, "number_of_nodes": 1,
                                    "number_of_data_nodes": 1,
                                    "active_primary_shards": len(self.engine.indices),
                                    "active_shards": len(self.engine.indices),
                                    "relocating_shards": 0, "initializing_shards": 0,
                                    "unassigned_shards": 0, "delayed_unassigned_shards": 0,
                                    "number_of_pending_tasks": 0,
                                    "number_of_in_flight_fetch": 0,
                                    "task_max_waiting_in_queue_millis": 0,
                                    "active_shards_percent_as_number": 100.0,
                                    "_nodes": {"total": 1, "successful": 1, "failed": 0},
                                    "_shards": {"total": max(1, len(self.engine.indices)),
                                                "successful": max(1, len(self.engine.indices)),
                                                "skipped": 0, "failed": 0},
                                    "_doc_count": docs})
        if rest and rest[0] == "_search":
            return self._search(name, self._body_from_params(params))
        try:
            idx = self.engine._require(name)
        except KeyError:
            return self._error(404, "index_not_found_exception",
                               {"index": name, "resource.id": name})
        if rest == ["_mapping"]:
            props = {f: {"type": "text"} for f in idx.text_fields}
            props.update({f: {"type": "keyword"} for f in idx.keyword_fields})
            props.update({f: {"type": "knn_vector"} for f in idx.vector_fields})
            return self._send(200, {name: {"mappings": {"properties": props}}})
        if rest in ([], ["_search"]):
            return self._search(name, self._body_from_params(params))
        return self._error(400, "unsupported_endpoint", {"path": self.path})

    def do_HEAD(self) -> None:  # noqa: N802
        """Handle HEAD (index existence checks)."""
        name, _ = self._path()
        exists = bool(name) and name in self.engine.indices
        self.send_response(200 if exists else 404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_PUT(self) -> None:  # noqa: N802
        """Handle PUT (create index, or index a document by id)."""
        name, rest = self._path()
        raw = self._raw()
        try:
            if not name:
                return self._error(400, "unsupported_endpoint", {"path": self.path})
            if rest[:1] == ["_doc"] and len(rest) > 1:
                body = json.loads(raw.decode("utf-8")) if raw.strip() else {}
                self._send(201, self.engine.index_doc(name, rest[1], body))
            elif not rest:
                self._send(200, self.engine.create_index(name, json.loads(raw.decode("utf-8"))
                                                         if raw.strip() else {}))
            else:
                self._error(400, "unsupported_endpoint", {"path": self.path})
        except KeyError:
            self._error(404, "index_not_found_exception", {"index": name})
        except json.JSONDecodeError as exc:
            self._error(400, "parse_exception", {"reason": str(exc)})

    def do_DELETE(self) -> None:  # noqa: N802
        """Handle DELETE (drop index or document)."""
        name, rest = self._path()
        try:
            if not rest:
                self._send(200, self.engine.delete_index(name))
            elif rest[0] == "_doc" and len(rest) > 1:
                self._send(200, self.engine.delete_doc(name, rest[1]))
            else:
                self._error(400, "unsupported_endpoint", {"path": self.path})
        except KeyError:
            self._error(404, "index_not_found_exception", {"index": name})

    def do_POST(self) -> None:  # noqa: N802
        """Handle POST (bulk, search, analyze, count, delete_by_query, index)."""
        name, rest = self._path()
        raw = self._raw()
        if not name and rest == ["_bulk"]:
            return self._send(200, self.engine.bulk(self._parse_ndjson(raw)))
        if not name:
            return self._error(400, "unsupported_endpoint", {"path": self.path})
        try:
            body = json.loads(raw.decode("utf-8")) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            return self._error(400, "parse_exception", {"reason": str(exc)})

        action = rest[0] if rest else ""
        if action == "_search":
            return self._search(name, body)
        if action == "_count":
            return self._send(200, {"count": self.engine.count(name,
                                body.get("query") or {"match_all": {}}),
                                "_shards": {"total": 1, "successful": 1, "skipped": 0,
                                            "failed": 0}})
        if action == "_delete_by_query":
            n = self.engine.delete_by_query(name, body.get("query") or {"match_all": {}})
            return self._send(200, {"deleted": n, "took": 1, "failures": []})
        if action == "_analyze":
            return self._analyze(name, body)
        if action == "_refresh":
            return self._send(200, {"_shards": {"total": 1, "successful": 1,
                                                "failed": 0}})
        if action == "_doc":
            doc_id = body.pop("_id", None) or body.pop("id", None) or "0"
            return self._send(201, self.engine.index_doc(name, str(doc_id), body))
        return self._error(400, "unsupported_endpoint", {"path": self.path})

    # ---------- pieces ----------

    def _parse_ndjson(self, raw: bytes) -> list[dict]:
        """Parse a bulk NDJSON body into a list of single-key dicts."""
        ops = []
        for line in raw.decode("utf-8").splitlines():
            line = line.strip()
            if line:
                ops.append(json.loads(line))
        return ops

    def _analyze(self, name: str, body: dict) -> None:
        """Run the analyzer and return the token stream (Session 21's demo)."""
        try:
            idx = self.engine._require(name)
        except KeyError:
            idx = Index(name)
        text = body.get("text", "")
        if isinstance(text, list):
            text = " ".join(text)
        field = body.get("field", "")
        analyzer = body.get("analyzer", "standard")
        if field and idx.is_text(field):
            analyzer = "standard"
        tokens = analyze(text, analyzer)
        if body.get("explain", False):
            return self._send(200, {"tokens": [{"token": t, "start_offset": 0,
                                                "end_offset": len(t), "type": "<ALPHANUM>",
                                                "position": i}
                                               for i, t in enumerate(tokens)]})
        self._send(200, {"tokens": tokens})

    def _search(self, name: str, body: dict) -> None:
        """Execute a search, translating missing indices into 404s."""
        try:
            self.engine._require(name)
        except KeyError:
            return self._error(404, "index_not_found_exception",
                               {"index": name, "resource.id": name})
        try:
            self._send(200, self.engine.search(name, body))
        except Exception as exc:  # noqa: BLE001 - surface parse errors as 400
            self._error(400, "query_shard_exception", {"reason": str(exc)})

    def _body_from_params(self, params: dict[str, list[str]]) -> dict:
        """Build a query body from URL parameters (GET /_search?q=...)."""
        out: dict[str, Any] = {}
        if "q" in params and params["q"]:
            text = params["q"][0]
            field = params.get("df", ["_all"])[0] if "df" in params else None
            out["query"] = ({"match": {field or "_all": text}} if field
                            else {"multi_match": {"query": text}})
            out["query"] = {"match": {field or "_all": text}}
        if "size" in params:
            out["size"] = int(params["size"][0])
        return out


def serve(host: str = "localhost", port: int = 9200) -> None:
    """Run the search server until interrupted."""
    engine = SearchEngine()
    handler = type("BoundHandler", (Handler,), {"engine": engine})
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"ir-course search server listening on http://{host}:{port}")
    print("  GET  /                 version handshake")
    print("  POST /<index>/_search  run a query")
    print("  POST /<index>/_analyze inspect the analyzer")
    print("  POST /_bulk             NDJSON bulk index")
    print("Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="OpenSearch-compatible teaching server")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=9200)
    args = ap.parse_args()
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
