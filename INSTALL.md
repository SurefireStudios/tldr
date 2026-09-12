# How to install tldr

`tldr` is one folder — [`skills/tldr/`](skills/tldr/), holding a short `SKILL.md` the model reads every time and a `reference.md` it opens on demand — plus thin adapters for each of the 20 supported agents. There is no runtime and nothing to compile.

**Jump to your agent:**
[Claude Code](#claude-code) ·
[Cybara](#cybara) ·
[OpenClaw](#openclaw) ·
[Hermes](#hermes) ·
[Cursor](#cursor) ·
[Codex](#codex) ·
[Gemini CLI](#gemini-cli) ·
[GitHub Copilot](#github-copilot) ·
[OpenCode](#opencode) ·
[Zed](#zed) ·
[Windsurf](#windsurf) ·
[Cline / Roo Code](#cline--roo-code) ·
[Aider](#aider) ·
[Amp](#amp) ·
[Qwen Code](#qwen-code) ·
[Kimi Code CLI](#kimi-code-cli) ·
[Pi and Oh My Pi](#pi-and-oh-my-pi-omp) ·
[Antigravity](#antigravity) ·
[Anything else](#anything-else)

---

## The universal route

Works in every agent, including ones not listed here. Paste this into the agent:

```text
Install the tldr skill from https://github.com/SurefireStudios/tldr — read the repo's AGENTS.md for instructions.
```

The agent reads [`AGENTS.md`](AGENTS.md), works out which harness it is running in, and installs itself the right way.

---

## Claude Code

### Install

```bash
claude plugin marketplace add SurefireStudios/tldr
claude plugin install tldr@tldr
```

Restart Claude Code, then type `/tldr`.

### Verify

```bash
claude plugin list
```

### Update

```bash
claude plugin marketplace update tldr
```

### Uninstall

```bash
claude plugin uninstall tldr
claude plugin marketplace remove tldr
```

### Always-on (optional)

Off by default — you invoke it with `/tldr`. To have it active from the first message of every session, create the opt-in flag file:

```bash
touch ~/.claude/.tldr-always
```

Set a default depth by writing a single digit into it:

```bash
echo 1 > ~/.claude/.tldr-always    # one-line summaries by default
```

Turn always-on back off:

```bash
rm ~/.claude/.tldr-always
```

`stop tldr` still turns it off for the current session without deleting the flag.

### Manual install (no plugin system)

```bash
git clone https://github.com/SurefireStudios/tldr.git
mkdir -p ~/.claude/skills ~/.claude/commands
cp -r tldr/skills/tldr ~/.claude/skills/tldr
cp tldr/commands/tldr.md ~/.claude/commands/tldr.md
```

---

## Cursor

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git
mkdir -p .cursor/skills
cp -r tldr/skills/tldr .cursor/skills/tldr
```

Or drop the same folder at `~/.cursor/skills/tldr/` to make it available in every project.

### Verify

Open Cursor's agent panel and type `/tldr`. The skill appears in the skill list.

### Always-on (optional)

Add a rule file at `.cursor/rules/tldr.mdc`:

```markdown
---
description: Lead with a three-line TL;DR and fold the detail
alwaysApply: true
---

Follow the TL;DR contract in .cursor/skills/tldr/SKILL.md for every response:
lead with a three-line TL;DR, then the complete detail underneath. Demote,
don't delete. Never fold destructive actions, security findings, data loss,
cost, or verbatim error text.
```

### Uninstall

```bash
rm -rf .cursor/skills/tldr .cursor/rules/tldr.mdc
```

---

## Codex

### Install

```bash
codex plugin marketplace add SurefireStudios/tldr
codex plugin install tldr
```

If your Codex build does not have a plugin command, use the manual route:

```bash
git clone https://github.com/SurefireStudios/tldr.git
mkdir -p ~/.codex/skills
cp -r tldr/skills/tldr ~/.codex/skills/tldr
```

### Verify and activate

Start a session and type:

```text
/tldr
```

### Always-on (optional)

Append to `~/.codex/AGENTS.md`:

```markdown
## Output style

Follow the TL;DR contract in ~/.codex/skills/tldr/SKILL.md for every response:
lead with a three-line TL;DR (what is true, what to do, what it costs), then the
complete detail underneath. Demote, don't delete. Never fold destructive actions,
security findings, data loss, cost, or verbatim error text.
```

### Uninstall

```bash
codex plugin uninstall tldr
# or, for the manual route:
rm -rf ~/.codex/skills/tldr
```

---

## Cybara

[Cybara](https://cybara.ai) discovers skills from four tiers: bundled, local (`~/.cybara/skills/`), workspace (`<workspace>/.skills/`), and registry.

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
mkdir -p ~/.cybara/skills
cp -r /tmp/tldr/skills/tldr ~/.cybara/skills/tldr
```

Or as a workspace skill, scoped to one project:

```bash
mkdir -p .skills && cp -r /tmp/tldr/skills/tldr .skills/tldr
```

Or through the plugin system, which also gives you enable/disable without restarting the gateway:

```bash
cybara plugin install /tmp/tldr/skills/tldr
```

### Verify

```bash
cybara plugin list
```

The skill also appears under Settings → Plugins in the web UI.

### Uninstall

```bash
cybara plugin disable tldr     # keep it installed, turn it off
rm -rf ~/.cybara/skills/tldr   # or remove it outright
```

### Note

Cybara reads `metadata.cybara` for eligibility gating — OS, required binaries, required
env vars. `tldr` declares no requirements, because it is markdown with no runtime, so it
is eligible everywhere and never hidden from the agent.

---

## OpenClaw

[OpenClaw](https://docs.openclaw.ai) installs skills at several scopes. Global is usually what you want.

### Install

```bash
openclaw skills install git:SurefireStudios/tldr@main --global
```

From a local clone instead:

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
openclaw skills install /tmp/tldr/skills/tldr --as tldr --global
```

Scopes, if you want something narrower than global:

| Scope | Path |
| --- | --- |
| Global | `~/.openclaw/skills` |
| Personal agent | `~/.agents/skills` |
| Project agent | `<workspace>/.agents/skills` |
| Workspace | `<workspace>/skills` |

### Verify

Type `/tldr`. The skill sets `user-invocable: true`, which is what makes it a slash command,
and `disable-model-invocation: true`, which stops the model reaching for it unprompted.

### Update

```bash
openclaw skills update @SurefireStudios/tldr --global
```

### Uninstall

```bash
rm -rf ~/.openclaw/skills/tldr
```

---

## Hermes

[Hermes Agent](https://hermes-agent.nousresearch.com) follows the [agentskills.io](https://agentskills.io)
open standard, so the same folder works without modification.

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
mkdir -p ~/.hermes/skills
cp -r /tmp/tldr/skills/tldr ~/.hermes/skills/tldr
```

On native Windows the config directory is `%LOCALAPPDATA%\hermes` instead of `~/.hermes`.
WSL2 installs use `~/.hermes` as on Linux.

### Verify

```text
/skills        # browse what is installed
/tldr          # invoke it
```

### Uninstall

```bash
rm -rf ~/.hermes/skills/tldr
```

### Note

Hermes writes its own skills and improves them during use. `tldr` is a fixed contract rather
than a learned one, so if you want Hermes to leave it alone, keep it out of any directory
Hermes treats as its own authoring space.

---

## Gemini CLI

### Install

```bash
gemini extensions install https://github.com/SurefireStudios/tldr
```

Or manually:

```bash
git clone https://github.com/SurefireStudios/tldr.git ~/.gemini/extensions/tldr
```

The extension declares `GEMINI.md` as its context file, which imports the canonical skill.

### Verify

```bash
gemini extensions list
```

### Always-on

Gemini CLI extensions load their context file on every session, so installing the extension *is* always-on. To make it opt-in instead, remove the extension and add this to your project `GEMINI.md` only when you want it:

```markdown
@./path/to/tldr/skills/tldr/SKILL.md
```

### Uninstall

```bash
gemini extensions uninstall tldr
```

---

## GitHub Copilot

### VS Code

Create `.github/copilot-instructions.md` in your repository:

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
mkdir -p .github
cp /tmp/tldr/skills/tldr/SKILL.md .github/copilot-instructions.md
```

This copies the core only. The `reference.md` link inside it is inert here; the core is written to stand alone.

Copilot Chat picks it up automatically for that repository. Strip the YAML frontmatter first if your Copilot version renders it literally.

### Copilot CLI

```bash
mkdir -p ~/.copilot
cp /tmp/tldr/skills/tldr/SKILL.md ~/.copilot/instructions.md
```

This copies the core only. The `reference.md` link inside it is inert here; the core is written to stand alone.

### Prompt file (opt-in instead of always-on)

Put it at `.github/prompts/tldr.prompt.md` and invoke it with `/tldr` in Copilot Chat rather than applying it to every response.

### Uninstall

```bash
rm .github/copilot-instructions.md
```

---

## OpenCode

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git ~/.config/opencode/tldr
```

Add the plugin to your `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["~/.config/opencode/tldr/.opencode/plugins/tldr.mjs"]
}
```

### Verify

```text
/tldr
```

### Always-on (optional)

```bash
touch ~/.config/opencode/.tldr-always
echo 1 > ~/.config/opencode/.tldr-always   # optional: set default depth
```

Turn it off:

```bash
rm ~/.config/opencode/.tldr-always
```

### Uninstall

Remove the `plugin` entry from `opencode.json`, then:

```bash
rm -rf ~/.config/opencode/tldr ~/.config/opencode/.tldr-always
```

---

## Zed

### Install

Zed reads a `.rules` file from the project root:

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
cp /tmp/tldr/skills/tldr/SKILL.md .rules
```

This copies the core only. The `reference.md` link inside it is inert here; the core is written to stand alone.

Zed also honours `.cursorrules` and `AGENT.md` if you already use one of those — copy the skill there instead to avoid a second rules file.

### Uninstall

```bash
rm .rules
```

---

## Windsurf

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
mkdir -p .windsurf/rules
cp /tmp/tldr/skills/tldr/SKILL.md .windsurf/rules/tldr.md
```

This copies the core only. The `reference.md` link inside it is inert here; the core is written to stand alone.

For a global rule, use `~/.codeium/windsurf/memories/global_rules.md` instead.

### Uninstall

```bash
rm .windsurf/rules/tldr.md
```

---

## Cline / Roo Code

### Cline

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
mkdir -p .clinerules
cp /tmp/tldr/skills/tldr/SKILL.md .clinerules/tldr.md
```

This copies the core only. The `reference.md` link inside it is inert here; the core is written to stand alone.

### Roo Code

```bash
mkdir -p .roo/rules
cp /tmp/tldr/skills/tldr/SKILL.md .roo/rules/tldr.md
```

This copies the core only. The `reference.md` link inside it is inert here; the core is written to stand alone.

Both load every file in the rules directory on every request, so this is always-on. To make it opt-in, keep the file outside the rules directory and reference it when you want it.

### Uninstall

```bash
rm .clinerules/tldr.md .roo/rules/tldr.md
```

---

## Aider

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
cp /tmp/tldr/skills/tldr/SKILL.md CONVENTIONS.md
```

This copies the core only. The `reference.md` link inside it is inert here; the core is written to stand alone.

Then load it read-only so it does not get edited:

```bash
aider --read CONVENTIONS.md
```

### Always-on

Add to `.aider.conf.yml`:

```yaml
read: CONVENTIONS.md
```

### Uninstall

Remove the `read` entry and delete `CONVENTIONS.md`.

---

## Amp

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git /tmp/tldr
mkdir -p .agents/skills
cp -r /tmp/tldr/skills/tldr .agents/skills/tldr
```

Amp discovers agent skills from `.agents/skills/`. For always-on, add a pointer to your `AGENT.md`:

```markdown
Follow the TL;DR contract in .agents/skills/tldr/SKILL.md for every response.
```

### Uninstall

```bash
rm -rf .agents/skills/tldr
```

---

## Qwen Code

### Install

```bash
qwen extensions install https://github.com/SurefireStudios/tldr
```

Or manually:

```bash
git clone https://github.com/SurefireStudios/tldr.git ~/.qwen/extensions/tldr
```

The extension manifest points at `skills/`, so `/tldr` becomes available.

### Verify

```bash
qwen extensions list
```

### Uninstall

```bash
qwen extensions uninstall tldr
```

---

## Kimi Code CLI

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git ~/.kimi/plugins/tldr
```

Kimi reads `kimi.plugin.json` from the plugin root and loads `./skills/`.

### Verify

Start a session and type `/tldr`.

### Uninstall

```bash
rm -rf ~/.kimi/plugins/tldr
```

---

## Pi and Oh My Pi (OMP)

Pi and OMP get the richest integration: a real extension with a status indicator, session-persistent state, and a depth dial that survives compaction.

### Install

```bash
pi package add SurefireStudios/tldr
```

Or manually:

```bash
git clone https://github.com/SurefireStudios/tldr.git ~/.pi/packages/tldr
```

### Use

```text
/tldr          toggle
/tldr 1        one-line summaries
/tldr 5        five-line summaries
/tldr off      back to normal
```

A `● TLDR 3` indicator appears in the status bar while the mode is on.

### Always-on

```bash
touch ~/.pi/.tldr-always
```

Or create `~/.pi/tldr.json`:

```json
{ "alwaysOn": true, "depth": "1", "hideStatus": false }
```

Or start a single session with it on:

```bash
pi --tldr
```

### Uninstall

```bash
rm -rf ~/.pi/packages/tldr ~/.pi/.tldr-always ~/.pi/tldr.json
```

---

## Antigravity

### Install

```bash
git clone https://github.com/SurefireStudios/tldr.git
```

Point Antigravity at the repository root — it reads `plugin.json` and loads `skills/`.

### Uninstall

Remove the plugin from your Antigravity plugin list.

---

## Anything else

Every harness that accepts custom instructions can run `tldr`, because `tldr` is just markdown.

1. Open [`skills/tldr/SKILL.md`](skills/tldr/SKILL.md).
2. Strip the YAML frontmatter at the top if your tool does not understand it.
3. Paste the rest into whatever your tool calls rules, skills, custom instructions, a system prompt, or a memory file.

If you get it working somewhere not listed here, [open a PR](CONTRIBUTING.md) adding the section. New harness adapters are the single most useful contribution to this repo.

---

## Turning it off

| Scope | How |
| --- | --- |
| This response only | Ask for "full output" or "explain in detail" |
| This session | Say `stop tldr`, `tldr off`, or `normal mode` |
| Always-on, permanently | Delete the flag file (`.tldr-always`) for your harness |
| Completely | Uninstall per the section above |

## Troubleshooting

<details>
<summary><strong><code>/tldr</code> does nothing</strong></summary>

The skill is not being discovered. Check that `SKILL.md` is at the exact path your harness expects (see your section above), and restart the agent — most harnesses only scan for skills at startup.
</details>

<details>
<summary><strong>It works for a few turns, then drifts back to verbose</strong></summary>

The ruleset has fallen out of context, usually after compaction. Type `/tldr` again, or switch to always-on so it is re-injected at every session start.
</details>

<details>
<summary><strong>I see literal <code>&lt;details&gt;</code> tags in my terminal</strong></summary>

The skill is meant to detect this and use a `--- detail ---` divider instead. Tell the agent "use the divider form, this terminal does not render HTML" and it will switch for the session. If it keeps happening in a specific harness, please open an issue naming the harness.
</details>

<details>
<summary><strong>It compressed something I needed in full</strong></summary>

That is a bug, not a preference. Open an issue with the prompt and the response — the never-compress list exists precisely to prevent this, and a miss means a rule needs sharpening or an eval case is missing.
</details>
