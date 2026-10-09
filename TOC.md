# TOC — Modern Information Retrieval (25 sessions)

> Each row links to the session folder. Folders are scaffolded; content is generated sequentially starting with Session 1.

| # | Session | Folder | Topic | Key deliverable |
|---|---|---|---|---|
| 1 | Course Intro & Python Text File I/O | [session-01-text-file-io](session-01-text-file-io/) | Roadmap pipeline, open/read/write, context managers, UTF-8, word counting | `text_stats.py` |
| 2 | Binary Data & OS-Level Files | [session-02-binary-data-os-files](session-02-binary-data-os-files/) | CSV/JSON/pickle, buffers vs page cache, hash vs B-tree sidebar | format-comparison table |
| 3 | Naive Search & the Idea of Indexing | [session-03-naive-search-indexing](session-03-naive-search-indexing/) | Linear scan vs dict lookup, O(corpus) vs O(query) | benchmark chart |
| 4 | IR Systems: Architecture | [session-04-ir-architecture](session-04-ir-architecture/) | IR vs DB, pipeline components, lexical vs semantic | annotated diagram + glossary |
| 5 | Inverted Index Construction | [session-05-inverted-index](session-05-inverted-index/) | Tokenization, postings, tf, hash/B-tree/inverted sidebar | `inverted_index.py` + tests |
| 6 | Boolean Retrieval | [session-06-boolean-retrieval](session-06-boolean-retrieval/) | AND/OR/NOT, postings intersection, query parsing | `boolean_search.py` |
| 7 | TF-IDF & Vector Space Model | [session-07-tfidf-vector-space](session-07-tfidf-vector-space/) | TF, IDF, cosine, length norm | `tfidf_ranker.py` |
| 8 | BM25 | [session-08-bm25](session-08-bm25/) | k1 saturation, b length norm, hand-computed example | `bm25.py` + tests |
| 9 | Probabilistic & Language Models | [session-09-probabilistic-models](session-09-probabilistic-models/) | PRP, BIM intuition, QL + Dirichlet | `ql_ranker.py` |
| 10 | Evaluation | [session-10-evaluation](session-10-evaluation/) | P/R, P@k, MRR, MAP, NDCG, qrels | `metrics.py` (reused S16/S22/S23) |
| 11 | Efficient Scoring | [session-11-efficient-scoring](session-11-efficient-scoring/) | Compression, skips, WAND demo, DAAT/TAAT | benchmark chart |
| 12 | Embeddings & Semantic Search | [session-12-embeddings](session-12-embeddings/) | Dense vectors, cosine, ANN problem | `numpy_semantic_search.py` |
| 13 | Vector Databases | [session-13-vector-databases](session-13-vector-databases/) | Milvus Lite + LanceDB, HNSW/IVF/PQ sidebar | comparison table |
| 14 | Semantic Search Engine | [session-14-semantic-engine](session-14-semantic-engine/) | Reusable class, metadata filter | `semantic_search.py` (→ S23) |
| 15 | Classification & Clustering | [session-15-clustering-classification](session-15-clustering-classification/) | k-means, hierarchical, NB | clustering notebook |
| 16 | Learning to Rank | [session-16-learning-to-rank](session-16-learning-to-rank/) | Pointwise/pairwise/listwise, LightGBM lambdarank | `ltr.py` + NDCG table |
| 17 | Web Search Architecture | [session-17-web-search-architecture](session-17-web-search-architecture/) | Frontier, robots, politeness, PageRank | `polite_crawler.py` skeleton |
| 18 | Crawling in Practice | [session-18-crawling-practice](session-18-crawling-practice/) | requests, BS4, pagination on mock shop | mock-shop scraper |
| 19 | Shop Crawl Workshop | [session-19-shop-crawl-workshop](session-19-shop-crawl-workshop/) | Retries, incremental, validation | `products.json` (≥100) or fallback |
| 20 | Near-Duplicates & Doc Graphs | [session-20-near-duplicates](session-20-near-duplicates/) | Shingling, MinHash, LSH, graphs | `dedup.py` + graph PNG |
| 21 | OpenSearch | [session-21-opensearch](session-21-opensearch/) | Shards, mappings, analyzers, BM25, bulk; BKD/FST sidebar | `index_products.py`, `queries.py` |
| 22 | Hybrid Search & Reranking | [session-22-hybrid-reranking](session-22-hybrid-reranking/) | BM25+kNN, RRF in Python, cross-encoder | results comparison table |
| 23 | End-to-End Build | [session-23-end-to-end-build](session-23-end-to-end-build/) | Orchestration, config, idempotent indexing | working pipeline demo |
| 24 | Integration Clinic | [session-24-integration-clinic](session-24-integration-clinic/) | Debugging, latency, hardening | capstone v1 + homework |
| 25 | Capstone Presentations | [session-25-capstone-presentations](session-25-capstone-presentations/) | Demos, rubric, RAG/LLM next steps | final repo + demo |

## Supporting material

- [Intro.html](Intro.html) — 30-slide course intro deck (start here)
- [SYLLABUS.md](SYLLABUS.md) — source of truth for session content
- [AGENTS.md](AGENTS.md) — generation contract (templates, image/code rules, validation)
- `setup/` — Session-0 prework (env check, model pre-cache, OpenSearch Docker, mock shop)
- `datasets/` — seeded corpus, qrels, fallback products (single source for all sessions)
- `tools/figstyle.py` — shared matplotlib style
