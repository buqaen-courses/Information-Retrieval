# SYLLABUS.md — Modern Information Retrieval: From File I/O to Hybrid Semantic Search

25 sessions × 90 min. Prerequisites: Python 3.10+, basic numpy/pandas comfort (state this in the course README).
Every session follows the same rhythm: **~45 min concept teaching (visuals + worked samples), ~45 min workshop.**

## Repository contract

```
ir-course/
├── AGENTS.md
├── SYLLABUS.md
├── README.md                  # course overview, setup, how to navigate sessions
├── requirements.txt
├── tools/
│   └── figstyle.py            # shared matplotlib style for ALL session images
├── setup/
│   ├── README.md              # session-0 prework checklist (python, venv, docker, model pre-cache)
│   ├── check_env.py           # verifies deps, docker, cached models; prints PASS/FAIL per item
│   ├── download_models.py     # pre-caches all-MiniLM-L6-v2 + cross-encoder/ms-marco-MiniLM-L-6-v2
│   ├── docker-compose-opensearch.yml
│   └── mock_shop/             # bundled static e-commerce site (10 pages, 120 products, pagination)
├── datasets/
│   ├── make_corpus.py         # deterministic (seeded) generator of ~200 short docs, 6 topics
│   ├── corpus/                # generated docs + qrels.json (relevance judgments, ~10 queries)
│   └── fallback_products.json # 120 products; used in S20–S23 if the real-site crawl fails
└── session-01-…/ … session-25-…/   # exactly 25 folders, contract per AGENTS.md
```

## Session map

| # | Folder name | Topic |
|---|---|---|
| 1 | session-01-text-file-io | Course intro + Python text file I/O |
| 2 | session-02-binary-data-os-files | Binary formats, buffers/cache, hash vs B-tree sidebar |
| 3 | session-03-naive-search-indexing | Linear scan vs dictionary lookup → why index |
| 4 | session-04-ir-architecture | IR systems: pipeline, IR vs DB, lexical vs semantic |
| 5 | session-05-inverted-index | Inverted index construction + hash/B-tree/inverted comparison |
| 6 | session-06-boolean-retrieval | Boolean model, postings intersection |
| 7 | session-07-tfidf-vector-space | TF-IDF, cosine similarity |
| 8 | session-08-bm25 | BM25 from scratch, k1/b tuning |
| 9 | session-09-probabilistic-models | BIM intuition, query likelihood, Dirichlet smoothing |
| 10 | session-10-evaluation | P/R, P@k, MRR, MAP, NDCG — build reusable metrics.py |
| 11 | session-11-efficient-scoring | Compression, skip pointers, WAND |
| 12 | session-12-embeddings | Embeddings + semantic search in pure numpy |
| 13 | session-13-vector-databases | Milvus Lite AND LanceDB + ANN index sidebar |
| 14 | session-14-semantic-engine | Reusable SemanticSearch class + metadata filtering |
| 15 | session-15-clustering-classification | k-means, hierarchical, Naïve Bayes |
| 16 | session-16-learning-to-rank | Pointwise/pairwise/listwise, LightGBM lambdarank |
| 17 | session-17-web-search-architecture | Crawler architecture, robots.txt, PageRank |
| 18 | session-18-crawling-practice | requests + BeautifulSoup on bundled mock shop |
| 19 | session-19-shop-crawl-workshop | Full crawl workshop → products dataset |
| 20 | session-20-near-duplicates | Shingling, MinHash, LSH, similarity graph |
| 21 | session-21-opensearch | OpenSearch indexing/querying + BKD/FST sidebar |
| 22 | session-22-hybrid-reranking | Hybrid BM25+kNN, RRF (Python fallback), cross-encoder rerank |
| 23 | session-23-end-to-end-build | Scaffolded pipeline: crawl→embed→index→hybrid |
| 24 | session-24-integration-clinic | Debugging, latency, hardening; capstone polish at home |
| 25 | session-25-capstone-presentations | Demos, rubric grading, course map, next steps (RAG/LLM) |

---

## Session specifications

Format per session: **Concepts** → content the README must teach (visuals first). **Images** → exact charts/diagrams to generate. **Workshop** → hands-on tasks in `workshop/`. **Deliverable** → what must work at the end.

### Session 1 — Course Intro & Python Text File I/O
- **Concepts:** course roadmap as pipeline (crawl→parse→index→query→rank→evaluate); `open/read/write/close`; context managers; UTF-8 encodings; iterating lines; word counting.
- **Images:** roadmap pipeline diagram; file-object lifecycle (open→buffer→flush→close); encode/decode flow diagram.
- **Workshop:** build `text_stats.py` — lines/words/char counts, top-10 words, on corpus from `datasets/corpus/`.
- **Deliverable:** stats script runs on any `.txt`.
- **Stretch:** handle multiple encodings gracefully.

### Session 2 — Binary Data & OS-Level Files
- **Concepts:** CSV/JSON/NDJSON vs pickle/struct/np.save; buffers (user-space) vs page cache (kernel) — intuition only; `flush()`/`fsync()`; file descriptors in one paragraph. **Sidebar (15 min):** hash index = O(1) exact lookup; B-tree = ordered, range queries, disk-friendly; why this matters later.
- **Images:** buffer vs page cache diagram; syscall-with/without-buffering comparison bar chart; hash lookup vs B-tree traversal side-by-side diagram. OS internals depth → `appendix-optional.md`.
- **Workshop:** save/load the same records as CSV/JSON/pickle; compare file size and load time; find a real-world use for `flush` (log tailing).
- **Deliverable:** format-comparison notebook with a results table.

### Session 3 — Naive Search & the Idea of Indexing
- **Concepts:** linear scan over files; term→file dictionary; complexity O(corpus) vs O(query); the "index" mental model.
- **Images:** linear-scan vs dict-lookup timing bar chart (measured, seeded); "book index vs page-flipping" analogy diagram.
- **Workshop:** implement both scanners over `datasets/corpus/`; benchmark; plot results.
- **Deliverable:** benchmark chart showing index wins.
- **Bridge:** explicit closing note — "this dict is one term away from an inverted index."

### Session 4 — IR Systems: Architecture
- **Concepts:** IR vs DB search; structured vs unstructured; full pipeline components; where semantic search plugs in; course preview mapped onto the diagram.
- **Images:** **large labeled IR architecture diagram** (reused/expanded in S23); lexical vs semantic comparison table-diagram.
- **Workshop:** students annotate the architecture diagram for a given scenario (e-commerce search); explore corpus with S1 stats.
- **Deliverable:** annotated diagram + 5-term glossary entry per student.

### Session 5 — Inverted Index Construction
- **Concepts:** tokenization, normalization, stop words, stemming/lemmatization; postings lists; tf per posting; positional index mention. **Sidebar (20 min):** hash vs B-tree vs inverted — table-diagram of what each can/cannot answer.
- **Images:** inverted index anatomy (terms→postings, labeled); tokenization pipeline flowchart; 3-way index comparison diagram.
- **Workshop:** build `{term: [doc_ids]}` then `{term: {doc_id: tf}}`; support 2-term AND queries; sanity tests.
- **Deliverable:** `inverted_index.py` + tests.

### Session 6 — Boolean Retrieval
- **Concepts:** AND/OR/NOT semantics; postings intersection/union; smallest-postings-first optimization; query parsing.
- **Images:** step-by-step postings intersection diagram; query parse tree.
- **Workshop:** Boolean engine parsing `"python AND search"`, `OR`, `NOT`; test suite with known answers.
- **Deliverable:** `boolean_search.py`.
- **Stretch:** parentheses; NOT-as-subtraction optimization.

### Session 7 — TF-IDF & Vector Space Model
- **Concepts:** TF, IDF, document vectors, cosine similarity, length normalization intuition.
- **Images:** cosine-angle diagram; IDF curve (rare vs common terms); 2D vector-space scatter with a query vector.
- **Workshop:** TF-IDF matrix in numpy from own inverted index; rank for sample queries; compare with Boolean output.
- **Deliverable:** `tfidf_ranker.py`.

### Session 8 — BM25
- **Concepts:** BM25 formula component-by-component; k1 = saturation; b = length normalization; hand-computed example.
- **Images:** TF saturation curves for 3 k1 values; score-vs-doc-length curves for 3 b values; TF-IDF vs BM25 ranked-list comparison.
- **Workshop:** implement BM25 from formula; grid-search k1,b ∈ {0.5,1.2,2.0}×{0,0.5,0.75} on corpus qrels (eyeball); compare vs TF-IDF.
- **Deliverable:** `bm25.py` with tests against hand-computed values.

### Session 9 — Probabilistic Models & Language Models  *(moved here to complete the theory arc)*
- **Concepts:** Probability Ranking Principle; BIM intuition (no full derivation); query-likelihood; Dirichlet smoothing; when LM-style scoring helps.
- **Images:** BIM relevance flow diagram; Dirichlet smoothing effect on small-document scores chart.
- **Workshop:** implement QL ranker with Dirichlet smoothing; compare rankings vs BM25 on 3 queries.
- **Deliverable:** `ql_ranker.py`.

### Session 10 — Evaluation  *(NEW — metrics built here feed S16, S22, S23)*
- **Concepts:** precision, recall, F1; P@k, R-precision; MRR; MAP; NDCG with graded relevance; test collections & qrels; why differences need care.
- **Images:** precision/recall grid diagram; NDCG discount curve; MRR worked example on a ranked list; sample results table.
- **Workshop:** implement P@k, MRR, MAP, NDCG@10 **from scratch**; evaluate TF-IDF vs BM25 vs QL on `datasets/qrels.json`; produce a results table.
- **Deliverable:** `metrics.py` — this exact module is copied into later workshops.

### Session 11 — Efficient Scoring
- **Concepts:** varint/delta compression (intuition); skip pointers; early termination; WAND/block-max WAND (demo-level); DAAT vs TAAT.
- **Images:** skip-pointer traversal diagram; WAND pruning illustration; compression size bar chart.
- **Workshop:** add skip pointers to postings intersection (guided); benchmark before/after on corpus. WAND: instructor-runs provided solution demo — **do not** make students implement it.
- **Deliverable:** benchmark chart.

### Session 12 — Embeddings & Semantic Search
- **Concepts:** dense vectors; word2vec → sentence-transformers; cosine/dot similarity; embedding-space intuition; ANN problem statement; model pre-cached from `setup/`.
- **Images:** 2D PCA scatter of embedded sentences colored by topic; cosine-similarity heatmap of 8 sentences; lexical-vs-semantic worked example (same query, different winners).
- **Workshop:** embed product mini-catalog with `all-MiniLM-L6-v2`; pure-numpy cosine search; find queries where semantic beats BM25 (and one where it fails).
- **Deliverable:** `numpy_semantic_search.py` + 2-page comparison notes.

### Session 13 — Vector Databases: Milvus Lite AND LanceDB  *(merged)*
- **Concepts:** collections/schemas/metric types; when to reach for a vector DB. **Sidebar (15 min):** HNSW, IVF, PQ — and why not B-trees (ANN ≠ ordered keys).
- **Images:** HNSW layered-graph diagram; IVF cluster diagram; PQ segmentation diagram; Milvus (server) vs LanceDB (embedded) architecture comparison.
- **Workshop:** index the same FAQ/product embeddings in **both** Milvus Lite (`MilvusClient("demo.db")`) and LanceDB (from a DataFrame); run identical queries; fill a comparison table (API ease, latency, disk format).
- **Deliverable:** completed comparison table + notebook.

### Session 14 — Building a Semantic Search Engine
- **Concepts:** architecture of a reusable search class; metadata filtering; error handling for missing embeddings.
- **Images:** `SemanticSearch` class diagram; filtered-search flow diagram.
- **Workshop:** implement `SemanticSearch` class (embed + search + category filter) using LanceDB or Milvus; unit tests.
- **Deliverable:** `semantic_search.py` — reused in S23.

### Session 15 — Classification & Clustering
- **Concepts:** text feature extraction; k-means; hierarchical clustering; Naïve Bayes; silhouette score.
- **Images:** k-means iteration frames (3 images); PCA cluster scatter of corpus; NB text-classification pipeline diagram.
- **Workshop:** cluster corpus docs (TF-IDF + k-means), visualize; classify with MultinomialNB; evaluate.
- **Deliverable:** clustering/classification notebook.

### Session 16 — Learning to Rank
- **Concepts:** pointwise/pairwise/listwise; ranking features; LambdaMART via LightGBM `lambdarank`; NDCG as training metric (reuse S10 metrics.py).
- **Images:** LTR pipeline diagram (features→model→rerank); pointwise vs pairwise illustration; training NDCG curve.
- **Workshop:** train lambdarank on synthetic judgments over corpus; evaluate NDCG@10 vs BM25 baseline.
- **Deliverable:** `ltr.py` + results table.

### Session 17 — Web Search Engines: Architecture & Crawling Theory
- **Concepts:** crawler components (frontier, dedup, politeness); robots.txt; rate limiting; PageRank intuition; scale case study (high level); **respectful crawling framed as non-negotiable ethics, not evasion**.
- **Images:** crawler architecture diagram; robots.txt decision flowchart; PageRank illustration on a small graph.
- **Workshop:** build `polite_crawler.py` skeleton — robots.txt checker, rate limiter, URL frontier — tested against a **local** mock site only.
- **Deliverable:** tested crawler skeleton (no external crawling).

### Session 18 — Web Crawling in Practice
- **Concepts:** HTTP requests; HTML parsing with BeautifulSoup; CSS selectors; pagination; identifying structured data; anti-bot awareness (what it is, why sites have it, why we avoid triggering it by being polite).
- **Images:** DOM tree of a product page; request lifecycle diagram; pagination crawl flow.
- **Workshop:** scrape the **bundled `setup/mock_shop/`** local site: product name, price, description across paginated listing pages → save NDJSON.
- **Deliverable:** working mock-shop scraper.

### Session 19 — Crawling Online Shops: Full Workshop
- **Concepts:** real-site constraints (JS rendering, ToS, rate limits); incremental crawls; data validation.
- **Images:** crawl→clean→schema pipeline diagram; product JSON schema diagram.
- **Workshop:** extend the crawl (caching, retries, incremental); validate output (no nulls, price parsing); produce ≥100 clean products. If a real permitted sandbox is available instructor may demo it live; **students always have `datasets/fallback_products.json`** so downstream sessions never break.
- **Deliverable:** `products.json` (≥100 items) or fallback dataset acknowledged.

### Session 20 — Near-Duplicate Detection & Document Graphs
- **Concepts:** shingling; Jaccard; MinHash signatures; LSH banding; similarity graphs; connected components.
- **Images:** shingling diagram; MinHash signature matrix diagram; LSH banding/buckets diagram; similarity graph rendered with networkx.
- **Workshop:** implement MinHash + LSH on product descriptions; find near-duplicates; build and visualize similarity graph.
- **Deliverable:** `dedup.py` + graph PNG.

### Session 21 — OpenSearch: Indexing & Querying
- **Concepts:** cluster/shards/replicas (intuition); mappings & analyzers (run the `_analyze` API); BM25 in OpenSearch; bulk API. **Sidebar (15 min):** BKD trees for numeric/geo, FSTs for term dictionaries.
- **Images:** shard architecture diagram; analyzer pipeline diagram; FST example diagram; BKD tree diagram.
- **Prework enforced:** `setup/check_env.py` must pass (Docker + OpenSearch up) before this session; include 10-min troubleshooting section.
- **Workshop:** create index with mappings; bulk-index the products; `match`, `term`, `range` queries; compare analyzer effects.
- **Deliverable:** `index_products.py` + `queries.py`.

### Session 22 — Hybrid Search & Reranking  *(corrected scope)*
- **Concepts:** two-stage retrieval (recall → rerank); score normalization; Reciprocal Rank Fusion; bi-encoder vs cross-encoder; **primary path = fetch BM25 + kNN separately, fuse with RRF in Python** (native `neural` clause shown as optional advanced path — ML Commons model deployment is not workshop-viable).
- **Images:** two-stage retrieval funnel diagram; RRF worked example (two ranked lists → fused); bi-encoder vs cross-encoder architecture diagram.
- **Workshop:** build `hybrid_search.py` (BM25 via OpenSearch + kNN via Milvus/Lance + RRF in Python); add cross-encoder rerank (`cross-encoder/ms-marco-MiniLM-L-6-v2`) over top-50; evaluate lexical-only vs hybrid vs hybrid+rerank with **S10 metrics.py**.
- **Deliverable:** results comparison table.

### Session 23 — End-to-End Build  *(scaffolded — not freeform)*
- **Concepts:** pipeline orchestration; config files; logging; idempotent indexing.
- **Images:** full system architecture diagram (S4 diagram, expanded with actual tools).
- **Workshop:** agent provides a **pre-scaffolded pipeline** with stubs + TODOs; students wire: products → embeddings → vector DB → OpenSearch → hybrid query → top-10 UI-in-terminal. 40 min pair work, 30 min debugging.
- **Deliverable:** working demo of the full pipeline.

### Session 24 — Integration Clinic & Capstone Hardening
- **Concepts:** systematic debugging of multi-component pipelines; latency measurement (time each stage); writing a project README; error handling.
- **Images:** debugging decision-tree flowchart; latency-budget bar chart template.
- **Workshop:** instructor-led debugging of 3 seeded broken pipelines; students harden their own; Q&A.
- **Deliverable:** capstone v1 done in class; **homework:** polish + add one novel feature (synonym expansion, filter UI, eval dashboard).

### Session 25 — Capstone Presentations & Course Review
- **Concepts:** presenting technical work; full course concept map; next steps: RAG, LLM-powered search, reranking at scale.
- **Images:** complete course concept map (all 25 sessions connected); grading rubric table.
- **Workshop:** 5–7 min demos; rubric: correctness (40), search relevance (30), code quality (20), presentation (10).
- **Deliverable:** final repo + demo.

---

## Continuity requirements (agent must enforce)
1. `datasets/corpus/`, `datasets/qrels.json`, `datasets/fallback_products.json` generated once in `datasets/make_corpus.py` with fixed seeds — every session reads the same data.
2. S10's `metrics.py` is the single source of evaluation truth for S16, S22, S23.
3. S14's `semantic_search.py`, S18–19's product dataset, S21's index all feed S23.
4. Every benchmark uses seeds so charts are reproducible.
