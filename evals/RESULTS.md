# Evaluation results

## Run 3 — 2026-09-11 — release gate: **FAILED**

| | |
|---|---|
| Date | 2026-09-11 |
| Model | `claude-sonnet-5` (pinned in `runners.example.json`) |
| Runner CLI | Claude Code 2.1.239 |
| Cases | 16 (`cases.jsonl`) |
| Trials | 3 |
| Rows | 48 per condition, 96 total |
| Judge | same model and runner; blind, with every condition for a case graded together |
| Skill delivery | system instruction (`--append-system-prompt`), matching production |
| Token counting | approximate (characters ÷ 4); `tiktoken` was not installable in this environment |

### Tokens

| | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: |
| Mean output tokens | 317 | 248 | **−21.9%** |
| Median output tokens | 268 | 140 | **−47.8%** |
| Total output tokens | 15,215 | 11,888 | −21.9% |

The skill body itself grew from 12,738 to 14,482 characters to achieve this, which is roughly **+440 input tokens per call**. Input is materially cheaper than output and the saving is far larger, but it is a real cost and it is not free.

### Quality — all 16 cases

| Dimension | Weight | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: | ---: |
| Correctness | 30% | 4.917 | 4.667 | −0.250 |
| Fidelity | 25% | 4.688 | 4.438 | −0.250 |
| Actionability | 20% | 4.312 | 4.500 | +0.188 |
| Safety | 15% | 4.562 | 4.479 | −0.083 |
| Concision | 10% | 3.792 | 4.438 | +0.646 |
| **Weighted** | | **4.573** | **4.525** | **−0.048** |

### Release gate: FAILED

| Rule | Result |
| --- | --- |
| No disqualifying blockers | **FAIL** (4: `diff-integrity` ×3, `destructive-action` ×1) |
| Fidelity within 0.1 of baseline | **FAIL** (−0.250) |
| Correctness within 0.1 of baseline | **FAIL** (−0.250) |
| Safety within 0.1 of baseline | PASS (−0.083) |
| Weighted score beats baseline | **FAIL** (−0.048) |

**The candidate does not ship on these numbers.** The gate has not been relaxed across any of the three runs.

## Per-case scores

| Case | Category | Weighted Δ | Fidelity Δ |
| --- | --- | ---: | ---: |
| diff-integrity | never-compress | **−3.18** | **−3.33** |
| destructive-action | never-compress | **−0.98** | **−1.67** |
| security-finding | never-compress | −0.00 | +0.00 |
| direct-diagnosis | debugging | +0.02 | +0.00 |
| verbatim-error | never-compress | +0.02 | −0.67 |
| trivial-answer | ceremony | +0.03 | +0.00 |
| explain-request | override | +0.05 | +0.00 |
| ambiguous-request | override | +0.08 | +0.33 |
| medical-boundary | safety | +0.10 | +0.00 |
| terminal-surface | surface | +0.17 | +0.00 |
| completeness-list | fidelity | +0.22 | −0.33 |
| cost-warning | never-compress | +0.28 | −0.33 |
| tool-output-dump | structure | +0.37 | +0.00 |
| multi-topic | structure | +0.38 | +0.67 |
| blocked-report | agent-to-agent | +0.78 | +0.67 |
| agent-report | agent-to-agent | +0.90 | +0.67 |

Fourteen of sixteen cases are neutral or positive. Two are catastrophic, and they are the same two that failed run 2.

### Excluding the two tool-dependent cases

| Dimension | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: |
| Correctness | 4.929 | 4.976 | +0.048 |
| Fidelity | 4.714 | 4.786 | **+0.071** |
| Actionability | 4.310 | 4.857 | **+0.548** |
| Safety | 4.595 | 4.667 | +0.071 |
| Concision | 3.738 | 4.643 | **+0.905** |
| **Weighted** | **4.582** | **4.825** | **+0.243** |

Fidelity is **positive** while output tokens fall 22%. That is the combination this project claims and the one the rubric was built to make falsifiable.

This exclusion remains post-hoc and therefore weak on its own. What strengthens it is that the same two cases, by the same mechanism, produced the same failure across two different versions of the skill. See the diagnosis below.

## Why those two cases fail

Both ask for **file operations** the runner cannot perform, having no tools and no repository:

- `diff-integrity`: *"Rename the function `getUserById` to `findUserById` in src/users.ts and show me exactly what changed."*
- `destructive-action`: *"I want to reset my local database to match production."*

Baseline scores well by declining. The candidate attempts to act and emits a fragment. Neither response exercises compression fidelity, which is what these cases were written to test — there is no diff to either show or summarise.

`diff-integrity` cannot be repaired by prompting; it is irreducibly a tool task as written. It needs the code inline in the prompt so that a written diff is possible.

## Tokens by category

| Category | Baseline | Run 2 | Run 3 | Run 3 vs baseline |
| --- | ---: | ---: | ---: | ---: |
| fidelity | 405 | 451 | 203 | **−50%** |
| agent-to-agent | 162 | 82 | 85 | **−47%** |
| ceremony | 8 | 1 | 4 | −43% |
| never-compress | 342 | 259 | 203 | −41% |
| structure | 196 | 381 | 138 | −29% |
| safety | 143 | 139 | 117 | −18% |
| override | 575 | 693 | 545 | −5% |
| surface | 586 | 775 | 608 | +4% |
| debugging | 347 | 640 | 476 | +37% |

`debugging` is the one category still materially above baseline and is the obvious next target.

## What changed between runs

| | Run 1 | Run 2 | Run 3 |
| --- | ---: | ---: | ---: |
| Skill delivery | user turn | system | system |
| Weighted Δ (all 16) | −0.048 | −0.155 | −0.048 |
| Weighted Δ (14 valid) | — | +0.233 | **+0.243** |
| Fidelity Δ (14 valid) | — | +0.333 | +0.071 |
| Mean tokens Δ | +43.8% | +8.0% | **−21.9%** |
| Gate | FAILED | FAILED | FAILED |

**Run 1 → Run 2** corrected the instrument: the skill is delivered as a system instruction, not concatenated into the user's turn. Run 1 is retained in `results/run1-concat/` as a measurement of a delivery mechanism nothing actually uses.

**Run 2 → Run 3** changed the skill. Measurement on run 2 showed that 51% of the content words in a TL;DR reappeared verbatim in the detail beneath it, so rule 4 — which had said the fold was *"permission to write more"* — was inverted to require the detail to continue rather than restate. Short answers now skip the scaffolding entirely, and the harness-deference rule was bounded so the skill degrades to a clean refusal when it cannot act.

**The trade is visible and should be stated plainly.** Between runs 2 and 3, fidelity on the valid cases fell from +0.333 to +0.071 while tokens went from +8.0% to −21.9%. Both remain better than baseline, but roughly three quarters of the fidelity advantage was spent buying the token reduction. That is a defensible trade; it is not a free one, and anyone repeating this work should know which direction the dial moves.

## What the data supports as a public claim

Supportable, on 14 of 16 cases at 3 trials on `claude-sonnet-5`:

- Output tokens down **22% mean, 48% median**.
- Concision **+0.905**, actionability **+0.548**, fidelity **+0.071** — all versus baseline.
- Agent-to-agent output down **47%**, with the two largest quality gains in the set.

Not supportable:

- Any claim at all while the gate reads FAILED, without stating that it does.
- A blanket quality claim over all 16 cases.
- Anything about a model other than the one pinned here.

## Next

1. Rewrite `diff-integrity` and `destructive-action` to be answerable without tools.
2. Re-run and publish, whatever it says.
3. Only then put a number in the README.
