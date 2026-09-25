# Modern Information Retrieval: From File I/O to Hybrid Semantic Search

> 25 sessions × 90 min. Each session = ~45 min concepts (visuals first) + ~45 min workshop.
> Prerequisites: Python 3.10+, basic numpy/pandas comfort.

You will build a complete search engine from scratch: files → inverted index → TF-IDF/BM25 →
embeddings → vector DBs → web crawling → OpenSearch → hybrid retrieval with reranking →
end-to-end demo + capstone.

**Pedagogical rule:** teach, then practice — never mix. Read the session `README.md` first
(visuals + tiny worked example), then open `workshop/WORKSHOP.md` and code.

## How to use this repo

1. Start at `setup/` — Session-0 prework: Python venv, Docker for OpenSearch, pre-cache models.
   Run `python setup/check_env.py` until everything passes.
2. Sessions are sequential: `session-01-…` → `session-25-…`. Do not skip evaluation (Session 10) —
   its `metrics.py` is reused in Sessions 16, 22, 23.
3. Each session folder follows the same contract (see `AGENTS.md`):
   `README.md` teaches, `images/` holds generated charts, `workshop/` holds practice
   (`WORKSHOP.md`, `data/`, `starter/` with TODOs, `solution/` with tests).
4. No network at runtime except pre-cached HuggingFace models and local OpenSearch Docker.
   All crawling targets the bundled `setup/mock_shop/` local site. If a crawl fails,
   fall back to `datasets/fallback_products.json` so downstream sessions never break.

## Repository layout

```
├── AGENTS.md          # how materials are generated (folder contract, image/code rules)
├── SYLLABUS.md        # what each of the 25 sessions teaches (source of truth)
├── README.md          # this file
├── TOC.md             # full table of contents with links
├── requirements.txt
├── tools/figstyle.py  # shared matplotlib style for ALL images
├── setup/             # prework: check_env, download_models, docker-compose, mock_shop
├── datasets/          # make_corpus.py → corpus/, qrels.json, fallback_products.json
└── session-01-…/ … session-25-…/
```

## Course pipeline

```
crawl → parse → index → query → rank → evaluate → hybrid + rerank → demo
 S17-19   S18     S5-6     S6-7   S7-9      S10        S22          S23-25
   │                  │               │          │                    │
   └─ files S1-2 ─────┴─ efficient S11 ─┴─ vectors S12-14 ─┴─ LTR S16 ─┘
```

## Table of contents (summary)

Full links in [TOC.md](TOC.md).

| Part | Sessions | Theme |
|---|---|---|
| I — Foundations | 01–04 | Files, OS basics, why index, IR architecture |
| II — Lexical retrieval | 05–10 | Inverted index, Boolean, TF-IDF, BM25, LM models, evaluation |
| III — Efficiency + semantics | 11–14 | Compression/WAND, embeddings, Milvus+LanceDB, semantic engine |
| IV — ML + web | 15–19 | Clustering/classification, LTR, crawler theory + practice + shop workshop |
| V — Scale + hybrid | 20–23 | Near-duplicates, OpenSearch, hybrid+rerank, end-to-end build |
| VI — Capstone | 24–25 | Integration clinic, presentations |

## Ethics note

Respectful crawling is non-negotiable (Sessions 17–19): robots.txt, rate limits, local-first.
We never crawl live third-party sites from student machines.

## Status

- [x] `AGENTS.md`, `SYLLABUS.md`, folder skeleton, `README.md`, `TOC.md`
- [ ] `tools/`, `setup/`, `datasets/` implementation
- [ ] Sessions 01→25 (generated sequentially, validated one by one)

Next: instruct the agent to generate `tools/` → `setup/` → `datasets/`, then Session 1.
