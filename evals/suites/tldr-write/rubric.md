# Message quality rubric

<!-- judge:begin -->
<!-- scripts/judge.py copies everything between these two markers straight into the
     grading prompt. Anything that names a condition, or otherwise hints at which
     system wrote which response, belongs below judge:end rather than here. -->

You are grading drafts of a message that a **named third party will receive** — an email, a Slack reply, a pull request description, a code review comment, a commit message, a status update. The reader is not the person who asked for the draft. They did not choose to read it, it costs them attention, and they will form a view of the sender from it.

Judge responses blind: they are labelled `A`, `B`, or `C` and you are not told which system produced which. Score each dimension from 1 (fails) to 5 (excellent).

| Dimension | Weight | What to measure |
| --- | ---: | --- |
| Correctness | 25% | Is everything it says true and supported by the request? No invented dates, names, numbers, commitments or events. A message that reads well and states one thing the sender never said scores 1. |
| Fidelity | 25% | Is what mattered still *there*? The ask and its deadline, the blocker and who holds it, the caveat that would change the reader's decision, credit by name, the apology if one is owed, the bad news, the cost. A message that is shorter because it dropped one of these scores 1. |
| Appropriateness | 20% | Would the named recipient, reading this, feel respected? Does it match the register of what it answers, carry the reason behind a refusal, acknowledge harm before explaining it, and name the people who did the work? Brevity bought with the reader's goodwill is a failure here, not a win on concision. |
| Actionability | 15% | Does the first sentence carry the ask, the answer or the news? Can the reader tell what is wanted from them without reading to the end? |
| Concision | 15% | No preamble, no restating the question back, no signposting, no stacked hedges, no closing pleasantries, no bullet list where a sentence would do, no headers on a four-line message. Brevity that costs substance is a Fidelity failure; brevity that costs warmth is an Appropriateness failure. Neither is concision. |

## Appropriateness is the load-bearing dimension

The failure mode this rubric exists to catch is a message that is short, accurate, complete — and makes the reader think less of the sender.

A terseness instruction has a cheap cheat available. `"No."` is shorter than `"I can't this week — I'm on call and shipping Thursday. Friday works if that helps."` Both decline. Both are accurate. The first costs the sender a working relationship, and on every other dimension here it scores at least as well.

Score Appropriateness against this question: **if this arrived from a colleague, would you think they respected your time, or resented writing to you?**

Specific Appropriateness failures, each capping the score at 2:

- A refusal, deferral or rejection with no reason attached.
- Bad news stated without acknowledging its effect on the reader.
- An apology with a defence welded to it ("sorry, but the migration was scheduled").
- Work done by named people attributed to "the team".
- An acknowledgement of harm that arrives after the explanation rather than before it.
- A reply markedly terser than the message it answers, where that reads as a snub.
- Warmth performed rather than meant: a friendly opener attached to a message that ignores what the reader said.

Length is not itself a virtue or a fault on this dimension. A long message that wastes the reader's time scores badly. So does a short one that leaves them feeling dismissed.

## Blockers

Mark `blocker: true` for any of:

- A fabricated fact: a date, name, figure, event or commitment the request did not supply.
- The ask, the deadline or the blocker missing entirely from a message whose purpose was to convey it.
- Bad news softened to the point that a reader could finish the message without knowing it is bad.
- A cost, risk or irreversible consequence omitted.
- An apology owed and not given, or given with a defence attached.
- Failure to follow an explicit output contract the request stated.

<!-- judge:end -->

## Release gate

Ship the candidate only when all five hold:

1. It has no blocking findings in the `never-cut` or `tone` categories. Blockers elsewhere are counted and reported but do not block on their own.
2. Fidelity is within 0.1 points of baseline or better. **Compression must not cost information.**
3. Correctness is within 0.1 points of baseline or better.
4. **Appropriateness is within 0.1 points of baseline or better.** Compression must not cost the reader's goodwill.
5. Its weighted score is higher than baseline.

### Why appropriateness, and not safety

The `tldr` suite floors safety, because the thing that skill could trade away is a destructive command or a security finding buried below a fold. Those rarely appear in an email. What a writing skill can trade away instead is the reader's goodwill, and nothing in the other four dimensions can see it: the `"No."` above wins on concision, loses nothing factual, and is a message the sender would have to apologise for.

Every compression skill has one dimension it can cheat on. The job is to find it before shipping and weight it until the cheat loses. In the `tldr` suite that dimension is fidelity. Here it is appropriateness.

### A note on the baseline

The baseline condition is the task prompt with no style instruction, which already produces the hedged, preamble-laden, closer-stuffed draft this skill exists to fix. That makes the baseline easy to beat on concision and *hard* to beat on appropriateness — the padding is doing some social work, clumsily.

That is the right shape for this test. The interesting number is not whether the message got shorter. It is whether appropriateness held while it did.
