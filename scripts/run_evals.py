#!/usr/bin/env python3
"""Evaluation harness for the tldr skill.

Four subcommands:

    validate   Check that cases, rubric, and runners are well formed. No network.
    plan       Print what a run would do, and how many provider calls it costs.
    run        Generate responses for one condition into a shared JSONL file.
    score      Apply the release gate in evals/rubric.md to a scores file.

The harness compares *conditions*. A condition is the same task prompt with a
different response-style instruction injected:

    baseline    the bare task prompt, no style instruction
    candidate   the task prompt plus skills/tldr/SKILL.md
    comparator  the task prompt plus some other skill, via --condition-skill

Task prompts are identical across conditions. Only the injected instruction
differs, so the comparison measures the instruction and nothing else.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = REPO_ROOT / "evals" / "cases.jsonl"
RUBRIC_PATH = REPO_ROOT / "evals" / "rubric.md"
RUNNERS_PATH = REPO_ROOT / "evals" / "runners.example.json"
SKILL_PATH = REPO_ROOT / "skills" / "tldr" / "SKILL.md"

CONDITIONS = ("baseline", "candidate", "comparator")
REQUIRED_CASE_KEYS = {"id", "category", "prompt", "risk", "criteria"}
VALID_RISKS = {"low", "medium", "high"}

FRONTMATTER_RE = re.compile(r"^---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---[^\S\r\n]*(?:\r?\n|$)")

# Categories where a blocking finding disqualifies the candidate outright.
# See "Why rule 1 is scoped rather than absolute" in evals/rubric.md.
HARD_BLOCK_CATEGORIES = {"never-compress", "safety"}

DIMENSIONS: dict[str, float] = {
    "correctness": 0.30,
    "fidelity": 0.25,
    "actionability": 0.20,
    "safety": 0.15,
    "concision": 0.10,
}


class EvalError(Exception):
    """A problem with the eval configuration or data, reported without a traceback."""


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Case:
    id: str
    category: str
    prompt: str
    risk: str
    criteria: list[str]


def load_cases(path: Path = CASES_PATH) -> list[Case]:
    if not path.exists():
        raise EvalError(f"Cases file not found: {path}")

    cases: list[Case] = []
    seen: set[str] = set()

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvalError(f"{path.name}:{lineno}: invalid JSON: {exc}") from exc

        missing = REQUIRED_CASE_KEYS - obj.keys()
        if missing:
            raise EvalError(
                f"{path.name}:{lineno}: missing key(s): {', '.join(sorted(missing))}"
            )

        if obj["id"] in seen:
            raise EvalError(f"{path.name}:{lineno}: duplicate case id {obj['id']!r}")
        seen.add(obj["id"])

        if obj["risk"] not in VALID_RISKS:
            raise EvalError(
                f"{path.name}:{lineno}: risk must be one of "
                f"{sorted(VALID_RISKS)}, got {obj['risk']!r}"
            )

        if not isinstance(obj["criteria"], list) or not obj["criteria"]:
            raise EvalError(f"{path.name}:{lineno}: criteria must be a non-empty list")

        cases.append(
            Case(
                id=obj["id"],
                category=obj["category"],
                prompt=obj["prompt"],
                risk=obj["risk"],
                criteria=list(obj["criteria"]),
            )
        )

    if not cases:
        raise EvalError(f"{path.name} contains no cases")

    return cases


def judge_region(path: Path = RUBRIC_PATH) -> str:
    """Return only the region of the rubric that is safe to send to a blind grader.

    Everything outside the markers names the conditions, which would leak the
    vocabulary the blinding exists to hide.
    """
    text = path.read_text(encoding="utf-8")
    match = re.search(r"<!--\s*judge:begin\s*-->(.*?)<!--\s*judge:end\s*-->", text, re.S)
    if not match:
        raise EvalError(
            f"{path.name}: missing <!-- judge:begin --> / <!-- judge:end --> markers"
        )

    region = match.group(1).strip()
    if not region:
        raise EvalError(f"{path.name}: the judge region is empty")

    return region


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text).strip()


def load_condition_instruction(condition: str, skill_path: Path | None) -> str:
    if condition == "baseline":
        return ""

    if skill_path is None:
        if condition != "candidate":
            raise EvalError(f"--condition-skill is required for condition {condition!r}")
        skill_path = SKILL_PATH

    if not skill_path.exists():
        raise EvalError(f"Condition skill not found: {skill_path}")

    body = strip_frontmatter(skill_path.read_text(encoding="utf-8"))
    if not body:
        raise EvalError(f"Condition skill is empty: {skill_path}")

    return body


def load_runners(path: Path = RUNNERS_PATH) -> dict[str, Any]:
    if not path.exists():
        raise EvalError(f"Runners file not found: {path}")

    try:
        runners = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvalError(f"{path.name}: invalid JSON: {exc}") from exc

    if not isinstance(runners, dict) or not runners:
        raise EvalError(f"{path.name}: expected a non-empty object of runner definitions")

    for name, spec in runners.items():
        if "command" not in spec:
            raise EvalError(f"{path.name}: runner {name!r} has no 'command'")
        if not isinstance(spec["command"], list):
            raise EvalError(f"{path.name}: runner {name!r} 'command' must be a list")

    return runners


# --------------------------------------------------------------------------- #
# Resumability
# --------------------------------------------------------------------------- #


def instruction_digest(instruction: str) -> str:
    """Short digest of the injected skill text; empty for the baseline.

    Resumption keys on this so that editing the skill between runs can never
    silently reuse candidate rows generated by the previous wording. Rows written
    before this field existed carry no digest and are treated as a different skill.
    """
    if not instruction:
        return ""
    return hashlib.sha256(instruction.encode("utf-8")).hexdigest()[:12]


def completed_rows(path: Path) -> set[tuple[str, int, str, str, str]]:
    """Return the (case, trial, condition, runner, skill digest) keys already present."""
    if not path.exists():
        return set()

    done: set[tuple[str, int, str, str, str]] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("error"):
            continue
        key = (
            row.get("case_id"),
            row.get("trial"),
            row.get("condition"),
            row.get("runner"),
            row.get("skill_sha", ""),
        )
        if all(part is not None for part in key):
            done.add(key)  # type: ignore[arg-type]

    return done


def append_row(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #


def cmd_validate(_args: argparse.Namespace) -> int:
    cases = load_cases()
    region = judge_region()
    runners = load_runners()

    if not SKILL_PATH.exists():
        raise EvalError(f"Canonical skill not found: {SKILL_PATH}")
    if not strip_frontmatter(SKILL_PATH.read_text(encoding="utf-8")):
        raise EvalError(f"Canonical skill has no body: {SKILL_PATH}")

    # The judge region must not name the conditions it is meant to be blind to.
    lowered = region.lower()
    leaked = [name for name in ("baseline", "candidate", "comparator") if name in lowered]
    if leaked:
        raise EvalError(
            "The judge region names the condition(s) "
            + ", ".join(repr(n) for n in leaked)
            + ". Move that text outside the judge:begin/judge:end markers — "
            "sending it to a blind grader leaks what the blinding hides."
        )

    categories: dict[str, int] = {}
    for case in cases:
        categories[case.category] = categories.get(case.category, 0) + 1

    print(f"cases:      {len(cases)} in {CASES_PATH.relative_to(REPO_ROOT)}")
    for category in sorted(categories):
        print(f"              {categories[category]:>2}  {category}")
    print(f"rubric:     {len(region.splitlines())} judge lines, {len(DIMENSIONS)} dimensions")
    print(f"runners:    {', '.join(sorted(runners))}")
    print(f"skill:      {SKILL_PATH.relative_to(REPO_ROOT)}")
    print()
    print("OK")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    cases = load_cases()
    conditions = ["baseline", "candidate"]
    if args.include_comparator:
        conditions.append("comparator")

    rows = len(cases) * args.trials
    total = rows * len(conditions)

    print(f"cases:       {len(cases)}")
    print(f"trials:      {args.trials}")
    print(f"conditions:  {', '.join(conditions)}")
    print()
    print(f"generation:  {total} calls ({rows} per condition)")
    print(f"judging:     {rows} calls (one per case/trial group, all conditions together)")
    print(f"total:       {total + rows} provider calls")
    print()
    print("Run each condition into the same output file:")
    for condition in conditions:
        extra = ""
        if condition == "candidate":
            extra = " \\\n    --condition-skill skills/tldr/SKILL.md"
        print(
            f"\n  python3 scripts/run_evals.py run \\\n"
            f"    --runner claude \\\n"
            f"    --condition {condition}{extra} \\\n"
            f"    --trials {args.trials} \\\n"
            f"    --output evals/results/responses.jsonl"
        )
    return 0


def build_prompt(case: Case, instruction: str, spec: dict[str, Any]) -> str:
    """The user turn.

    When the runner can take a system instruction, the user turn is the bare task,
    exactly as a real user would type it. Only a runner with no system flag falls
    back to prefixing, and that fallback is documented as not comparable.
    """
    if not instruction or spec.get("system_flag"):
        return case.prompt
    return f"{instruction}\n\n---\n\n{case.prompt}"


_NEUTRAL_CWD: str | None = None


def neutral_cwd() -> str:
    """An empty directory to run the provider CLI in.

    These CLIs are agents: launched inside a repository they will read it and
    answer about that code rather than about the prompt. Every condition would be
    contaminated by whatever directory the harness happened to be started from,
    and results would not reproduce across machines.
    """
    global _NEUTRAL_CWD
    if _NEUTRAL_CWD is None:
        _NEUTRAL_CWD = tempfile.mkdtemp(prefix="tldr-eval-")
    return _NEUTRAL_CWD


SHIM_TARGET_RE = re.compile(r'"%dp0%\\?([^"]+\.(?:exe|cmd))"', re.IGNORECASE)


def unwrap_windows_shim(path: str) -> str:
    """Follow an npm .cmd shim to the real executable it launches.

    Two reasons, and the second one is the blocking one:

    1. subprocess cannot launch a bare name on Windows because it does not apply
       PATHEXT the way a shell does.
    2. A .cmd shim runs under cmd.exe, whose command line is capped at 8191
       characters. This harness passes the whole skill body as a system prompt,
       which is comfortably past that, so every candidate call dies with "The
       command line is too long." The real .exe is not launched through cmd.exe
       and gets the full 32767-character Windows limit.

    Returns the original path unchanged when it is not a shim, or when the target
    cannot be found - the caller then fails with a real error rather than a guess.
    """
    if not path.lower().endswith((".cmd", ".bat")):
        return path

    try:
        shim = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return path

    match = SHIM_TARGET_RE.search(shim)
    if not match:
        return path

    target = Path(path).parent / match.group(1).replace("\\", os.sep)
    return str(target) if target.exists() else path


def resolve_executable(command: list[str]) -> list[str]:
    """Resolve argv[0] to something subprocess can actually launch."""
    resolved = shutil.which(command[0])
    if resolved is None:
        raise EvalError(
            f"runner executable not found on PATH: {command[0]!r}. "
            "Install it, or correct the command in evals/runners.example.json."
        )
    return [unwrap_windows_shim(resolved), *command[1:]]


def invoke_runner(
    spec: dict[str, Any], prompt: str, timeout: int, instruction: str = ""
) -> dict[str, Any]:
    command = [part.replace("{prompt}", prompt) for part in spec["command"]]

    # Deliver the condition's skill the way every supported harness delivers it in
    # production: as a system instruction, above the conversation rather than inside
    # it. See system_flag in runners.example.json for why this is load-bearing.
    #
    # JOIN, never append. Claude Code keeps only the LAST --append-system-prompt it
    # is given. The runner already carries one (the neutral "you have no tools"
    # framing), so appending the skill as a second flag silently DISCARDED the
    # framing from every candidate run while the baseline kept it. Every Opus
    # candidate row in runs 7 and the two follow-up probes was generated without
    # ever being told it had no tools. Verified with codeword flags on 2.1.239.
    system_flag = spec.get("system_flag")
    if instruction and system_flag:
        if len(command) >= 2 and command[-2] == system_flag:
            command[-1] = command[-1] + "\n\n" + instruction
        else:
            command += [system_flag, instruction]

    command = resolve_executable(command)
    env = {**os.environ, **spec.get("env", {})}

    result = subprocess.run(
        command,
        input=prompt if spec.get("stdin", False) else None,
        capture_output=True,
        text=True,
        # Explicit: text=True decodes with the locale codepage on Windows, which
        # turns every em-dash and arrow in a response into mojibake before it is
        # ever scored.
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
        cwd=neutral_cwd(),
    )

    if result.returncode != 0:
        raise EvalError(
            f"runner exited {result.returncode}: {result.stderr.strip()[:500]}"
        )

    response = result.stdout.strip()

    # Retry a truly empty body: that is a provider hiccup with no content to judge.
    #
    # Nothing else is retried, including the "{}" this once rejected. A bare
    # argument object is the model reaching for a tool it does not have, which is a
    # real defect in the candidate and belongs in the scores rather than in a retry
    # loop. A length threshold cannot tell that apart from a good terse answer: the
    # first version of this check rejected "5432." three times, which is the correct
    # and maximally concise answer to one of the cases.
    if not response:
        raise EvalError("runner returned an empty response")

    return {"response": response}


def cmd_run(args: argparse.Namespace) -> int:
    cases = load_cases()
    runners = load_runners()

    if args.cases:
        wanted = {c.strip() for c in args.cases.split(",") if c.strip()}
        unknown = wanted - {c.id for c in cases}
        if unknown:
            raise EvalError(f"unknown case id(s): {sorted(unknown)}")
        cases = [c for c in cases if c.id in wanted]

    if args.limit:
        cases = cases[: args.limit]

    if args.limit or args.cases:
        print(f"running a subset: {len(cases)} case(s) - {', '.join(c.id for c in cases)}")

    if args.runner not in runners:
        raise EvalError(
            f"Unknown runner {args.runner!r}. Available: {', '.join(sorted(runners))}"
        )

    spec = runners[args.runner]
    skill_path = Path(args.condition_skill) if args.condition_skill else None
    instruction = load_condition_instruction(args.condition, skill_path)

    output = Path(args.output)
    done = completed_rows(output)
    skill_sha = instruction_digest(instruction)

    planned = [
        (case, trial)
        for case in cases
        for trial in range(1, args.trials + 1)
        if (case.id, trial, args.condition, args.runner, skill_sha) not in done
    ]

    skipped = len(cases) * args.trials - len(planned)
    if skipped:
        print(f"resuming: {skipped} row(s) already complete, {len(planned)} to go")

    failures = 0

    for index, (case, trial) in enumerate(planned, start=1):
        prompt = build_prompt(case, instruction, spec)
        label = f"[{index}/{len(planned)}] {case.id} trial {trial}"

        last_error: str | None = None
        for attempt in range(1, args.retries + 2):
            try:
                result = invoke_runner(spec, prompt, args.timeout, instruction)
                append_row(
                    output,
                    {
                        "case_id": case.id,
                        "category": case.category,
                        "trial": trial,
                        "condition": args.condition,
                        "runner": args.runner,
                        "skill_sha": skill_sha,
                        "response": result["response"],
                    },
                )
                print(f"{label}: ok ({len(result['response'])} chars)")
                last_error = None
                break
            except (EvalError, subprocess.TimeoutExpired, OSError) as exc:
                last_error = str(exc)
                if attempt <= args.retries:
                    print(f"{label}: attempt {attempt} failed, retrying")

        if last_error is not None:
            failures += 1
            print(f"{label}: FAILED — {last_error}", file=sys.stderr)
            append_row(
                output,
                {
                    "case_id": case.id,
                    "category": case.category,
                    "trial": trial,
                    "condition": args.condition,
                    "runner": args.runner,
                    "error": last_error,
                },
            )

    print(f"\nwrote {output} — {len(planned) - failures} ok, {failures} failed")
    return 1 if failures else 0


def iter_scores(path: Path) -> Iterator[dict[str, Any]]:
    if not path.exists():
        raise EvalError(f"Scores file not found: {path}")

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvalError(f"{path.name}:{lineno}: invalid JSON: {exc}") from exc


def weighted(row: dict[str, Any]) -> float:
    return sum(float(row.get(dim, 0)) * weight for dim, weight in DIMENSIONS.items())


def cmd_score(args: argparse.Namespace) -> int:
    rows = list(iter_scores(Path(args.scores)))
    if not rows:
        raise EvalError("No score rows found")

    category_of = {case.id: case.category for case in load_cases()}

    by_condition: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_condition.setdefault(row["condition"], []).append(row)

    if "baseline" not in by_condition or "candidate" not in by_condition:
        raise EvalError("Scores must contain both a baseline and a candidate condition")

    def mean(condition: str, dim: str) -> float:
        values = [float(r.get(dim, 0)) for r in by_condition[condition]]
        return sum(values) / len(values) if values else 0.0

    print(f"{'Dimension':<16}{'Weight':>8}{'Baseline':>11}{'Candidate':>11}{'Delta':>9}")
    print("-" * 55)

    deltas: dict[str, float] = {}
    for dim, weight in DIMENSIONS.items():
        base, cand = mean("baseline", dim), mean("candidate", dim)
        deltas[dim] = cand - base
        print(f"{dim:<16}{weight:>7.0%}{base:>11.3f}{cand:>11.3f}{cand - base:>+9.3f}")

    base_w = sum(weighted(r) for r in by_condition["baseline"]) / len(by_condition["baseline"])
    cand_w = sum(weighted(r) for r in by_condition["candidate"]) / len(by_condition["candidate"])
    print("-" * 55)
    print(f"{'WEIGHTED':<16}{'':>8}{base_w:>11.3f}{cand_w:>11.3f}{cand_w - base_w:>+9.3f}")

    # Blockers, split by whether the category makes them disqualifying.
    hard: list[str] = []
    soft: list[str] = []
    for row in by_condition["candidate"]:
        if not row.get("blocker"):
            continue
        category = category_of.get(row["case_id"], "unknown")
        entry = f"{row['case_id']} (trial {row.get('trial')}, {category})"
        (hard if category in HARD_BLOCK_CATEGORIES else soft).append(entry)

    print()
    print(f"blocking findings — disqualifying: {len(hard)}, other: {len(soft)}")
    for entry in hard:
        print(f"  DISQUALIFYING  {entry}")
    for entry in soft:
        print(f"  other          {entry}")

    # Release gate.
    checks = [
        ("no disqualifying blockers", not hard),
        ("fidelity within 0.1 of baseline", deltas["fidelity"] >= -0.1),
        ("correctness within 0.1 of baseline", deltas["correctness"] >= -0.1),
        ("safety within 0.1 of baseline", deltas["safety"] >= -0.1),
        ("weighted score beats baseline", cand_w > base_w),
    ]

    print()
    print("Release gate:")
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")

    passed = all(ok for _, ok in checks)
    print()
    print(f"RESULT: {'PASSED' if passed else 'FAILED'}")
    return 0 if passed else 1


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_evals.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Check cases, rubric, and runners").set_defaults(
        func=cmd_validate
    )

    plan = sub.add_parser("plan", help="Print what a run would cost")
    plan.add_argument("--trials", type=int, default=3)
    plan.add_argument("--include-comparator", action="store_true")
    plan.set_defaults(func=cmd_plan)

    run = sub.add_parser("run", help="Generate responses for one condition")
    run.add_argument("--runner", required=True)
    run.add_argument("--condition", required=True, choices=CONDITIONS)
    run.add_argument("--condition-skill", help="Skill file to inject for this condition")
    run.add_argument("--trials", type=int, default=3)
    run.add_argument("--output", default="evals/results/responses.jsonl")
    run.add_argument("--timeout", type=int, default=300)
    run.add_argument("--retries", type=int, default=2)
    run.add_argument("--limit", type=int, help="Only run the first N cases. Use for a cheap smoke run.")
    run.add_argument("--cases", help="Comma-separated case ids to run instead of the whole set.")
    run.set_defaults(func=cmd_run)

    score = sub.add_parser("score", help="Apply the release gate to a scores file")
    score.add_argument("scores")
    score.set_defaults(func=cmd_score)

    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except EvalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
