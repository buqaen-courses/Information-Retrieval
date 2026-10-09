"""Check that a Persian translation preserves all code from its English source.

Compares fenced blocks and inline code spans between README.md and README_fa.md
(or WORKSHOP.md / WORKSHOP_fa.md). Inline code and fenced blocks must be
byte-identical: a student copies and runs them.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FENCE = re.compile(r"```.*?```", re.S)
# A code span may wrap across a line break in the source; normalize whitespace
# so a line-wrapped span compares equal to the same span written on one line.
INLINE = re.compile(r"`([^`]+)`", re.S)


def _norm(span: str) -> str:
    """Collapse internal whitespace so wrapped spans compare equal."""
    return " ".join(span.split())


def parts(path: Path) -> tuple[list[str], list[str]]:
    """Return (fenced blocks, inline code spans) from a markdown file.

    Fenced blocks are removed from the text before inline spans are scanned:
    a fence contributes three backticks, which would desynchronize any scan
    that walked the raw text.
    """
    if not path.exists():
        return [], []
    text = path.read_text(encoding="utf-8")
    fences = FENCE.findall(text)
    outside = FENCE.sub("", text)
    return fences, [_norm(s) for s in INLINE.findall(outside)]


def main() -> int:
    """Compare every pair given on the command line."""
    if len(sys.argv) < 2:
        print("usage: python check_code_parity.py <en.md> <fa.md> [...]")
        return 2
    problems = 0
    for pair in range(1, len(sys.argv), 2):
        en = Path(sys.argv[pair])
        fa = Path(sys.argv[pair + 1])
        if not fa.exists():
            print(f"{fa}: MISSING")
            problems += 1
            continue
        fe, ie = parts(en)
        ff, ifa = parts(fa)
        print(f"\n{en.name} -> {fa.name}")
        if fe == ff:
            print(f"  fenced blocks : OK ({len(fe)} identical)")
        else:
            print(f"  fenced blocks : MISMATCH  en={len(fe)} fa={len(ff)}")
            problems += 1
        if ie == ifa:
            print(f"  inline code   : OK ({len(ie)} identical)")
            continue
        bad = [(a, b) for a, b in zip(ie, ifa) if a != b]
        print(f"  inline code   : MISMATCH  en={len(ie)} fa={len(ifa)}, "
              f"{len(bad)} differ")
        for a, b in bad[:20]:
            print(f"     EN {a!r}")
            print(f"     FA {b!r}")
        problems += 1
    print(f"\n{'all code preserved' if not problems else f'{problems} file pair(s) need fixing'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
