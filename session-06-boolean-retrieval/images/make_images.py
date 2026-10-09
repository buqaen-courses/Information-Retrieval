"""Regenerate every PNG for Session 6 (deterministic; run in course venv).

Usage:
    python images/make_images.py        # from session-06-boolean-retrieval/

Every doc id, list length and cost number plotted here is read from the real
datasets/corpus/ at run time — nothing is invented.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.figstyle import COLORS, apply_style  # noqa: E402

HERE = Path(__file__).resolve().parent
CORPUS = ROOT / "datasets" / "corpus"
PUNCT = ".,!?;:'\"()"


def _box(ax, xy, w, h, text, sub="", color=None, fc=None, tc="white", fs=10):
    box = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02",
                         facecolor=fc if fc else (color or COLORS["primary"]),
                         edgecolor="black", alpha=0.9, linewidth=1.0)
    ax.add_patch(box)
    if text:
        ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center",
                color=tc, fontsize=fs, weight="bold")
    if sub:
        ax.text(xy[0] + w / 2, xy[1] - 0.06, sub, ha="center", va="top",
                fontsize=8, style="italic", color="black")


def _arrow(ax, start, end, color="black", lw=1.5, style="-|>"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, color=color,
                                 linewidth=lw, mutation_scale=12,
                                 shrinkA=1, shrinkB=3))


def _cell(ax, x, y, w, h, text, fc, tc="black", fs=8, weight="normal"):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008",
                         facecolor=fc, edgecolor="black", linewidth=0.8,
                         alpha=0.95)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            family="monospace", color=tc, weight=weight)


def tokenize(text: str) -> list[str]:
    """Course tokenization: lower, split on whitespace, strip punctuation."""
    out: list[str] = []
    for raw in text.lower().split():
        word = raw.strip(PUNCT)
        if word:
            out.append(word)
    return out


def build_postings() -> dict[str, list[str]]:
    """Return {term: [doc_id, ...]} built from datasets/corpus/."""
    postings: dict[str, list[str]] = {}
    for name in sorted(os.listdir(CORPUS)):
        if not name.endswith(".txt"):
            continue
        doc_id = name[:-4]
        f = open(CORPUS / name, mode="r", encoding="utf-8")
        text = f.read()
        f.close()
        for term in tokenize(text):
            if term not in postings:
                postings[term] = []
            if doc_id not in postings[term]:
                postings[term].append(doc_id)
    return postings


# --- 06-01: step-by-step intersection of two real postings lists ------------

def intersection_steps():
    """06-01: walk two real postings lists step by step, pointer by pointer."""
    apply_style()
    post = build_postings()
    left, right = post["jupiter"], post["mars"]
    hits = sorted(set(left) & set(right))

    fig, ax = plt.subplots(figsize=(11.5, 8.2))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    ax.set_title("AND = intersection, walked step by step — real postings from "
                 "datasets/corpus/", fontsize=12)

    ax.text(0.25, 7.86,
            "postings['jupiter'] (%d docs)          AND          "
            "postings['mars'] (%d docs)" % (len(left), len(right)),
            fontsize=11, weight="bold", family="monospace")

    cw = 1.05
    ch = 0.34
    x_left, x_right, x_res = 0.45, 3.35, 8.05
    y0 = 7.28

    # both lists laid out as two columns, one cell per doc id
    for i, doc in enumerate(left):
        fc = "#d9ead3" if doc in hits else "#e8e8e8"
        _cell(ax, x_left, y0 - i * (ch + 0.07), cw, ch, doc.replace("doc-", ""),
              fc, weight="bold" if doc in hits else "normal")
    for i, doc in enumerate(right):
        fc = "#d9ead3" if doc in hits else "#e8e8e8"
        _cell(ax, x_right, y0 - i * (ch + 0.07), cw, ch,
              doc.replace("doc-", ""), fc,
              weight="bold" if doc in hits else "normal")

    ax.text(x_left + cw / 2, y0 + 0.28, "jupiter", ha="center", fontsize=9.5,
            weight="bold", color=COLORS["primary"])
    ax.text(x_right + cw / 2, y0 + 0.28, "mars", ha="center", fontsize=9.5,
            weight="bold", color=COLORS["accent"])
    ax.text(x_res + 0.6, y0 + 0.28, "result", ha="center", fontsize=9.5,
            weight="bold", color=COLORS["ok"])

    # walk it: two pointers, always advance the smaller id
    i = j = 0
    row = 0
    steps = 0
    while i < len(left) and j < len(right):
        steps += 1
        a, b = left[i], right[j]
        y_step = 1.72 - row * 0.62
        if a == b:
            action = "%s == %s  -> KEEP" % (a, b)
            color = COLORS["ok"]
            _cell(ax, x_res, y_step - ch / 2, cw, ch, a.replace("doc-", ""),
                  "#d9ead3", weight="bold")
            ax.plot([x_left + cw, x_res], [y_step, y_step], color=color,
                    linewidth=0.7, linestyle=":", alpha=0.8)
            i += 1
            j += 1
        elif a < b:
            action = "%s  <  %s  -> skip jupiter" % (a, b)
            color = COLORS["warn"]
            i += 1
        else:
            action = "%s  >  %s  -> skip mars" % (b, a)
            color = COLORS["warn"]
            j += 1
        ax.text(0.25, y_step + 0.12, "step %2d   %s" % (steps, action),
                fontsize=8.6, family="monospace", color=color, weight="bold")
        ax.text(5.35, y_step + 0.12,
                "i=%d  j=%d" % (i, j), fontsize=8.6, family="monospace",
                color=COLORS["neutral"])
        row += 1

    ax.text(0.25, 0.30,
            "Both lists are sorted, so one pass of two pointers is enough: "
            "advance whichever side holds the smaller doc id.",
            fontsize=9, style="italic")
    ax.text(0.25, 0.08,
            "Measured on the real corpus: %d pointer advances, %d docs kept of "
            "204 (%d + %d postings read)."
            % (steps, len(hits), len(left) + len(right), len(hits)),
            fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(HERE / "06-01-postings-intersection-steps.png")
    plt.close(fig)
    print("06-01 jupiter(%d) mars(%d) -> %d hits in %d steps: %s"
          % (len(left), len(right), len(hits), steps, hits))


# --- 06-02: the three set operations --------------------------------------

def set_operations():
    """06-02: AND / OR / NOT as three pictures over the same two postings."""
    apply_style()
    post = build_postings()
    total = len(post["topic"])
    a, b = post["jupiter"], post["mars"]
    sa, sb = set(a), set(b)

    panels = [
        ("AND", "intersection", sorted(sa & sb), len(sa & sb),
         "keep doc ids in BOTH lists", COLORS["primary"]),
        ("OR", "union", sorted(sa | sb), len(sa | sb),
         "keep doc ids in EITHER list", COLORS["accent"]),
        ("NOT", "difference", sorted(sa - sb), len(sa - sb),
         "jupiter but NOT mars", COLORS["warn"]),
    ]

    fig, ax = plt.subplots(figsize=(12.5, 4.9))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 4.9)
    ax.axis("off")
    ax.set_title("Three set operations over the same two real postings lists "
                 "(%d docs each)" % len(a), fontsize=12)

    x = 0.35
    for name, kind, doc_ids, count, caption, color in panels:
        _box(ax, (x, 4.05), 3.9, 0.55, name + "  =  " + kind, "", color=color,
             fs=12)
        _box(ax, (x, 0.72), 3.9, 3.16, "", "", fc="#f7f7f7")
        header = "  doc ids kept (n = %d of %d)" % (count, total)
        rows = []
        shown = doc_ids[:9]
        rows.append(header)
        for k, doc in enumerate(shown):
            rows.append("  %-9s %s" % (doc, "in jupiter" if doc in sa else
                                       ("in mars" if doc in sb else "neither")))
        rest = len(doc_ids) - len(shown)
        if rest > 0:
            rows.append("  ... + %d more" % rest)
        ax.text(x + 0.12, 3.72, "\n".join(rows), family="monospace",
                fontsize=7.8, va="top", ha="left")
        ax.text(x + 1.95, 0.90, caption, ha="center", fontsize=8.6,
                style="italic")
        x += 4.1

    ax.text(6.25, 0.36,
            "Measured counts on datasets/corpus/: "
            "|jupiter|=%d  |mars|=%d  |both|=%d  |either|=%d  |jupiter only|=%d  "
            "|neither|=%d"
            % (len(sa), len(sb), len(sa & sb), len(sa | sb), len(sa - sb),
               total - len(sa | sb)),
            ha="center", fontsize=9, family="monospace")
    ax.text(6.25, 0.10,
            "The postings lists never change — only which doc ids survive.",
            ha="center", fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(HERE / "06-02-and-or-not-set-operations.png")
    plt.close(fig)
    print("06-02 jupiter=%d mars=%d AND=%d OR=%d NOT=%d neither=%d"
          % (len(sa), len(sb), len(sa & sb), len(sa | sb), len(sa - sb),
             total - len(sa | sb)))


# --- 06-03: smallest-postings-first, measured ------------------------------

def _intersect_cost(left, right):
    """Return (hits, tests): probe the SHORTER list against the longer one."""
    if len(left) <= len(right):
        small, big = left, right
    else:
        small, big = right, left
    hits = []
    for doc in small:
        if doc in big:
            hits.append(doc)
    return hits, len(small)


def _cost(post, terms, smallest_first):
    """Total doc-id membership tests for an AND chain, plus the result size."""
    if smallest_first:
        terms = sorted(terms, key=lambda t: len(post[t]))
    acc = post[terms[0]]
    cost = 0
    for term in terms[1:]:
        acc, used = _intersect_cost(acc, post[term])
        cost += used
    return cost, len(acc)


def smallest_first():
    """06-03: measured comparison counts, written order vs smallest-first."""
    apply_style()
    post = build_postings()
    queries = [
        ("sauce AND bread", ["sauce", "bread"]),
        ("jupiter AND mars", ["jupiter", "mars"]),
        ("python AND sauce", ["python", "sauce"]),
        ("sauce AND bread AND basil", ["sauce", "bread", "basil"]),
        ("the AND python AND sauce", ["the", "python", "sauce"]),
        ("topic AND python AND bread AND sauce",
         ["topic", "python", "bread", "sauce"]),
        ("the AND topic AND jupiter AND mars AND sauce",
         ["the", "topic", "jupiter", "mars", "sauce"]),
    ]

    written = []
    smallest = []
    labels = []
    for label, terms in queries:
        c1, n1 = _cost(post, terms, False)
        c2, n2 = _cost(post, terms, True)
        assert n1 == n2, label
        written.append(c1)
        smallest.append(c2)
        labels.append(label)
        print("06-03 %-46s sizes=%-26s written=%4d smallest=%4d hits=%d"
              % (label, [len(post[t]) for t in terms], c1, c2, n1))

    import numpy as np
    y = np.arange(len(labels))
    height = 0.36

    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.barh(y + height / 2, written, height, color=COLORS["warn"],
            label="terms in the order you wrote them")
    ax.barh(y - height / 2, smallest, height, color=COLORS["ok"],
            label="terms sorted shortest postings list first")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5, family="monospace")
    ax.invert_yaxis()
    ax.set_xlabel("doc-id membership tests performed (counted, not estimated)")
    ax.set_title("Smallest-postings-first: measured cost of AND chains over "
                 "datasets/corpus/ (204 docs)")
    ax.legend(loc="lower right")
    for k, (c1, c2) in enumerate(zip(written, smallest)):
        ax.text(c1 + 3, k + height / 2, str(c1), va="center", fontsize=8)
        ax.text(c2 + 3, k - height / 2, str(c2), va="center", fontsize=8)
    total_w = sum(written)
    total_s = sum(smallest)
    ax.set_xlim(0, max(written) * 1.16)
    fig.tight_layout(rect=(0, 0.16, 1, 1))
    fig.text(0.5, 0.085,
             "Totals over the 7 queries above: %d tests written-order vs %d "
             "tests smallest-first (%.2fx fewer). Every query returns the "
             "identical result set." % (total_w, total_s, total_w / total_s),
             ha="center", fontsize=9, style="italic")
    fig.text(0.5, 0.025,
             "Method: intersect by walking the shorter list and testing "
             "membership in the longer, counting one test per walked doc id.",
             ha="center", fontsize=8.5, style="italic", color="black")
    fig.savefig(HERE / "06-03-smallest-postings-first.png")
    plt.close(fig)
    print("06-03 TOTAL written=%d smallest=%d ratio=%.2f"
          % (total_w, total_s, total_w / total_s))


# --- 06-04: parse tree for a real query ------------------------------------

def parse_tree():
    """06-04: how 'sauce AND bread OR basil' is grouped, with real set sizes."""
    apply_style()
    post = build_postings()
    total = len(post["topic"])
    S, B, L = set(post["sauce"]), set(post["bread"]), set(post["basil"])
    and_hits = sorted(S & B)
    or_hits = sorted((S & B) | L)

    fig, ax = plt.subplots(figsize=(11.5, 6.6))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.6)
    ax.axis("off")
    ax.set_title("Query parsing: 'sauce AND bread OR basil' is grouped as "
                 "(sauce AND bread) OR basil — AND binds tighter", fontsize=12)

    # root
    _box(ax, (4.05, 5.55), 3.4, 0.6, "OR   -> %d docs" % len(or_hits),
         "the whole query", color=COLORS["primary"], fs=12)

    # left child: the AND node
    _arrow(ax, (4.95, 5.55), (2.75, 4.72))
    _box(ax, (1.15, 4.12), 3.2, 0.6, "AND   -> %d docs" % len(and_hits),
         "left side of the OR", color=COLORS["primary"], fs=12)

    # right child: the lone term
    _arrow(ax, (6.55, 5.55), (8.25, 4.72))
    _box(ax, (7.15, 4.12), 3.2, 0.6, "basil   -> %d docs" % len(L),
         "right side of the OR", color=COLORS["accent"], fs=12)

    # leaves
    _arrow(ax, (2.15, 4.12), (1.55, 3.32))
    _arrow(ax, (3.35, 4.12), (3.05, 3.32))
    _box(ax, (0.45, 2.72), 2.2, 0.6, "sauce   -> %d docs" % len(S),
         "", color=COLORS["primary"])
    _box(ax, (2.25, 2.72), 2.2, 0.6, "bread   -> %d docs" % len(B),
         "", color=COLORS["primary"])
    _box(ax, (7.15, 2.72), 3.2, 0.6, "postings lists, untouched",
         "", color=COLORS["neutral"])

    # what a wrong grouping would have produced
    wrong = len(S | (B & L))
    ax.text(0.25, 2.10,
            "Reading the same words left to right without precedence gives a "
            "different answer:", fontsize=9.5, weight="bold")
    _box(ax, (0.25, 1.28), 4.3, 0.62,
         "(sauce OR bread) AND basil", "", color=COLORS["warn"], fs=11)
    _arrow(ax, (4.7, 1.59), (5.5, 1.59))
    _box(ax, (5.6, 1.28), 3.3, 0.62, "%d docs (wrong)" % wrong, "",
         color=COLORS["warn"], fs=11)

    ax.text(0.25, 0.88,
            "Correct grouping = %d docs;  naive left-to-right grouping = %d "
            "docs.  Same 204 documents, same three postings lists."
            % (len(or_hits), wrong),
            fontsize=9, style="italic")
    ax.text(0.25, 0.52,
            "NOT is unary and binds tightest: 'sauce NOT bread' is one group "
            "[sauce, NOT bread], not two.",
            fontsize=9, style="italic")
    ax.text(0.25, 0.22,
            "Parentheses are the stretch goal that lets a user override this "
            "precedence explicitly.",
            fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(HERE / "06-04-query-parse-tree.png")
    plt.close(fig)
    print("06-04 sauce=%d bread=%d basil=%d AND=%d OR=%d wrong=%d"
          % (len(S), len(B), len(L), len(S & B), len((S & B) | L), wrong))


def main() -> None:
    intersection_steps()
    set_operations()
    smallest_first()
    parse_tree()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()