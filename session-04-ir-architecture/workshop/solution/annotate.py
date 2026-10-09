"""Annotate the IR architecture with a shop's requirements, in code.

Run from this session folder (with the course venv active):

    python workshop/solution/annotate.py            # print the annotation

The printed output IS the annotated diagram: every box of the architecture
mapped to the requirement it serves, plus the sessions that build it, and a
measured vocabulary gap that justifies the EMBED box.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "..", "..", "datasets", "corpus")



# The eight boxes of images/04-01-ir-architecture.png, and which sessions
# build each one. This is the vocabulary of the whole course.
PIPELINE = [
    ("CRAWL", "S17-19"),
    ("PARSE", "S18-19"),
    ("DEDUPE", "S20"),
    ("INDEX", "S5-6, S21"),
    ("EMBED", "S12-13"),
    ("QUERY", "S1-3"),
    ("RANK", "S8-9, S16, S22"),
    ("EVALUATE", "S10"),
]

# The shop manager's eight requirements, from workshop/data/scenario.md,
# each answered by exactly one box of the architecture.
REQUIREMENTS = [
    ("R1", "fetch all 128 product pages, one page per second", "CRAWL"),
    ("R2", "pull name, price and description out of each page", "PARSE"),
    ("R3", "eight products repeat one description; show no copies", "DEDUPE"),
    ("R4", "keep a term dictionary of every word shoppers type", "INDEX"),
    ("R5", "a shopper searching 'soccer' must find football boots", "EMBED"),
    ("R6", "one search box; 'under 100' filter must apply", "QUERY"),
    ("R7", "show the ten most relevant products first", "RANK"),
    ("R8", "log every click so we can measure the new ordering", "EVALUATE"),
]


def corpus_paths() -> list[str]:
    """Paths of the 204 seeded corpus docs, sorted so runs are reproducible."""
    return [os.path.join(CORPUS, n) for n in sorted(os.listdir(CORPUS))
            if n.endswith(".txt")]


def load_corpus() -> list[tuple[str, str, list[str]]]:
    """Return (doc_id, topic, tokens) for every corpus document.

    Tokenizing here is exactly the Session 1 recipe: lowercase, then peel
    punctuation off each end of a word. The whole file counts, including the
    ``topic:`` header line — otherwise every topic word (football, space, ...)
    would look absent and the measurement below would be wrong.
    """
    out = []
    for path in corpus_paths():
        with open(path, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
        topic = lines[0].split(":", 1)[1].strip() if lines else ""
        tokens = []
        for line in lines:
            for raw in line.lower().split():
                word = raw.strip(".,!?;:\"'()")
                if word:
                    tokens.append(word)
        out.append((os.path.basename(path)[:-4], topic, tokens))
    return out


def docs_with(docs: list[tuple[str, str, list[str]]], word: str) -> int:
    """How many corpus documents contain `word` exactly."""
    total = 0
    for _doc_id, _topic, tokens in docs:
        if word in tokens:
            total += 1
    return total


def annotate() -> list[dict]:
    """Return one row per requirement: the box it belongs to and who builds it."""
    sessions_of = dict(PIPELINE)
    rows = []
    for rid, demand, box in REQUIREMENTS:
        rows.append({"id": rid, "demand": demand, "box": box,
                     "sessions": sessions_of[box]})
    return rows


def unclaimed_boxes() -> list[str]:
    """Boxes that no requirement maps to — the completeness check."""
    used = {box for _r, _d, box in REQUIREMENTS}
    return [box for box, _s in PIPELINE if box not in used]


def vocabulary_gap(docs: list[tuple[str, str, list[str]]]) -> list[dict]:
    """Measure the words a shopper types that the corpus never writes."""
    probes = [("rover", "rovers"), ("soccer", "football"),
              ("telescope", "telescopes")]
    rows = []
    for typed, written in probes:
        rows.append({"typed": typed, "docs_with_typed": docs_with(docs, typed),
                     "written": written, "docs_with_written": docs_with(docs, written)}
                    )
    return rows


def main() -> int:
    """Print the annotated architecture, then the vocabulary gap."""
    docs = load_corpus()
    rows = annotate()
    print("the IR architecture, annotated for shop search")
    print("=" * 68)
    for row in rows:
        print(f"{row['id']}  {row['box']:<9s} ({row['sessions']:<18s})"
              f" {row['demand']}")
    print("=" * 68)
    print(f"boxes claimed: {len({r['box'] for r in rows})} of {len(PIPELINE)}")
    missing = unclaimed_boxes()
    print("boxes with no requirement: " + (str(missing) if missing else "none"))

    print()
    print(f"the vocabulary gap (measured on {len(docs)} corpus docs)")
    print("-" * 68)
    for row in vocabulary_gap(docs):
        print(f"shopper types {row['typed']:<8s} -> {row['docs_with_typed']:3d} docs;"
              f"  corpus writes {row['written']:<9s} ->"
              f" {row['docs_with_written']:3d} docs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
