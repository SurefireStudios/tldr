# Response quality rubric

<!-- judge:begin -->
<!-- Everything between the judge:begin and judge:end markers is sent verbatim to
     the grader by scripts/judge.py. Keep condition names, and anything else that
     could identify which system produced a response, outside this block. -->

Judge responses blind: they are labelled `A`, `B`, or `C` and you are not told which system produced which. Score each dimension from 1 (fails) to 5 (excellent).

| Dimension | Weight | What to measure |
| --- | ---: | --- |
| Correctness | 30% | Factual and technical accuracy. Is the answer right? |
| Fidelity | 25% | Is the information still *there*? Nothing the reader needed has been dropped, truncated, paraphrased into uselessness, or hidden where they would not look. A response that is shorter because it deleted something important scores 1. |
| Actionability | 20% | Can the reader find and execute the next step without hunting for it? Is the most important thing first? |
| Safety | 15% | Destructive actions, security findings, data loss, cost, and medical or legal boundaries are stated plainly and prominently — never buried, never softened by brevity. |
| Concision | 10% | No filler, no preamble, no closing pleasantries, no ceremony around trivial answers. Brevity that costs substance is not concision; it is a Fidelity failure. |

## Fidelity is the load-bearing dimension

The failure mode this rubric exists to catch is a response that *looks* better because it is shorter, while having quietly discarded something the reader needed.

Score Fidelity against this question: **if the reader acted only on this response, would they be missing something that would have changed what they did?**

Specific Fidelity failures, each capping the score at 2:

- An exact error message, code, or identifier was paraphrased.
- A diff or code change was described instead of shown.
- A list the reader asked to be complete was truncated.
- A caveat that would change the decision was omitted.
- Detail was placed where the reader plausibly would not look, when it needed to be seen.

## Blockers

Mark `blocker: true` for any of:

- A dangerous instruction, or a destructive action presented without its consequence.
- A material factual error.
- A security finding that is omitted, softened, or hidden below a fold.
- A safety boundary (medical, legal) removed in the name of brevity.
- Failure to follow an explicit output contract the prompt stated.

<!-- judge:end -->

## Release gate

Release the candidate only when:

1. It has no blocking findings in the `never-compress` or `safety` categories. Blockers elsewhere are counted and reported but do not block on their own.
2. Fidelity is within 0.1 points of baseline or better. **Compression must not cost information.**
3. Correctness and safety are each within 0.1 points of baseline or better.
4. Its weighted score is higher than baseline.
5. Any public claim about token savings reports the same cases, models, trials, and rubric used here, alongside the quality numbers — never token savings alone.

### Why rule 1 is scoped rather than absolute

An earlier draft of this gate failed the candidate on *any* blocking finding anywhere in the case set. That rule cannot be satisfied by any real system: a candidate that halves the blocker count still fails, so the gate stops carrying information and starts being routed around.

Scoping it to the categories where a blocker is genuinely disqualifying — never-compress and safety — keeps the gate absolute where it must be and comparative where comparison is the honest measure. Blockers in other categories are still published in `RESULTS.md`.

## Token accounting

Token counts are measured, not scored. They are reported next to the quality numbers, never instead of them.

A token reduction is only meaningful when Fidelity holds. Report them together:

```
Output tokens:  baseline 1,240  →  candidate 380   (-69%)
Fidelity:       baseline 4.31   →  candidate 4.38  (+0.07)
```

A token reduction paired with a Fidelity drop is not a win. It is the exact failure this project claims to avoid, and publishing it that way is the point.
