#!/usr/bin/env python3
"""Verify that every mirror of the canonical skill is byte-identical to it.

`skills/tldr/` is the single source of truth: `SKILL.md` is the core the model
reads every time, `reference.md` is the long form it opens on demand. Harnesses
that cannot read from that path get a copy, and a copy that drifts is worse than
no copy at all: two harnesses would then follow two different rulesets while both
claiming to run tldr.

CI runs this on every pull request. Fix a failure by re-copying, never by editing
the mirror:

    cp skills/tldr/SKILL.md     .cursor/skills/tldr/SKILL.md
    cp skills/tldr/reference.md .cursor/skills/tldr/reference.md
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DIR = REPO_ROOT / "skills" / "tldr"

# Every file the split ships. A mirror must carry all of them.
FILES = ["SKILL.md", "reference.md"]

MIRROR_DIRS = [
    REPO_ROOT / ".cursor" / "skills" / "tldr",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures = 0
    checked = 0

    for name in FILES:
        canonical = CANONICAL_DIR / name
        if not canonical.exists():
            print(f"error: canonical file not found: {canonical}", file=sys.stderr)
            return 2

        expected = digest(canonical)
        print(f"canonical  {canonical.relative_to(REPO_ROOT)}  {expected[:12]}")

        for mirror_dir in MIRROR_DIRS:
            mirror = mirror_dir / name
            rel = mirror.relative_to(REPO_ROOT)
            checked += 1

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
            f"\n{failures} mirror file(s) out of sync. Re-copy from the canonical skill:\n"
            f"  cp skills/tldr/<file> <mirror-dir>/<file>",
            file=sys.stderr,
        )
        return 1

    print(f"\nOK - {checked} mirror file(s) in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
