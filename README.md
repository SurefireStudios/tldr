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

### Brief mode

`<details>` folds only where HTML renders. In a terminal, and in some chat apps, there is no triangle to click — so a complete answer lands as one block however small the summary is.

`/tldr brief` is the fold those surfaces cannot draw. The TL;DR prints, the detail waits:

```
**TL;DR**
- `listOrders` queries the customer table per row: 241 queries per page.
- Fix: `include: { customer: true }` at `src/orders/repository.ts:88`.
- ~10 minutes; the orders benchmark covers this path.

Say "more" for the full detail.
```

Say `more` and you get the detail in full — complete, not a shortened version. `/tldr detail` turns it back off.

One thing it will not do: **hold back anything on the never-compress list.** Destructive commands, security findings, cost, verbatim errors and diffs print in the brief response itself. A held-back security finding is an unreported one.

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

## `tldr-write`: the same idea, pointed outward

`tldr` shapes what an agent says **to you**. It gets *longer* on the cases that matter, because it stops thinning caveats.

`tldr-write` shapes what you send **to someone else** — an email, a Slack reply, a PR description, a review comment, a commit message. Different job, opposite output:

```
Before   Hi team! Hope everyone had a great weekend. I wanted to circle back on the
         caching discussion we had last Tuesday. So, as you may recall, we were
         debating whether to use Redis or in-process caching for the session store.
         I took some time to look into it and I think, based on my analysis, that
         Redis is probably the better option here, mainly because we run four app
         servers and in-process caching would mean a user's session could land on a
         server that does not have it. Anyway, let me know your thoughts! Happy to
         discuss further. Thanks!

After    Recommending Redis for the session store: we run four app servers, and
         in-process caching means a user's session can land on one that doesn't
         have it.
```

The ask goes first. Preamble, restated questions, hedge stacks and "Hope this helps!" go entirely. But **short is not the same as curt**, and a never-cut list holds the line: the ask and its deadline, the blocker and who holds it, the decision-changing caveat, credit by name, the apology if one is owed, bad news early and plain, cost and irreversibility.

Turn it on with `/tldr-write`, or fire it once: `/tldr-write this PR description`.

### Why it has its own rubric

`tldr` could cheat by deleting, so its eval weights fidelity at 25%.

This one's cheat is cheaper. `"No."` is shorter than `"I can't this week — I'm on call and shipping Thursday. Friday works if that helps."` Both decline, both are accurate, and on every dimension the first rubric measures, the rude one wins.

So this suite grades **appropriateness at 20%** and floors it in the gate: *would the named recipient, reading this, feel respected?* A candidate that reads colder than baseline does not ship, however few tokens it used.

| | Sonnet | | Opus | |
| --- | ---: | --- | ---: | --- |
| Correctness | 4.479 → **4.854** | +0.375 | 3.521 → **4.771** | **+1.250** |
| Fidelity | 4.833 → **4.833** | +0.000 | 4.917 → **4.896** | −0.021 |
| Appropriateness | 4.083 → **4.375** | +0.292 | 4.333 → **4.688** | +0.354 |
| Actionability | 3.458 → **4.958** | +1.500 | 4.104 → **4.979** | +0.875 |
| Concision | 2.646 → **4.896** | +2.250 | 2.625 → **4.938** | +2.312 |
| Output tokens | 226 → **87** | **−61%** | 373 → **124** | **−67%** |

Release gate passes 5 of 5 on both. Appropriateness rising while output falls two thirds is the result that dimension exists to be able to *fail*, and it didn't.

### The number that isn't the token count

Opus baseline correctness of 3.521 is the lowest figure anywhere in the eval results, and it has one cause: **an unstyled model invents facts when it drafts a message for you.** 20 of 48 baseline responses score 3 or below, every time for the same reason.

The whole `apology-owed` prompt is: *"I deployed a migration at 4pm that locked the orders table for 20 minutes during business hours. Support took about 40 calls. Write my message to the support team lead."*

The baseline draft:

> It's resolved — **no data was lost or corrupted**, and **the backlog cleared once the lock released**. **Customers who retried after ~4:20pm should have gone through normally.** […] **migrations like this go out off-hours from now on**

Four things nobody said. Three are claims about a production incident you cannot support; the fourth commits you to a process change. You were about to send that to a colleague.

With the skill:

> The orders table lock at 4pm today was my migration — I ran it during business hours without thinking through the lock. Sorry; that's on me, and your team ate about 40 calls for it. […]
>
> *Left out any promise about future migration windows — didn't want to commit you to a process you haven't agreed with your own team yet.*

Invented dates, across the full set: Sonnet 6/48 → 1/48, **Opus 5/48 → 0/48**.

−67% fewer tokens is the number that fits on a slide. "Stops your agent putting *no data was lost* in an incident apology" is the one that matters.

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

Measured on 16 cases × 3 trials, blind-graded against a no-skill baseline, on two models with the same instrument. This is the shipped skill (v0.4.0), runs 16 and 17:

| | Sonnet | | Opus | |
| --- | ---: | --- | ---: | --- |
| Correctness | 4.896 → **4.938** | +0.042 | 4.708 → **4.875** | +0.167 |
| Fidelity | 4.583 → **4.854** | +0.271 | 4.667 → **4.854** | +0.188 |
| Actionability | 4.417 → **4.875** | +0.458 | 4.500 → **4.833** | +0.333 |
| Safety | 4.458 → **4.750** | +0.292 | 4.542 → **4.896** | +0.354 |
| Concision | 4.083 → **4.333** | +0.250 | 3.938 → **4.562** | +0.625 |
| Fabricated tool calls | 0/48 → **0/48** | | 0/48 → **0/48** | |
| Agent-to-agent output tokens | 172 → **105** | −39% | 320 → **137** | −57% |
| Human-facing output tokens, mean | 346 → 374 | +8% | 535 → 555 | +4% |
| Skill tokens per always-on turn | 4,380 → **1,078** | −75% | 4,380 → **1,078** | −75% |

Better on every dimension, on both models, and **the release gate passes 5 of 5 on both.** Read the token rows carefully, because they are not the story a compression skill is expected to tell:

- **Where the skill compresses — agent-to-agent reports — output falls by a third to a half.** That is the headline feature and it is where the saving lives.
- **Where the skill refuses to compress — destructive actions, security findings, cost, errors — output gets longer**, because the model now keeps every caveat above the fold instead of thinning it. Every one of those cases scored higher on fidelity or safety. That is the trade, and it is why the human-facing *mean* rises rather than falls.
- **The median is not quoted here, deliberately.** Earlier versions of this table published a −13% median on Sonnet. Re-running the same skill, two lines different, produced +15% — a sign flip. Per-case figures show the movement is diffuse, not concentrated: at 48 rows the median is about one case's variance wide. The mean has held its sign and rough magnitude across six runs on two models; the median has not, so it is in [`evals/RESULTS.md`](evals/RESULTS.md) with that caveat attached rather than on this table.
- **The per-turn cost is unchanged from v0.3.0.** The v0.4.0 core is ten characters larger than the v0.3.0 core — 4,995 against 4,985 — so the row above still describes it. Measured with `cl100k_base` for a like-for-like check: 1,059 body tokens to 1,077, +1.7%.
- **The biggest number is the skill's own size.** An always-on harness re-sends the skill on every turn; the old 18k version cost roughly 80× per turn what it saved in output. The core is a quarter of that.

The gate result carries one caveat: Sonnet's "no blockers" rule passed because the judge did not escalate a `pg_dump` fact error that Sonnet makes in 5 of 6 responses *with or without the skill*; in the previous run it did. Both runs are in the file.

### The run that was wrong

An earlier version of this section said the skill failed every gate rule on Opus, and passed all five on Sonnet with a 16% token saving. Neither was measured correctly.

The eval harness handed the skill to Claude Code as a *second* `--append-system-prompt` flag. Claude Code keeps only the last one. So every candidate run silently lost the "you have no tools" framing that every baseline kept. Sonnet passed regardless — it defers to tool absence in the request. Opus, told by Claude Code's own system prompt that it had Glob, Read and Bash and never told otherwise, reached for them and fabricated the results. That was published as a skill defect and "fixed" twice with prompt wording before a review agent tested the flag with codewords instead of trusting the harness's comments about itself.

On the corrected harness, Opus fabricates nothing, and Sonnet's saving is −8% rather than −16% — the table above is the like-for-like one. The one "genuine Opus finding" I kept after the correction — that it paraphrased `ERR_PNPM_OUTDATED_LOCKFILE` — did not survive a second look either: a grep of all 12 responses on that case shows neither model echoes the exact code in either condition. It is the weakest case on both models, logged as open, and not a skill defect.

It took thirteen runs. [`evals/RESULTS.md`](evals/RESULTS.md) has all of them — the four that failed on the skill's merits, the one where optimising for tokens cost fidelity, the one that was my own harness, and the two where the first cut of the shorter skill made Opus thin its answers until two sentences went back in.

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
