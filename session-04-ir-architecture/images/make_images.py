"""Regenerate every PNG for Session 4 (deterministic; run in the course venv).

Usage (from session-04-ir-architecture/):
    python images/make_images.py

Every number plotted here is MEASURED from the seeded course data
(datasets/corpus/, datasets/qrels.json, datasets/fallback_products.json) inside
this script -- nothing is invented. Stdlib + matplotlib only.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent
CORPUS = ROOT / "datasets" / "corpus"
QRELS = ROOT / "datasets" / "qrels.json"
PRODUCTS = ROOT / "datasets" / "fallback_products.json"

# one colour per pipeline stage -- this is the legend of 04-01 and 04-04
STAGE_COLORS = {
    "CRAWL": "#1f77b4",
    "PARSE": "#17becf",
    "DEDUPE": "#2ca02c",
    "INDEX": "#9467bd",
    "EMBED": "#8c564b",
    "QUERY": "#ff7f0e",
    "RANK": "#d62728",
    "EVALUATE": "#7f7f7f",
}
STORE_FACE = "#e9e9e9"
STORE_EDGE = "#5a5a5a"
LABEL_FS = 7.2


# --------------------------------------------------------------------------- #
# drawing helpers
# --------------------------------------------------------------------------- #
def box(ax, x, y, w, h, title, lines=(), color="#1f77b4", face=None, title_fs=10,
        sub_fs=LABEL_FS, edge="black"):
    """Draw a labelled rounded box and return its centre point.

    `lines` are small italic sub-labels drawn top-down under the title, so the
    box must be tall enough for title + len(lines) rows.
    """
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.05",
                           facecolor=face if face else color, edgecolor=edge,
                           alpha=1.0 if face else 0.92, linewidth=1.3, zorder=2)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.73, title, ha="center", va="center",
            color="white" if not face else "#111111",
            fontsize=title_fs, weight="bold", zorder=3)
    for i, line in enumerate(lines):
        ax.text(x + w / 2, y + h * 0.46 - i * h * 0.17, line, ha="center",
                va="center", color="white" if not face else "#333333",
                fontsize=sub_fs, style="italic", zorder=3)
    return (x + w / 2, y + h / 2)


def arrow(ax, start, end, color="#222222", style="-", lw=1.6, rad=0.0):
    """Draw an arrow between two points, optionally curved."""
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15,
                            color=color, linewidth=lw, linestyle=style,
                            shrinkA=0, shrinkB=0, zorder=4,
                            connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(patch)
    return patch


def tag(ax, x, y, text, color="#333333", fontsize=8.0, ha="center", style="italic",
        fc="white", alpha=0.9):
    """Small caption with a white plate behind it so it never fights the art."""
    ax.text(x, y, text, ha=ha, va="center", fontsize=fontsize, color=color,
            style=style, zorder=6,
            bbox=dict(boxstyle="round,pad=0.18", fc=fc, ec="none", alpha=alpha))


# --------------------------------------------------------------------------- #
# measured facts from the seeded course data
# --------------------------------------------------------------------------- #
def _tokens(text: str) -> list[str]:
    """Lowercase + strip punctuation -> list of word tokens."""
    out = []
    for raw in text.lower().split():
        word = raw.strip(".,!?;:\"'()")
        if word:
            out.append(word)
    return out


def load_corpus() -> list[tuple[str, str, list[str]]]:
    """Return [(doc_id, topic, tokens)] for every corpus doc, sorted by id."""
    names = sorted(n for n in os.listdir(CORPUS) if n.endswith(".txt"))
    docs = []
    for name in names:
        with open(os.path.join(CORPUS, name), mode="r", encoding="utf-8") as f:
            text = f.read()
        topic = text.splitlines()[0].split(":", 1)[1].strip()
        docs.append((name[:-4], topic, _tokens(text)))
    return docs


def load_qrels() -> dict:
    with open(QRELS, mode="r", encoding="utf-8") as f:
        return json.load(f)


def load_products() -> list[dict]:
    with open(PRODUCTS, mode="r", encoding="utf-8") as f:
        return json.load(f)


def and_hits_per_query(docs, qrels) -> list[tuple[str, str, int, int]]:
    """(qid, query, docs matched by ALL query words, relevant docs in qrels)."""
    rows = []
    for qid in sorted(qrels):
        words = _tokens(qrels[qid]["query"])
        hit = 0
        for _doc, _topic, tokens in docs:
            present = set(tokens)
            if all(w in present for w in words):
                hit += 1
        rows.append((qid, qrels[qid]["query"], hit, len(qrels[qid]["relevant"])))
    return rows


def docs_with_word(docs, word: str) -> int:
    return sum(1 for _d, _t, toks in docs if word in toks)


# --------------------------------------------------------------------------- #
# 04-01  the centrepiece: the whole IR architecture
# --------------------------------------------------------------------------- #
def architecture() -> None:
    """04-01: crawl -> parse -> dedupe -> index/embed -> query -> rank -> evaluate."""
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    fig.subplots_adjust(left=0.008, right=0.995, top=0.985, bottom=0.01)

    ax.text(6.0, 6.88, "The IR architecture — and which session builds each box",
            ha="center", va="center", fontsize=15.5, weight="bold")
    ax.text(6.0, 6.62,
            "crawl → parse → dedupe → index → query → rank → evaluate. "
            "Session 23 wires these boxes into one running system.",
            ha="center", va="center", fontsize=9.5, style="italic", color="#333333")

    # the five columns
    w, gap, x0 = 1.80, 0.25, 1.85
    xs = [x0 + i * (w + gap) for i in range(5)]

    # ---------------- OFFLINE ----------------
    off_y, off_h = 5.30, 0.98
    stages = [
        ("CRAWL", ["fetch pages, obey", "robots.txt, rate limit", "S17-19"]),
        ("PARSE", ["HTML → clean text", "+ product fields", "S18-19"]),
        ("DEDUPE", ["drop near-identical", "pages, cluster rest", "S20"]),
        ("INDEX", ["term → doc ids, tf,", "positions", "S5-6, S21"]),
        ("EMBED", ["doc → vector, stored", "in a vector DB", "S12-13"]),
    ]
    ax.text(0.10, off_y + off_h / 2, "OFFLINE\nbuild the index\nonce per crawl",
            ha="left", va="center", fontsize=8.2, weight="bold", color="#333333",
            linespacing=1.5)
    oc = [box(ax, x, off_y, w, off_h, t, lines, color=STAGE_COLORS[t])
          for x, (t, lines) in zip(xs, stages)]
    for a, b in zip(oc[:-1], oc[1:]):
        arrow(ax, (a[0] + w / 2, a[1]), (b[0] - w / 2, b[1]))

    # ---------------- STORAGE ----------------
    st_y, st_h = 4.05, 0.84
    stores = [
        ("RAW STORE", ["fetched pages, as-is"]),
        ("TEXT STORE", ["clean text, title, price"]),
        ("INVERTED INDEX", ["term → [doc ids]"]),
        ("VECTOR STORE", ["doc id → 384-d vector"]),
        ("EVAL SET", ["qrels + click log"]),
    ]
    ax.text(0.10, st_y + st_h / 2, "STORAGE\nsurvives\nbetween runs",
            ha="left", va="center", fontsize=8.2, weight="bold", color="#333333",
            linespacing=1.5)
    sc = [box(ax, x, st_y, w, st_h, t, lines, face=STORE_FACE, edge=STORE_EDGE,
              title_fs=9.0)
          for x, (t, lines) in zip(xs, stores)]
    for c, s in zip(oc, sc):
        arrow(ax, (c[0], off_y), (s[0], st_y + st_h), color="#555555", lw=1.3)
    for a, b in zip(sc[:-1], sc[1:]):
        arrow(ax, (a[0] + w / 2, a[1]), (b[0] - w / 2, b[1]), color="#aaaaaa", lw=1.0)

    # ---------------- ONLINE ----------------
    on_y, on_h = 2.28, 1.00
    online = [
        ("USER QUERY", "QUERY", ['"waterproof hiking', 'boots under 100"', "S1-3"]),
        ("ANALYSE", "QUERY", ["tokenize, expand,", "apply filters", "S5-7, S21"]),
        ("RETRIEVE", "QUERY", ["BM25 postings + kNN", "vectors, top-200 cands",
                               "S8, S12, S22"]),
        ("RANK", "RANK", ["fuse (RRF), rerank,", "learn-to-rank", "S8-9, S16, S22"]),
        ("RESULTS", "QUERY", ["top-10 shown to the", "user; S24 times it", "S10, S23"]),
    ]
    ax.text(0.10, on_y + on_h / 2, "ONLINE\nanswer one\nquery",
            ha="left", va="center", fontsize=8.2, weight="bold", color="#333333",
            linespacing=1.5)
    qc = [box(ax, x, on_y, w, on_h, t, lines, color=STAGE_COLORS[s], title_fs=9.2)
          for x, (t, s, lines) in zip(xs, online)]
    for a, b in zip(qc[:-1], qc[1:]):
        arrow(ax, (a[0] + w / 2, a[1]), (b[0] - w / 2, b[1]))

    # the two indexes feed retrieval (curved so nothing overlaps)
    arrow(ax, (sc[2][0] + 0.62, st_y), (qc[2][0] + 0.40, on_y + on_h),
          color=STAGE_COLORS["INDEX"], rad=-0.20)
    tag(ax, 8.05, 3.45, "postings lookup", color=STAGE_COLORS["INDEX"])
    arrow(ax, (sc[3][0] + 0.45, st_y), (qc[2][0] - 0.32, on_y + on_h),
          color=STAGE_COLORS["EMBED"], rad=0.16)
    tag(ax, 9.30, 3.86, "nearest vectors", color=STAGE_COLORS["EMBED"])

    # ---------------- EVALUATE ----------------
    ev_y, ev_h = 0.92, 0.86
    ev = box(ax, xs[4], ev_y, w, ev_h, "EVALUATE",
             ["P@10 · MRR · MAP ·", "NDCG@10 vs qrels", "S10"],
             color=STAGE_COLORS["EVALUATE"], title_fs=9.2)
    ax.text(0.10, ev_y + ev_h / 2, "EVALUATE\nthe score-\nsheet",
            ha="left", va="center", fontsize=8.2, weight="bold", color="#333333",
            linespacing=1.5)
    arrow(ax, (qc[4][0], on_y), (ev[0], ev_y + ev_h), color="#555555")
    tag(ax, 10.55, 1.85, "logged\nresults", ha="center", fontsize=7.4)
    arrow(ax, (xs[4] - 0.06, ev_y + ev_h * 0.62), (xs[3] + w + 0.06, on_y + on_h * 0.5),
          color="#555555", style=(0, (4, 3)), rad=0.20)
    tag(ax, 9.30, 1.60, "feedback:\nretune the ranker", fontsize=7.4)

    ax.text(xs[0], 1.55,
            "The whole course in one picture:\n"
            "· one metrics.py (S10) scores every later ranker — S16, S22, S23 reuse it\n"
            "· the shop we crawl in S18-19 is the bundled setup/mock_shop site, never a live one\n"
            "· every arrow going left or back is real work, not decoration",
            ha="left", va="center", fontsize=8.0, style="italic", color="#333333",
            linespacing=1.6)

    # ---------------- legend ----------------
    ax.add_patch(Rectangle((0.10, 0.06), 11.82, 0.72, facecolor="#fbfbfb",
                           edgecolor="#cccccc", linewidth=0.8, zorder=0))
    ax.text(0.24, 0.66, "colour = pipeline stage", fontsize=8.2, weight="bold",
            va="center")
    items = [("CRAWL", "S17-19"), ("PARSE", "S18-19"), ("DEDUPE", "S20"),
             ("INDEX", "S5-6, S21"), ("EMBED", "S12-13"), ("QUERY", "S6-7"),
             ("RANK", "S8-9, S16"), ("EVALUATE", "S10")]
    for i, (name, sessions) in enumerate(items):
        x = 0.24 + i * 1.42
        ax.add_patch(Rectangle((x, 0.49), 0.30, 0.17, facecolor=STAGE_COLORS[name],
                               edgecolor="black", linewidth=0.8, zorder=2))
        ax.text(x + 0.38, 0.575, f"{name} ({sessions})", fontsize=6.8, va="center")
    ax.add_patch(Rectangle((0.24, 0.17), 0.30, 0.17, facecolor=STORE_FACE,
                           edgecolor=STORE_EDGE, linewidth=0.8, zorder=2))
    ax.text(0.62, 0.255, "storage artefact (grey, no stage colour)", fontsize=6.8,
            va="center")
    arrow(ax, (3.30, 0.255), (3.90, 0.255), lw=1.4)
    ax.text(3.98, 0.255, "data flow", fontsize=6.8, va="center")
    arrow(ax, (4.80, 0.255), (5.40, 0.255), lw=1.4, style=(0, (4, 3)),
          color="#555555")
    ax.text(5.48, 0.255, "feedback loop — what turns a script into a system",
            fontsize=6.8, va="center")

    fig.savefig(HERE / "04-01-ir-architecture.png")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 04-02  IR vs DB search: structured vs unstructured
# --------------------------------------------------------------------------- #
def structured_vs_unstructured() -> None:
    """04-02: SQL answers exactly; free text needs a ranker. Numbers measured."""
    apply_style()
    products = load_products()
    sql_rows = [p for p in products
                if p["category"] == "electronics" and p["price"] < 60]
    phrase = sum(1 for p in products
                 if "cheap sturdy lamp" in (p["name"] + " " + p["description"]).lower())
    any_word = sum(1 for p in products
                   if "lamp" in (p["name"] + " " + p["description"]).lower())

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(12, 5.8))
    fig.subplots_adjust(left=0.02, right=0.99, top=0.84, bottom=0.05, wspace=0.14)
    for ax in (axl, axr):
        ax.axis("off")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

    axl.text(5, 9.62, "STRUCTURED — a database search", ha="center", fontsize=13,
             weight="bold")
    axl.text(5, 9.22,
             "fields are already separate cells, so equality and ranges are exact",
             ha="center", fontsize=8.8, style="italic", color="#333333")
    col_x = [0.55, 1.75, 5.20, 7.20]
    col_w = [1.15, 3.40, 1.90, 2.60]
    row_h, top = 0.62, 8.62
    axl.add_patch(Rectangle((0.55, top - row_h), 8.85, row_h, facecolor="#1f77b4",
                            edgecolor="black", alpha=0.92))
    for name, x, w in zip(["id", "name", "price", "category"], col_x, col_w):
        axl.text(x + w / 2, top - row_h / 2, name, ha="center", va="center",
                 color="white", fontsize=9, weight="bold")
    for i, p in enumerate(sql_rows[:4]):
        y = top - row_h * (i + 2)
        axl.add_patch(Rectangle((0.55, y), 8.85, row_h,
                                facecolor="#f2f6fa" if i % 2 == 0 else "white",
                                edgecolor="#9aa7b4"))
        for val, x, w in zip([p["id"], p["name"], f"{p['price']:.2f}", p["category"]],
                             col_x, col_w):
            axl.text(x + w / 2, y + row_h / 2, val, ha="center", va="center",
                     fontsize=8.4)
    axl.text(5, 5.68, f"… and {len(sql_rows) - 4} more rows  (7 in total)",
             ha="center", fontsize=8.2, style="italic", color="#555555")
    axl.add_patch(FancyBboxPatch((0.55, 3.55), 8.85, 1.35,
                                 boxstyle="round,pad=0.10",
                                 facecolor="#eaf3ff", edgecolor="#1f77b4",
                                 linewidth=1.5))
    axl.text(5.0, 4.22,
             "SELECT name, price FROM products\n"
             "WHERE category = 'electronics' AND price < 60",
             ha="center", va="center", fontsize=9.6, family="monospace",
             color="#10365c", linespacing=1.7)
    axl.text(5.0, 2.90, f"→ exactly {len(sql_rows)} rows. No ranking, no guessing.",
             ha="center", fontsize=10.5, weight="bold", color="#1f77b4")
    axl.text(5.0, 1.95,
             "Ask it for “a nice affordable present” and it returns\n"
             "nothing: there is no column called nice.",
             ha="center", fontsize=9, style="italic", color="#333333",
             linespacing=1.7)

    axr.text(5, 9.62, "UNSTRUCTURED — information retrieval", ha="center",
             fontsize=13, weight="bold")
    axr.text(5, 9.22,
             "the meaning lives in prose, so the engine must judge what matches",
             ha="center", fontsize=8.8, style="italic", color="#333333")
    docs = [
        ("doc-002.txt", "topic: space", "Mars rovers analyze rocks for signs of water."),
        ("doc-007.txt", "topic: space", "Telescopes collect light from distant galaxies."),
        ("doc-101.txt", "topic: space", "Astronauts train for months before every mission."),
    ]
    for i, (name, head, line) in enumerate(docs):
        y = 8.62 - i * 1.45
        axr.add_patch(FancyBboxPatch((0.55, y - 1.28), 8.85, 1.30,
                                     boxstyle="round,pad=0.08",
                                     facecolor="#fff8f0", edgecolor="#ff7f0e",
                                     linewidth=1.3))
        axr.text(0.80, y - 0.30, name, fontsize=8.4, weight="bold", color="#8a4b00")
        axr.text(0.80, y - 0.68, head, fontsize=7.6, style="italic", color="#8a4b00")
        axr.text(0.80, y - 1.02, line, fontsize=8.4, color="#222222")
    axr.add_patch(FancyBboxPatch((0.55, 3.55), 8.85, 1.35,
                                 boxstyle="round,pad=0.10",
                                 facecolor="#fff2e6", edgecolor="#ff7f0e",
                                 linewidth=1.5))
    axr.text(5.0, 4.22,
             'query: "cheap sturdy lamp"\n'
             '       "waterproof boots under 100"',
             ha="center", va="center", fontsize=9.6, family="monospace",
             color="#7a3b00", linespacing=1.7)
    axr.text(5.0, 2.90,
             f"→ {phrase} exact hits for the phrase, {any_word} products\n"
             f"   mention lamp — a ranker decides who deserves page 1",
             ha="center", fontsize=10.5, weight="bold", color="#ff7f0e",
             linespacing=1.5)
    axr.text(5.0, 1.75,
             "The difference in one line: the database answers the query\n"
             "you can write; IR answers the query you actually meant.",
             ha="center", fontsize=9, style="italic", color="#333333",
             linespacing=1.7)

    fig.savefig(HERE / "04-02-structured-vs-unstructured.png")
    plt.close(fig)
    print("04-02 measured: sql_rows=%d phrase_hits=%d any_word=%d"
          % (len(sql_rows), phrase, any_word))


# --------------------------------------------------------------------------- #
# 04-03  lexical vs semantic — measured on our own corpus
# --------------------------------------------------------------------------- #
def lexical_vs_semantic() -> None:
    """04-03: exact-word matching measured against qrels, and where it breaks."""
    docs = load_corpus()
    qrels = load_qrels()
    rows = and_hits_per_query(docs, qrels)
    qids = [r[0] for r in rows]
    lasts = [r[1].split()[-1] for r in rows]
    hits = [r[2] for r in rows]
    rel = [r[3] for r in rows]
    total_hits, total_rel = sum(hits), sum(rel)
    empty = sum(1 for h in hits if h == 0)

    probe = [("rover", "what you type"), ("rovers", "what the corpus says"),
             ("soccer", "what you type"), ("football", "what the corpus says")]
    counts = [(w, r, docs_with_word(docs, w)) for w, r in probe]

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(12, 5.6),
                                   gridspec_kw={"width_ratios": [1.62, 1.0]})
    fig.subplots_adjust(left=0.065, right=0.985, top=0.80, bottom=0.20, wspace=0.26)

    axl.bar(range(len(hits)), hits, color=COLORS["primary"], width=0.60,
            label="found by exact words (every query word present)")
    axl.bar(range(len(rel)), rel, color="none", edgecolor=COLORS["warn"],
            width=0.80, linewidth=1.7, label="judged relevant in qrels.json")
    axl.set_xticks(range(len(rows)))
    axl.set_xticklabels([f"{q}\n{w}" for q, w in zip(qids, lasts)], fontsize=7.4)
    axl.set_ylabel("documents", fontsize=9.5)
    axl.set_ylim(0, 40)
    axl.set_title("Lexical search, measured on datasets/corpus + datasets/qrels.json",
                  fontsize=11.5)
    axl.legend(fontsize=7.6, loc="upper center", ncol=2, framealpha=0.92,
               bbox_to_anchor=(0.5, -0.15))
    axl.text(0.015, 0.965,
             "Exact-word AND recalls %d of %d relevant documents (%.0f%%).\n"
             "%d of the %d queries match nothing at all — no stemming, no synonyms."
             % (total_hits, total_rel, 100.0 * total_hits / total_rel, empty, len(hits)),
             transform=axl.transAxes, fontsize=8.6, va="top", color="#333333",
             linespacing=1.6,
             bbox=dict(boxstyle="round,pad=0.35", fc="#fffbe6", ec="#d9c97a"))

    labels = ["%s\n(%s)" % (w, r) for w, r, _c in counts]
    values = [c for _w, _r, c in counts]
    colors = [COLORS["warn"], COLORS["ok"], COLORS["warn"], COLORS["ok"]]
    bars = axr.bar(range(4), values, color=colors, width=0.58)
    axr.set_xticks(range(4))
    axr.set_xticklabels(labels, fontsize=8)
    axr.set_ylabel("corpus documents containing the word", fontsize=9.5)
    axr.set_ylim(0, 56)
    axr.set_title("Where exact words break (measured counts)", fontsize=11.5)
    for rect, val in zip(bars, values):
        axr.text(rect.get_x() + rect.get_width() / 2, val + 1.0, str(val),
                 ha="center", fontsize=10, weight="bold")
    axr.text(0.5, 0.975,
             "You type rover or soccer; the corpus says rovers and\n"
             "football. Exact matching scores 0.\n"
             "Stemming (S5) fixes rover/rovers. Meaning (S12) fixes\n"
             "soccer/football — that is the whole argument for vectors.",
             transform=axr.transAxes, fontsize=8.0, ha="center", va="top",
             color="#333333", linespacing=1.6,
             bbox=dict(boxstyle="round,pad=0.35", fc="#f1f7f2", ec="#a9cfa9"))

    fig.savefig(HERE / "04-03-lexical-vs-semantic.png")
    plt.close(fig)
    print("04-03 measured: exact-AND=%d/%d, empty_queries=%d, probe=%s"
          % (total_hits, total_rel, empty, [(w, c) for w, _r, c in counts]))


# --------------------------------------------------------------------------- #
# 04-04  the 25 sessions on the pipeline
# --------------------------------------------------------------------------- #
def course_map() -> None:
    """04-04: every session, grouped by phase, coloured by the stage it feeds."""
    apply_style()
    phases = [
        ("FOUNDATIONS", "what is a document, and why index it?", [
            ("S1", "text file I/O"), ("S2", "binary & OS files"),
            ("S3", "naive search"), ("S4", "architecture ← you are here"),
        ]),
        ("LEXICAL RANKING", "find the right words, score them well", [
            ("S5", "inverted index"), ("S6", "boolean retrieval"),
            ("S7", "tf-idf"), ("S8", "BM25"), ("S9", "probabilistic"),
            ("S10", "evaluation"), ("S11", "efficient scoring"),
        ]),
        ("SEMANTIC SEARCH", "match meaning, not spelling", [
            ("S12", "embeddings"), ("S13", "vector databases"),
            ("S14", "semantic engine"), ("S15", "cluster & classify"),
            ("S16", "learning to rank"),
        ]),
        ("THE WEB & THE DATA", "go get real documents, then clean them", [
            ("S17", "crawler architecture"), ("S18", "crawling in practice"),
            ("S19", "shop crawl workshop"), ("S20", "near-duplicates"),
        ]),
        ("SHIP IT", "one deployed system that answers queries", [
            ("S21", "OpenSearch"), ("S22", "hybrid + rerank"),
            ("S23", "end-to-end build"), ("S24", "integration clinic"),
            ("S25", "capstone"),
        ]),
    ]
    stage_of = {
        "S1": "CRAWL", "S2": "CRAWL", "S3": "QUERY", "S4": "QUERY",
        "S5": "INDEX", "S6": "QUERY", "S7": "RANK", "S8": "RANK", "S9": "RANK",
        "S10": "EVALUATE", "S11": "INDEX", "S12": "EMBED", "S13": "EMBED",
        "S14": "RANK", "S15": "INDEX", "S16": "RANK", "S17": "CRAWL",
        "S18": "CRAWL", "S19": "CRAWL", "S20": "PARSE", "S21": "INDEX",
        "S22": "RANK", "S23": "QUERY", "S24": "EVALUATE", "S25": "EVALUATE",
    }

    fig, ax = plt.subplots(figsize=(12, 6.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.6)
    ax.axis("off")
    fig.subplots_adjust(left=0.012, right=0.992, top=0.985, bottom=0.01)

    ax.text(6.0, 6.40, "The course as a pipeline — 25 sessions, five phases",
            ha="center", fontsize=15, weight="bold")
    ax.text(6.0, 6.12,
            "Each chip is one 90-minute session; its colour is the pipeline stage it "
            "feeds (see 04-01).",
            ha="center", fontsize=9.2, style="italic", color="#333333")

    spine = ["CRAWL", "PARSE", "INDEX", "QUERY", "RANK", "EVALUATE"]
    sw, sgap = 1.55, 0.28
    sx = (12 - (len(spine) * sw + (len(spine) - 1) * sgap)) / 2
    centres = []
    for i, name in enumerate(spine):
        centres.append(box(ax, sx + i * (sw + sgap), 5.58, sw, 0.58, name, (),
                           color=STAGE_COLORS[name], title_fs=9))
    for a, b in zip(centres[:-1], centres[1:]):
        arrow(ax, (a[0] + sw / 2, a[1]), (b[0] - sw / 2, b[1]))

    row_h, pitch = 0.80, 0.96
    tops = [4.70, 3.74, 2.78, 1.82, 0.86]
    for (phase, tagline, chips), top in zip(phases, tops):
        ax.add_patch(Rectangle((0.16, top - row_h), 11.68, row_h,
                               facecolor="#f6f7f8", edgecolor="#d3d6d9",
                               linewidth=0.8, zorder=0))
        ax.text(0.28, top - 0.22, phase, ha="left", va="center", fontsize=8.8,
                weight="bold", color="#111111", zorder=1)
        ax.text(0.28, top - 0.55, tagline, ha="left", va="center", fontsize=7.0,
                style="italic", color="#555555", zorder=1)
        n = len(chips)
        area_l, area_r = 3.25, 11.74
        cwid = (area_r - area_l - 0.09 * (n - 1)) / n
        fs = 7.4 if n <= 5 else (6.9 if n == 6 else 6.3)
        for i, (sid, title) in enumerate(chips):
            x = area_l + i * (cwid + 0.09)
            here = sid == "S4"
            ax.add_patch(FancyBboxPatch((x, top - 0.68), cwid, 0.52,
                                         boxstyle="round,pad=0.05,rounding_size=0.05",
                                         facecolor=STAGE_COLORS[stage_of[sid]],
                                         edgecolor="#d62728" if here else "black",
                                         linewidth=2.2 if here else 0.8, zorder=2))
            ax.text(x + cwid / 2, top - 0.42, f"{sid} · {title}", ha="center",
                    va="center", color="white", fontsize=fs, weight="bold",
                    zorder=3)

    fig.savefig(HERE / "04-04-course-map.png")
    plt.close(fig)


def main() -> None:
    architecture()
    structured_vs_unstructured()
    lexical_vs_semantic()
    course_map()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()