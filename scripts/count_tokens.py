#!/usr/bin/env python3
"""Count output tokens per condition in an eval responses file.

Compression's whole point is cost, so token counts belong next to the quality
numbers — never instead of them. See "Token accounting" in evals/rubric.md.

    python3 scripts/count_tokens.py evals/results/responses.jsonl

Uses tiktoken when it is installed. Without it, falls back to a characters/4
approximation, which is clearly labelled in the output: an approximation is fine
for a relative comparison between conditions on the same cases, and not fine for
a published absolute number.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Callable

APPROX_CHARS_PER_TOKEN = 4


def build_counter() -> tuple[Callable[[str], int], str]:
    try:
        import tiktoken  # type: ignore

        encoding = tiktoken.get_encoding("cl100k_base")
        return (lambda text: len(encoding.encode(text)), "tiktoken/cl100k_base")
    except Exception:
        return (
            lambda text: max(1, round(len(text) / APPROX_CHARS_PER_TOKEN)),
            f"approximate (chars/{APPROX_CHARS_PER_TOKEN}) — install tiktoken for exact counts",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("responses", help="Path to a responses JSONL file")
    parser.add_argument("--by-category", action="store_true", help="Break down by case category")
    args = parser.parse_args()

    path = Path(args.responses)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    count, method = build_counter()

    by_condition: dict[str, list[int]] = {}
    by_category: dict[tuple[str, str], list[int]] = {}
    errors = 0

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue

        if row.get("error") or "response" not in row:
            errors += 1
            continue

        tokens = count(row["response"])
        condition = row.get("condition", "unknown")
        by_condition.setdefault(condition, []).append(tokens)
        by_category.setdefault((row.get("category", "unknown"), condition), []).append(tokens)

    if not by_condition:
        print("error: no scoreable rows found", file=sys.stderr)
        return 2

    print(f"counting method: {method}")
    if errors:
        print(f"skipped {errors} row(s) with errors")
    print()

    print(f"{'Condition':<14}{'Rows':>6}{'Total':>10}{'Mean':>9}{'Median':>9}{'Max':>8}")
    print("-" * 56)
    for condition in sorted(by_condition):
        values = by_condition[condition]
        print(
            f"{condition:<14}{len(values):>6}{sum(values):>10,}"
            f"{statistics.mean(values):>9.0f}{statistics.median(values):>9.0f}{max(values):>8,}"
        )

    baseline = by_condition.get("baseline")
    candidate = by_condition.get("candidate")
    if baseline and candidate:
        base_mean = statistics.mean(baseline)
        cand_mean = statistics.mean(candidate)
        change = (cand_mean - base_mean) / base_mean * 100 if base_mean else 0.0
        print()
        print(f"mean output tokens: {base_mean:.0f} -> {cand_mean:.0f} ({change:+.1f}%)")
        print()
        print(
            "A token reduction only counts as a win when Fidelity holds.\n"
            "Report this number beside the rubric scores from scripts/run_evals.py score,\n"
            "never on its own."
        )

    if args.by_category:
        print()
        print(f"{'Category':<20}{'Condition':<14}{'Rows':>6}{'Mean':>9}")
        print("-" * 49)
        for (category, condition) in sorted(by_category):
            values = by_category[(category, condition)]
            print(f"{category:<20}{condition:<14}{len(values):>6}{statistics.mean(values):>9.0f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
