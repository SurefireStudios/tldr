<p align="center">
  <img src="./assets/logo.svg" alt="tldr — too long; didn't read, for AI coding agents" width="150" />
</p>

<h1 align="center">tldr</h1>

<p align="center">
  <strong>Too long; didn't read — for AI coding agents.</strong>
</p>

<p align="center">
  Your coding agent buries the answer in four paragraphs.<br/>
  This makes it lead with three lines and fold the rest.<br/>
  <em>Demote, don't delete.</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/SurefireStudios/tldr?style=flat-square" alt="License: MIT"></a>
  <a href="https://github.com/SurefireStudios/tldr/stargazers"><img src="https://img.shields.io/github/stars/SurefireStudios/tldr?style=flat-square" alt="Stars"></a>
  <a href="INSTALL.md"><img src="https://img.shields.io/badge/agents-20%20supported-blue?style=flat-square" alt="20 agents supported"></a>
  <a href="evals/"><img src="https://img.shields.io/badge/evals-reproducible-green?style=flat-square" alt="Reproducible evals"></a>
</p>

<p align="center">
  <strong title="English">🇬🇧 English</strong> ·
  <a href=".github/readme/README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href=".github/readme/README.es.md" title="Español">🇪🇸</a> ·
  <a href=".github/readme/README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <a href=".github/readme/README.ja.md" title="日本語">🇯🇵</a> ·
  <a href="CONTRIBUTING.md#translations" title="Add your language">➕ add yours</a>
</p>

---

## Install

Paste this into your agent. It works in Claude Code, Cursor, Codex, Gemini CLI, and the 20 agents in the table below.

```text
Install the tldr skill from https://github.com/SurefireStudios/tldr — read the repo's AGENTS.md for instructions.
```

Prefer a real command? Claude Code:

```bash
claude plugin marketplace add SurefireStudios/tldr
claude plugin install tldr@tldr
```

Every other agent: 🔗 **[INSTALL.md](INSTALL.md)**

Then type `/tldr`.

<p align="center">
  <img src="./assets/demo.gif" alt="A verbose answer, then the same question with tldr on: three lines and a fold" width="820" />
</p>

<p align="center">
  <sub>Real output from the eval suite, not a mockup — both halves are in <a href="evals/results/run6-pass/">evals/results/run6-pass/</a>.</sub>
</p>

## The problem

Two problems, actually.

**Your agent talks too much.** You asked a yes/no question. You got four paragraphs, a numbered plan, a caveat about edge cases, and "Hope this helps!" The answer was in there somewhere.

**Your agents talk too much to each other.** A subagent finishes a search and returns 4,000 tokens of narration to the orchestrator, which needed three lines. You paid for all of it, twice — once to write it, once to carry it in context for the rest of the session.

Most "be concise" prompts fix the first problem by deleting information. That is a bad trade the moment you are doing code review, a security audit, or anything you will be held to.

## Demote, don't delete

`tldr` does not make your agent say less. It makes your agent say the important part **first**, and put everything else directly underneath.

Nothing is thrown away. You choose your depth.

```markdown
**TL;DR**
- `listOrders` queries the customer table once per row: 241 round trips to render one page.
- Fix: pass `include: { customer: true }` at `src/orders/repository.ts:88`, then delete the loop under it.
- ~10 minutes. The orders benchmark already covers this path.

<details>
<summary>Full detail</summary>

...everything the agent would normally have said, in full...

</details>
```

In a terminal, where `<details>` does not render, it uses a plain divider instead. The skill knows the difference.

## What changes

<table>
<tr><td width="50%">

### Before

> Thanks for flagging this — there's a fair bit going on with the orders endpoint. The route handler calls `listOrders` over in the repository layer, which pulls the order rows and then, for each individual row, issues a separate query to resolve that order's customer record. On a page rendering 240 orders that works out to 241 round trips to the database, which is almost certainly where the latency is coming from. Prisma does support eager loading through the `include` option, so one possible approach would be to pass the customer relation into the initial query and then remove the per-row lookup beneath it. You might also want to confirm there's an index on `orders.customer_id`, though that's more of a nice-to-have than the actual fix here. While I was in there I noticed the invoices repository looks like it has the same shape of problem, and separately your Prisma client is a couple of minor versions behind. Hope that helps — let me know if you'd like me to dig into any of that!

</td><td width="50%">

### After

> **TL;DR**
> - `listOrders` runs one customer query per row: 241 queries per page.
> - Fix: add `include: { customer: true }` at `src/orders/repository.ts:88`, drop the loop under it.
> - ~10 min. Separately: `invoices/repository.ts` has the same bug.
>
> <details><summary>Full detail</summary>
>
> The endpoint has three stages — fetch, resolve, serialize. All of the cost is in stage two...
>
> *(the rest, in full, one click away)*
>
> </details>

</td></tr>
</table>

## The depth dial

You set how much lands above the fold.

| Command | What you get |
| --- | --- |
| `/tldr 0` | Headline only. One line, no detail. |
| `/tldr 1` | One line, then the detail. |
| `/tldr 3` | **Default.** Three lines, then the detail. |
| `/tldr 5` | Five lines, then the detail. |
| `/tldr full` | Off. Back to normal. |

The dial resizes the summary. It never thins the detail.

## `/tldr` is also a verb

Turn it on as a mode, or fire it once at a specific thing:

```text
/tldr this file
/tldr that stack trace
/tldr the last 20 commits
/tldr this PR — what should I review first?
/tldr your last answer
```

One-shot. No mode change.

## Agent-to-agent: where the money is

This is the half that other output-style skills do not do.

When output goes to **another agent** instead of a human, `tldr` switches to a parseable block. Subagent reports, task results, handoffs, commit messages, PR bodies:

````markdown
```tldr
status: ok
summary: Removed N+1 in listOrders; orders page drops from 241 queries to 2.
changed:
  - src/orders/repository.ts:88-104
  - test/orders.bench.ts
next: none
risk: low — changes row ordering when a customer record is null
full: docs/reports/orders-n1.md
```
````

Three rules do the work:

1. **Return the block and stop.** The orchestrator asked for a result, not a journey.
2. **Write the long version to a file, reference the path.** Don't pipe it through the context window.
3. **Never compress what the caller needs verbatim** — exact errors, exact diffs, exact paths.

Your orchestrator gets a struct. Your context window stops filling with narration. Your bill notices.

## Never compressed

Compression is safe for prose. It is not safe for consequences. These always appear in full, above the fold, never folded:

- Destructive actions — `rm -rf`, force push, dropped tables, migrations
- Security findings — a folded vulnerability is an unreported vulnerability
- Irreversibility and data loss
- Money, quota, and rate limits
- Verbatim error text you need to paste or search
- Diffs of code being changed — a compressed diff is a lie
- Legal, medical, and safety boundaries
- Anything you explicitly asked to see in full

The governing rule, in the skill's own words: *a reader who reads only the TL;DR must not end up with a false belief.*

## Does it actually work?

Measured on 16 cases × 3 trials, blind-graded against a no-skill baseline, on two models with the same instrument:

| | Sonnet | | Opus | |
| --- | ---: | --- | ---: | --- |
| Mean output tokens | 333 → **305** | −8% | 558 → **500** | −10% |
| Median output tokens | 297 → **234** | −21% | 457 → **304** | −33% |
| Correctness | 4.833 → **4.854** | +0.021 | 4.854 → 4.854 | 0.000 |
| Fidelity | 4.458 → **4.688** | +0.229 | 4.771 → 4.667 | −0.104 |
| Actionability | 4.375 → **4.833** | +0.458 | 4.521 → **4.833** | +0.312 |
| Safety | 4.562 → **4.667** | +0.104 | 4.667 → **4.875** | +0.208 |
| Concision | 3.771 → **4.500** | +0.729 | 3.833 → **4.729** | +0.896 |
| Fabricated tool calls | 0/48 → **0/48** | | 0/48 → **0/48** | |

Fewer tokens and better on nearly every dimension, on both models. **The release gate reads 4 of 5 on each**, and it is not being relaxed:

- **Sonnet** misses on one blocker — a factual error about `pg_dump` defaults, in a response whose safety behaviour scored 5/5. The gate counts any blocker in a never-compress case, whatever its type.
- **Opus** misses fidelity by **0.004** against a −0.1 threshold, with a standard error of 0.085.

Both are inside noise. Both stay as FAILED, because a threshold that moves when a result lands next to it is not a threshold.

### The run that was wrong

An earlier version of this section said the skill failed every gate rule on Opus, and passed all five on Sonnet with a 16% token saving. Neither was measured correctly.

The eval harness handed the skill to Claude Code as a *second* `--append-system-prompt` flag. Claude Code keeps only the last one. So every candidate run silently lost the "you have no tools" framing that every baseline kept. Sonnet passed regardless — it defers to tool absence in the request. Opus, told by Claude Code's own system prompt that it had Glob, Read and Bash and never told otherwise, reached for them and fabricated the results. That was published as a skill defect and "fixed" twice with prompt wording before a review agent tested the flag with codewords instead of trusting the harness's comments about itself.

On the corrected harness, Opus fabricates nothing, and Sonnet's saving is −8% rather than −16% — the table above is the like-for-like one. The one "genuine Opus finding" I kept after the correction — that it paraphrased `ERR_PNPM_OUTDATED_LOCKFILE` — did not survive a second look either: a grep of all 12 responses on that case shows neither model echoes the exact code in either condition. It is the weakest case on both models, logged as open, and not a skill defect.

It took nine runs. [`evals/RESULTS.md`](evals/RESULTS.md) has all of them — the four that failed on the skill's merits, the one where optimising for tokens cost fidelity, and the one that was my own harness.

Reproduce it:

```bash
scripts/run_full_eval.sh --smoke   # cheap, proves the wiring
scripts/run_full_eval.sh           # the real thing
```

The harness measures **tokens and fidelity together**, and the gate fails a candidate whose fidelity drops even when tokens improve. That rule fired on runs 2, 3 and 4 — it is load-bearing, not decoration.

## Supported agents

| Agent | Install | Always-on |
| --- | --- | --- |
| **Claude Code** | `claude plugin marketplace add SurefireStudios/tldr` | ✅ hook |
| **Cursor** | [copy the skill](INSTALL.md#cursor) | ✅ rules |
| **Cybara** | `cybara plugin install` | ✅ plugin |
| **OpenClaw** | `openclaw skills install git:SurefireStudios/tldr@main` | ✅ global scope |
| **Hermes** | [agentskills.io standard](INSTALL.md#hermes) | ✅ |
| **Codex** | [plugin](INSTALL.md#codex) | ✅ hook |
| **Gemini CLI** | [extension](INSTALL.md#gemini-cli) | ✅ context file |
| **GitHub Copilot** | [VS Code + CLI](INSTALL.md#github-copilot) | ✅ instructions |
| **OpenCode** | [plugin](INSTALL.md#opencode) | ✅ flag file |
| **Zed** | [rules](INSTALL.md#zed) | ✅ |
| **Qwen Code** | [extension](INSTALL.md#qwen-code) | ✅ |
| **Kimi Code CLI** | [plugin](INSTALL.md#kimi-code-cli) | ✅ |
| **Windsurf** | [rules](INSTALL.md#windsurf) | ✅ |
| **Amp** | [agent skill](INSTALL.md#amp) | ✅ |
| **Aider** | [conventions](INSTALL.md#aider) | ✅ |
| **Cline / Roo** | [custom instructions](INSTALL.md#cline--roo-code) | ✅ |
| **Pi / Oh My Pi** | [extension](INSTALL.md#pi-and-oh-my-pi-omp) | ✅ status bar + dial |
| **Antigravity** | [plugin](INSTALL.md#antigravity) | ✅ |
| **Anything else** | [paste the sentence](#install) | — |

## FAQ

<details>
<summary><strong>How do I make Claude Code less verbose?</strong></summary>

Install this skill and type `/tldr`. Claude Code will lead every response with a three-line summary and fold the rest. Use `/tldr 1` for one line, `/tldr full` to turn it off. For always-on, see [INSTALL.md](INSTALL.md#claude-code).
</details>

<details>
<summary><strong>How is this different from just saying "be concise"?</strong></summary>

"Be concise" deletes information and the agent drifts back to verbose within a few turns. `tldr` relocates information — the detail is always there, folded — and the ruleset persists for the whole session. It also covers agent-to-agent output, which a style instruction does not touch.
</details>

<details>
<summary><strong>How do I reduce subagent token usage?</strong></summary>

Use the agent-to-agent block. Subagents return a parseable `tldr` struct and write their long output to a file instead of piping it into the orchestrator's context. See [agent-to-agent](#agent-to-agent-where-the-money-is).
</details>

<details>
<summary><strong>Will it hide something important from me?</strong></summary>

It is explicitly designed not to. Destructive actions, security findings, data loss, cost, and verbatim errors are on a never-compress list and always render above the fold. See [Never compressed](#never-compressed).
</details>

<details>
<summary><strong>Does it work with agents other than Claude?</strong></summary>

Yes — 14 harnesses, listed above. The skill is plain markdown with no runtime, so it works anywhere you can give an agent instructions, including ones not on the list.
</details>

<details>
<summary><strong>Is this safe to install? What does it run?</strong></summary>

Nothing, by default. The skill is two markdown files: a core under 5,000 characters that the model reads every time, and a reference it opens on demand. The optional always-on hook is a ~40-line Node script that reads the core and prints it. Read [`skills/tldr/SKILL.md`](skills/tldr/SKILL.md) in two minutes and decide for yourself.
</details>

<details>
<summary><strong>Can I change the rules?</strong></summary>

Yes, see [Tune it](#tune-it). It is one markdown file. Fork it and edit it.
</details>

## Tune it

Fork, edit [`skills/tldr/SKILL.md`](skills/tldr/SKILL.md), then swap your copy in:

```bash
claude plugin uninstall tldr
claude plugin marketplace remove tldr
claude plugin marketplace add <your-username>/tldr
claude plugin install tldr@tldr
```

Restart your agent, then `/tldr`.

## Contributing

Translations, new harness adapters, and eval cases are the three highest-value contributions. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. Do whatever you want with it.

---

<p align="center">
  <strong>TL;DR: star it. ⭐</strong><br/>
  <sub>You just read an entire README about not reading things.<br/>
  Don't be too lazy for the last click.</sub>
</p>
