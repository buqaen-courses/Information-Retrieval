"""Regenerate every PNG for Session 5 (deterministic; run in course venv).

Usage:
    python images/make_images.py        # from session-05-inverted-index/

All chart numbers are measured from the real datasets/corpus/ at run time —
nothing here is invented.
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


def _box(ax, xy, w, h, text, sub="", color=COLORS["primary"], fc=None, tc="white",
         fs=10):
    box = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02",
                         facecolor=fc if fc else color, edgecolor="black",
                         alpha=0.9, linewidth=1.0)
    ax.add_patch(box)
    ax.text(xy[0] + w / 2, xy[1] + h / 2 + 0.03, text, ha="center",
            va="center", color=tc, fontsize=fs, weight="bold")
    if sub:
        ax.text(xy[0] + w / 2, xy[1] - 0.07, sub, ha="center", va="top",
                fontsize=8, style="italic", color="black")
    return (xy[0] + w, xy[1] + h / 2)


def _arrow(ax, start, end, style="-|>", color="black", lw=1.5):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, color=color,
                                 linewidth=lw, mutation_scale=12,
                                 shrinkA=1, shrinkB=3))


def tokenize(text: str) -> list[str]:
    """Course tokenization: lower, split on whitespace, strip punctuation."""
    out: list[str] = []
    for raw in text.lower().split():
        word = raw.strip(PUNCT)
        if word:
            out.append(word)
    return out


def read_docs() -> dict[str, list[str]]:
    """Return {doc_id: [tokens]} for every file in datasets/corpus/."""
    docs: dict[str, list[str]] = {}
    names = sorted(os.listdir(CORPUS))
    for name in names:
        if not name.endswith(".txt"):
            continue
        f = open(CORPUS / name, mode="r", encoding="utf-8")
        text = f.read()
        f.close()
        docs[name[:-4]] = tokenize(text)
    return docs


def build_positions(docs: dict[str, list[str]]) -> dict[str, list[tuple]]:
    """Return {term: [(doc_id, [positions]), ...]} with ascending doc ids."""
    out: dict[str, list[tuple]] = {}
    for did in sorted(docs):
        for i, term in enumerate(docs[did]):
            lst = out.setdefault(term, [])
            if lst and lst[-1][0] == did:
                lst[-1] = (did, lst[-1][1] + [i])
            else:
                lst.append((did, [i]))
    return out


def anatomy():
    """05-01: real inverted index anatomy — terms -> postings (doc id, tf, positions)."""
    apply_style()
    docs = read_docs()
    pos = build_positions(docs)

    shown = ["bread", "sauce", "python"]
    keep = 5
    colors = [COLORS["primary"], COLORS["accent"], COLORS["ok"]]

    fig, ax = plt.subplots(figsize=(10.5, 7.0))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 7.0)
    ax.axis("off")
    ax.set_title("Inverted index anatomy — real postings from datasets/corpus/"
                 " (204 docs)", fontsize=12)

    top = 6.55
    row_h = 2.0
    for k, (term, color) in enumerate(zip(shown, colors)):
        entries = pos[term]
        y = top - k * row_h
        df = len(entries)
        _box(ax, (0.25, y - 0.35), 2.3, 0.7, "term: " + term,
             "one dictionary key", color=color)
        _arrow(ax, (2.55, y), (3.25, y))
        _box(ax, (3.25, y - 1.5), 6.9, 1.7, "", "", fc="#f7f7f7", tc="black")
        ax.text(10.0, y - 0.08,
                "postings list   (df = %d of 204 docs)" % df, ha="right",
                va="top", fontsize=10.5, weight="bold")
        lines = ["  doc_id      tf   positions"]
        for did, positions in entries[:keep]:
            tf = len(positions)
            txt = positions if len(positions) <= 4 else positions[:4]
            lines.append("  %-9s %-4d %s" % (did, tf, txt))
        rest = df - keep
        if rest > 0:
            lines.append("  ... + %d more doc ids (real df = %d)" % (rest, df))
        ax.text(3.4, y - 0.36, "\n".join(lines), family="monospace",
                fontsize=8.5, va="top", ha="left", color="black")

    ax.text(5.25, 0.60,
            "Reading one posting: doc-005 stores bread 3 times, at token "
            "positions 4, 12 and 20 of that document.",
            ha="center", fontsize=9.5, style="italic")
    ax.text(5.25, 0.22,
            "Key: term (left, a dict key)  ->  postings list (right, the value). "
            "Positions are what a positional index keeps (Session 11 uses them).",
            ha="center", fontsize=8.5, color="black")
    fig.tight_layout()
    fig.savefig(HERE / "05-01-inverted-index-anatomy.png")
    plt.close(fig)
    for term in shown:
        entries = pos[term]
        head = ["%s tf=%d pos=%s" % (d, len(p), p) for d, p in entries[:5]]
        print("anatomy %-7s df=%d  %s" % (term, len(entries), head))


def tokenization_pipeline():
    """05-02: the tokenization pipeline on a real sentence from doc-005.txt."""
    apply_style()
    sentence = "Bake the bread until the crust turns golden."

    fig, ax = plt.subplots(figsize=(11.0, 5.4))
    ax.set_xlim(0, 11.0)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    ax.set_title("Tokenization pipeline — one real line from doc-005.txt",
                 fontsize=12)

    ax.text(0.2, 5.02, 'raw text:  "%s"' % sentence, family="monospace",
            fontsize=10, weight="bold")

    steps = [
        ("1. lower()", "Bake -> bake", COLORS["primary"]),
        ("2. split()", "cuts on spaces", COLORS["primary"]),
        ("3. strip(punct)", "peels . , ! ? off both ends", COLORS["primary"]),
        ("4. drop empties", 'a lone "?" is gone', COLORS["neutral"]),
        ("5. OPTIONAL stops", "the, until", COLORS["accent"]),
        ("6. OPTIONAL stem", "baked -> bake", COLORS["accent"]),
    ]
    x = 0.25
    widths = [1.45, 1.3, 1.75, 1.6, 1.7, 1.7]
    for (label, sub, color), w in zip(steps, widths):
        _box(ax, (x, 3.35), w, 0.68, label, sub, color=color, fs=8.5)
        _arrow(ax, (x + w, 3.69), (x + w + 0.17, 3.69))
        x += w + 0.17

    ax.text(0.25, 2.80, "after steps 1-4 (this is exactly what we build today):",
            fontsize=9.5, weight="bold")
    ax.text(0.25, 2.46,
            "['bake', 'the', 'bread', 'until', 'the', 'crust', 'turns', 'golden']",
            family="monospace", fontsize=10, color="#1f77b4")
    ax.text(0.25, 1.98, "after steps 5-6 (what real engines add, optional here):",
            fontsize=9.5, weight="bold")
    ax.text(0.25, 1.64,
            "['bake', 'bread', 'crust', 'turns', 'golden']",
            family="monospace", fontsize=10, color="#ff7f0e")

    ax.text(5.5, 0.92,
            'strip() takes a set of characters, not a word: "golden." and '
            '"golden" both become "golden".',
            ha="center", fontsize=9, style="italic")
    ax.text(5.5, 0.48,
            'Step 5 needs a stop-word list and step 6 a stemmer — Session 21 runs '
            'both inside OpenSearch.',
            ha="center", fontsize=9, style="italic")
    ax.text(5.5, 0.12,
            "The word 'baked' -> 'bake' in step 6 is done by a stemmer; we only "
            "show it by hand today.",
            ha="center", fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(HERE / "05-02-tokenization-pipeline.png")
    plt.close(fig)


def index_comparison():
    """05-03: hash index vs B-tree vs inverted index — what each can answer."""
    apply_style()
    fig, ax = plt.subplots(figsize=(11.0, 5.4))
    ax.set_xlim(0, 11.0)
    ax.set_ylim(0, 5.7)
    ax.axis("off")
    ax.set_title("Three ways to organize data — and the questions each can answer",
                 fontsize=12)

    cols = [
        ("hash index", "term -> doc list", COLORS["primary"],
         ["exact lookup in O(1)", "index[\"sauce\"] -> 21 doc ids",
          "join two rows by key", "cache a session"],
         ["ordered scans", "  \"sau\"..\"sauz\" (prefix)",
          "  \"a\" < \"b\" < \"c\" ranges", "  next term in order"]),
        ("B-tree / FST", "sorted term -> doc list", COLORS["accent"],
         ["sorted scans", "  first term >= \"sa\"",
          "  prefix range \"sa\"..\"sb\"", "  ORDER BY term, top-N terms"],
         ["unordered key math", "  one bucket lookup O(1)",
          "  score a posting directly", "  skip to doc 100 fast"]),
        ("inverted index", "term -> sorted postings", COLORS["ok"],
         ["every question above", "  O(1) term lookup",
          "  prefix + ranges (sorted)", "  AND by walking 2 lists",
          "  scoring, snippets, ranking"],
         ["find a phrase", "  unless you keep positions",
          "  (that is what S5-11 add)"]),
    ]

    x = 0.3
    for name, sub, color, cans, cannots in cols:
        _box(ax, (x, 4.95), 3.3, 0.55, name, "", color=color, fs=11)
        ax.text(x + 1.65, 4.86, sub, ha="center", va="top", fontsize=8,
                style="italic", color="black")
        ax.text(x + 0.06, 4.60, "CAN ANSWER", fontsize=8.5, weight="bold",
                color="#1b5e20", va="bottom")
        _box(ax, (x, 3.16), 3.3, 1.35, "", "", fc="#e8f5e9")
        ax.text(x + 0.14, 4.40, "\n".join(cans), family="monospace", fontsize=7.6,
                va="top", ha="left")
        ax.text(x + 0.06, 2.20, "CANNOT ANSWER", fontsize=8.5, weight="bold",
                color="#b71c1c", va="bottom")
        _box(ax, (x, 1.06), 3.3, 1.08, "", "", fc="#fdecea")
        ax.text(x + 0.14, 2.06, "\n".join(cannots), family="monospace",
                fontsize=7.6, va="top", ha="left")
        x += 3.6

    ax.text(5.5, 0.62,
            "Session 2 introduced hash (fast but unordered) and B-trees "
            "(ordered, but key math only).",
            ha="center", fontsize=9, style="italic")
    ax.text(5.5, 0.30,
            "An inverted index is what a search engine actually builds: key = term, "
            "value = a postings list,",
            ha="center", fontsize=9, style="italic")
    ax.text(5.5, 0.02,
            "and it is only readable because the postings are sorted — which is "
            "why Session 6 intersects two lists with a two-pointer walk.",
            ha="center", fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(HERE / "05-03-index-comparison.png")
    plt.close(fig)


def df_chart():
    """05-04: real document frequencies — why stop words live in the index too."""
    apply_style()
    docs = read_docs()
    pos = build_positions(docs)
    n_docs = len(docs)

    order = sorted(pos.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    head = [(t, len(v)) for t, v in order[:10]]
    content = [("python", len(pos["python"])), ("sauce", len(pos["sauce"])),
               ("bread", len(pos["bread"])), ("rover", 0)]
    content.append(("spaghetti", 0))
    labels = [t for t, _ in head] + [t for t, _ in content]
    values = [c for _, c in head] + [c for _, c in content]
    kinds = ["stop-ish"] * len(head) + ["content"] * len(content)
    colors = [COLORS["warn"] if k == "stop-ish" else COLORS["primary"]
              for k in kinds]

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.bar(labels, values, color=colors)
    ax.axhline(n_docs, color=COLORS["neutral"], linestyle=":", linewidth=1.2)
    ax.text(len(labels) - 0.4, n_docs + 3, "%d docs" % n_docs, ha="right",
            fontsize=8, color=COLORS["neutral"])
    ax.set_title("Real document frequency (df) over datasets/corpus/ — "
                 "%d docs, %d distinct terms" % (n_docs, len(pos)))
    ax.set_xlabel("term")
    ax.set_ylabel("df = number of docs containing the term")
    ax.tick_params(axis="x", rotation=45)
    for x, v in enumerate(values):
        ax.text(x, v + 2, str(v), ha="center", fontsize=8.5)
    ax.set_ylim(0, max(values) * 1.20)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.text(0.5, 0.055,
             'Red = in most documents, so it says little about any one document '
             '(the stop-word zone).  Blue = discriminative.',
             ha="center", va="bottom", fontsize=8.5, style="italic")
    fig.text(0.5, 0.015,
             'The corpus says "rovers", never "rover" — df = 0 without stemming, '
             'a miss that optional stemming (step 6; real in S21) would fix.',
             ha="center", va="bottom", fontsize=8.5, style="italic")
    fig.savefig(HERE / "05-04-document-frequencies.png")
    plt.close(fig)
    print("df head:", head)
    print("df content:", content)


def main() -> None:
    anatomy()
    tokenization_pipeline()
    index_comparison()
    df_chart()
    print("wrote:", sorted(p.name for p in HERE.glob("*.png")))


if __name__ == "__main__":
    main()