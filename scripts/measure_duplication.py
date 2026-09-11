#!/usr/bin/env python3
"""Measure how much of a TL;DR is repeated in the detail beneath it.

This is the specific waste the skill's rule 4 exists to prevent. It is worth
measuring directly rather than inferring from token counts, because the two move
independently: a run can get shorter overall (by skipping the fold on short
answers) while the answers that *do* fold keep saying everything twice.

    python3 scripts/measure_duplication.py evals/results/responses.jsonl
    python3 scripts/measure_duplication.py evals/results/responses.jsonl --worst 5

Reported per category, since the categories that still fold are the ones where
the remaining savings are.

The metric is deliberately crude: the share of distinct content words (5+ letters)
in the summary that reappear anywhere in the detail. It cannot tell a useful
restatement from a wasteful one, so treat a high number as somewhere to look
rather than as a verdict. Some repetition is correct — a runbook that forces the
reader to scroll back up for a command is worse than one that repeats it.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import sys
from pathlib import Path

SPLIT_RE = re.compile(r"--- detail ---|<details>", re.IGNORECASE)
WORD_RE = re.compile(r"[a-zA-Z]{5,}")
CODE_RE = re.compile(r"`[^`]+`|```[\s\S]*?```")

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = REPO_ROOT / "evals" / "cases.jsonl"


def categories() -> dict[str, str]:
    out = {}
    for line in CASES_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            case = json.loads(line)
            out[case["id"]] = case["category"]
    return out


def split_fold(text: str) -> tuple[str, str] | None:
    """Return (summary, detail), or None when the response has no fold at all."""
    parts = SPLIT_RE.split(text, maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        return None
    return parts[0], parts[1]


def overlap(summary: str, detail: str) -> float | None:
    head = {w.lower() for w in WORD_RE.findall(summary)}
    tail = {w.lower() for w in WORD_RE.findall(detail)}
    if not head:
        return None
    return len(head & tail) / len(head)


def repeated_code(summary: str, detail: str) -> list[str]:
    """Code spans and commands that appear in both halves.

    Tracked separately from prose overlap: a repeated command is the most
    defensible kind of repetition and the most expensive, so it is worth being
    able to see it on its own.
    """
    head = {c.strip("`").strip() for c in CODE_RE.findall(summary)}
    tail = {c.strip("`").strip() for c in CODE_RE.findall(detail)}
    return sorted(span for span in head & tail if len(span) > 6)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("responses", help="A responses JSONL file from run_evals.py")
    parser.add_argument("--condition", default="candidate")
    parser.add_argument("--worst", type=int, default=0, help="Also print the N worst individual responses")
    args = parser.parse_args()

    path = Path(args.responses)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    cats = categories()
    by_cat: dict[str, list[float]] = collections.defaultdict(list)
    tokens: dict[str, list[int]] = collections.defaultdict(list)
    unfolded: dict[str, int] = collections.Counter()
    rows: list[tuple[float, str, int, list[str]]] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("condition") != args.condition or "response" not in row:
            continue

        category = cats.get(row["case_id"], "unknown")
        text = row["response"]
        tokens[category].append(len(text) // 4)

        halves = split_fold(text)
        if halves is None:
            unfolded[category] += 1
            continue

        score = overlap(*halves)
        if score is None:
            continue
        by_cat[category].append(score)
        rows.append((score, f"{row['case_id']} t{row['trial']}", len(text) // 4, repeated_code(*halves)))

    if not tokens:
        print(f"error: no {args.condition} responses found", file=sys.stderr)
        return 2

    print(f"condition: {args.condition}   file: {path}")
    print()
    print(f"{'category':<18}{'folded':>7}{'plain':>7}{'dup':>7}{'tokens':>8}")
    print("-" * 47)

    for category in sorted(tokens, key=lambda c: -(statistics.mean(by_cat[c]) if by_cat[c] else -1)):
        dup = f"{statistics.mean(by_cat[category]):.0%}" if by_cat[category] else "-"
        print(
            f"{category:<18}{len(by_cat[category]):>7}{unfolded[category]:>7}"
            f"{dup:>7}{statistics.mean(tokens[category]):>8.0f}"
        )

    every = [x for v in by_cat.values() for x in v]
    folded = sum(len(v) for v in by_cat.values())
    total = folded + sum(unfolded.values())
    print("-" * 47)
    if every:
        print(f"overall duplication across folded responses: {statistics.mean(every):.0%}")
    print(f"responses with a fold: {folded} of {total} ({folded / total:.0%})")
    print()
    print("A falling token count with a rising duplication share means the saving came")
    print("from skipping the fold on short answers, not from the answers that still fold.")

    if args.worst and rows:
        print()
        print(f"worst {args.worst} individual responses:")
        for score, label, tok, code in sorted(rows, reverse=True)[: args.worst]:
            print(f"  {score:.0%}  {label:<26} {tok:>4} tok")
            for span in code[:3]:
                print(f"         repeated verbatim: {span[:70]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
