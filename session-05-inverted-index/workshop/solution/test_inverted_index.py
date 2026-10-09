"""Tests for solution/inverted_index.py.

Every expected value here is hand-checkable against the 3-document mini-corpus
in workshop/data/ (read it while you read these numbers):

    doc-a.txt  topic: python / Python builds an inverted index term by term.
               Every term maps to a list of documents.
    doc-b.txt  topic: search / An inverted index answers a query without
               reading every document.  The index keeps a postings list for
               each term.
    doc-c.txt  topic: cooking / Simmer the tomato sauce for twenty minutes.
               A good sauce depends on fresh basil.

Run from the repo root:
    python -m pytest session-05-inverted-index/workshop/solution/ -v
"""
import os

from inverted_index import (add_tf, build_postings, doc_path, list_doc_ids,
                            read_tokens, search_and, tokenize)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
CORPUS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "datasets", "corpus")


# --- tokenization -----------------------------------------------------------

def test_tokenize_lowercases_and_strips_punctuation():
    # "Bake the bread until the crust turns golden." -> the final "." goes away
    assert tokenize("Bake the bread until the crust turns golden.") == [
        "bake", "the", "bread", "until", "the", "crust", "turns", "golden"]


def test_tokenize_drops_empty_results_from_punctuation_only_words():
    assert tokenize("... ? !") == []
    assert tokenize("\"python\" (index)") == ["python", "index"]


def test_read_tokens_doc_a():
    # doc-a is 3 lines / 18 tokens; "Python" folds to "python", "term." -> "term"
    assert read_tokens(doc_path(DATA, "doc-a"))[:4] == [
        "topic", "python", "python", "builds"]
    assert len(read_tokens(doc_path(DATA, "doc-a"))) == 18


# --- the v1 index {term: [doc_ids]} ----------------------------------------

def test_list_doc_ids_sorted():
    assert list_doc_ids(DATA) == ["doc-a", "doc-b", "doc-c"]


def test_postings_lists_are_sorted_and_unique():
    p = build_postings(DATA)
    for term in p:
        assert p[term] == sorted(p[term])
        assert len(p[term]) == len(set(p[term]))
    # keys are sorted too — that is the B-tree property Session 6 relies on
    assert sorted(p) == list(p)


def test_postings_single_doc_term():
    # "sauce" appears in doc-c only (twice), so df = 1
    assert build_postings(DATA)["sauce"] == ["doc-c"]


def test_postings_two_doc_term():
    # "index" is in doc-a ("an inverted index") and doc-b ("inverted index",
    # "The index keeps"), so df = 2
    assert build_postings(DATA)["index"] == ["doc-a", "doc-b"]


def test_postings_term_in_all_three_docs():
    # "topic" is the metadata first line of all three files — we index it
    assert build_postings(DATA)["topic"] == ["doc-a", "doc-b", "doc-c"]


def test_postings_missing_term_is_absent_not_empty():
    assert "zzz" not in build_postings(DATA)


def test_postings_count_is_hand_checkable():
    # 37 distinct terms across the 3 docs (count them in the printed index)
    assert len(build_postings(DATA)) == 37


# --- the v2 index {term: {doc_id: tf}} -------------------------------------

def test_tf_counts_repeats_inside_one_document():
    # doc-a says "term" three times; doc-b says it once
    assert add_tf(DATA)["term"] == {"doc-a": 3, "doc-b": 1}


def test_tf_of_index_is_1_in_doc_a_and_2_in_doc_b():
    assert add_tf(DATA)["index"] == {"doc-a": 1, "doc-b": 2}


def test_tf_equals_length_of_v1_postings_list():
    p = build_postings(DATA)
    i = add_tf(DATA)
    for term in p:
        assert sorted(i[term]) == p[term]


# --- AND queries -----------------------------------------------------------

def test_and_two_terms_both_present():
    # index -> [doc-a, doc-b]; term -> [doc-a, doc-b]; intersection is both
    assert search_and(add_tf(DATA), "index", "term") == ["doc-a", "doc-b"]


def test_and_one_term_missing_everywhere():
    # sauce -> [doc-c]; nothing overlaps index -> empty result, no crash
    assert search_and(add_tf(DATA), "index", "sauce") == []


def test_and_unknown_term_is_empty():
    assert search_and(add_tf(DATA), "index", "zzz") == []
    assert search_and(add_tf(DATA), "zzz", "index") == []


def test_and_is_order_independent():
    i = add_tf(DATA)
    assert search_and(i, "index", "term") == search_and(i, "term", "index")


# --- the real 204-document course corpus -----------------------------------

def brute_force_and(folder, term_a, term_b):
    """Linear scan: read every file, keep docs containing both terms."""
    hits = []
    for doc_id in list_doc_ids(folder):
        tokens = read_tokens(doc_path(folder, doc_id))
        if term_a in tokens and term_b in tokens:
            hits.append(doc_id)
    return hits


def test_index_matches_brute_force_on_the_real_corpus():
    corpus = os.path.normpath(CORPUS)
    assert len(list_doc_ids(corpus)) == 204
    index = add_tf(corpus)
    for term_a, term_b in [("sauce", "bread"), ("python", "index"),
                           ("tomato", "simmer"), ("sauce", "zzz"),
                           ("striker", "scored"), ("rover", "mars")]:
        assert search_and(index, term_a, term_b) == \
            brute_force_and(corpus, term_a, term_b), (term_a, term_b)


def test_postings_match_brute_force_on_the_real_corpus():
    corpus = os.path.normpath(CORPUS)
    p = build_postings(corpus)
    for term in ["bread", "sauce", "python", "twist", "goalkeeper"]:
        expected = []
        for doc_id in list_doc_ids(corpus):
            if term in read_tokens(doc_path(corpus, doc_id)):
                expected.append(doc_id)
        assert p[term] == expected, term
    # hand-checked against a grep of the real corpus
    assert len(p["bread"]) == 20
    assert len(p["sauce"]) == 21
    assert len(p["python"]) == 34