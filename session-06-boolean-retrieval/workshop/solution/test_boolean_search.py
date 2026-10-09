"""Tests for solution/boolean_search.py.

Every expected value here is hand-checkable against the 4-document mini-corpus
in workshop/data/ (read it while you read these numbers):

    doc-a.txt  topic: python   / Python builds an inverted index term by term.
                               / A search query reads the postings lists.
    doc-b.txt  topic: cooking  / Simmer the tomato sauce for twenty minutes.
                               / A good sauce depends on fresh basil.
    doc-c.txt  topic: search   / An inverted index answers a search query
                               instantly. / Python powers most search tools.
    doc-d.txt  topic: cooking  / Bread and sauce make a simple dinner.
                               / The bread soaks up the sauce.

So, reading the postings straight off those files:

    python -> doc-a, doc-c        sauce -> doc-b, doc-d
    basil  -> doc-b               bread -> doc-d
    index  -> doc-a, doc-c        search -> doc-a, doc-c

Run from the repo root:
    python -m pytest session-06-boolean-retrieval/workshop/solution/ -v
"""
import os

from boolean_search import (build_groups, build_postings, doc_path, evaluate,
                            intersect, list_doc_ids, parse_query, postings_for,
                            read_tokens, search, subtract, tokenize, union)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
DATA = os.path.normpath(DATA)
CORPUS = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "datasets", "corpus"))


def index():
    """The mini-corpus postings index, built fresh for each test."""
    return build_postings(DATA)


# --- the index (Session 5 code, unchanged) --------------------------------

def test_list_doc_ids_sorted():
    assert list_doc_ids(DATA) == ["doc-a", "doc-b", "doc-c", "doc-d"]


def test_postings_for_sauce_is_exactly_doc_b_and_doc_d():
    # doc-b: "the tomato sauce" + "A good sauce"; doc-d: "Bread and sauce" +
    # "the sauce". No other document says sauce.
    assert index()["sauce"] == ["doc-b", "doc-d"]


def test_postings_for_basil_and_bread_are_single_docs():
    assert index()["basil"] == ["doc-b"]
    assert index()["bread"] == ["doc-d"]


def test_postings_for_python_and_index_agree():
    # doc-a and doc-c both say "python" and both say "index"
    assert index()["python"] == ["doc-a", "doc-c"]
    assert index()["index"] == ["doc-a", "doc-c"]


def test_postings_term_count_is_hand_checkable():
    assert len(index()) == 39


def test_tokenize_unchanged_from_session_5():
    assert tokenize("Simmer the tomato sauce.") == [
        "simmer", "the", "tomato", "sauce"]
    assert read_tokens(doc_path(DATA, "doc-b"))[:4] == [
        "topic", "cooking", "simmer", "the"]


def test_postings_for_unknown_term_is_empty_not_a_crash():
    assert postings_for(index(), "zzz") == []
    assert "zzz" not in index()


# --- AND: intersection ----------------------------------------------------

def test_intersect_keeps_only_shared_doc_ids():
    # sauce -> [doc-b, doc-d], basil -> [doc-b]  ->  [doc-b]
    assert intersect(["doc-b", "doc-d"], ["doc-b"]) == ["doc-b"]


def test_intersect_is_order_independent():
    assert intersect(["doc-a", "doc-c"], ["doc-a", "doc-b"]) == ["doc-a"]
    assert intersect(["doc-a", "doc-b"], ["doc-a", "doc-c"]) == ["doc-a"]


def test_intersect_disjoint_lists_is_empty():
    # basil -> [doc-b], bread -> [doc-d]; no document says both
    assert intersect(["doc-b"], ["doc-d"]) == []


def test_intersect_with_empty_list_is_empty():
    assert intersect(["doc-b", "doc-d"], []) == []
    assert intersect([], ["doc-b"]) == []


def test_intersect_walks_the_shorter_list():
    # Same answer whichever list is shorter: result cannot depend on the order
    # of the two arguments, only on their sizes.
    left = ["doc-a", "doc-c"]
    right = ["doc-b"]
    assert intersect(left, right) == intersect(right, left) == []


# --- OR: union ------------------------------------------------------------

def test_union_keeps_every_doc_id_from_both_lists():
    # bread -> [doc-d], sauce -> [doc-b, doc-d]  ->  [doc-b, doc-d]
    assert union(["doc-d"], ["doc-b", "doc-d"]) == ["doc-b", "doc-d"]


def test_union_never_duplicates():
    # doc-d is in both lists and must appear once
    assert union(["doc-a", "doc-d"], ["doc-c", "doc-d"]) == \
        ["doc-a", "doc-c", "doc-d"]


def test_union_with_empty_list_is_the_other_list():
    assert union([], ["doc-b"]) == ["doc-b"]
    assert union(["doc-b"], []) == ["doc-b"]


def test_union_output_is_sorted():
    assert union(["doc-d"], ["doc-a", "doc-c"]) == ["doc-a", "doc-c", "doc-d"]


# --- NOT: subtraction -----------------------------------------------------

def test_subtract_removes_the_second_list():
    # sauce -> [doc-b, doc-d], basil -> [doc-b]  ->  [doc-d]
    assert subtract(["doc-b", "doc-d"], ["doc-b"]) == ["doc-d"]


def test_subtract_with_disjoint_list_changes_nothing():
    assert subtract(["doc-b", "doc-d"], ["doc-a"]) == ["doc-b", "doc-d"]


def test_subtract_everything_gives_empty():
    assert subtract(["doc-b", "doc-d"], ["doc-b", "doc-d"]) == []


def test_subtract_is_not_the_same_as_intersect():
    # doc-b is shared by sauce and basil: AND keeps it, NOT drops it
    assert intersect(["doc-b", "doc-d"], ["doc-b"]) == ["doc-b"]
    assert subtract(["doc-b", "doc-d"], ["doc-b"]) == ["doc-d"]


# --- query parsing --------------------------------------------------------

def test_parse_query_uppercases_operators_and_lowercases_terms():
    assert parse_query("sauce AND basil") == ["sauce", "AND", "basil"]
    assert parse_query("Sauce And Basil") == ["sauce", "AND", "basil"]


def test_parse_query_keeps_a_real_word_that_looks_like_an_operator_alone():
    # "and" is a term in doc-d ("Bread and sauce"), so it is a real query word
    assert index()["and"] == ["doc-d"]


def test_parse_query_strips_trailing_punctuation():
    assert parse_query("sauce AND basil.") == ["sauce", "AND", "basil"]


def test_build_groups_pairs_each_term_with_a_not_flag():
    assert build_groups(["sauce", "AND", "NOT", "bread"]) == [
        [("sauce", False), ("bread", True)]]


def test_build_groups_splits_on_or_so_and_binds_tighter():
    # "bread OR basil AND sauce" -> [bread] OR [basil AND sauce]
    assert build_groups(["bread", "OR", "basil", "AND", "sauce"]) == [
        [("bread", False)], [("basil", False), ("sauce", False)]]


def test_build_groups_of_a_lone_not_term_starts_from_every_doc():
    assert build_groups(["NOT", "sauce"]) == [[("sauce", True)]]


# --- full queries against the mini-corpus ---------------------------------

def all_docs():
    return list_doc_ids(DATA)


def test_query_and_over_two_cooking_terms():
    # sauce -> [doc-b, doc-d], basil -> [doc-b]  ->  doc-b only
    assert search(index(), all_docs(), "sauce AND basil") == ["doc-b"]


def test_query_or_of_python_and_sauce_covers_every_document():
    assert search(index(), all_docs(), "python OR sauce") == \
        ["doc-a", "doc-b", "doc-c", "doc-d"]


def test_query_not_drops_the_docs_containing_the_second_term():
    assert search(index(), all_docs(), "python NOT sauce") == ["doc-a", "doc-c"]
    assert search(index(), all_docs(), "sauce NOT basil") == ["doc-d"]


def test_query_and_binds_tighter_than_or():
    # (sauce AND basil) OR bread = [doc-b] OR [doc-d] = [doc-b, doc-d]
    assert search(index(), all_docs(), "sauce AND basil OR bread") == \
        ["doc-b", "doc-d"]


def test_query_not_applies_to_the_term_that_follows_it():
    # NOT sauce -> every doc except doc-b and doc-d
    assert search(index(), all_docs(), "NOT sauce") == ["doc-a", "doc-c"]


def test_query_with_a_term_no_document_contains_returns_nothing():
    assert search(index(), all_docs(), "zzz AND sauce") == []
    assert search(index(), all_docs(), "zzz OR sauce") == ["doc-b", "doc-d"]
    assert search(index(), all_docs(), "zzz") == []


def test_query_is_case_insensitive():
    assert search(index(), all_docs(), "SAUCE and BASIL") == ["doc-b"]


def test_query_with_two_not_terms_subtracts_both():
    # sauce -> [doc-b, doc-d]; minus basil [doc-b], minus bread [doc-d] -> []
    assert search(index(), all_docs(), "sauce NOT basil NOT bread") == []


# --- brute-force cross-check on the real 204-doc corpus -------------------

def brute_force(folder, query):
    """Read every document and decide membership the naive way: term by term.

    A document matches when it satisfies at least one AND-group, i.e. it holds
    every positive term of that group and none of its NOT terms.
    """
    groups = build_groups(parse_query(query))
    hits = []
    for doc_id in list_doc_ids(folder):
        tokens = read_tokens(doc_path(folder, doc_id))
        any_good = False
        for group in groups:
            good = True
            for term, negated in group:
                present = term in tokens
                if negated and present:
                    good = False
                if not negated and not present:
                    good = False
            if good:
                any_good = True
        if any_good:
            hits.append(doc_id)
    return hits


def test_engine_matches_brute_force_on_the_real_corpus():
    corpus = CORPUS
    assert len(list_doc_ids(corpus)) == 204
    postings = build_postings(corpus)
    docs = list_doc_ids(corpus)
    for query in ["sauce AND bread", "jupiter AND mars", "python OR sauce",
                  "sauce NOT bread", "bread OR basil AND sauce",
                  "python AND sauce", "sauce AND basil NOT bread",
                  "rover", "topic AND python AND sauce"]:
        assert search(postings, docs, query) == brute_force(corpus, query), query


def test_real_corpus_sizes_are_the_ones_the_readme_quotes():
    corpus = CORPUS
    postings = build_postings(corpus)
    assert len(list_doc_ids(corpus)) == 204
    assert len(postings) == 221
    assert len(search(postings, list_doc_ids(corpus), "sauce AND bread")) == 10
    assert search(postings, list_doc_ids(corpus), "jupiter AND mars") == [
        "doc-002", "doc-037", "doc-118", "doc-128", "doc-155"]
    assert len(search(postings, list_doc_ids(corpus), "sauce NOT bread")) == 11
    assert len(search(postings, list_doc_ids(corpus), "python OR sauce")) == 55
    assert len(search(postings, list_doc_ids(corpus), "python AND sauce")) == 0


def test_evaluate_is_just_parse_then_evaluate():
    postings = build_postings(DATA)
    docs = list_doc_ids(DATA)
    for query in ["sauce AND basil", "python OR sauce", "NOT sauce",
                  "sauce NOT basil NOT bread"]:
        assert evaluate(postings, docs, parse_query(query)) == \
            search(postings, docs, query)