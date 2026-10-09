# PLANS.md — remaining work, resumable state of this repository

Single source of truth for "what is left". Written for a future agent (or a
future you) picking this up cold. Update it **in the same commit** as any work
that changes the plan.

Last updated: after Session 10 (evaluation) was completed and pushed.

---

## 1. Current state

| area | status |
|---|---|
| `setup/` infrastructure | **done** — mock shop (128 products), `check_env.py`, `download_models.py`, docker compose, bundled `search_server.py` |
| course venv + dependencies | **done** — Python 3.14, all packages installed and verified |
| Session 01–10 | **done** — README, images, WORKSHOP, starter, solution, tests; all validated in the venv |
| Session 11 | **partial** — `workshop/solution/fast_score.py` + `test_fast_score.py` written and passing; **missing** README, WORKSHOP, images, starter |
| Session 12–25 | **not started** — placeholder `.gitkeep` dirs only |
| Persian translations | **not started** |

Sessions 01–10 test counts (all passing in the venv):
`3, 9, 11, 7, 19, 37, 8, 13, 11, 16`.

---

## 2. Hard rules that survive a context reset

These are non-negotiable and are also written into `AGENTS.md`:

1. **Every number in every file comes from a real run.** No invented benchmark,
   timing, or score. If you paste a number, you ran it in the course venv.
2. **Validate before committing.** For each session: `make_images.py` runs and
   is deterministic, the starter runs without crashing, `pytest` passes, every
   README image link resolves, the worked example's output matches what is
   pasted.
3. **Commit and push per session.** Never a batch spanning many sessions.
4. **`Session 10`'s `metrics.py` is copied, never reimplemented**, into
   Sessions 16, 22, 23.
5. **Two load-bearing artefacts:** Session 14's `semantic_search.py` and
   Session 19's product dataset both feed Session 23. Build 14 and 19 before 23.
6. **Every `*.md` that ships also has a `*_fa.md` Persian translation** beside
   it, committed in the same commit.

---

## 3. Immediate next actions (in this order)

### 3.1 Finish Session 11 — efficient scoring
Already done: `workshop/solution/fast_score.py` (delta encoding, varint,
skip pointers, block-max WAND, benchmark) and `test_fast_score.py`.

Still needed:

- `session-11-efficient-scoring/images/make_images.py` + PNGs, all plots
  plotting **measured** values:
  - `11-01-skip-pointer-traversal.png` — diagram of the skip-list traversal
  - `11-02-compression-size.png` — bar chart of raw int32 bytes vs delta+varint
    (measured: 19,044 → 4,761 bytes = **4.00×** on `datasets/corpus`)
  - `11-03-comparisons-vs-time.png` — the honest two-panel chart: skip pointers
    examine **6.2× fewer** postings but are *slower* in pure Python
- `session-11-efficient-scoring/workshop/starter/fast_score.py` with 5–6 TODOs
- `session-11-efficient-scoring/README.md`
- `session-11-efficient-scoring/workshop/WORKSHOP.md`

Content to teach: varint/delta compression (intuition), skip pointers,
early termination, WAND (demo only — students do NOT implement WAND),
DAAT vs TAAT.

**Critical gotcha, already paid for once:** a skip pointer must record the
*maximum* doc id in its block, not the first. Recording the first lets you jump
over entries larger than your target and silently loses matches. The equivalence
test over all 48,841 term pairs of the real corpus catches this.

**Also:** the benchmark must not fake a speedup. Skip pointers are slower in
pure Python (`x in list` is already a C loop). Report comparisons examined as
the portable claim, and say why wall-clock disagrees.

### 3.2 Persian translations, one session at a time
For Sessions 01 → 11 in order, per session:

1. Translate `README.md` → `README_fa.md`
2. Translate `workshop/WORKSHOP.md` → `workshop/WORKSHOP_fa.md`
3. Translate any other `*.md` in that session (Session 02:
   `appendix-optional.md`; Session 04: `workshop/data/scenario.md`)
4. **Editor pass** on each translation: read as a Persian editor, fix register,
   ZWNJ, Persian characters/digits, گیومه, remove AI tells and em dashes
5. Run the skill's checkers: `persian_cleanup.py --edit` then `fa_lint.py --check`
6. Commit and push that session's translations

Translation rules are in `AGENTS.md` § Persian translations. Short version:
prose in Persian, **code blocks / commands / paths / output blocks untouched**,
technical terms Persian with the English in parentheses on first use, Persian
digits in prose but Latin digits inside code.

### 3.3 Sessions 12–25
Each needs README + 3–4 images + WORKSHOP + starter + solution + tests,
validated in the venv, committed and pushed individually. Suggested order
respecting the dependency rules above:

| # | folder | note |
|---|---|---|
| 12 | `session-12-embeddings` | `all-MiniLM-L6-v2`, cached. numpy cosine |
| 13 | `session-13-vector-databases` | Milvus Lite + LanceDB, same queries both |
| 14 | `session-14-semantic-engine` | **`SemanticSearch` class — feeds S23** |
| 15 | `session-15-clustering-classification` | k-means + MultinomialNB |
| 16 | `session-16-learning-to-rank` | LightGBM lambdarank, **copies S10 metrics.py** |
| 17 | `session-17-web-search-architecture` | robots.txt, frontier, rate limit, PageRank. Local only |
| 18 | `session-18-crawling-practice` | scrape `setup/mock_shop` |
| 19 | `session-19-shop-crawl-workshop` | **produces the product dataset — feeds S23** |
| 20 | `session-20-near-duplicates` | MinHash + LSH + networkx graph |
| 21 | `session-21-opensearch` | works against `setup/search_server.py` or real OpenSearch |
| 22 | `session-22-hybrid-reranking` | RRF in Python, cross-encoder rerank, **copies S10 metrics.py** |
| 23 | `session-23-end-to-end-build` | scaffolded pipeline; consumes S14 + S19 + **copies S10 metrics.py** |
| 24 | `session-24-integration-clinic` | 3 seeded broken pipelines |
| 25 | `session-25-capstone-presentations` | rubric, course map, RAG/LLM next steps |

---

## 4. Environment notes worth keeping

- Invoke Python as `& "F:\Courses\Buqaen\Information Retrieval\.venv\Scripts\python.exe" <script>`
  with `workdir` set to the repo root. Never hardcode the venv path into course files.
- **`datasets/` shadows the HuggingFace `datasets` package.** The repo folder has no
  `__init__.py`, so Python treats it as a *namespace package*. LanceDB does
  `from datasets import Dataset`, finds the namespace package instead, and raises
  ImportError. Any test that imports LanceDB needs a `conftest.py` that removes the
  repo root from the front of `sys.path`. Session 13 has one — copy that pattern.
- **Milvus Lite needs a manual install on Python 3.14.** `pymilvus[milvus_lite]` fails
  to resolve; the working command is
  `pip install --only-binary=:all: --no-deps milvus-lite`. Keep it in `requirements.txt`.
- **Milvus Lite writes a directory, not a file.** `milvus_lite.db` is a folder holding
  `collections/`, `wal/` and `schema.json`. Measure it by summing files, and expect
  `PermissionError` on Windows when a previous handle still holds it.
- The two databases report **different metrics**: Milvus gives `distance` (cosine),
  LanceDB gives `_distance` (squared L2). For length-1 vectors `cos = (2 - d²)/2`.
- `requirements.txt` is pinned to what actually builds on Python 3.14, which is
  **not** the original pin list in `SYLLABUS.md`. Do not "restore" the old pins.
- Docker Hub rate-limits this machine (403). The compose file takes an
  `OS_IMAGE_PREFIX` env var for a mirror. Sessions 21–23 do not need Docker:
  `setup/search_server.py` implements the OpenSearch subset the course uses,
  and `setup/test_search_server.py` proves `opensearch-py` talks to it (14/14).
- Models are cached: `sentence-transformers/all-MiniLM-L6-v2` (384 dims) and
  `cross-encoder/ms-marco-MiniLM-L-6-v2`.

## 5. Known findings that are deliberate, not bugs

Do not "fix" these without reading the section that explains them:

- **Session 9:** BM25 and query likelihood score *identically* on this corpus.
  Real measurement, kept and explained.
- **Session 10:** all three rankers score NDCG@10 = 1.0 because `qrels.json`
  grades documents by "contains ≥2 query terms", the same signal the rankers
  maximize; and recall is hard-capped at `10/34 = 0.2941`. Circular evaluation,
  taught on purpose. Consequence: S10's evaluation cannot discriminate between
  rankers. Later sessions must bring their own judgments to say anything.
- **Session 10 / Session 9:** `mu = 200` over-smooths a 45-token toy corpus by
  more than 2×. Pinned by a test, explained in the README.
- **Session 11:** skip pointers are slower in pure Python while examining 6.2×
  fewer postings. Both numbers are reported.
