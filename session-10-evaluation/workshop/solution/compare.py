"""Score TF-IDF, BM25 and query likelihood against the course qrels.

This is the Session 10 deliverable: one results table produced by ONE metric
implementation, so the three rankers can be compared honestly.

Run from the repo root:
    python session-10-evaluation/workshop/solution/compare.py
    python session-10-evaluation/workshop/solution/compare.py --k 5
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "session-08-bm25", "workshop", "solution"))
sys.path.insert(0, os.path.join(ROOT, "session-09-probabilistic-models",
                                "workshop", "solution"))

from metrics import evaluate_run  # noqa: E402

import bm25 as bm25_mod          # noqa: E402
import ql_ranker as ql_mod       # noqa: E402

CORPUS = os.path.join(ROOT, "datasets", "corpus")
QRELS = os.path.join(ROOT, "datasets", "qrels.json")
PUNCTUATION = ".,!?;:'\""


def tokenize(text: str) -> list[str]:
    """Session 1's recipe: lowercase, peel punctuation, split."""
    out = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word:
            out.append(word)
    return out


def load_docs(folder: str) -> dict[str, list[str]]:
    """{doc_id: tokens} for every corpus document."""
    docs = {}
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".txt"):
            continue
        with open(os.path.join(folder, name), mode="r", encoding="utf-8") as f:
            docs[name[:-4]] = tokenize(f.read())
    return docs


def load_qrels() -> dict[str, dict]:
    with open(QRELS, mode="r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- #
# Three rankers, each producing {query_id: [ranked doc ids]}
# --------------------------------------------------------------------------- #
def tfidf_run(docs: dict[str, list[str]], qrels: dict, top: int = 10
              ) -> dict[str, list[str]]:
    """TF-IDF with log-tf weighting and cosine similarity."""
    vocab = sorted({t for toks in docs.values() for t in toks})
    idx = {t: i for i, t in enumerate(vocab)}
    n_docs = len(docs)
    df = {t: sum(1 for toks in docs.values() if t in toks) for t in vocab}

    vectors = {}
    for doc_id, toks in docs.items():
        vec = [0.0] * len(vocab)
        counts = {}
        for t in toks:
            counts[t] = counts.get(t, 0) + 1
        for t, c in counts.items():
            idf = math.log(1 + (n_docs - df[t] + 0.5) / (df[t] + 0.5))
            vec[idx[t]] = (1 + math.log(c)) * idf
        vectors[doc_id] = vec

    run = {}
    for qid, info in qrels.items():
        q_vec = [0.0] * len(vocab)
        for t in set(tokenize(info["query"])):
            if t in idx:
                q_vec[idx[t]] = math.log(1 + (n_docs - df[t] + 0.5) / (df[t] + 0.5))
        qn = math.sqrt(sum(v * v for v in q_vec)) or 1.0
        scored = []
        for doc_id, vec in vectors.items():
            dn = math.sqrt(sum(v * v for v in vec)) or 1.0
            s = sum(a * b for a, b in zip(q_vec, vec)) / (qn * dn)
            if s > 0:
                scored.append((doc_id, s))
        scored.sort(key=lambda kv: (-kv[1], kv[0]))
        run[qid] = [d for d, _ in scored[:top]]
    return run


def bm25_run(folder: str, qrels: dict, top: int = 10) -> dict[str, list[str]]:
    stats = bm25_mod.build_stats(folder)
    run = {}
    for qid, info in qrels.items():
        ranked = bm25_mod.search(folder, info["query"])
        run[qid] = [d for d, s in ranked[:top] if s > 0]
    return run


def ql_run(folder: str, qrels: dict, top: int = 10) -> dict[str, list[str]]:
    run = {}
    for qid, info in qrels.items():
        run[qid] = [d for d, _ in ql_mod.search(folder, info["query"], top=top)]
    return run


def main() -> int:
    k = 10
    if "--k" in sys.argv:
        k = int(sys.argv[sys.argv.index("--k") + 1])

    qrels = load_qrels()
    flat_qrels = {qid: info["relevant"] for qid, info in qrels.items()}

    runs = {
        "TF-IDF": tfidf_run(load_docs(CORPUS), qrels, top=k),
        "BM25": bm25_run(CORPUS, qrels, top=k),
        "Query likelihood": ql_run(CORPUS, qrels, top=k),
    }

    metrics = [f"P@{k}", f"R@{k}", "R-precision", "MRR", "MAP", f"NDCG@{k}"]
    print(f"{len(flat_qrels)} queries over {len(os.listdir(CORPUS))} documents,"
          f" judged relevance > 0")
    print()
    header = "ranker".ljust(18) + "".join(m.rjust(12) for m in metrics)
    print(header)
    print("-" * len(header))
    rows = []
    for name, run in runs.items():
        row = evaluate_run(run, flat_qrels, k=k)
        rows.append((name, row))
        print(name.ljust(18) + "".join(f"{row[m]:12.4f}" for m in metrics))

    best = max(rows, key=lambda r: r[1][f"NDCG@{k}"])[1][f"NDCG@{k}"]
    print()
    print(f"best NDCG@{k}: {best:.4f}")
    print()

    # ------------------------------------------------------------------ #
    # Why is everything perfect? Because the judgments and the rankers use
    # the same signal. This is the most important lesson in the session.
    # ------------------------------------------------------------------ #
    qid = "q05"
    info = qrels[qid]
    judged = info["relevant"]
    relevant = sum(1 for g in judged.values() if g > 0)
    grade2 = sum(1 for g in judged.values() if g >= 2)
    print(f"diagnostic — query {qid}: {info['query']!r}")
    print(f"  documents judged relevant (>0): {relevant}")
    print(f"  of those, graded highly (2):    {grade2}")
    print(f"  slots in the top-{k} list:        {k}")
    print(f"  so R@{k} is capped near {k}/{relevant} = {k / relevant:.4f}"
          f" — measured {rows[1][1][f'R@{k}']:.4f}")
    print()
    print("  NDCG is 1.0 for every ranker because the grade-2 documents are")
    print("  defined as 'contains at least two query terms' — which is exactly")
    print("  what BM25 and TF-IDF maximize. The judgments were generated from")
    print("  the same signal the rankers use, so the evaluation cannot fail.")
    print()
    print("  This is a trap you can fall into with any synthetic dataset: a")
    print("  perfect score means your test is circular, not that your engine")
    print("  is good. Real judgments come from humans who read the documents.")
    print("  Sessions 16, 22 and 23 reuse these metrics — reuse the METRIC,")
    print("  but bring your own judgments.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
