# Evaluations

This harness measures two things that output-style prompts are usually asked to trade against each other:

- **Quality** — correctness, fidelity, actionability, safety, and concision, graded blind against a baseline.
- **Tokens** — actual output-token counts, because the entire point of compression is cost.

Reporting either one alone is how compression claims get to be misleading. A skill that halves your token count by deleting the caveat that would have stopped you is not a win, and this harness is built to catch exactly that.

The scoring contract is [`rubric.md`](rubric.md). The cases are [`cases.jsonl`](cases.jsonl).

## Conditions

| Condition | What it is |
| --- | --- |
| `baseline` | The bare task prompt, no style instruction |
| `candidate` | The same prompt plus `skills/tldr/SKILL.md` |
| `comparator` | The same prompt plus some other skill, via `--condition-skill` |

Task prompts are identical across conditions. Only the injected instruction differs, so the comparison measures the instruction and nothing else.

## Validate and plan

Neither command touches the network.

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3
```

`validate` also checks that the judge region of the rubric does not name the conditions — sending that text to a blind grader would leak the vocabulary the blinding exists to hide.

## Run

Run each condition into the same results file.

```bash
python3 scripts/run_evals.py run \
  --runner claude \
  --condition baseline \
  --trials 3 \
  --output evals/results/responses.jsonl

python3 scripts/run_evals.py run \
  --runner claude \
  --condition candidate \
  --condition-skill skills/tldr/SKILL.md \
  --trials 3 \
  --output evals/results/responses.jsonl
```

Runs are resumable: rerun the same command after a provider failure and completed `(case, trial, condition, runner)` rows are skipped. Each incomplete call is retried twice by default and the final provider error is preserved in the output.

### Isolation is not optional

Both example runners isolate the call from the operator's own agent configuration: `--setting-sources ""` for Claude, `--ignore-user-config --ephemeral` for Codex. Keep that isolation when adding a runner. Without it, user-level plugins, hooks, memory, and output styles leak into every condition and shape the responses being judged.

The sharpest case is this repo's own always-on flag (`~/.claude/.tldr-always`), which would inject the full tldr ruleset into the **baseline** condition and make the comparison measure the skill against itself.

Isolation also drops the operator's saved model and effort settings, so the Claude runner pins `--model` explicitly. Keep a pin when editing a runner: without one, the eval silently runs whatever the operator — or the CLI release — happens to default to. The model would vary between operators and over time, and per-token cost varies with it. The pinned model is part of the result. Record it with any published numbers.

## Judge

```bash
python3 scripts/judge.py \
  --runner claude \
  --responses evals/results/responses.jsonl \
  --output evals/results/scores.jsonl
```

Responses are grouped by `(case_id, trial)` and every condition for a case is graded in one call, so the conditions are compared against each other rather than scored in isolation.

Blinding is structural, not a convention the grader is asked to respect: each condition is relabelled `A`/`B`/`C` before the prompt is built, and the label order is permuted per group. The permutation comes from a digest of the group key rather than a random source, so a resumed run reproduces the labels it used the first time.

Only the region of `rubric.md` between the `<!-- judge:begin -->` and `<!-- judge:end -->` markers reaches the grader. The release-gate rules below those markers name the conditions. Keep anything condition-identifying outside that block.

A group missing a condition cannot be scored — the conditions would no longer be judged on identical rows — so it is reported on stderr and left out rather than silently dropped.

### Grading by hand

Also supported. Blind the `condition` field yourself and write one JSON object per response:

```json
{"case_id":"security-finding","trial":1,"condition":"candidate","correctness":5,"fidelity":5,"actionability":5,"safety":5,"concision":4,"blocker":false,"notes":"SQL injection reported in the summary, not folded."}
```

## Score

```bash
python3 scripts/run_evals.py score evals/results/scores.jsonl
python3 scripts/count_tokens.py evals/results/responses.jsonl
```

The first applies the release gate. The second reports token counts. **Publish both.** The rubric's token-accounting section explains why a token number on its own is not a result.

Exit code is `0` when the gate passes and `1` when it fails, so the gate can run in CI.

## Adding a case

Cases are one JSON object per line:

```json
{"id":"kebab-case-id","category":"never-compress","prompt":"...","risk":"high","criteria":["...","..."]}
```

`risk` is `low`, `medium`, or `high`. `category` is free-form, but two values are load-bearing: a blocking finding in **`never-compress`** or **`safety`** disqualifies the candidate outright, while blockers elsewhere are counted and reported without blocking on their own.

The most valuable cases to add are traps — prompts where compressing would lose something that matters. If you find a real-world case where `tldr` dropped something it should have kept, that case belongs here before the fix does.

Run `python3 scripts/run_evals.py validate` after editing.

## Reporting results

Record the exact CLI version, model, case count, trial count, and rubric with any published numbers. Do not compare conditions produced with different cases, models, trial counts, or rubrics.

Publish results whether or not they flatter the skill, including runs that fail the gate. A benchmark that only appears when it wins is marketing, not measurement.
