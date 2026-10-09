"""Starter: Boolean retrieval over an inverted index — 5 TODOs.

Runs without crashing: unfinished TODOs print a friendly hint. Work top to
bottom. Sessions 5's tokenizer and postings builder are already here, unchanged.

Usage (from session-06-boolean-retrieval/, with the course venv active):
    python workshop/starter/boolean_search.py workshop/data "sauce AND basil"
"""
from __future__ import annotations

TODO_COUNT = 5
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
    import os

    names = os.listdir(folder)
    doc_ids = []
    for name in sorted(names):
        if name.endswith(".txt"):
            doc_ids.append(name.replace(".txt", ""))
    return doc_ids


def build_postings(folder: str) -> dict[str, list[str]]:
    """Return {term: [doc_id, ...]} with both keys and values ascending."""
    postings: dict[str, list[str]] = {}
    for doc_id in list_doc_ids(folder):
        with open(folder + "/" + doc_id + ".txt", mode="r", encoding="utf-8") as f:
            for term in tokenize(f.read()):
                if term not in postings:
                    postings[term] = []
                if doc_id not in postings[term]:
                    postings[term].append(doc_id)
    ordered: dict[str, list[str]] = {}
    for term in sorted(postings):
        ordered[term] = sorted(postings[term])
    return ordered


def postings_for(postings: dict[str, list[str]], term: str) -> list[str]:
    """Return the postings list for term, or [] when the term is unknown."""
    if term not in postings:
        return []
    return postings[term]


# --- the three set operations ----------------------------------------------

def intersect(left: list[str], right: list[str]) -> list[str]:
    """AND: doc ids present in BOTH lists, ascending.  (TODO-1)"""
    # TODO-1: walk the SHORTER list and probe the longer one. Snippet shape:
    #     if len(left) <= len(right):
    #         small, big = left, right
    #     else:
    #         small, big = right, left
    #     hits = []
    #     for doc_id in small:
    #         if doc_id in big:
    #             hits.append(doc_id)
    #     return hits
    # (Probing the longer list with the shorter one halves the work when the
    #  lists differ wildly — that is smallest-postings-first in miniature.)
    raise NotImplementedError("TODO-1 not done yet — intersect the two postings lists")


def union(left: list[str], right: list[str]) -> list[str]:
    """OR: doc ids in EITHER list, ascending, no duplicates.  (TODO-2)"""
    # TODO-2: concatenate, sort, drop repeats. Snippet shape:
    #     out = []
    #     for doc_id in sorted(left + right):
    #         if doc_id not in out:
    #             out.append(doc_id)
    #     return out
    # (sorted(left + right) merges the two lists into one; the 'not in out'
    #  test is what makes it a set rather than a multiset.)
    raise NotImplementedError("TODO-2 not done yet — union the two postings lists")


def subtract(left: list[str], right: list[str]) -> list[str]:
    """NOT: doc ids in left but NOT in right, ascending.  (TODO-3)"""
    # TODO-3: keep what is only on the left. Snippet shape:
    #     out = []
    #     for doc_id in left:
    #         if doc_id not in right:
    #             out.append(doc_id)
    #     return out
    # (The same membership test as TODO-1, used the other way round.)
    raise NotImplementedError("TODO-3 not done yet — subtract right from left")


def parse_query(query: str) -> list[str]:
    """Split a query string into tokens; operators uppercase, terms lowercase.

    "sauce AND NOT bread" -> ['sauce', 'AND', 'NOT', 'bread']   (TODO-4)
    """
    # TODO-4: split, strip punctuation, uppercase operators, lowercase the rest.
    # Snippet shape:
    #     tokens = []
    #     for raw in query.split():
    #         word = raw.strip(PUNCTUATION)
    #         if word == "":
    #             continue
    #         upper = word.upper()
    #         if upper in OPERATORS:
    #             tokens.append(upper)
    #         else:
    #             tokens.append(word.lower())
    #     return tokens
    # (Checking 'upper in OPERATORS' is what lets a user type "and" or "AND"
    #  and be understood the same way.)
    raise NotImplementedError("TODO-4 not done yet — split the query into tokens")


def evaluate_group(postings: dict[str, list[str]], all_docs: list[str],
                   group: list[tuple[str, bool]]) -> list[str]:
    """Evaluate one AND-group: intersect the positive terms, subtract the NOTs.

    (TODO-5) `group` is a list of (term, negated) pairs, e.g.
    [('sauce', False), ('basil', True)] for "sauce NOT basil".
    """
    # TODO-5: split the group into positive and negative terms, then apply
    # intersect left-to-right and subtract the negatives. Snippet shape:
    #     positive = []
    #     negative = []
    #     for term, negated in group:
    #         if negated:
    #             negative.append(term)
    #         else:
    #             positive.append(term)
    #     hits = None
    #     for term in positive:
    #         current = postings_for(postings, term)
    #         if hits is None:
    #             hits = current
    #         else:
    #             hits = intersect(hits, current)
    #     if hits is None:
    #         hits = sorted(all_docs)
    #     for term in negative:
    #         hits = subtract(hits, postings_for(postings, term))
    #     return hits
    # (Starting from None and taking the first list unchanged avoids inventing
    #  a "match everything" list that would be wrong for OR-less queries.)
    raise NotImplementedError("TODO-5 not done yet — evaluate one AND-group")


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


def evaluate(postings: dict[str, list[str]], all_docs: list[str],
             tokens: list[str]) -> list[str]:
    """Evaluate parsed query tokens: OR the AND-groups together."""
    result: list[str] = []
    for group in build_groups(tokens):
        if group == []:
            continue
        result = union(result, evaluate_group(postings, all_docs, group))
    return result


def main(argv: list[str] | None = None) -> int:
    """Print a Boolean retrieval report for one folder of documents."""
    import sys

    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        print('usage: python boolean_search.py <folder> "<query>"')
        return 2
    folder = args[0]
    query = " ".join(args[1:])
    all_docs = list_doc_ids(folder)
    postings = build_postings(folder)
    try:
        tokens = parse_query(query)
        hits = evaluate(postings, all_docs, tokens)
    except NotImplementedError as exc:
        print(exc)
        print("(" + str(TODO_COUNT)
              + " TODOs total — open starter/boolean_search.py top to bottom.)")
        return 0

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
    main()
