#!/usr/bin/env python3
"""Verify that every mirror of the canonical skill is byte-identical to it.

`skills/tldr/SKILL.md` is the single source of truth. Harnesses that cannot read
from that path get a copy, and a copy that drifts is worse than no copy at all:
two harnesses would then follow two different rulesets while both claiming to run
tldr.

CI runs this on every pull request. Fix a failure by re-copying, never by editing
the mirror:

    cp skills/tldr/SKILL.md .cursor/skills/tldr/SKILL.md
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / "skills" / "tldr" / "SKILL.md"

MIRRORS = [
    REPO_ROOT / ".cursor" / "skills" / "tldr" / "SKILL.md",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not CANONICAL.exists():
        print(f"error: canonical skill not found: {CANONICAL}", file=sys.stderr)
        return 2

    expected = digest(CANONICAL)
    print(f"canonical  {CANONICAL.relative_to(REPO_ROOT)}  {expected[:12]}")

    failures = 0
    for mirror in MIRRORS:
        rel = mirror.relative_to(REPO_ROOT)

        if not mirror.exists():
            print(f"MISSING    {rel}", file=sys.stderr)
            failures += 1
            continue

        actual = digest(mirror)
        if actual != expected:
            print(f"DRIFTED    {rel}  {actual[:12]}", file=sys.stderr)
            failures += 1
        else:
            print(f"ok         {rel}  {actual[:12]}")

    if failures:
        print(
            f"\n{failures} mirror(s) out of sync. Re-copy from the canonical skill:\n"
            f"  cp {CANONICAL.relative_to(REPO_ROOT)} <mirror>",
            file=sys.stderr,
        )
        return 1

    print(f"\nOK — {len(MIRRORS)} mirror(s) in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
