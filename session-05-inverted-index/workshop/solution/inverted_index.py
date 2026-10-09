"""Session 5 — Inverted index construction over a folder of .txt documents.

Two index shapes, built with basics only (open(), for loops, plain dict/list,
sorted()): no Counter, no lambda, no regex, no third-party libraries.

    build_postings(folder) -> {"term": ["doc-a", "doc-b"]}       (v1)
    add_tf(folder)         -> {"term": {"doc-a": 3, "doc-b": 1}} (v2)
    search_and(index, t1, t2) -> docs containing BOTH terms

Tokenization is the course pipeline taught in the README:
    lower() -> split() -> strip(".,!?;:'\\"()") -> drop empties

The first line of every document ("topic: <name>") is indexed too, exactly as
it appears in the file. Simpler is better here; real engines separate fields.

Usage:
    python inverted_index.py <folder> [termA] [termB]
"""
from __future__ import annotations

import os
import sys

PUNCTUATION = ".,!?;:'\"()"


def tokenize(text: str) -> list[str]:
    """Turn raw text into a list of normalized terms.

    lower() folds case, split() cuts on whitespace, strip(PUNCTUATION) peels
    punctuation off both ends, empty results are dropped.
    """
    tokens: list[str] = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word != "":
            tokens.append(word)
    return tokens


def read_tokens(path: str) -> list[str]:
    """Read one .txt file and return its normalized terms."""
    f = open(path, mode="r", encoding="utf-8")
    text = f.read()
    f.close()
    return tokenize(text)


def list_doc_ids(folder: str) -> list[str]:
    """Return the sorted doc ids of every .txt file in folder.

    "doc-a.txt" -> "doc-a". os.listdir() returns names in arbitrary order, so
    sorted() is what makes the postings lists come out in ascending doc order.
    """
    names = os.listdir(folder)
    doc_ids = []
    for name in sorted(names):
        if name.endswith(".txt"):
            doc_ids.append(name.replace(".txt", ""))
    return doc_ids


def doc_path(folder: str, doc_id: str) -> str:
    """Build the file path for a doc id inside folder."""
    return folder + "/" + doc_id + ".txt"


def build_postings(folder: str) -> dict[str, list[str]]:
    """Return {term: [doc_id, ...]} — the v1 inverted index.

    Walk the docs in ascending order, append each doc id at most once per
    term, then sort both the keys and every postings list.
    """
    postings: dict[str, list[str]] = {}
    for doc_id in list_doc_ids(folder):
        for term in read_tokens(doc_path(folder, doc_id)):
            if term not in postings:
                postings[term] = []
            if doc_id not in postings[term]:
                postings[term].append(doc_id)
    ordered: dict[str, list[str]] = {}
    for term in sorted(postings):
        ordered[term] = sorted(postings[term])
    return ordered


def add_tf(folder: str) -> dict[str, dict[str, int]]:
    """Return {term: {doc_id: tf}} — the v2 index, tf = term frequency.

    tf is how many times the term occurs in that one document. Counting is a
    second pass over the same tokens, so both index shapes stay in sync.
    """
    index: dict[str, dict[str, int]] = {}
    for doc_id in list_doc_ids(folder):
        for term in read_tokens(doc_path(folder, doc_id)):
            if term not in index:
                index[term] = {}
            if doc_id not in index[term]:
                index[term][doc_id] = 0
            index[term][doc_id] = index[term][doc_id] + 1
    return index


def search_and(index: dict[str, dict[str, int]], term_a: str,
               term_b: str) -> list[str]:
    """Return doc ids containing BOTH terms, sorted ascending.

    AND is set intersection. Walking the smaller list and testing membership in
    the other is the simplest correct version (Session 6 makes it faster).
    """
    if term_a not in index:
        return []
    if term_b not in index:
        return []
    left = index[term_a]
    right = index[term_b]
    if len(left) > len(right):
        small, big = right, left
    else:
        small, big = left, right
    hits = []
    for doc_id in sorted(small):
        if doc_id in big:
            hits.append(doc_id)
    return hits


def main(argv: list[str] | None = None) -> int:
    """Print a small report for one folder of documents."""
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python inverted_index.py <folder> [termA] [termB]")
        return 2
    folder = args[0]
    term_a = args[1] if len(args) > 1 else "index"
    term_b = args[2] if len(args) > 2 else "term"

    doc_ids = list_doc_ids(folder)
    index = add_tf(folder)
    preview = ", ".join(doc_ids[:3])
    if len(doc_ids) > 3:
        preview = preview + ", ..."
    print("folder: " + folder)
    print("documents: " + str(len(doc_ids)) + " (" + preview + ")")
    print("terms: " + str(len(index)))
    print("postings for '" + term_a + "':")
    if term_a in index:
        for doc_id in sorted(index[term_a]):
            print("  " + doc_id + "  tf=" + str(index[term_a][doc_id]))
    else:
        print("  (term not in index)")
    print("AND '" + term_a + "', '" + term_b + "': "
          + ", ".join(search_and(index, term_a, term_b)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())