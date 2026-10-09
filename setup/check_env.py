"""Verify the course environment. Prints PASS/FAIL per item.

Usage (from the repo root, with the course venv active):
    python setup/check_env.py

Run this before Session 21 (OpenSearch) — it is a hard prerequisite there.
Items marked OPTIONAL do not block the course.
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PY_LIBS = [
    ("numpy", "sessions 7, 12, 15"),
    ("matplotlib", "every session's images"),
    ("pandas", "sessions 13, 15, 16"),
    ("sklearn", "sessions 12, 15"),
    ("requests", "sessions 18-19"),
    ("bs4", "sessions 18-19"),
    ("networkx", "session 20"),
    ("sentence_transformers", "sessions 12-14, 22"),
    ("lancedb", "sessions 13, 14, 22"),
    ("pymilvus", "sessions 13, 22"),
    ("opensearchpy", "sessions 21-23"),
    ("lightgbm", "session 16"),
]

OPENSEARCH_URL = "http://localhost:9200"


def check_python() -> tuple[bool, str]:
    """The course needs Python 3.10+."""
    v = sys.version_info
    ok = v >= (3, 10)
    return ok, f"python {v.major}.{v.minor}.{v.micro}"


def check_in_venv() -> tuple[bool, str]:
    """Warn if running with the system Python instead of the course venv."""
    in_venv = sys.prefix != sys.base_prefix
    return in_venv, f"prefix={sys.prefix}" + ("" if in_venv else "  (NOT a venv)")


def check_libs() -> list[tuple[bool, str, str]]:
    """Import every course library and report its version."""
    out = []
    for name, used_in in PY_LIBS:
        try:
            mod = __import__(name)
            ver = getattr(mod, "__version__", "ok")
            out.append((True, f"{name}=={ver}", used_in))
        except Exception as exc:  # noqa: BLE001 - a missing lib is a report, not a crash
            out.append((False, f"{name} MISSING ({type(exc).__name__})", used_in))
    return out


def check_models() -> list[tuple[bool, str, str]]:
    """Verify both models resolve offline from the local cache."""
    out = []
    try:
        from sentence_transformers import CrossEncoder, SentenceTransformer

        m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2",
                                local_files_only=True)
        dim = len(m.encode(["offline check"], normalize_embeddings=True)[0])
        out.append((dim == 384, f"all-MiniLM-L6-v2 cached (dim={dim})", "sessions 12-14, 22"))
        c = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", local_files_only=True)
        c.predict([["ping", "pong"]])
        out.append((True, "ms-marco-MiniLM-L-6-v2 cached", "session 22"))
    except Exception as exc:  # noqa: BLE001
        out.append((False, f"models not cached ({type(exc).__name__})",
                    "run setup/download_models.py"))
    return out


def check_datasets() -> list[tuple[bool, str, str]]:
    """Corpus docs, qrels and fallback products must all exist and be non-empty."""
    out = []
    corpus = ROOT / "datasets" / "corpus"
    n_docs = len(list(corpus.glob("doc-*.txt"))) if corpus.exists() else 0
    out.append((n_docs >= 200, f"corpus docs = {n_docs}", "sessions 3, 5-11"))

    qrels = ROOT / "datasets" / "qrels.json"
    if qrels.exists():
        n_q = len(json.loads(qrels.read_text(encoding="utf-8")))
        out.append((n_q >= 10, f"qrels queries = {n_q}", "sessions 8-11, 16, 22-23"))
    else:
        out.append((False, "qrels.json MISSING", "run datasets/make_corpus.py"))

    fb = ROOT / "datasets" / "fallback_products.json"
    if fb.exists():
        n_p = len(json.loads(fb.read_text(encoding="utf-8")))
        out.append((n_p >= 120, f"fallback products = {n_p}", "sessions 19-23"))
    else:
        out.append((False, "fallback_products.json MISSING", "run datasets/make_corpus.py"))
    return out


def check_mock_shop() -> tuple[bool, str]:
    """The bundled static shop must be generated (Session 18-19 crawl it)."""
    shop = ROOT / "setup" / "mock_shop"
    n_detail = len(list((shop / "product").glob("*.html"))) if (shop / "product").exists() else 0
    pages = len(list((shop / "products").glob("page-*.html"))) if (shop / "products").exists() else 0
    ok = n_detail >= 120 and pages >= 4
    return ok, f"mock shop: {n_detail} detail pages, {pages} listing pages"


def check_docker() -> tuple[bool, str]:
    """Docker is optional until Session 21."""
    try:
        out = subprocess.run(["docker", "--version"], capture_output=True,
                             text=True, timeout=15)
        if out.returncode != 0:
            return False, "docker not found (OPTIONAL — needed for session 21)"
        return True, out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, "docker not found (OPTIONAL — needed for session 21)"


def check_opensearch() -> tuple[bool, str]:
    """Is OpenSearch actually up right now? Optional until Session 21."""
    try:
        with socket.create_connection(("localhost", 9200), timeout=3):
            pass
    except OSError:
        return False, "nothing listening on :9200 (OPTIONAL — session 21 prework)"
    try:
        import requests

        info = requests.get(OPENSEARCH_URL, timeout=5).json()
        return True, f"opensearch {info.get('version', {}).get('number', '?')} at :9200"
    except Exception as exc:  # noqa: BLE001
        return False, f":9200 open but query failed ({type(exc).__name__})"


def report(title: str, rows: list[tuple[bool, str]], note: str = "") -> int:
    """Print a titled block of PASS/FAIL rows; return the number of failures."""
    print(f"\n{title}")
    print("-" * len(title))
    failures = 0
    for ok, msg in rows:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        failures += 0 if ok else 1
    if note:
        print(f"  note: {note}")
    return failures


def main() -> int:
    """Run every check and print a final verdict."""
    print("IR course environment check")
    print("=" * 34)

    blocking = 0

    ok, msg = check_python()
    blocking += report("Python", [(ok, msg)],
                       "needs 3.10+" if not ok else "")
    if not ok:
        print("\nPython too old — stop here and install 3.10+.")
        return 1

    ok, msg = check_in_venv()
    print(f"\nVirtualenv\n----------\n  {'PASS' if ok else 'WARN'}  {msg}")
    if not ok:
        print("  Activate the course venv before continuing:")
        print("    .venv\\Scripts\\activate      (Windows)")
        print("    source .venv/bin/activate  (macOS/Linux)")

    libs = check_libs()
    blocking += report("Libraries", [(ok, msg) for ok, msg, _ in libs],
                       "used by: " + "; ".join(sorted({u for _, _, u in libs})))

    blocking += report("Models (offline cache)",
                       [(ok, msg) for ok, msg, _ in check_models()],
                       "run: python setup/download_models.py")

    blocking += report("Course data", [(ok, msg) for ok, msg, _ in check_datasets()],
                       "run: python datasets/make_corpus.py")

    ok, msg = check_mock_shop()
    blocking += report("Mock shop", [(ok, msg)],
                       "run: python setup/mock_shop/build_shop.py" if not ok else "")

    optional_rows = [check_docker(), check_opensearch()]
    report("Optional (session 21 only)", optional_rows,
           "start OpenSearch: docker compose -f setup/docker-compose-opensearch.yml up -d")

    print("\n" + "=" * 46)
    if blocking == 0:
        print("RESULT: all required checks PASS. You're ready for every session.")
        return 0
    print(f"RESULT: {blocking} required check(s) FAILED — see the FAIL lines above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
