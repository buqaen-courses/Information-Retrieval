"""Copy each session's workshop guide into `workshop/README.md`.

GitHub renders a folder's `README.md` inline when you open the folder, so a
student clicking `session-08-bm25/workshop/` lands on the instructions instead
of a bare file list. This script makes `workshop/README.md` an exact copy of
`workshop/WORKSHOP.md` (and `README_fa.md` an exact copy of `WORKSHOP_fa.md`),
so there is exactly one source of truth and nothing to keep in sync by hand.

Usage (from the repo root):
    python tools/sync_workshop_readme.py           # copy
    python tools/sync_workshop_readme.py --check    # report drift, copy nothing
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSIONS = sorted(ROOT.glob("session-*"))
PAIRS = [("WORKSHOP.md", "README.md"), ("WORKSHOP_fa.md", "README_fa.md")]


def sync(session: Path, check: bool) -> list[str]:
    """Mirror a session's workshop files; return the paths it touched."""
    touched = []
    workshop = session / "workshop"
    for source_name, target_name in PAIRS:
        source = workshop / source_name
        target = workshop / target_name
        if not source.exists():
            continue
        if check:
            if not target.exists():
                print(f"MISSING {target.relative_to(ROOT)}")
                touched.append(str(target))
            elif target.read_text(encoding="utf-8") != source.read_text(encoding="utf-8"):
                print(f"STALE   {target.relative_to(ROOT)}")
                touched.append(str(target))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        touched.append(str(target.relative_to(ROOT)))
    return touched


def main() -> int:
    """Mirror every session's workshop guide into its README.md."""
    check = "--check" in sys.argv
    total = 0
    for session in SESSIONS:
        total += len(sync(session, check))
    print(f"{'checked' if check else 'synced'} {total} file(s) across "
          f"{len(SESSIONS)} session folders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
