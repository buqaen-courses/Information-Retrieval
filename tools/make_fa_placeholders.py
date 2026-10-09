"""Create the empty `*_fa.md` Persian placeholder files for every student-facing
Markdown document in the course.

The Persian versions are translated by hand later; this script only makes sure
every English file already has its `_fa` twin so nothing is forgotten.

Files that ship to students (per AGENTS.md) get a placeholer:
    README.md, WORKSHOP.md, appendix-optional.md, workshop/data/*.md,
    and the root docs README.md, TOC.md, SYLLABUS.md, setup/README.md

AGENTS.md and PLANS.md are generation contracts for agents, not course
material for students, so they stay English-only.

Usage (from the repo root):
    python tools/make_fa_placeholders.py            # create what is missing
    python tools/make_fa_placeholders.py --check    # report only
"""
from __future__ import annotations

import os
import sys

HEADER = ""


def student_facing(path: str) -> bool:
    """Is this a document that ships to students?"""
    name = os.path.basename(path)
    if name in ("AGENTS.md", "PLANS.md"):
        return False
    # never mirror anything out of a cache, venv or VCS directory
    parts = path.split("/")
    if any(p.startswith(".") for p in parts if p not in (".", "..")):
        return False
    return path.endswith(".md") and not path.endswith("_fa.md")


def fa_path(path: str) -> str:
    """`a/b/README.md` -> `a/b/README_fa.md`"""
    base, ext = os.path.splitext(path)
    return base + "_fa" + ext


def main() -> int:
    """Create every missing Persian placeholder file."""
    check = "--check" in sys.argv
    created: list[str] = []
    for current, _dirs, files in os.walk("."):
        if ".git" in current.split(os.sep) or ".venv" in current.split(os.sep):
            continue
        for name in sorted(files):
            path = os.path.join(current, name).replace(os.sep, "/")[2:]
            if not student_facing(path):
                continue
            target = fa_path(path)
            if os.path.exists(target):
                continue
            if check:
                print(f"MISSING {target}")
            else:
                parent = os.path.dirname(target)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(HEADER)
                print(f"created {target}")
            created.append(target)
    print(f"\n{len(created)} placeholder(s) "
          f"{'missing' if check else 'written'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
