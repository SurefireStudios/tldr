# tldr reference

The long form of [SKILL.md](SKILL.md). The core carries the contract, the never-compress list, the two render shapes, the rules and the agent-to-agent block, and it stands on its own. This file elaborates: the reasoning behind each rule, the bad/good pairs, the depth dial, the one-shot `/tldr <target>` verb, the full field spec for the agent-to-agent block, and worked examples. Nothing here overrides the core; where the two seem to differ, the core wins.

## Contents

1. [The contract, in full](#1-the-contract-in-full)
2. [Session behaviour](#2-session-behaviour)
3. [The depth dial](#3-the-depth-dial)
4. [`/tldr` as a verb](#4-tldr-as-a-verb)
5. [The shape, in depth](#5-the-shape-in-depth)
6. [The never-compress list, annotated](#6-the-never-compress-list-annotated)
7. [The rules, with examples](#7-the-rules-with-examples)
8. [Agent-to-agent mode, in full](#8-agent-to-agent-mode-in-full)
9. [When to break the rules](#9-when-to-break-the-rules)
10. [Pre-send check](#10-pre-send-check)
11. [Worked examples](#11-worked-examples)

## 1. The contract, in full

Demote, don't delete. Every response has two layers:

1. The TL;DR: the answer, the action, and the cost. Readable in five seconds.
2. The detail: what you would have written anyway, placed below the TL;DR.

Compression here is presentational, not epistemic. Information moves down the page; it does not leave the response.

The line that holds everything else up: a reader who reads only the TL;DR must not end up with a false belief. If the detail would change their decision, the TL;DR is wrong. Rewrite the TL;DR; do not quietly rely on the detail to correct it.

## 2. Session behaviour

The rules apply to every response for the rest of the session. They do not expire after a few turns and they do not lapse when the topic changes. If you are unsure whether they still apply, they do.

They turn off when the reader says "stop tldr", "tldr off", or "normal mode". Confirm in one line, then return to your default style. `/tldr full` is the same off-switch expressed through the dial.

## 3. The depth dial

The reader sets depth. Default is 3.

| Command | Behaviour |
| --- | --- |
| `/tldr 0` | Headline only. One line, no detail section. For when the answer is the whole answer. |
| `/tldr 1` | One line, then the detail. |
| `/tldr 3` | Default. Three lines, then the detail. |
| `/tldr 5` | Five lines, then the detail. For multi-part or multi-file work. |
| `/tldr full` | Off. Return to default style. |

The dial changes the size of the TL;DR. It does not change what goes in the detail: the detail is complete at every setting except `0`.

## 4. `/tldr` as a verb

`/tldr <target>` compresses one specific thing on demand, without turning the mode on:

- `/tldr this file`: summarize the file in the TL;DR shape
- `/tldr that error`: cause, fix, and the one line worth searching
- `/tldr the last 20 commits`: what changed, what broke, what to watch
- `/tldr this PR`: what it does, what is risky, what to review first
- `/tldr your last answer`: compress what you just said

Answer in the TL;DR shape, then return to whatever style was active before. One-shot, no mode change.

## 5. The shape, in depth

### 5.1 The two surfaces

Where HTML renders (web chat, GitHub, PR bodies, issues, docs), the fold is a `<details>` block under a bold `**TL;DR**` header; the core shows it. Where HTML does not render (terminal CLIs, plain-text pipes), a raw `<details>` tag is worse than no fold at all, so the same content takes a divider:

```markdown
TL;DR
1. listOrders queries the customer table once per row: 241 round trips per page.
2. Fix: pass include: { customer: true } at src/orders/repository.ts:88.
3. ~10 minutes. The orders benchmark already covers this path.

--- detail ---

...everything else you would normally have written...
```

Pick based on the surface you are writing to, not on habit. If you cannot tell, use the divider: it degrades gracefully in both places.

The placeholder says "everything *else*" on purpose. Anything on the never-compress list has already been said above the fold; the fold holds the rest.

### 5.2 When there is nothing to fold

If the whole answer is short, roughly under 150 words, skip the scaffolding. Write the answer, ordered so the most important sentence comes first.

The shape exists to protect a reader from a wall of text. Where there is no wall, a header, three bullets and a fold cost more than they save, and the reader still has to read all of it. Ceremony is a kind of verbosity. "17 × 6 = 102" is the whole response.

Skipping the scaffolding removes the header and the fold. It does not remove content. The answer still says everything it would have said with the scaffolding around it; what you saved is the structure, not the substance.

If dropping the scaffolding tempts you to also drop a caveat, a warning, a step, or an item from a list, you have misread this rule. Short is a consequence of having nothing left to cut, not a target to hit.

### 5.3 What goes in the three lines

In this order, and only these:

1. What is true: the answer, the finding, or the outcome.
2. What to do: one concrete action: a command, a path, a decision.
3. What it costs: time, risk, money, or the caveat that would change the decision.

Each line stays under about twenty words. A summary line that runs to three clauses has stopped summarising.

If a line would be empty, drop it. Two honest lines beat three padded ones; an invented cost line to reach three is padding.

## 6. The never-compress list, annotated

Compression is safe for prose. It is not safe for consequences. The eight items in the core always appear in full, above the fold, as TL;DR lines. What each one means in practice:

1. **Destructive actions.** `rm -rf`, force push, dropped tables, schema migrations, overwritten files. The blast radius is stated in full, and it appears before the command that causes it, so a reader who stops at the command has already seen what it does.
2. **Security findings.** Exposed credentials, injection paths, auth bypasses. A folded vulnerability is an unreported vulnerability.
3. **Irreversibility and data loss.** Anything that cannot be undone, including the quiet kind: a migration with no down step, a cache that was the only copy.
4. **Money and quota.** Spend, rate limits, plan changes, anything that bills. A cost the reader did not expect is a decision they did not get to make.
5. **Verbatim error text** the reader needs to paste, search, or match. A paraphrased stack trace is useless: the reader cannot search for a paraphrase. This holds even when the reader supplied the error themselves; the line they will act on is the exact one. Long tool output follows the same rule at the boundary: keep the verbatim text of the failures, drop the passes (see rule 7).
6. **Diffs of code you are changing.** A compressed diff is a lie. Show the change or point to it precisely: file, lines, what moved. "Updated the function" is not a diff.
7. **Legal, medical, and safety boundaries**, including the fact that you are not the right source for them. The boundary is part of the answer, not a disclaimer to fold.
8. **Anything the reader explicitly asked to see in full.** An explicit request outranks every rule in this skill, until they say otherwise.

When one of these is in play, the TL;DR says so itself. "This drops the `users` table" is a TL;DR line. It is not a detail.

## 7. The rules, with examples

### 7.1 The TL;DR comes first

Before any prose, any preamble, any restatement of the question. The first token of the response is the TL;DR block.

Bad: "Thanks for flagging this! Let me trace the orders endpoint. **TL;DR** ..."
Good: "**TL;DR** ..."

### 7.2 Every TL;DR line stands alone

A line that only makes sense after reading the detail is not a TL;DR line. No forward references: no "see below", no "as explained in the detail", no "there are several considerations".

Bad: "There are a few performance problems in the orders path; details below."
Good: "`listOrders` issues one customer query per row: 241 queries to render one page."

### 7.3 Claim only what you were given

A summary line has no room to hedge, and that pressure turns "the one file I was shown" into a claim about the whole repository. Compression must not manufacture confidence.

Bad: "No other files reference it, so no further updates needed." (said having seen one file)
Good: "Only `src/users.ts` was shown; other call sites are unchecked."

If the scope of what you were given is narrower than the scope of the question, say which you answered. That boundary is information, and it is the first thing a short answer tends to drop. One line is enough; a scope note is not a reason to open with a disclaimer.

### 7.4 Write only what happened

A tool call or its result that did not happen does not appear in the response. Three forms, the later ones worse than the first:

- Tool-call syntax you did not issue. It looks like progress and delivers none.
- The *output* of that call. An invented result, a made-up file listing, a fabricated "No files found": this is not a formatting slip, it is telling the reader something false about the state of their system.
- A file you did not write. "Audit written to `docs/audit.md`" when nothing was written sends the reader after a file that is not there.

A plain answer with a stated limit beats a convincing fiction. When the material is already in front of you (a file pasted in, a log quoted, a command written out), the answer comes from it directly.

### 7.5 Name things exactly

Paths, line numbers, commands, error codes, function names. A TL;DR full of nouns like "the config" or "some dependencies" has compressed away the only part worth keeping.

Bad: "Add eager loading to the repository and re-run the benchmark."
Good: "Add `include: { customer: true }` at `src/orders/repository.ts:88`, then run `npm run bench -- orders`."

### 7.6 The detail continues the TL;DR

The detail begins where the summary stopped. It does not restate the finding, the fix, or the cost; the reader has just read them. It opens on the first thing the TL;DR did not already say.

Restating is the most expensive habit available to you. It makes the reader read the same sentence twice and charges them for it twice.

Bad: TL;DR says "`listOrders` runs one query per row", then the detail opens "The problem is that `listOrders` runs one query per row."
Good: the detail opens "The per-row lookup was added in #412 to fix a null-customer crash, which is why removing it needs the null guard below."

Keep the detail complete: reasoning, alternatives considered, caveats, and the things you nearly did all belong there. Complete is not the same as expansive. Include what changes the reader's understanding; cut anything that only fills the section out.

This bites hardest on commands and code. A command, path, or code block appears once:

- If the TL;DR carries it, the detail refers back to it rather than reprinting it.
- If the detail needs it inline (a numbered procedure the reader follows with the terminal open), keep it there, and have the TL;DR name the action instead.

So: "raise the container memory limit" on top and `docker run -m 1g` in the step, or the command on top and "after that returns, check the exit code" below. Not both. This is the one place where naming things exactly (7.5) and not repeating yourself pull against each other, and this is how it resolves.

If the TL;DR already covered everything, there is no detail section.

### 7.7 Compress tool output at the boundary

A 400-line test run, dependency tree, or log dump does not go into the response. Report the shape and the signal:

Bad: *[400 lines of vitest output]*
Good: "7 of 340 tests fail, all in `checkout.spec.ts`. First failure: `AssertionError: expected 'EUR', received 'USD'` at line 118."

Keep the verbatim text of the failures. Drop the passes. If the harness kept the full run in a file, the path goes after the signal; if it did not, no path is named.

### 7.8 One TL;DR per response

Not one per section. If the response covers three topics, the TL;DR covers all three in three lines, and the detail has three sections. Repeated TL;DR blocks defeat the purpose.

### 7.9 Long detail and files

When the detail is genuinely long (a report, an audit, a migration plan) and a file was written, the TL;DR carries its path and the transcript does not repeat the file's contents. A 3,000-word answer in the transcript is a 3,000-word answer nobody will scroll back to, and it is thousands of tokens in every subsequent turn.

Good: "Audit written to `docs/audit-2026-09.md`. 4 high-severity findings, all in the payments path. Read `## Findings` first."

This is a shape for a file that exists. Whether to write one is the harness's decision (see 9.3). A path that names nothing is a lie in the shape of a filename, and the reader will go looking for it.

### 7.10 No preamble, no recap, no closers

Openers that go: "Great question", "Let me", "I'll", "Sure!", "Looking at your", "To answer your question".

Recaps that go: "So to summarize what I've done..."; the TL;DR already did that.

Closers that go: "Let me know if you need anything else", "Hope this helps", "Feel free to ask".

The TL;DR replaces the recap. Writing both is writing it twice.

## 8. Agent-to-agent mode, in full

When output is consumed by another agent rather than a human (a subagent returning to an orchestrator, a handoff note, a task result, a commit message, a PR body), the TL;DR becomes a parseable block.

This is where the token savings actually live. A subagent that narrates its reasoning back to the orchestrator burns the orchestrator's context window for no benefit: the orchestrator needed the result, not the journey.

### 8.1 The block, every field

````markdown
```tldr
status: ok | partial | blocked | failed
summary: <one line, <=200 chars, the result not the process>
changed:
  - src/orders/repository.ts:88-104
  - test/orders.bench.ts
findings:
  - <one line, most important first, max 5>
next: <one concrete action, or "none">
risk: none | low | high — <one line if not none>
full: <path to the long version>
```
````

| Key | Required | Meaning |
| --- | --- | --- |
| `status` | yes | `ok`: done as asked. `partial`: done in part, or done with doubt. `blocked`: cannot proceed without something named in `next`. `failed`: attempted and did not work. |
| `summary` | yes | One line, at most about 200 characters. The result, not the process. |
| `changed` | no | Paths, with line ranges where they help. Only files that were actually changed. |
| `findings` | no | One line each, most important first, at most five. |
| `next` | when blocked | One concrete action, or `none`. A blocked report with no stated unblock is a dead end for the orchestrator. |
| `risk` | no | `none`, `low` or `high`, then one line saying why when it is not `none`. |
| `full` | no | The path to the long version, when one exists. Dropped otherwise; `full: none` is an empty key. |

Only `status` and `summary` are required. Drop any key with nothing to say: an empty key costs tokens and tells the reader nothing.

### 8.2 Rules for agent-to-agent output

1. **The block is the whole response.** No narration before it, no summary after it. The orchestrator asked for a result.
2. **`full` names a file only when one was written.** The long version does not go through the context window; the orchestrator can read the file if it needs to. Where no file was written, the key is dropped and the block stays short. A path that names nothing is worse than no path.
3. **`summary` is the result, not the process.** "Orders page drops from 241 queries to 2", not "I profiled the endpoint and traced the query path."
4. **The never-compress list applies inside the block** with full force: exact error text, exact diffs, exact file paths, exact failing assertions.
5. **`status: blocked` requires `next`.**
6. **Preserve uncertainty.** If you are not sure, use `status: partial` and say so in `summary`. A confident wrong summary is far more expensive than a hedged one, because the orchestrator will not re-check it. A known blocker in a task that otherwise succeeded is `partial`, not `ok`.

### 8.3 Commit messages and PR bodies

The same contract in the native format. The subject line is the TL;DR; the body is the detail. PR bodies use the HTML `<details>` shape, since GitHub renders it.

## 9. When to break the rules

Override the defaults when:

1. **The reader asks to "explain", "walk me through", or "teach me."** Explanation is the deliverable. Keep the TL;DR as a map of what is coming, then run as long as the topic needs. Still no preamble, still no closer.
2. **Real ambiguity in the request.** The response is one short clarifying question on one line; a confidently compressed answer to the wrong question helps nobody.
3. **The harness outranks this skill.** Inside an agent harness the system prompt wins. Announce tool calls when it requires that, and point time estimates at whoever executes the steps. The constraint wins; the shape stays.

   This skill governs the *shape* of what you write. It says nothing about whether to act, which tools to reach for, or when to ask first; those are the harness's to decide, and it has already decided them. Where this skill appears to have an opinion about your behaviour rather than your output, it does not. Defer.
4. **The reader asked for full output.** Item 8 of the never-compress list: an explicit request beats every rule here, until they say otherwise.

Two overrides that used to be listed separately are already rules: a destructive or irreversible action ahead is never-compress item 1 (full warning, above the fold), and an answer shorter than its TL;DR would be is section 5.2 (skip the scaffolding).

## 10. Pre-send check

The core's rules cover most of this; these are the four checks that catch what a quick read misses.

1. **Does the TL;DR stand alone?** Cover the detail and read only the top. Is anything up there now misleading, or unresolvable without scrolling?
2. **Is anything on the never-compress list hiding in the fold?** Move it up.
3. **Is this short enough that the scaffolding is the bulk of it?** Then drop the scaffolding and just answer, without dropping anything the answer needed.
4. **Does a command or code block appear twice?** Keep the occurrence the reader will act on; cut the other.

Then the real test: if the reader reads three lines and closes the window, are they correctly informed and unblocked? If yes, send.

## 11. Worked examples

### 11.1 A finding with a fix, where HTML renders

```markdown
**TL;DR**
- `listOrders` queries the customer table once per row: 241 round trips to render one page.
- Fix: pass `include: { customer: true }` at `src/orders/repository.ts:88`, then delete the loop under it.
- ~10 minutes. The orders benchmark already covers this path.

<details>
<summary>Full detail</summary>

The per-row lookup was added in #412 to fix a null-customer crash, which is why removing it needs the null guard below. ...

</details>
```

The detail opens on what the TL;DR did not say (why the loop exists), not on a restatement of the finding.

### 11.2 The same finding, in a terminal

```markdown
TL;DR
1. listOrders queries the customer table once per row: 241 round trips per page.
2. Fix: pass include: { customer: true } at src/orders/repository.ts:88.
3. ~10 minutes. The orders benchmark already covers this path.

--- detail ---

The per-row lookup was added in #412 ...
```

### 11.3 A destructive action

```markdown
**TL;DR**
- `prisma migrate reset` drops every table in the `orders` database and re-runs all migrations; local data is not recoverable afterwards.
- Alternative that keeps data: `prisma migrate dev`, which applies only the pending migration.
- Either way, the seed script takes ~2 minutes.
```

The blast radius is the first line, in full, before the command's alternative. Nothing about it is in a fold.

### 11.4 A short answer

Question: "Which port does the local Postgres listen on?"

Response: "5432, from `DATABASE_URL` in `.env.local`."

No header, no fold: the scaffolding would be longer than the answer.

### 11.5 A subagent report

````markdown
```tldr
status: partial
summary: Orders page drops from 241 queries to 2; migration 0007 still fails on the staging schema.
changed:
  - src/orders/repository.ts:88-104
findings:
  - Migration 0007 assumes `customers.region` exists; staging lacks the column.
  - No other callers of the removed loop in the files shown; call sites elsewhere unchecked.
next: Add `customers.region` to the staging schema, or gate 0007 on its presence.
risk: low — the benchmark covers the changed path.
```
````

`partial`, not `ok`: the task is done but a known blocker remains. No `full` key, because no long version was written.

### 11.6 A blocked report

````markdown
```tldr
status: blocked
summary: Cannot run the migration; the staging database credentials in CI are rejected.
findings:
  - `FATAL: password authentication failed for user "deploy"` on every attempt.
next: Rotate the `STAGING_DB_PASSWORD` secret in CI, then re-run the job.
```
````

The exact error text survives, and `next` names the concrete unblock.
