"""Starter: annotate the IR architecture — 4 TODOs (prints hints until done).

Everything here runs without crashing: unfinished TODOs print a friendly hint
instead of blowing up. Work top to bottom.

Usage (from session-04-ir-architecture/, with the course venv active):
    python workshop/starter/annotate.py
"""

TODO_COUNT = 4

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


def annotate():
    """Return one row per requirement: box, sessions, demand.  (TODO-2)"""
    # TODO-2: turn PIPELINE into a lookup dict, then build one row per
    # requirement. Snippet shape:
    #     sessions_of = dict(PIPELINE)
    #     rows = []
    #     for rid, demand, box in REQUIREMENTS:
    #         rows.append({"id": rid, "demand": demand, "box": box,
    #                     "sessions": sessions_of[box]})
    #     return rows
    # (dict(PIPELINE) turns a list of pairs into a box -> sessions mapping,
    #  so sessions_of["RANK"] gives you "S8-9, S16, S22".)
    raise NotImplementedError(
        "TODO-2 not done yet — map each requirement to its box and sessions")


def unclaimed_boxes(rows):
    """Boxes no requirement maps to — the completeness check.  (TODO-3)"""
    # TODO-3: collect the boxes the requirements used, then keep any pipeline
    # box that is missing. Snippet shape:
    #     used = set()
    #     for row in rows:
    #         used.add(row["box"])
    #     missing = []
    #     for box, sessions in PIPELINE:
    #         if box not in used:
    #             missing.append(box)
    #     return missing
    # (A set is the same trick the Boolean session uses to intersect postings.)
    raise NotImplementedError(
        "TODO-3 not done yet — report which boxes no requirement claimed")


def main():
    print("the IR architecture, annotated for shop search")
    print("=" * 68)
    try:
        rows = annotate()
    except NotImplementedError as exc:
        print(exc)
        print("("
              + str(TODO_COUNT)
              + " TODOs total — open starter/annotate.py and work top to bottom.)")
        return 0

    # TODO-4: print each row: id, box, sessions, demand. Snippet shape:
    #     for row in rows:
    #         print(row["id"] + "  " + row["box"] + "  (" + row["sessions"]
    #               + ")  " + row["demand"])
    #     print("boxes claimed:", len(set(r["box"] for r in rows)), "of",
    #           len(PIPELINE))
    #     missing = unclaimed_boxes(rows)
    #     print("boxes with no requirement:", missing if missing else "none")
    raise NotImplementedError(
        "TODO-4 not done yet — print the annotated table and the completeness check")


if __name__ == "__main__":
    main()
