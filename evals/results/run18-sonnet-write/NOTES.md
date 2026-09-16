# Run 18 — what these files are

`claude-sonnet-5`, suite `tldr-write`, 16 cases × 3 trials, 2026-09-16.

**Release gate: FAILED** (1 of 5 rules). This run is published because it failed,
not despite it: it is the measurement that produced the fixes shipped in run 19.

Every other run directory in `evals/results/` holds exactly two files. This one
carries a note because its grading pass was thrown away and redone, and a reader
who finds `scores.jsonl` on its own has no way to know which pass it is.

## The scores here are the second grading pass. The first was discarded.

`judge.py` wrote the grader's output contract by hand, hardcoding the *default*
suite's five dimension names:

    [{"label":"A","correctness":5,"fidelity":5,"actionability":5,"safety":5,"concision":5,...}]

The `tldr-write` suite grades **appropriateness** and does not grade safety. So the
grader was asked for a key nobody scores and never asked for the one the gate
floors. 35 of 48 groups failed to parse with `appropriateness=None is not 1-5`.

The 13 that did parse were worse than useless: they succeeded by ignoring the
example and reading the rubric table instead — a sample selected by how carefully
the judge disobeyed its instructions. Those 13 rows were deleted, not kept.

The judge's contract is generated from the active suite now, and
`tests/test_eval_harness.py::TestJudgeContractFollowsTheSuite` fails if any suite
is ever asked for dimensions it does not grade.

**`scores.jsonl` in this directory is the clean re-grade: 48 of 48 groups, 0
failures, every row carrying an appropriateness score.** The numbers below are
sound. They describe a version of the skill that should not ship, which is a
different thing from being unsound.

## What it measured

| Dimension | Weight | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: | ---: |
| Correctness | 25% | 4.438 | 4.854 | +0.417 |
| Fidelity | 25% | 4.771 | 4.688 | −0.083 |
| Appropriateness | 20% | 4.104 | 4.521 | +0.417 |
| Actionability | 15% | 3.604 | 4.917 | +1.313 |
| Concision | 15% | 2.812 | 4.958 | +2.146 |
| **Weighted** | | **4.085** | **4.771** | **+0.685** |

Tokens 237 → 87 (−63.6%). Four of five gate rules passed. Rule 1 failed on two
disqualifying blockers, both on `credit-survives`.

## The two defects it found

**The skill invented calendar dates.** The prompt says "last Thursday's load
test"; two of three trials wrote "Thu Sep 11", a date nobody supplied — and Sep 11
2026 is a Friday, so it was not even internally consistent. The cause was a
conflict inside the skill: "Name things exactly: dates, not 'soon'" was outranking
"never invent a date". The rule carries its precedence now. Fabricated dates fell
from 3 of 48 here to 1 of 48 in run 19.

Note the blocker fired on `credit-survives`, but credit was never the problem —
Priya and Dan are named in all three trials. The never-cut list held; the
fabrication rule did not.

**One case was wrong rather than hard.** `explain-requested` asked the model to
write "your full reasoning on why you chose SQS over Kafka" without supplying any
reasoning. The only way to satisfy the "write long when asked" override was to
fabricate an architecture rationale, which the never-cut list forbids. The skill
returned a skeleton and the judge marked it a blocker; the skill was right and the
case was unpassable. It now supplies the reasoning and tests what it meant to.

A case that can only be passed by fabricating is not a hard case. It is a broken
one, and it would have gone on producing a blocker every run until someone read
the response instead of the score.

## Successor

Run 19 — same suite and model, both fixes applied — passed 5 of 5.
See [`../../RESULTS.md`](../../RESULTS.md).
