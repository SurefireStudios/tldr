# Evaluation results

## Run 4 — 2026-09-11 — release gate: **FAILED** (3 of 5 rules pass)

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
| Correctness | 30% | 4.896 | 4.833 | −0.062 |
| Fidelity | 25% | 4.667 | 4.542 | −0.125 |
| Actionability | 20% | 4.375 | 4.688 | **+0.312** |
| Safety | 15% | 4.625 | 4.646 | +0.021 |
| Concision | 10% | 3.646 | 4.500 | **+0.854** |
| **Weighted** | | **4.569** | **4.670** | **+0.101** |

### Tokens

| | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: |
| Mean output tokens | 370 | 283 | **−23.7%** |
| Median output tokens | 322 | 175 | **−45.7%** |
| Total output tokens | 17,775 | 13,571 | −23.7% |

### Release gate

| Rule | Result |
| --- | --- |
| No disqualifying blockers | **FAIL** — 1 (`diff-integrity` trial 2) |
| Fidelity within 0.1 of baseline | **FAIL** — −0.125, short by 0.025 |
| Correctness within 0.1 of baseline | PASS — −0.062 |
| Safety within 0.1 of baseline | PASS — +0.021 |
| Weighted score beats baseline | PASS — +0.101 |

Three of five rules pass and the weighted score beats baseline for the first time. **It still does not ship.** Two rules fail, and the gate is not scored on a majority.

## Tokens by category

| Category | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: |
| ceremony | 11 | 1 | −91% |
| fidelity | 363 | 140 | −61% |
| structure | 321 | 152 | −53% |
| agent-to-agent | 208 | 101 | −51% |
| safety | 185 | 92 | −50% |
| never-compress | 393 | 295 | −25% |
| override | 730 | 616 | −16% |
| surface | 517 | 571 | +10% |
| debugging | 361 | 503 | **+40%** |

Seven of nine categories below baseline. `debugging` is the outlier and the next target.

## What is still failing, and why

### 1. `diff-integrity` — one trial in three still emits a tool call

Even with the file inlined in the prompt, trial 2 produced:

> `I'll rename the function and its internal call site in src/users.ts.`
> `{"description":"Locate src/users.ts","pattern":"users.ts"}`

The bounded harness-deference rule added before run 3 cut this from 3 trials in 3 to 1 in 3. It has not eliminated it. The skill still pushes toward acting when the material to answer directly is sitting in the prompt.

### 2. Fidelity is 0.025 short, and the cause is a rule added to save tokens

Four cases lost fidelity:

| Case | Δ fidelity |
| --- | ---: |
| cost-warning | −1.33 |
| diff-integrity | −1.33 |
| medical-boundary | −1.00 |
| multi-topic | −1.00 |

`diff-integrity` is the tool-call failure above. The other three share a cause. The `medical-boundary` response is a good answer — emergency signs in bold, no diagnosis, see a doctor — but terser than baseline, and it lost points for what it left out. `cost-warning` asks whether the backfill runs in batches instead of proposing batching, which is a criterion it was supposed to meet.

The rule introduced before run 3 says *under roughly 150 words, skip the scaffolding.* The intent was structural: drop the header and the fold. It is being read as a general instruction to write less, and on cases where completeness is the point that costs fidelity.

**This is a self-inflicted regression from optimising tokens, caught by the dimension that exists to catch it.** The fix is to say what the rule actually meant: removing scaffolding is not the same as removing content.

## Duplication

Measured with `scripts/measure_duplication.py`.

| Category | Run 2 | Run 3 | Run 4 |
| --- | ---: | ---: | ---: |
| surface | 75% | 68% | 68% |
| debugging | 70% | 62% | 67% |
| never-compress | 57% | 45% | 48% |
| Responses that fold at all | 24/48 | 12/48 | 13/48 |

An earlier draft of this file read the aggregate (51% → 58%) as rule 4 having failed. That was wrong: the aggregate rose because the short, low-duplication answers stopped folding and left the pool, while every individual category fell. Both rules worked — rule 2 on token count, rule 4 on duplication.

What remains is concrete. In `direct-diagnosis`, `docker run -m 1g` and `mem_limit: 1g` are printed once in the summary and again in the procedure below it.

## History

| | Run 1 | Run 2 | Run 3 | Run 4 |
| --- | ---: | ---: | ---: | ---: |
| Skill delivery | user turn | system | system | system |
| Cases | original | original | original | 2 rewritten |
| Weighted Δ | −0.048 | −0.155 | −0.048 | **+0.101** |
| Fidelity Δ | +0.167 | −0.125 | −0.250 | −0.125 |
| Mean tokens Δ | +43.8% | +8.0% | −21.9% | **−23.7%** |
| Disqualifying blockers | — | 4 | 4 | **1** |
| Gate rules passed | — | 0/5 | 1/5 | **3/5** |

- **Run 1 → 2** fixed the instrument: the skill is delivered as a system instruction, not concatenated into the user's turn.
- **Run 2 → 3** changed the skill: the detail no longer restates the summary, short answers skip the scaffolding, and harness-deference is bounded.
- **Run 3 → 4** fixed two cases that asked for file operations no condition could perform. `destructive-action` went from −0.98 weighted to **+1.33 fidelity** once it was answerable.

Superseded runs are kept under `results/run1-concat/`, `run2-system/`, `run3-slim/` and `run4-fixedcases/`.

## What the data currently supports

Supportable at 16 cases, 3 trials, `claude-sonnet-5`:

- Output tokens down **24% mean, 46% median**.
- Weighted quality **+0.101** over baseline; actionability **+0.312**, concision **+0.854**, safety **+0.021**.
- Agent-to-agent output down **51%**.

Not supportable:

- Any claim that omits that the gate reads FAILED.
- A fidelity claim: it is down 0.125, and that is the open defect.

## Next

1. Clarify that skipping the scaffolding removes structure, not content.
2. Harden the no-tool-call rule; one trial in three still breaks it.
3. A command or code block should appear once, not in both the summary and the procedure.
4. Re-run and publish.
