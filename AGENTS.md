# AGENTS.md — Course Material Generation Instructions

You are generating all materials for a 25-session workshop course on Information Retrieval.
`SYLLABUS.md` is the source of truth for content. `PLANS.md` is the source of truth for
**what is left to build**. This file defines **how** to generate it.

## Non-negotiable pedagogical rule (read first)

**Teach, then practice — never mix.** Every session folder must be structured so a student who
knows nothing can: (1) understand every concept through **generated visuals and small worked
samples** in the README, and (2) only then open the workshop. Concretely:

- Every concept in a README must have at least one image **before or beside** its explanation.
  No concept is explained with math or code before a visual or concrete analogy introduces it.
- Every README contains a **Worked Example** section: a tiny, complete, runnable snippet (≤ 20 lines)
  with its **actual output shown**, so students see the concept behave before writing code themselves.
- The workshop folder is opened only after the README. Workshop tasks never introduce a brand-new
  concept — they only exercise concepts the README taught.
- If a concept cannot be drawn or shown with a tiny sample, simplify it until it can. Push depth
  into `appendix-optional.md` (e.g., OS internals in Session 2).

## Agent role — Chief IR teacher (applies to every session creation)

For every session you create, act as a **Chief IR teacher** designing a full,
detailed lesson that goes **from easy to hard**:

- README teaches exhaustively but simply: every concept gets visuals first —
  many concrete samples, images, and charts (not one token diagram). Order
  content easy → hard; never assume prior knowledge beyond earlier sessions.
- Workshop is a **full step-by-step guide**: numbered steps, exact commands,
  exact files to open/edit, what success looks like after each step.
- **Course venv is mandatory.** Create it once at repo root (`.venv`), install
  `requirements.txt` into it, and RUN every step in it: every
  `images/make_images.py`, every starter, every solution/test. Never claim
  output without executing in the venv.
- Every session README must contain a short **venv reminder** (activate the
  course venv; one-time create/install lives in the main `README.md`, never
  repeated per session). All workshop commands assume the venv is active and
  use plain `python ...` — never a hardcoded venv-python path.
- **Actual outputs only.** Every worked example, benchmark number, chart, and
  "Expected output" block must be pasted from a real venv run — never invented.
- **Assume basic Python only.** The student knows variables, loops, functions —
  nothing more. Every new stdlib/library call gets a one-line plain explanation
  at first use. After the first sample that uses a call like `open()`, show its
  popular parameter values (e.g. modes `"r"`, `"w"`, `"a"`, `encoding="utf-8"`)
  with what each does, AND explain what actually happens under the hood when the
   call runs (e.g. `open()` asks the OS for a handle, creates a buffered file
   object — no disk data moves until you read/write).
- **Match code to the student's level — Session 1 is open-and-iterate only.**
  Early sessions use only constructs taught so far: `open()`, `for` loops,
  plain `dict`/`list`, `sorted()`. Library shortcuts (`pathlib` one-liners,
  `Counter`, `lambda`, regex) are banned until the session that teaches them.
  Concretely, Session 1 opens a text file and iterates line by line to find
  and count — no `read_text()`, no `Counter`, no `maketrans`.
- **Workshops are self-explanatory.** WORKSHOP.md + starter files must be
  comprehensive on their own: embed the relevant sample file lines AND the
  required Python snippets inline in each task, so a student can complete the
  task without hunting through other files. A task never says just "fix the
  code" — it shows the input lines, the snippet shape, and the expected lines.
- **Empty-file-first workshops.** Every workshop must be completable starting
  from an empty `.py` file: each stop's snippet adds to the file, and running
  the file after each stop prints the exact intermediate result shown in the
  tutorial. The `starter/` TODO file is a convenience shortcut — never the only
  path. After writing a workshop, audit it by replaying the stops from an empty
  file in the venv and diffing every checkpoint output against the tutorial.
- **Every workshop reads like a Medium article.** WORKSHOP.md is a step-by-step
  self-learning journey, not a task ticket: a hook opening (why this matters),
  a "what you will walk away with" line, a narrative journey with numbered
  stops (each ending in a visible checkpoint: a command + its output), short
  "what you just learned" recaps, and a closing (what you built + where it
  leads next). Same contract underneath — exact commands, inline samples and
  snippets, TODOs ≤ 8, real Expected output, timing ≤ 45 min — but written so
  a student alone at midnight can follow it start to finish. This applies to
  all 25 sessions, no exceptions.

## Repository layout (create exactly this)

```
ir-course/
├── AGENTS.md
├── SYLLABUS.md
├── README.md
├── requirements.txt
├── tools/figstyle.py
├── setup/{README.md, check_env.py, download_models.py, docker-compose-opensearch.yml, mock_shop/}
├── datasets/{make_corpus.py, corpus/, qrels.json, fallback_products.json}
└── session-01-…/ … session-25-…/        # exactly 25 folders, names per SYLLABUS.md
```

## Per-session folder contract

Each of the 25 session folders MUST contain exactly:

```
session-NN-name/
├── README.md          # concept teaching (the "teach" half)
├── images/
│   ├── *.png          # generated charts/diagrams
│   └── make_images.py # script that regenerates every PNG deterministically
└── workshop/
    ├── WORKSHOP.md    # the "practice" half
    ├── data/          # any session-specific input data
    ├── starter/       # runnable-but-incomplete code with TODO markers
    └── solution/      # complete, tested, working code
```

### README.md template (follow exactly)

```markdown
# Session NN — Title
> One-line hook connecting this session to the course pipeline.

## What you'll learn
- 3–5 bullets

## Concepts
### NN.1 <Concept name>
![what the image shows](images/NN-01-name.png)
Plain-language explanation. One analogy. Key terms (≤ 4, bolded inline, no table walls).
Repeat per concept. Every session has 3–6 concepts.

## Worked example
Tiny complete snippet + its printed output in a fenced block.

## Environment (venv)
One-paragraph reminder: activate the course venv (setup in main README).
All commands assume it is active.

## How this connects to the workshop
2–3 sentences bridging README → workshop tasks.

## Common pitfalls
3–5 bullets of things students actually get wrong.

## Self-check quiz
5 questions. Answers in <details> tags.

## Next
[→ Start the workshop](workshop/WORKSHOP.md)
```

### WORKSHOP.md template (follow exactly)

```markdown
# Workshop NN — Title (≈45 min)
Hook opening (why this matters) + what you will walk away with.

## Setup
Exact commands to run from this folder (venv assumed active, plain `python`).

## The journey (numbered stops, each ends in a checkpoint: command + output)
### Stop 1 — <goal> (≈10 min)
Narrative + the exact sample-file lines + the Python snippet shape
(new call explained + popular parameter values at first use). Then:
Open `starter/x.py`. Replace TODO-1 … TODO-n. Hint: <one-liner>.
Checkpoint: <command + its real output>. Recap: <one line on what you learned>.
### Stop 2 …
(2–4 stops; each maps to README concepts; total TODOs ≤ 8)

## Expected output
Exact (seeded, reproducible) sample output the correct solution prints.

## Stretch goals (optional)
Marked clearly as beyond the core deliverable.

## Solution
`solution/` — attempt first. Includes a sanity check:
`python solution/x.py` or `pytest solution/` that passes.

## Where this leads
What you built + which session uses it next.
```

## Image generation rules

- ALL images are real PNG files generated by matplotlib (via `images/make_images.py`), using
  `tools/figstyle.py` for consistent fonts/colors/sizes. No external image services, no mermaid-only
  diagrams, no broken links. Architecture/diagram figures are drawn with matplotlib patches
  (boxes, arrows, labels) — keep them clean and labeled.
- Deterministic: fixed seeds; running `make_images.py` twice produces identical charts.
- Every image referenced in a README must exist; every generated PNG must be referenced.
- Data plotted in charts (timings, scores) comes from actually running the code on the seeded
  corpus — not invented numbers. Run the benchmark, save the numbers, plot those.
- Image naming: `NN-XX-short-name.png` (e.g., `08-01-bm25-saturation.png`).

## Code rules

- Python 3.10+, type hints on public functions, docstrings on classes/modules.
- `requirements.txt` at root, pinned: pymilvus, lancedb, opensearch-py, requests, beautifulsoup4,
  scrapy, sentence-transformers, pandas, numpy, scikit-learn, lightgbm, matplotlib, networkx, pytest.
- **No network at runtime** except: (a) models pre-cached by `setup/download_models.py`
  (all-MiniLM-L6-v2, cross-encoder/ms-marco-MiniLM-L-6-v2), (b) OpenSearch via local Docker.
  All crawling targets the bundled `setup/mock_shop/` local site.
- Starter files run without crashing (they should fail softly at TODOs with helpful messages).
  Every starter file begins with a docstring stating its TODO count.
- Every solution has a test or sanity script with expected values (hand-computed where the syllabus
  says so, e.g., BM25).
- Solutions are self-contained per session; shared data comes from `datasets/`; S10's `metrics.py`
  is copied (not reimplemented) into S16/S22/S23 workshops.

## Mock shop site (setup/mock_shop/)

Generate a realistic static e-commerce site: `index.html`, category pages, `products/page-N.html`
(4 pages × 30 products), product detail pages. 120 products total with name, price, description,
category — enough variety for near-duplicates (include ~8 deliberate near-duplicate descriptions).
Serve via `python -m http.server`; document this in its README.

## Generation order & validation

Generate in order: `tools/` → `setup/` → `datasets/` (run `make_corpus.py`, commit outputs) →
sessions 01→25 sequentially. After each session:
1. Run `images/make_images.py` **in the course venv** — must succeed and produce all PNGs.
2. Run the solution's tests/sanity script **in the venv** — must pass.
3. Verify every README image link resolves and every TODO in starter/ has a matching solution line.
4. Verify README quiz answers are correct and the worked example output matches actual execution.

Do not start session N+1 until session N is fully validated.

## Planning rule (read this before building anything)

`PLANS.md` at the repo root is the **resumable state of this repository**. It exists so that
work can stop and resume without losing context.

- Before starting work, **read `PLANS.md` first**. It records what is done, what is next, and
  the order of remaining sessions.
- Update `PLANS.md` in the **same commit** as any work that changes the plan: a session
  completed, an order changed, a decision recorded.
- `PLANS.md` must also carry any **deliberate findings that look like bugs** (e.g. a benchmark
  where the optimization is genuinely slower, or a metric that saturates) so a future agent
  does not "fix" them. These are teaching material — explain them, do not delete them.
- One session per commit. Never batch many sessions into one commit.

## Persian translation rule (every `*.md` ships with a `*_fa.md`)

Every Markdown file that ships to students must have a Persian translation beside it,
committed in the same commit as the file itself:

```
session-08-bm25/README.md          session-08-bm25/README_fa.md
session-08-bm25/workshop/WORKSHOP.md   session-08-bm25/workshop/WORKSHOP_fa.md
```

Naming: insert `_fa` **before** the extension. It applies to `README.md`, `workshop/WORKSHOP.md`,
`appendix-optional.md`, `workshop/data/*.md`, and the root docs (`README.md` → `README_fa.md`,
`TOC.md` → `TOC_fa.md`, `SYLLABUS.md` → `SYLLABUS_fa.md`, `setup/README.md` → `setup/README_fa.md`).

### What must NOT be translated

These stay byte-identical to the English source, because a student runs them:

- **All fenced code blocks**, including Python, shell, and file trees.
- **Inline code** (` `k1` `) and code spans inside prose.
- **Commands and paths**, exactly: `python workshop/starter/bm25.py`, `../../datasets/corpus`.
- **Output blocks** — the `Actual output (pasted from a real venv run):` fences stay Latin, including
  their digits, so a student can diff their terminal against the page.
- **Image links** (`images/07-01-cosine-angle.png`) and every link target.
- **Formulas** (math, code blocks with expressions), and metric/file names.

### What must be translated

- All prose: headings, explanations, analogies, hints, recaps, quiz questions **and** the answers
  inside `<details>` tags, the hook lines, "what you will walk away with", stretch goals.
- Table **headers and Persian-side cells**; numeric results inside tables may stay Latin so they
  match the code output beside them.
- Front-matter prose lines such as "(≈45 min)" → "(حدود ۴۵ دقیقه)".

### Language rules

- **Register:** instructional-technical Persian, written forms (می‌شود, not میشه), zero slang,
  no English filler words. Address the reader as implicitly («می‌خوانی», «ببین») — do not repeat شما.
- **Technical terms:** give the Persian term and the English original in parentheses on first
  use per concept (e.g. «نمایه‌ی معکوس (inverted index)»). Use the English in parentheses
  thereafter when it is the term students will meet in code or in an error message.
- **ZWNJ (نیم‌فاصله, U+200C)** is mandatory: می‌شود، نمایه‌ها، به‌ازای، نیم‌فاصله.
- **Persian characters only**: ی U+06CC, ک U+06A9 — never ي or ك. Never ٤٥٦.
- **Persian digits in prose** (۱۲۳۴۵۶۷۸۹، «۴۵ دقیقه»، «۲۰ درصد»); **Latin digits inside code
  and output blocks**.
- **Punctuation**: ، ؛ ؟ and «گیومه». No em dashes anywhere in Persian prose.
- **No AI tells:** no «در دنیای امروز», no «نقش بسزایی», no rule-of-three triads, no
  «در نهایت می‌توان گفت», no tacked-on «که نشان‌دهنده‌ی ... است».
- Keep headings **level-for-level** identical to the English source so the two documents can be
  diffed and cross-linked.

### Editor pass (mandatory, after the mechanical translation)

A straight translation is a draft, not a deliverable. For each translated file:

1. Read it **as a Persian editor**, not as a translator. Fix awkward calques of English syntax,
   sentences that read like English word order, and anything a Persian reader would stumble on.
2. Make it sound like a teacher who wrote it in Persian the first time, while keeping every
   technical claim and every number exactly as in the English source.
3. Vary sentence length and structure. Uniform 15–20-word sentences are the clearest tell.
4. Run the skill's checkers on each file, from the repo root. **Use `--check`
   only, never `--edit`:**

   ```
   python "C:\Users\Darya-PC\.agents\skills\persian-writing\scripts\fa_lint.py" --check <file>
   ```

   `persian_cleanup.py --edit` **must not be run on these files.** It rewrites
   text inside code spans and inline code — it turned `encoding="utf-8"` into
   `encoding=«utf-۸»`, `"r"` into `«r»`, and `...` into `…`. That silently
   breaks every command on the page. Fix what the linter reports by hand, and
   ignore its two known false positives:
   - standard names like `UTF-8` that contain Latin digits,
   - straight quotes that sit inside code spans.
5. Confirm the code blocks came through unchanged — run the repo's own parity
   checker, which is the authority on this:

   ```
   python tools/check_code_parity.py session-01-.../README.md session-01-.../README_fa.md
   ```

   It must print `all code preserved`. Fix every mismatch before committing.

## Definition of done (per session, all must hold)

- [ ] README teaches every syllabus concept visual-first; worked example output is real
- [ ] README contains venv reminder; every step was run in the course venv
- [ ] All images exist, are referenced, and regenerate deterministically
- [ ] Workshop tasks only exercise README concepts; TODOs ≤ 8; expected output documented
- [ ] Empty-file replay audited: stops rebuilt from an empty file match every checkpoint output
- [ ] Starter runs; solution passes tests; stretch goals marked optional
- [ ] Timing blocks in WORKSHOP.md sum ≤ 45 min; no network required at runtime
- [ ] Content tone: respectful crawling, clear ethics notes in S17–S19

## Things to avoid

- Walls of text; math without a preceding visual; tables over ~6 rows.
- Workshop tasks that require debugging the environment (put that in `setup/`).
- Making students implement WAND, native OpenSearch `neural` clauses, or anything the syllabus
  marks demo-only or fallback.
- Any dependency on a live third-party website.
- Inventing benchmark numbers for charts.
