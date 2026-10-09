# Session 0 — Setup & Prework Checklist

Do this **once**, before Session 1. It takes about 15 minutes (plus model
downloads). After it, every session runs offline with no extra setup.

```
python --version          # need 3.10 or newer
```

---

## 1. Create the course virtual environment

A **venv** is a private folder holding this course's libraries, so your system
Python stays clean. One command, run from the repo root:

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Activate it **every time** you open a terminal to study:

```powershell
.\.venv\Scripts\Activate.ps1     # Windows
source .venv/bin/activate        # macOS / Linux
```

> PowerShell may block activation with an "execution policy" error. Fix it once:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

## 2. Install the libraries

`torch` is the slow one (~200 MB), so install it first from the CPU-only index,
then the rest:

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

## 3. Cache the two models (one download, then offline forever)

```bash
python setup/download_models.py
```

Downloads `all-MiniLM-L6-v2` (bi-encoder, Sessions 12-14 and 22) and
`cross-encoder/ms-marco-MiniLM-L-6-v2` (Session 22) into your local cache.

## 4. Generate the course data

Already committed, but regenerate any time to prove it is deterministic:

```bash
python datasets/make_corpus.py           # 204 docs, 10 queries, 128 products
python setup/mock_shop/build_shop.py     # the static shop Sessions 18-19 crawl
```

## 5. Verify everything

```bash
python setup/check_env.py
```

Prints `PASS`/`FAIL` per item and exits 0 only if every **required** check
passes. Run it again before Session 21 — OpenSearch is a hard prerequisite there.

---

## The mock shop (Sessions 18-19)

The bundled static site lives in `setup/mock_shop/`. Serve it on localhost:

```bash
python -m http.server 8000 --directory setup/mock_shop
```

Then open <http://localhost:8000/index.html>. It has:

| Path | What |
|---|---|
| `index.html` | landing page, 12 product cards |
| `products/page-1.html` … `page-4.html` | 4 listing pages, 32 products each |
| `category/<name>.html` | 4 category pages (books, electronics, kitchen, sports) |
| `product/<id>.html` | 128 product detail pages |
| `robots.txt` | the crawl policy Session 17's crawler obeys |
| `sitemap.xml` | all 138 URLs, handy for testing a crawler frontier |

The products are generated from `datasets/fallback_products.json`, so a local
crawl and the offline fallback dataset hold **identical values** — Sessions
20-23 behave the same either way. Eight products are deliberate near-duplicates
(Session 20 finds them).

## The search server (Sessions 21-23)

Session 21 needs a search engine over HTTP. Two options — try them in this order.

### Option A — the bundled server (no Docker, always works)

```bash
python setup/search_server.py            # listens on http://localhost:9200
```

It speaks the subset of the OpenSearch REST API this course uses, with real
inverted-index BM25 scoring behind it, so `opensearch-py` connects to it
unchanged. Verify the client agrees with it:

```bash
python setup/test_search_server.py       # 14/14 passed
```

### Option B — real OpenSearch via Docker

```bash
docker compose -f setup/docker-compose-opensearch.yml up -d opensearch
```

Check it is healthy before Session 21 (`docker ps` should show `healthy`).
OpenSearch Dashboards is optional and only needed for a visual UI.

**If Docker Hub rate-limits the pull** (`403 Forbidden`), point the compose file
at a mirror without editing it:

```bash
# Windows PowerShell
$env:OS_IMAGE_PREFIX="docker.devneeds.ir/"
docker compose -f setup/docker-compose-opensearch.yml up -d opensearch
```

```bash
# macOS / Linux
OS_IMAGE_PREFIX=docker.devneeds.ir/ docker compose -f setup/docker-compose-opensearch.yml up -d opensearch
```

Sessions 21-23 detect which server is live on their own, so both paths work.

## Offline mode

After step 3 nothing in the course needs the network. To prove it:

```bash
# Windows PowerShell
$env:HF_HUB_OFFLINE="1"
# macOS / Linux
export HF_HUB_OFFLINE=1
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: matplotlib` | venv not active — run the Activate line again |
| `PowerShell ... execution policy` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| torch install very slow | it is ~200 MB; use the CPU wheel index in step 2 |
| model download fails | re-run `python setup/download_models.py` when online |
| `Address already in use` on :8000 / :9200 | another server is running: `docker ps`, or change the port |
| Docker `403 Forbidden` on pull | set `OS_IMAGE_PREFIX` as shown in Option B |
| OpenSearch container restarts | add `- Xms2g -Xmx2g` to `OPENSEARCH_JAVA_OPTS` and restart |

## Where to go next

Ready? Start with [Session 01](../session-01-text-file-io/README.md).
