# Evaluation results

## Status: no run published yet

The harness in [`scripts/`](../scripts/) is complete and runnable. **No scored run has been published against it yet**, so this file has no numbers in it.

That is deliberate. The alternative — shipping plausible-looking figures and backfilling the run later — is the thing this project exists to argue against. There are no numbers in the README either, for the same reason.

To produce the first published run, follow [README.md](README.md) and replace this file with the template below.

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3

python3 scripts/run_evals.py run --runner claude --condition baseline \
  --trials 3 --output evals/results/responses.jsonl
python3 scripts/run_evals.py run --runner claude --condition candidate \
  --condition-skill skills/tldr/SKILL.md \
  --trials 3 --output evals/results/responses.jsonl

python3 scripts/judge.py --runner claude \
  --responses evals/results/responses.jsonl \
  --output evals/results/scores.jsonl

python3 scripts/run_evals.py score evals/results/scores.jsonl
python3 scripts/count_tokens.py evals/results/responses.jsonl
```

At 16 cases and 3 trials that is 96 generation calls plus 48 judging calls.

---

## Template for a published run

Replace everything above this line with the filled-in version.

### Run metadata

| | |
|---|---|
| Date | `YYYY-MM-DD` |
| Model | `<pinned model id from runners.example.json>` |
| Runner CLI | `<tool and exact version>` |
| Cases | 16 (`cases.jsonl`) |
| Trials | 3 |
| Rows | 48 per condition, 96 total |
| Judge | same model and runner, blind, one call per `(case, trial)` group |
| Reported cost | `$X.XX` generation + `$X.XX` judging |

### Quality

| Dimension | Weight | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: | ---: |
| Correctness | 30% | | | |
| Fidelity | 25% | | | |
| Actionability | 20% | | | |
| Safety | 15% | | | |
| Concision | 10% | | | |
| **Weighted** | | | | |

### Tokens

| | Baseline | Candidate | Δ |
| --- | ---: | ---: | ---: |
| Mean output tokens | | | |
| Median output tokens | | | |
| Total output tokens | | | |

**Report these two tables together, always.** A token reduction paired with a Fidelity drop is not a win — it is the exact failure this project claims to avoid, and publishing it that way is the point.

### Blocking findings

| Category | Baseline | Candidate | Disqualifying? |
| --- | ---: | ---: | --- |
| `never-compress` | | | yes |
| `safety` | | | yes |
| everything else | | | no |

### Release gate: `PASSED` / `FAILED`

State which rules passed and which failed, and why. If the gate failed, say so in the heading and leave the numbers in place. If a gate rule turns out to be badly specified, argue that in writing here rather than quietly relaxing it — a gate that gets edited whenever it fails is not a gate.

### Per-case weighted scores

| Case | Category | Baseline | Candidate | Δ | Candidate SD |
| --- | --- | ---: | ---: | ---: | ---: |

### Notes

Anything that would change how a reader interprets the numbers: cases no run can pass, high-variance cases, model-specific behaviour, or places where the rubric itself proved to be the weak link.
