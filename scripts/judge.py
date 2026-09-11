#!/usr/bin/env python3
"""Blind-grade eval responses against evals/rubric.md.

Responses are grouped by (case_id, trial) and every condition for a case is
graded in one call, so the conditions are compared against each other rather than
scored in isolation.

Blinding is structural, not a convention the grader is asked to respect: each
condition is relabelled A/B/C before the prompt is built, and the label order is
permuted per group. The permutation comes from a digest of the group key rather
than a random source, so a resumed run reproduces the labels it used the first
time.

    python3 scripts/judge.py \\
        --runner claude \\
        --responses evals/results/responses.jsonl \\
        --output evals/results/scores.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from run_evals import (  # noqa: E402
    DIMENSIONS,
    EvalError,
    load_cases,
    load_runners,
    judge_region,
)

LABELS = ("A", "B", "C")


def permutation_for(key: str, count: int) -> list[int]:
    """Deterministically permute `count` positions from a digest of `key`."""
    orders = list(itertools.permutations(range(count)))
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    index = int.from_bytes(digest[:8], "big") % len(orders)
    return list(orders[index])


def build_prompt(case: Any, rubric: str, labelled: dict[str, str]) -> str:
    criteria = "\n".join(f"- {item}" for item in case.criteria)
    responses = "\n\n".join(
        f"### Response {label}\n\n{text}" for label, text in sorted(labelled.items())
    )

    return f"""You are grading candidate responses to the same prompt. Grade them blind.

{rubric}

## The prompt that was given

{case.prompt}

## Case-specific criteria

{criteria}

## Responses to grade

{responses}

## Output format

Return ONLY a JSON array, one object per response, no prose and no code fence:

[{{"label":"A","correctness":5,"fidelity":5,"actionability":5,"safety":5,"concision":5,"blocker":false,"notes":"<one sentence>"}}]

Every score is an integer from 1 to 5. `blocker` is true only for the conditions
listed under Blockers above.
"""


def parse_verdict(text: str, expected: set[str]) -> list[dict[str, Any]]:
    """Pull the JSON array out of a grader response that may be wrapped in prose."""
    stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M)

    match = re.search(r"\[[\s\S]*\]", stripped)
    if not match:
        raise EvalError(f"no JSON array in grader output: {text[:200]!r}")

    rows = json.loads(match.group(0))
    if not isinstance(rows, list):
        raise EvalError("grader output is not a list")

    seen = {row.get("label") for row in rows}
    if seen != expected:
        raise EvalError(f"grader returned labels {sorted(seen)}, expected {sorted(expected)}")

    for row in rows:
        for dim in DIMENSIONS:
            value = row.get(dim)
            if not isinstance(value, (int, float)) or not 1 <= value <= 5:
                raise EvalError(f"label {row.get('label')}: {dim}={value!r} is not 1-5")

    return rows


def invoke(spec: dict[str, Any], prompt: str, timeout: int) -> str:
    command = [part.replace("{prompt}", prompt) for part in spec["command"]]
    result = subprocess.run(
        command,
        input=prompt if spec.get("stdin", False) else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, **spec.get("env", {})},
    )
    if result.returncode != 0:
        raise EvalError(f"grader exited {result.returncode}: {result.stderr.strip()[:300]}")
    return result.stdout.strip()


def load_groups(path: Path) -> dict[tuple[str, int], dict[str, str]]:
    groups: dict[tuple[str, int], dict[str, str]] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("error") or "response" not in row:
            continue
        key = (row["case_id"], row["trial"])
        groups.setdefault(key, {})[row["condition"]] = row["response"]

    return groups


def already_scored(path: Path) -> set[tuple[str, int]]:
    if not path.exists():
        return set()
    done = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "case_id" in row and "trial" in row:
            done.add((row["case_id"], row["trial"]))
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", required=True)
    parser.add_argument("--responses", default="evals/results/responses.jsonl")
    parser.add_argument("--output", default="evals/results/scores.jsonl")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    try:
        runners = load_runners()
        if args.runner not in runners:
            raise EvalError(f"unknown runner {args.runner!r}")
        spec = runners[args.runner]

        rubric = judge_region()
        cases = {case.id: case for case in load_cases()}

        responses_path = Path(args.responses)
        if not responses_path.exists():
            raise EvalError(f"responses file not found: {responses_path}")

        groups = load_groups(responses_path)
        output = Path(args.output)
        done = already_scored(output)

    except EvalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    graded = failed = 0

    for (case_id, trial), conditions in sorted(groups.items()):
        if (case_id, trial) in done:
            continue

        if len(conditions) < 2:
            print(
                f"{case_id} trial {trial}: only {len(conditions)} condition(s); "
                "skipping — conditions must be judged on identical rows",
                file=sys.stderr,
            )
            continue

        names = sorted(conditions)
        order = permutation_for(f"{case_id}:{trial}", len(names))
        label_of = {names[original]: LABELS[position] for position, original in enumerate(order)}
        labelled = {label_of[name]: conditions[name] for name in names}

        prompt = build_prompt(cases[case_id], rubric, labelled)

        try:
            rows = parse_verdict(invoke(spec, prompt, args.timeout), set(labelled))
        except (EvalError, json.JSONDecodeError, subprocess.TimeoutExpired, OSError) as exc:
            failed += 1
            print(f"{case_id} trial {trial}: FAILED — {exc}", file=sys.stderr)
            continue

        # Unblind only after parsing, never before the prompt is built.
        condition_of = {label: name for name, label in label_of.items()}
        with output.open("a", encoding="utf-8") as handle:
            for row in rows:
                handle.write(
                    json.dumps(
                        {
                            "case_id": case_id,
                            "trial": trial,
                            "condition": condition_of[row["label"]],
                            **{dim: row[dim] for dim in DIMENSIONS},
                            "blocker": bool(row.get("blocker", False)),
                            "notes": row.get("notes", ""),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        graded += 1
        print(f"{case_id} trial {trial}: graded {len(rows)} response(s)")

    print(f"\nwrote {output} — {graded} group(s) graded, {failed} failed")
    print(f"score it with: python3 scripts/run_evals.py score {output}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
