"""Tests for solution/text_stats.py (hand-computed expected values)."""
from text_stats import count_stats, find_lines, top_words

SAMPLE = "Search engines index text.\nSearch engines rank text.\n"


def test_count_stats(tmp_path):
    f = tmp_path / "tiny.txt"
    f.write_text(SAMPLE, encoding="utf-8")
    # 2 lines; 4+4 = 8 words; chars = 27 + 26 = 53 (measured)
    assert count_stats(f) == {"lines": 2, "words": 8, "chars": 53}


def test_top_words(tmp_path):
    f = tmp_path / "tiny.txt"
    f.write_text(SAMPLE, encoding="utf-8")
    assert top_words(f, 3) == [("search", 2), ("engines", 2), ("text", 2)]


def test_find_lines(tmp_path):
    f = tmp_path / "tiny.txt"
    f.write_text(SAMPLE, encoding="utf-8")
    assert find_lines(f, "rank") == ["Search engines rank text."]
    assert find_lines(f, "Search") == [
        "Search engines index text.",
        "Search engines rank text.",
    ]
    assert find_lines(f, "zzz") == []
