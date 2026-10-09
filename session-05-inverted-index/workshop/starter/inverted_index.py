"""Starter: inverted index construction — 7 TODOs (prints a hint until each is done).

Basics only: open(), for loops, plain dict/list, sorted(). No Counter, no
lambda, no regex. Usage (from the session folder, venv active):

    python workshop/starter/inverted_index.py workshop/data index term

The 3 mini-corpus files in workshop/data/ (read them, they are tiny):

    doc-a.txt
        topic: python
        Python builds an inverted index term by term.
        Every term maps to a list of documents.

    doc-b.txt
        topic: search
        An inverted index answers a query without reading every document.
        The index keeps a postings list for each term.

    doc-c.txt
        topic: cooking
        Simmer the tomato sauce for twenty minutes.
        A good sauce depends on fresh basil.

This file RUNS without crashing: unfinished TODOs print a hint instead.
Work top to bottom; each TODO shows the exact snippet shape to write.
Match your finished code against workshop/solution/inverted_index.py afterwards.
"""

import os
import sys

TODO_COUNT = 7

PUNCTUATION = ".,!?;:'\"()"


def tokenize(text):
    """Turn raw text into a list of normalized terms."""
    # TODO-1: lowercase, split, strip punctuation, drop empties. Snippet shape:
    #     tokens = []
    #     for raw in text.lower().split():
    #         word = raw.strip(PUNCTUATION)
    #         if word != "":
    #             tokens.append(word)
    #     return tokens
    # (text.lower() folds case; .split() cuts on whitespace; .strip(chars)
    #  peels those characters off BOTH ends; PUNCTUATION is defined above.)
    raise NotImplementedError(
        "TODO-1 not done yet - make tokenize() return a list of terms")


def read_tokens(path):
    """Read one .txt file and return its normalized terms."""
    # TODO-2: open, read, close, then hand the text to tokenize(). Snippet:
    #     f = open(path, mode="r", encoding="utf-8")
    #     text = f.read()
    #     f.close()
    #     return tokenize(text)
    raise NotImplementedError("TODO-2 not done yet - open the file and tokenize")


def list_doc_ids(folder):
    """Return the sorted doc ids of every .txt file in folder."""
    # TODO-3: list the folder, keep .txt names, sorted. Snippet shape:
    #     names = os.listdir(folder)
    #     doc_ids = []
    #     for name in sorted(names):
    #         if name.endswith(".txt"):
    #             doc_ids.append(name.replace(".txt", ""))
    #     return doc_ids
    # (os.listdir(p) returns the file names inside folder p — any order;
    #  sorted() is what makes the postings lists come out ascending;
    #  .endswith(".txt") tests the suffix, .replace() drops it.)
    raise NotImplementedError("TODO-3 not done yet - list the .txt files")


def doc_path(folder, doc_id):
    """Build the file path for a doc id inside folder."""
    return folder + "/" + doc_id + ".txt"


def build_postings(folder):
    """Return {term: [doc_id, ...]} — the v1 inverted index."""
    # TODO-4: walk the docs, add each doc id at most once per term, then sort.
    # Snippet shape:
    #     postings = {}
    #     for doc_id in list_doc_ids(folder):
    #         for term in read_tokens(doc_path(folder, doc_id)):
    #             if term not in postings:
    #                 postings[term] = []
    #             if doc_id not in postings[term]:
    #                 postings[term].append(doc_id)
    #     ordered = {}
    #     for term in sorted(postings):
    #         ordered[term] = sorted(postings[term])
    #     return ordered
    # (the second `if` is what keeps one doc from being added twice when the
    #  term repeats inside it — that repeat count is TODO-5's job, not this one.)
    raise NotImplementedError("TODO-4 not done yet - build {term: [doc_ids]}")


def add_tf(folder):
    """Return {term: {doc_id: tf}} — the v2 index, tf = term frequency."""
    # TODO-5: same walk, but count instead of deduplicating. Snippet shape:
    #     index = {}
    #     for doc_id in list_doc_ids(folder):
    #         for term in read_tokens(doc_path(folder, doc_id)):
    #             if term not in index:
    #                 index[term] = {}
    #             if doc_id not in index[term]:
    #                 index[term][doc_id] = 0
    #             index[term][doc_id] = index[term][doc_id] + 1
    #     return index
    # ("if doc_id not in ... = 0" seeds the counter the first time a doc is
    #  seen for that term; then +1 per occurrence.)
    raise NotImplementedError("TODO-5 not done yet - build {term: {doc_id: tf}}")


def search_and(index, term_a, term_b):
    """Return doc ids containing BOTH terms, sorted ascending."""
    # TODO-6: intersect two postings lists. Snippet shape:
    #     if term_a not in index:
    #         return []
    #     if term_b not in index:
    #         return []
    #     left = index[term_a]
    #     right = index[term_b]
    #     if len(left) > len(right):
    #         small, big = right, left
    #     else:
    #         small, big = left, right
    #     hits = []
    #     for doc_id in sorted(small):
    #         if doc_id in big:
    #             hits.append(doc_id)
    #     return hits
    # (walking the SHORTER list and testing `doc_id in big` is set
    #  intersection; `sorted(small)` keeps the answer in ascending doc order.)
    raise NotImplementedError("TODO-6 not done yet - intersect two postings lists")


def main(argv=None):
    """Print a small report for one folder of documents."""
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python inverted_index.py <folder> [termA] [termB]")
        return 2
    folder = args[0]
    term_a = args[1] if len(args) > 1 else "index"
    term_b = args[2] if len(args) > 2 else "term"
    try:
        # TODO-7: build the index and print the report. Snippet shape:
        #     doc_ids = list_doc_ids(folder)
        #     index = add_tf(folder)
        #     preview = ", ".join(doc_ids[:3])
        #     if len(doc_ids) > 3:
        #         preview = preview + ", ..."
        #     print("folder: " + folder)
        #     print("documents: " + str(len(doc_ids)) + " (" + preview + ")")
        #     print("terms: " + str(len(index)))
        #     print("postings for '" + term_a + "':")
        #     if term_a in index:
        #         for doc_id in sorted(index[term_a]):
        #             print("  " + doc_id + "  tf=" + str(index[term_a][doc_id]))
        #     else:
        #         print("  (term not in index)")
        #     print("AND '" + term_a + "', '" + term_b + "': "
        #           + ", ".join(search_and(index, term_a, term_b)))
        raise NotImplementedError("TODO-7 not done yet - build the index and print")
    except NotImplementedError as exc:
        print(exc)
        print("(" + str(TODO_COUNT) + " TODOs total - open starter/inverted_index.py "
              "and work top to bottom.)")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())