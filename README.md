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
  <strong title="English" aria-label="English">🇬🇧</strong> ·
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
- Auth fails because `verifyToken` uses the pre-9.0 `jsonwebtoken` API.
- Fix: upgrade the package, then rewrite `src/auth.ts:42-58`.
- ~15 minutes if the auth tests already cover this path.

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

> Great question! Let me take a look at this. Your auth flow has a few moving pieces here — there's the middleware layer, the token verification step, and the cookie handling on the way back out. Looking at `src/auth.ts`, the `verifyToken` function around lines 42-58 appears to be calling an older version of the `jsonwebtoken` API that was changed in the 9.0 release. One approach would be to update the package and rewrite that function to match the new signature. After you make that change, you'd want to run the auth test suite to confirm nothing else breaks. By the way, while I was in there I noticed a few of your other dependencies are also somewhat out of date, and your README still references the old setup steps. Hope this helps! Let me know if you'd like me to dig into any of this further.

</td><td width="50%">

### After

> **TL;DR**
> - `verifyToken` calls a `jsonwebtoken` API removed in 9.0.
> - Fix: `npm i jsonwebtoken@latest`, then rewrite `src/auth.ts:42-58`.
> - ~15 min. Separately: 3 stale deps, stale README.
>
> <details><summary>Full detail</summary>
>
> The auth flow has three stages — middleware, token verification, cookie serialization. The break is in stage two...
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
summary: Fixed token refresh race in auth middleware; 3 tests added.
changed:
  - src/auth.ts:42-58
  - test/auth.spec.ts
next: none
risk: low — touches session invalidation, watch for early logouts
full: docs/reports/auth-refresh-fix.md
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

There is a reproducible eval harness in [`evals/`](evals/) that measures two things most output-style prompts never measure together:

- **Quality** — correctness, **fidelity**, actionability, safety, and concision, graded blind against a baseline.
  Fidelity is weighted at 25% specifically to catch a response that looks better only because it deleted something.
- **Tokens** — actual output-token counts, because the entire point of compression is cost.

Run it yourself:

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3
```

Results, methodology, and the release gate live in [`evals/RESULTS.md`](evals/RESULTS.md). Numbers there are published whether or not they flatter the skill — including runs that fail the gate.

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
  <strong>Star ⭐ if it saved you one scroll.</strong><br/>
  <sub>too long; didn't read · also accepted: too lazy, didn't read</sub>
</p>
