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
  <a href="INSTALL.md"><img src="https://img.shields.io/badge/agents-17%20supported-blue?style=flat-square" alt="17 agents supported"></a>
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

Paste this into your agent. It works in Claude Code, Cursor, Codex, Gemini CLI, and the 17 agents in the table below.

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

Measured on 16 cases × 3 trials against `claude-sonnet-5`, blind-graded against a no-skill baseline:

| | Baseline | With `tldr` | |
| --- | ---: | ---: | --- |
| Mean output tokens | 339 | **283** | −16% |
| Median output tokens | 295 | **186** | −37% |
| Correctness | 4.771 | **4.979** | +0.208 |
| Fidelity | 4.521 | **4.750** | +0.229 |
| Actionability | 4.312 | **4.896** | +0.583 |
| Safety | 4.417 | **4.604** | +0.188 |
| Concision | 3.604 | **4.667** | +1.063 |

Fewer tokens **and** better on every dimension, with zero blocking findings. The release gate passes on all five rules.

**Now the caveats, because a number without them is marketing.** The baseline is regenerated each run and drifted down this time, so roughly a quarter of the headline gain is the comparison point moving rather than the skill improving. Across all 48 paired rows the standard error is about 0.090. The candidate wins 34 pairs, loses 11 — better on average, not better every time. And this is one run, on one model.

It took six runs to get here, and the first four failed the gate. [`evals/RESULTS.md`](evals/RESULTS.md) has all of them, including the run where optimising for tokens cost fidelity and the gate caught it, and the check I added that rejected `5432.` as a malformed answer.

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

Nothing, by default. The skill is a single markdown file. The optional always-on hook is a ~30-line Node script that reads one file and prints it. Read [`skills/tldr/SKILL.md`](skills/tldr/SKILL.md) in two minutes and decide for yourself.
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
