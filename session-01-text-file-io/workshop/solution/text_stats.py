"""Corpus text statistics: line/word/char counts, top-N words, find-a-word.

Built with basics only: open(), for loops, plain dicts/lists, sorted().
Usage:
    python text_stats.py <file> [N]

Runs on any .txt file (defaults to top-10 words).
"""


def count_stats(path):
    """Return {'lines': n, 'words': n, 'chars': n} for a UTF-8 text file."""
    lines = 0
    words = 0
    chars = 0
    f = open(path, mode="r", encoding="utf-8")
    for line in f:
        lines = lines + 1
        pieces = line.split()
        words = words + len(pieces)
        chars = chars + len(line)
    f.close()
    return {"lines": lines, "words": words, "chars": chars}


def top_words(path, n=10):
    """Return the n most common words as [(word, count), ...], best first."""
    counts = {}
    f = open(path, mode="r", encoding="utf-8")
    for line in f:
        for raw in line.lower().split():
            word = raw.strip(".,!?;:\"'()")
            if word == "":
                continue
            if word in counts:
                counts[word] = counts[word] + 1
            else:
                counts[word] = 1
    f.close()
    ordered = sorted(counts, key=counts.get, reverse=True)
    result = []
    for word in ordered[:n]:
        result.append((word, counts[word]))
    return result


def find_lines(path, word):
    """Return the lines (stripped) that contain word, in file order."""
    hits = []
    f = open(path, mode="r", encoding="utf-8")
    for line in f:
        if word in line:
            hits.append(line.strip())
    f.close()
    return hits


def main(argv=None):
    import sys
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python text_stats.py <file> [N]")
        return 2
    path = args[0]
    if len(args) > 1:
        n = int(args[1])
    else:
        n = 10
    stats = count_stats(path)
    print("file: " + str(path))
    print("lines: " + str(stats["lines"]))
    print("words: " + str(stats["words"]))
    print("chars: " + str(stats["chars"]))
    print("top-" + str(n) + " words:")
    for pair in top_words(path, n):
        print("  " + pair[0] + ": " + str(pair[1]))
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
