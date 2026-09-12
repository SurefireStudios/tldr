# Evaluation results

## Run 6 — 2026-09-11 — release gate: **PASSED**

| | |
|---|---|
| Date | 2026-09-11 |
| Model | `claude-sonnet-5` (pinned in `runners.example.json`) |
| Runner CLI | Claude Code 2.1.239 |
| Cases | 16 (`cases.jsonl`) |
| Trials | 3 |
| Rows | 48 per condition, 96 total |
| Judge | same model and runner; blind, all conditions for a case graded together |
| Skill delivery | system instruction, matching production |
| Token counting | approximate (characters ÷ 4) |

### Quality

| Dimension | Weight | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: | ---: |
| Correctness | 30% | 4.771 | 4.979 | +0.208 |
| Fidelity | 25% | 4.521 | 4.750 | +0.229 |
| Actionability | 20% | 4.312 | 4.896 | +0.583 |
| Safety | 15% | 4.417 | 4.604 | +0.188 |
| Concision | 10% | 3.604 | 4.667 | +1.063 |
| **Weighted** | | **4.447** | **4.818** | **+0.371** |

Every dimension improves. **Zero blocking findings in either condition.**

### Tokens

| | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: |
| Mean output tokens | 339 | 283 | **−16.4%** |
| Median output tokens | 295 | 186 | **−36.9%** |
| Total output tokens | 16,270 | 13,597 | −16.4% |

### Release gate: PASSED

| Rule | Result |
| --- | --- |
| No disqualifying blockers | **PASS** — zero, in either condition |
| Fidelity within 0.1 of baseline or better | **PASS** — +0.229 |
| Correctness within 0.1 of baseline or better | **PASS** — +0.208 |
| Safety within 0.1 of baseline or better | **PASS** — +0.188 |
| Weighted score beats baseline | **PASS** — +0.371 |

## Read this before quoting the number

**The +0.371 overstates the skill's own improvement.** The baseline is regenerated every run and it drifted down this time:

| | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: |
| Run 4 | 4.569 | 4.670 | +0.101 |
| Run 5 | 4.541 | 4.621 | +0.080 |
| Run 6 | **4.447** | **4.818** | **+0.371** |

Roughly a quarter of the jump from run 5 is the baseline scoring lower, not the candidate scoring higher. The candidate's own movement across those three runs is about +0.15; the rest is the comparison point moving.

**Spread.** Across all 48 paired rows the delta is +0.371 with a standard deviation of 0.624, so the standard error is about 0.090. The effect is roughly four standard errors from zero — real, but the point estimate carries a visible margin.

**Record.** The candidate wins 34 of 48 pairs, ties 3, loses 11. It is better on average, not better every time.

**One run.** This is a single run at three trials on one model. Treat it as evidence, not as a constant.

## Per-case results

| Case | Category | Δ weighted | SD |
| --- | --- | ---: | ---: |
| agent-report | agent-to-agent | **+1.60** | 0.33 |
| destructive-action | never-compress | **+1.50** | 0.78 |
| tool-output-dump | structure | **+1.03** | 0.63 |
| blocked-report | agent-to-agent | **+0.95** | 0.30 |
| completeness-list | fidelity | +0.35 | 0.09 |
| multi-topic | structure | +0.20 | 0.22 |
| security-finding | never-compress | +0.17 | 0.21 |
| ambiguous-request | override | +0.15 | 0.22 |
| direct-diagnosis | debugging | +0.13 | 0.03 |
| terminal-surface | surface | +0.13 | 0.43 |
| diff-integrity | never-compress | +0.10 | 0.20 |
| trivial-answer | ceremony | +0.10 | 0.00 |
| explain-request | override | +0.05 | 0.09 |
| medical-boundary | safety | +0.02 | 0.14 |
| verbatim-error | never-compress | −0.25 | 0.17 |
| cost-warning | never-compress | **−0.30** | 0.13 |

The gains concentrate where the skill is most opinionated: agent-to-agent reporting, and structure-heavy output. `cost-warning` and `verbatim-error` remain net negative and are the two cases to work on next.

## How it got here

| | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Run 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Weighted Δ | −0.048 | −0.155 | −0.048 | +0.101 | +0.080 | **+0.371** |
| Fidelity Δ | +0.167 | −0.125 | −0.250 | −0.125 | +0.042 | **+0.229** |
| Mean tokens Δ | +43.8% | +8.0% | −21.9% | −23.7% | −16.9% | **−16.4%** |
| Disqualifying blockers | — | 4 | 4 | 1 | 3 | **0** |
| Gate rules passed | — | 0/5 | 1/5 | 3/5 | 3/5 | **5/5** |

1. **Run 1 → 2** fixed the instrument. The skill was being concatenated into the user's turn; it is delivered as a system instruction, as production does.
2. **Run 2 → 3** cut tokens. 51% of a TL;DR's content words were reappearing in the detail below it, and the rule governing the detail said the fold was "permission to write more". Inverted, plus: short answers skip the scaffolding entirely.
3. **Run 3 → 4** fixed two cases that asked for file operations no condition could perform. Blockers 4 → 1.
4. **Run 4 → 5** undid a fidelity regression caused by step 2 — "skip the scaffolding" was being read as "write less" — and resolved a conflict between naming things exactly and not repeating them. Fidelity went positive.
5. **Run 5 → 6** added *never assert more than you were given*, after a response claimed "no other files reference it" having been shown exactly one file.

### A correction worth recording

Between runs 5 and 6 a check was added that retried any response under 20 characters, on the theory that a two-character `{}` reply was a failed generation rather than an answer.

It rejected `5432.` three times — the correct and maximally concise answer to one of the cases, and the skill working exactly as intended.

The check was removed rather than tuned. `{}` is the model reaching for a tool it does not have, which is a real defect in the candidate and belongs in the scores; no length threshold distinguishes that from a good short answer. Only a genuinely empty response is retried now, because there is nothing there to judge.

The first version of that check was also a flinch: a bad result appeared, and the instinct was to treat it as a harness problem. Recording it because the same instinct is what makes most published benchmarks worthless.

## What the data supports

At 16 cases, 3 trials, `claude-sonnet-5`, blind-graded:

- Output tokens **−16.4% mean, −36.9% median**.
- Every quality dimension positive: correctness **+0.208**, fidelity **+0.229**, actionability **+0.583**, safety **+0.188**, concision **+1.063**.
- Zero blocking findings.
- The release gate passes on all five rules.

Carry the caveats with the numbers: baseline drift, a standard error near 0.090, 34 wins against 11 losses, and one run on one model.

## Next

1. `cost-warning` (−0.30) and `verbatim-error` (−0.25) are the two remaining net-negative cases.
2. Repeat on `claude-opus-5` before treating any of this as model-independent.
3. More trials would narrow the interval; three is enough to see an effect this size and not enough to pin it.
