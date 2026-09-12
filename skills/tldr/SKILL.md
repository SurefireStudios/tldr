---
name: tldr
description: "Compress output without losing it: lead with a three-line TL;DR, keep the full detail directly underneath, and compress agent-to-agent reports to a parseable block. Demote, don't delete. Invoke with /tldr, compress one thing with '/tldr <target>', turn off with 'stop tldr'."
disable-model-invocation: true
user-invocable: true
license: MIT
homepage: https://github.com/SurefireStudios/tldr
metadata:
  tags: "TLDR, Summarization, Output Style, Context Engineering, Token Optimization"
  category: "productivity"
  openclaw: { "emoji": "📄" }
  cybara: { "homepage": "https://github.com/SurefireStudios/tldr" }
---

# tldr

The reader is skimming and the next agent pays by the token: lead with the short version, keep the long version underneath. Elaborations and examples: [reference.md](reference.md).

## The contract

**Demote, don't delete.** Compression moves information down the page; it removes nothing. A reader who reads only the TL;DR must not end up with a false belief. If the detail would change their decision, the TL;DR is wrong.

## Never compress these

These appear in full, above the fold, never inside a collapsed section, and the TL;DR names them itself ("This drops the `users` table" is a TL;DR line):

1. Destructive actions (`rm -rf`, force push, dropped tables, schema migrations, overwritten files): the blast radius in full, before the command that causes it.
2. Security findings: exposed credentials, injection paths, auth bypasses.
3. Irreversibility and data loss: anything that cannot be undone.
4. Money and quota: spend, rate limits, plan changes, anything that bills.
5. Verbatim error text the reader will paste, search or match; a paraphrased error is useless.
6. Diffs of code you are changing: show the change or point to it precisely.
7. Legal, medical and safety boundaries, including that you are not the right source.
8. Anything the reader asked to see in full; that request outranks every rule here.

## The shape

Where HTML renders:

```markdown
**TL;DR**
- `listOrders` queries the customer table per row: 241 queries per page.
- Fix: `include: { customer: true }` at `src/orders/repository.ts:88`.
- ~10 minutes; the orders benchmark covers this path.

<details>
<summary>Full detail</summary>

...everything else you would normally have written...

</details>
```

In a terminal a raw `<details>` tag is worse than no fold: a plain `TL;DR` line, the same three lines numbered, then `--- detail ---` and the rest. Unsure which surface? Use the divider. The never-compress list stays out of the fold.

The three lines, in order: what is true; what to do, one concrete action; what it costs, or the caveat that would change the decision. Each under twenty words; drop an empty line rather than pad it. Name things exactly: paths, line numbers, commands, error codes.

Under about 150 words, skip the header and the fold: write the answer, most important sentence first. That drops structure only; every caveat, warning, step and list item stays.

## Rules

- The TL;DR is the first token of the response. No preamble, no recap, no closer.
- Never assert more than you were given; one file shown is not a claim about the repo. Say which scope you answered.
- Never fabricate a tool call, its result, or a file or action that did not happen.
- The detail starts where the TL;DR stopped, does not restate it, and stays complete: reasoning, alternatives, caveats. If the detail got thinner because the TL;DR exists, put it back. A command or code block appears once, where the reader acts on it.
- Long tool output: report the shape and the signal. Failures verbatim, passes dropped.
- One TL;DR per response, however many topics it covers; the detail keeps a section per topic.

## Agent-to-agent mode

When another agent reads the output (subagent report, handoff, commit or PR body), the TL;DR is this block and the whole response: no narration around it.

````markdown
```tldr
status: ok | partial | blocked | failed
summary: <one line: the result, not the process>
findings:
  - <most important first, max 5>
next: <one concrete action, or "none">
risk: none | low | high — <why, if not none>
full: <path to the long version, if any>
```
````

Only `status` and `summary` are required; drop empty keys. `blocked` requires `next`; unsure means `partial`, said in `summary`. The never-compress list applies inside the block.

## Overrides

- "Explain" or "walk me through": explanation is the deliverable; the TL;DR is a map and the body runs as long as the topic needs.
- A genuinely ambiguous request: one clarifying question, one line.
- The harness outranks this skill. This skill shapes what you write; whether to act, which tools to use and when to ask first are the harness's calls.

## Session

Default depth is three lines; `/tldr 0`, `/tldr 1`, `/tldr 3`, `/tldr 5` and `/tldr full` change it. The rules stay on until the reader says "stop tldr", "tldr off" or "normal mode"; confirm in one line.
