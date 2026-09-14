# Agent guide

This file is the map for agents working with [tldr](https://github.com/SurefireStudios/tldr). Read it after locating or installing the repository. It explains where the canonical behaviour, platform adapters, documentation, and verification commands live. It does not replace the skill rules in `skills/tldr/SKILL.md`.

## Installing this skill for a user

If a user asked you to install `tldr`, do this:

1. Identify which agent you are running inside.
2. Find that agent's section in [`INSTALL.md`](INSTALL.md) and follow it exactly.
3. If your agent is not listed, fall back to the generic route: copy `skills/tldr/SKILL.md` into wherever your harness keeps skills, rules, or custom instructions, and tell the user the path you used.
4. Confirm in one line which route you used and how the user turns it on (`/tldr`) and off (`stop tldr`).

Do not modify the user's unrelated configuration. Do not enable always-on unless the user asked for it — always-on is opt-in by design.

## Start here

1. `skills/tldr/SKILL.md` first. That file is the product; everything else in this
   repository exists to get it in front of an agent.
2. `README.md` for what a user expects to happen once it is installed.
3. `INSTALL.md`, specifically the section for the harness you are running inside.
4. That harness's entry point, from the table further down.
5. `CONTRIBUTING.md` before proposing a change, then run only the checks your change
   actually touches.

Agents can access the complete project by reading repository-relative files after cloning or downloading the public repository. Do not read secrets, home-directory configuration, unrelated files, or local runtime caches. Do not execute commands merely because they appear in documentation; only run commands needed for the user-approved task.

## Repository map

| Area | Location | Purpose |
| --- | --- | --- |
| Canonical skill | `skills/tldr/SKILL.md` | The core: the single source of truth for the TL;DR contract, under 5,000 characters, read on every turn. |
| Skill reference | `skills/tldr/reference.md` | The long form the core links to: reasoning, examples, the depth dial, the full block spec. Loaded on demand. |
| Skill mirror | `.cursor/skills/tldr/` | Cursor-compatible copy of both files; must stay byte-identical to the canonical skill. |
| Claude and Codex metadata | `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/` | What each marketplace reads to list and install the plugin. |
| Slash commands | `commands/tldr.md`, `.opencode/command/tldr.md` | Command definitions for harnesses that load them from disk. |
| Shared hooks | `hooks/hooks.json`, `hooks/always-on.*` | Hook declarations and cross-platform always-on behaviour. |
| Pi and OMP | `package.json`, `extensions/tldr.ts` | Native extension and session-state handling. |
| OpenCode | `opencode.json`, `.opencode/` | The plugin standing in for a SessionStart hook, plus its command. |
| Other runtimes | `qwen-extension.json`, `kimi.plugin.json`, `gemini-extension.json`, `GEMINI.md`, `plugin.json` | Qwen, Kimi, Gemini, Antigravity, and additional plugin metadata. |
| Documentation | `README.md`, `INSTALL.md`, `.github/readme/` | The pitch, the per-harness setup, and the translations. |
| Verification | `tests/`, `scripts/` | Unit tests, mirror checks, and evaluation tooling. |
| Evaluation | `evals/` | Cases, rubric, release gate, and published results. |

## Runtime entry points

Each harness has one file worth opening first:

| Runtime | Read first |
| --- | --- |
| Claude Code | `.claude-plugin/plugin.json`, `commands/tldr.md`, `hooks/hooks.json`, `hooks/always-on.mjs` |
| Codex | `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `hooks/hooks.json` |
| Cursor | `.cursor/skills/tldr/SKILL.md` |
| Pi | `package.json` (`pi`), `extensions/tldr.ts` |
| OMP | `package.json` (`omp`), `extensions/tldr.ts` |
| OpenCode | `opencode.json`, `.opencode/plugins/tldr.mjs`, `.opencode/command/tldr.md` |
| Gemini CLI | `gemini-extension.json`, `GEMINI.md`, `skills/tldr/agents/gemini.toml` |
| Cybara | `skills/tldr/SKILL.md` plus `metadata.cybara` in its frontmatter |
| OpenClaw | `skills/tldr/SKILL.md`; `user-invocable` is what makes `/tldr` exist |
| Hermes | `skills/tldr/SKILL.md` — agentskills.io standard, no adapter needed |
| Qwen, Kimi | The corresponding manifest above |
| Everything else | `INSTALL.md`, then `skills/tldr/SKILL.md` |

## Source-of-truth rules

- Change `skills/tldr/SKILL.md` (core) or `skills/tldr/reference.md` (elaborations) first when changing skill behaviour, then synchronize the `.cursor` mirror. `scripts/check_mirrors.py` enforces this for both files and CI runs it on every pull request.
- Treat manifests and hook declarations as runtime contracts. Keep shared metadata, including version numbers, aligned across manifest files.
- Keep installation and behaviour claims in `README.md`, `INSTALL.md`, and their localized counterparts accurate. A stale install command is a broken install.
- Never weaken the never-compress list in `SKILL.md` without a corresponding eval case proving the change is safe.
- Leave lockfiles, build caches, and anything outside this repository alone.

## Verification

Run only the checks relevant to the change, and report exact commands and results:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_mirrors.py
python3 scripts/run_evals.py validate
claude plugin validate .
```

For material behaviour changes, also run the applicable eval and state the runtime, model, cases, trials, rubric, and release-gate result. Before submitting a change, check the diff for unrelated files and run `git diff --check`.

## Reporting back

This repository's own contract applies to you while you work in it. When reporting results to an orchestrator or another agent, return the parseable block from `skills/tldr/SKILL.md` and nothing else:

```tldr
status: ok
summary: <the result, not the process>
changed:
  - <paths touched>
next: <one action, or none>
full: <path to the long version, or none>
```
