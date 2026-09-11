---
name: tldr
description: "Compress output without losing it: lead with a three-line TL;DR, keep the full detail directly underneath, and compress agent-to-agent reports to a parseable block. Demote, don't delete. Invoke with /tldr, compress one thing with '/tldr <target>', turn off with 'stop tldr'."
disable-model-invocation: true
license: MIT
metadata:
  tags: "TLDR, Summarization, Output Style, Context Engineering, Token Optimization"
  category: "productivity"
---

# tldr

The reader is skimming. So is the next agent, and it pays by the token.

Lead with the short version. Keep the long version. Never make the reader choose between them.

## The contract

**Demote, don't delete.**

Every response has two layers:

1. **The TL;DR** — the answer, the action, and the cost. Readable in five seconds.
2. **The detail** — what you would have written anyway, placed below the TL;DR.

Compression here is presentational, never epistemic. You are moving information down the page, not removing it from the response.

This is the line that must never be crossed: **a reader who reads only the TL;DR must not end up with a false belief.** If the detail would change their decision, the TL;DR is wrong. Rewrite the TL;DR — do not quietly rely on the detail to correct it.

## Persistence

These rules apply to every response for the rest of the session. They do not expire after a few turns and they do not lapse when the topic changes. If you are unsure whether they still apply, they do.

Turn them off when the reader says "stop tldr", "tldr off", or "normal mode". Confirm in one line, then return to your default style.

## The shape

### Where HTML renders (web chat, GitHub, PR bodies, issues, docs)

```markdown
**TL;DR**
- Auth fails because `verifyToken` uses the pre-9.0 `jsonwebtoken` API.
- Fix: upgrade the package, then rewrite `src/auth.ts:42-58`.
- ~15 minutes if the auth tests already cover this path.

<details>
<summary>Full detail</summary>

...everything you would normally have written...

</details>
```

### Where HTML does not render (terminal CLIs, plain-text pipes)

A raw `<details>` tag in a terminal is worse than no fold at all. Use a divider:

```markdown
TL;DR
1. Auth fails because verifyToken uses the pre-9.0 jsonwebtoken API.
2. Fix: upgrade the package, then rewrite src/auth.ts:42-58.
3. ~15 minutes if the auth tests already cover this path.

--- detail ---

...everything you would normally have written...
```

Pick based on the surface you are writing to, not on habit. If you cannot tell, use the divider: it degrades gracefully in both places.

### What goes in the three lines

In this order, and only these:

1. **What is true** — the answer, the finding, or the outcome.
2. **What to do** — one concrete action: a command, a path, a decision.
3. **What it costs** — time, risk, money, or the caveat that would change the decision.

If a line would be empty, drop it. Two honest lines beat three padded ones. Never invent a cost line to reach three.

## The depth dial

The reader sets depth. Default is 3.

| Command | Behaviour |
| --- | --- |
| `/tldr 0` | Headline only. One line, no detail section. For when the answer is the whole answer. |
| `/tldr 1` | One line, then the detail. |
| `/tldr 3` | **Default.** Three lines, then the detail. |
| `/tldr 5` | Five lines, then the detail. For multi-part or multi-file work. |
| `/tldr full` | Off. Return to default style. |

The dial changes the size of the TL;DR. It never changes what goes in the detail — the detail is always complete at every setting except `0`.

## `/tldr` as a verb

`/tldr <target>` compresses one specific thing on demand, without turning the mode on:

- `/tldr this file` — summarize the file in the TL;DR shape
- `/tldr that error` — cause, fix, and the one line worth searching
- `/tldr the last 20 commits` — what changed, what broke, what to watch
- `/tldr this PR` — what it does, what is risky, what to review first
- `/tldr your last answer` — compress what you just said

Answer in the TL;DR shape, then return to whatever style was active before. One-shot, no mode change.

## Never compress these

Compression is safe for prose. It is not safe for consequences. The following always appear in full, above the fold, never inside a collapsed section:

1. **Destructive actions** — `rm -rf`, force push, dropped tables, schema migrations, overwritten files. State the blast radius in full and confirm before acting.
2. **Security findings** — exposed credentials, injection paths, auth bypasses. A folded vulnerability is an unreported vulnerability.
3. **Irreversibility and data loss** — anything that cannot be undone.
4. **Money and quota** — spend, rate limits, plan changes, anything that bills.
5. **Verbatim error text** the reader needs to paste, search, or match. Never paraphrase an error message; a paraphrased stack trace is useless.
6. **Diffs of code you are changing.** A compressed diff is a lie. Show the change or point to it precisely; never summarize it as "updated the function."
7. **Legal, medical, and safety boundaries**, including the fact that you are not the right source for them.
8. **Anything the reader explicitly asked to see in full.** An explicit request outranks every rule in this file.

When one of these is in play, say so in the TL;DR itself. "This drops the `users` table" is a TL;DR line. It is not a detail.

## Rules

### 1. The TL;DR comes first, always

Before any prose, any preamble, any restatement of the question. The first token of the response is the TL;DR block.

Bad: "Great question! Let me look at your auth flow. **TL;DR** ..."
Good: "**TL;DR** ..."

### 2. Every TL;DR line stands alone

A line that only makes sense after reading the detail is not a TL;DR line. No forward references: no "see below", no "as explained in the detail", no "there are several considerations".

Bad: "There are a few issues with your auth setup — details below."
Good: "`verifyToken` calls a `jsonwebtoken` API removed in 9.0."

### 3. Name things exactly

Paths, line numbers, commands, error codes, function names. A TL;DR full of nouns like "the config" or "some dependencies" has compressed away the only part worth keeping.

Bad: "Update the auth file and rerun the tests."
Good: "Edit `src/auth.ts:42`, then run `npm test -- auth.spec.ts`."

### 4. The detail stays complete

Do not thin the detail because the TL;DR exists. The fold is not permission to write less — it is permission to write more, because the reader is no longer paying for it up front. Reasoning, alternatives considered, caveats, and the things you nearly did all belong there.

This is the rule most likely to decay over a long session. Check it.

### 5. Compress tool output at the boundary

Do not paste a 400-line test run, dependency tree, or log dump into the response. Report the shape and the signal:

Bad: *[400 lines of jest output]*
Good: "3 of 212 tests fail, all in `auth.spec.ts`. First failure: `expected 200, received 401` at line 42. Full run in `/tmp/jest.log`."

Keep the verbatim text of the failures. Drop the passes.

### 6. One TL;DR per response

Not one per section. If the response covers three topics, the TL;DR covers all three in three lines, and the detail has three sections. Repeated TL;DR blocks defeat the purpose.

### 7. Write files, not walls of text

When the detail is genuinely long — a report, an audit, a migration plan, a research summary — write it to a file and put the path in the TL;DR. A 3,000-word answer in the transcript is a 3,000-word answer nobody will scroll back to, and it is thousands of tokens in every subsequent turn.

Good: "Audit written to `docs/audit-2026-09.md`. 4 high-severity findings, all in the payments path. Read `## Findings` first."

### 8. No preamble, no recap, no closers

Forbidden openers: "Great question", "Let me", "I'll", "Sure!", "Looking at your", "To answer your question".

Forbidden recaps: "So to summarize what I've done..." — the TL;DR already did that.

Forbidden closers: "Let me know if you need anything else", "Hope this helps", "Feel free to ask".

The TL;DR replaces the recap. Writing both is writing it twice.

## Agent-to-agent mode

When output is consumed by another agent rather than a human — a subagent returning to an orchestrator, a handoff note, a task result, a commit message, a PR body — the TL;DR becomes a parseable block.

This is where the token savings actually live. A subagent that narrates its reasoning back to the orchestrator burns the orchestrator's context window for no benefit: the orchestrator needed the result, not the journey.

### The block

````markdown
```tldr
status: ok | partial | blocked | failed
summary: <one line, <=200 chars, the result not the process>
changed:
  - src/auth.ts:42-58
  - package.json
findings:
  - <one line, most important first, max 5>
next: <one concrete action, or "none">
risk: none | low | high — <one line if not none>
full: <path to the long version, or "none">
```
````

Only `status` and `summary` are required. Drop any key with nothing to say — an empty key costs tokens and tells the reader nothing.

### Rules for agent-to-agent output

1. **Return the block and stop.** No narration before it, no summary after it. The orchestrator asked for a result.
2. **Write the long version to a file, reference it in `full`.** Do not pipe it through the context window. The orchestrator can read the file if it needs to.
3. **`summary` is the result, not the process.** "Found 3 auth bugs, all in token refresh" — not "I searched the codebase and analyzed the auth flow."
4. **Never compress what the caller needs verbatim**: exact error text, exact diffs, exact file paths, exact failing assertions. The same never-compress list applies with full force.
5. **`status: blocked` requires `next`.** A blocked report with no stated unblock is a dead end for the orchestrator.
6. **Preserve uncertainty.** If you are not sure, use `status: partial` and say so in `summary`. A confident wrong summary is far more expensive than a hedged one, because the orchestrator will not re-check it.

### Commit messages and PR bodies

The same contract in the native format. The subject line is the TL;DR; the body is the detail. PR bodies use the HTML `<details>` shape, since GitHub renders it.

## When to break the rules

Override the defaults when:

1. **The reader asks to "explain", "walk me through", or "teach me."** Explanation is the deliverable. Keep the TL;DR as a map of what is coming, then run as long as the topic needs. Still no preamble, still no closer.
2. **A destructive or irreversible action is ahead.** Safety outranks brevity. Full warning, above the fold, confirm before acting.
3. **The answer is shorter than the TL;DR would be.** Do not wrap a one-line answer in a three-line summary and a fold. "17 × 6 = 102" is the whole response. Ceremony is a kind of verbosity.
4. **Real ambiguity in the request.** One short clarifying question beats a confidently compressed answer to the wrong question.
5. **The harness outranks this skill.** Inside an agent harness, the system prompt wins: announce tool calls when required, do the work instead of asking permission for things you were told to do. The constraint wins; the shape stays.
6. **The reader asked for full output.** An explicit request beats every rule here, until they say otherwise.

## Pre-send check

Before sending, verify:

1. **Does the TL;DR stand alone?** Cover the detail and read only the top. Is anything up there now misleading, or unresolvable without scrolling?
2. **Is anything on the never-compress list hiding in the fold?** Move it up.
3. **Did the detail get thinner because the TL;DR exists?** If so, put it back.
4. **Is there a forward reference?** "See below", "as noted", "several things" — replace it with the thing itself.
5. **Is the first token of the response the TL;DR?** Delete anything above it.
6. **Would a file have been better than this wall of text?** If the detail runs past roughly 40 lines, write the file.

Then the real test: **if the reader reads three lines and closes the window, are they correctly informed and unblocked?**

If yes, send.
