"""Session 6 — Boolean retrieval over an inverted index.

AND is set intersection, OR is set union, NOT is set difference. All three
operate on the sorted postings lists that Session 5 built, so a Boolean query
never touches the documents themselves.

    search(postings, all_docs, "python AND sauce")  -> ["doc-b"]
    search(postings, all_docs, "sauce OR bread")    -> ["doc-b", "doc-d"]
    search(postings, all_docs, "sauce NOT basil")   -> ["doc-d"]

Precedence is the usual one: NOT binds tightest, then AND, then OR. So
"sauce AND basil OR bread" means "(sauce AND basil) OR bread".

Query parsing is plain string splitting and a small loop — no regex, no eval.
Tokenizer and index builder are Session 5's code, unchanged.

Usage:
    python boolean_search.py <folder> "<query>"
    python boolean_search.py <folder> "sauce AND basil OR bread"
"""
from __future__ import annotations

import os
import sys

PUNCTUATION = ".,!?;:'\"()"
OPERATORS = ["AND", "OR", "NOT"]


# --- Session 5 code, reused unchanged ---------------------------------------

def tokenize(text: str) -> list[str]:
    """Turn raw text into a list of normalized terms."""
    tokens: list[str] = []
    for raw in text.lower().split():
        word = raw.strip(PUNCTUATION)
        if word != "":
            tokens.append(word)
    return tokens


def list_doc_ids(folder: str) -> list[str]:
    """Return the sorted doc ids of every .txt file in folder."""
    names = os.listdir(folder)
    doc_ids = []
    for name in sorted(names):
        if name.endswith(".txt"):
            doc_ids.append(name.replace(".txt", ""))
    return doc_ids


def doc_path(folder: str, doc_id: str) -> str:
    """Build the file path for a doc id inside folder."""
    return folder + "/" + doc_id + ".txt"


def read_tokens(path: str) -> list[str]:
    """Read one .txt file and return its normalized terms."""
    f = open(path, mode="r", encoding="utf-8")
    text = f.read()
    f.close()
    return tokenize(text)


def build_postings(folder: str) -> dict[str, list[str]]:
    """Return {term: [doc_id, ...]} with both keys and values ascending."""
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


# --- the three set operations ----------------------------------------------

def postings_for(postings: dict[str, list[str]], term: str) -> list[str]:
    """Return the postings list for term, or [] when the term is unknown."""
    if term not in postings:
        return []
    return postings[term]


def intersect(left: list[str], right: list[str]) -> list[str]:
    """AND: doc ids present in BOTH lists, ascending.

    Walk the SHORTER list and probe the longer one — that is why the loop body
    is a single membership test. This is the smallest-postings-first rule
    applied to two lists.
    """
    if len(left) <= len(right):
        small, big = left, right
    else:
        small, big = right, left
    hits: list[str] = []
    for doc_id in small:
        if doc_id in big:
            hits.append(doc_id)
    return hits


def union(left: list[str], right: list[str]) -> list[str]:
    """OR: doc ids present in EITHER list, ascending, no duplicates."""
    out: list[str] = []
    for doc_id in sorted(left + right):
        if doc_id not in out:
            out.append(doc_id)
    return out


def subtract(left: list[str], right: list[str]) -> list[str]:
    """NOT: doc ids in left but NOT in right, ascending."""
    out: list[str] = []
    for doc_id in left:
        if doc_id not in right:
            out.append(doc_id)
    return out


# --- query parsing ---------------------------------------------------------

def parse_query(query: str) -> list[str]:
    """Split a query string into tokens; operators uppercase, terms lowercase.

    "sauce AND NOT bread" -> ['sauce', 'AND', 'NOT', 'bread']
    An unknown word is just lowercased, so it becomes a term with no postings
    (df = 0) rather than an error.
    """
    tokens: list[str] = []
    for raw in query.split():
        word = raw.strip(PUNCTUATION)
        if word == "":
            continue
        upper = word.upper()
        if upper in OPERATORS:
            tokens.append(upper)
        else:
            tokens.append(word.lower())
    return tokens


def build_groups(tokens: list[str]) -> list[list[tuple[str, bool]]]:
    """Split tokens on OR, then pair every term with a NOT flag.

    [['sauce', 'AND', 'NOT', 'bread']] ->
        [[('sauce', False), ('bread', True)]]
    ('bread', True) means "exclude the docs in bread's postings list".
    """
    groups: list[list[tuple[str, bool]]] = [[]]
    negate_next = False
    for token in tokens:
        if token == "OR":
            groups.append([])
            negate_next = False
        elif token == "AND":
            negate_next = False
        elif token == "NOT":
            negate_next = True
        else:
            groups[len(groups) - 1].append((token, negate_next))
            negate_next = False
    return groups


# --- evaluation ------------------------------------------------------------

def by_shortest_list(postings: dict[str, list[str]], terms: list[str]) -> None:
    """Sort terms in place by postings length, shortest first.

    smallest-postings-first: the shortest list can only remove postings, so
    every later intersection starts from the smallest possible candidate set.
    """
    for outer in range(len(terms)):
        for inner in range(len(terms) - outer - 1):
            left_size = len(postings_for(postings, terms[inner]))
            right_size = len(postings_for(postings, terms[inner + 1]))
            if right_size < left_size:
                terms[inner], terms[inner + 1] = \
                    terms[inner + 1], terms[inner]


def evaluate_group(postings: dict[str, list[str]], all_docs: list[str],
                   group: list[tuple[str, bool]]) -> list[str]:
    """Evaluate one AND-group: intersect the positive terms, subtract the NOTs.

    Positive terms are consumed shortest-postings-list-first, so the growing
    result stays small and every step is cheap.
    """
    positive: list[str] = []
    negative: list[str] = []
    for term, negated in group:
        if negated:
            negative.append(term)
        else:
            positive.append(term)
    by_shortest_list(postings, positive)

    hits: list[str] | None = None
    for term in positive:
        current = postings_for(postings, term)
        if hits is None:
            hits = current
        else:
            hits = intersect(hits, current)
    if hits is None:
        hits = sorted(all_docs)
    for term in negative:
        hits = subtract(hits, postings_for(postings, term))
    return hits


def evaluate(postings: dict[str, list[str]], all_docs: list[str],
             tokens: list[str]) -> list[str]:
    """Evaluate parsed query tokens: OR the AND-groups together."""
    result: list[str] = []
    for group in build_groups(tokens):
        if group == []:
            continue
        result = union(result, evaluate_group(postings, all_docs, group))
    return result


def search(postings: dict[str, list[str]], all_docs: list[str],
           query: str) -> list[str]:
    """Answer a Boolean query string against a {term: [doc_ids]} index."""
    return evaluate(postings, all_docs, parse_query(query))


# --- command line ----------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Print a Boolean retrieval report for one folder of documents."""
    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        print('usage: python boolean_search.py <folder> "<query>"')
        print('example: python boolean_search.py workshop/data '
              '"sauce AND basil OR bread"')
        return 2
    folder = args[0]
    query = " ".join(args[1:])

    all_docs = list_doc_ids(folder)
    postings = build_postings(folder)
    tokens = parse_query(query)
    hits = evaluate(postings, all_docs, tokens)

    preview = ", ".join(all_docs[:3])
    if len(all_docs) > 3:
        preview = preview + ", ..."
    print("folder: " + folder)
    print("documents: " + str(len(all_docs)) + " (" + preview + ")")
    print("terms: " + str(len(postings)))
    print("query: " + query)
    print("tokens: " + str(tokens))
    for k, group in enumerate(build_groups(tokens)):
        terms = [("NOT " + term if neg else term) for term, neg in group]
        print("  group " + str(k + 1) + ": " + " AND ".join(terms))
    for token in tokens:
        if token not in OPERATORS:
            found = postings_for(postings, token)
            print("  postings '" + token + "': " + str(len(found)) + " of "
                  + str(len(all_docs)) + " docs")
    print("hits (" + str(len(hits)) + "): " + ", ".join(hits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())