"""Starter: text file statistics — 6 TODOs (prints hints until each is done).

Basics only: open(), for loops, plain dicts/lists, sorted(). Nothing fancy.
Usage (from the session folder, with the course venv active):

    python workshop/starter/text_stats.py workshop/data/sample.txt 5

The sample file looks like this (3 lines):

    Search engines index text.
    Search engines rank text.
    Evaluation measures ranking quality.

This file RUNS without crashing: unfinished TODOs print a hint instead.
Work top to bottom; each TODO shows the exact snippet shape to write.
Match your finished code against workshop/solution/text_stats.py afterwards.
"""

TODO_COUNT = 6


def count_stats(path):
    """Return {'lines': n, 'words': n, 'chars': n} for a UTF-8 text file."""
    # TODO-1: open the file for reading. Snippet shape:
    #     f = open(path, mode="r", encoding="utf-8")
    # (mode="r" means read; encoding="utf-8" decodes text the same everywhere.)
    raise NotImplementedError("TODO-1 not done yet — open the file with mode='r'")
    # TODO-2: walk through the file line by line and count. Snippet shape:
    #     lines = 0
    #     words = 0
    #     chars = 0
    #     for line in f:
    #         lines = lines + 1
    #         words = words + len(line.split())
    #         chars = chars + len(line)
    #     f.close()
    #     return {"lines": lines, "words": words, "chars": chars}
    # (The for loop hands you one line at a time; .split() cuts a line into
    #  words; len(line) counts every character including the newline.)


def top_words(path, n=10):
    """Return the n most common words as [(word, count), ...], best first."""
    # TODO-3: count each word with a plain dict. Snippet shape:
    #     counts = {}
    #     f = open(path, mode="r", encoding="utf-8")
    #     for line in f:
    #         for raw in line.lower().split():
    #             word = raw.strip(".,!?;:\"'()")
    #             if word == "":
    #                 continue
    #             if word in counts:
    #                 counts[word] = counts[word] + 1
    #             else:
    #                 counts[word] = 1
    #     f.close()
    # (Lowercase first so "Text" and "text" merge; .strip(...) peels punctuation
    #  off both ends; counts.get-style if/else keeps the tally.)
    raise NotImplementedError("TODO-3 not done yet — tally words into a dict")
    # TODO-4: order the dict best-first and take the top n. Snippet shape:
    #     ordered = sorted(counts, key=counts.get, reverse=True)
    #     result = []
    #     for word in ordered[:n]:
    #         result.append((word, counts[word]))
    #     return result
    # (sorted() with key=counts.get orders words by their count, biggest first;
    #  ordered[:n] keeps the first n.)


def find_lines(path, word):
    """Return the lines (stripped) that contain word, in file order."""
    # TODO-5: keep every line that contains the word. Snippet shape:
    #     hits = []
    #     f = open(path, mode="r", encoding="utf-8")
    #     for line in f:
    #         if word in line:
    #             hits.append(line.strip())
    #     f.close()
    #     return hits
    # (The 'in' test is the seed of every search engine: keep what matches.)
    raise NotImplementedError("TODO-5 not done yet — collect lines containing the word")


def main(argv=None):
    import sys
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python text_stats.py <file> [N]")
        return 2
    try:
        # TODO-6: call your three functions and print the report. Snippet shape:
        #     path = args[0]
        #     if len(args) > 1:
        #         n = int(args[1])
        #     else:
        #         n = 10
        #     stats = count_stats(path)
        #     print("file: " + str(path))
        #     print("lines: " + str(stats["lines"]))
        #     print("words: " + str(stats["words"]))
        #     print("chars: " + str(stats["chars"]))
        #     print("top-" + str(n) + " words:")
        #     for pair in top_words(path, n):
        #         print("  " + pair[0] + ": " + str(pair[1]))
        raise NotImplementedError("TODO-6 not done yet — call your functions and print the report")
    except NotImplementedError as exc:
        print(exc)
        print("(" + str(TODO_COUNT) + " TODOs total — open starter/text_stats.py and work top to bottom.)")
        return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
