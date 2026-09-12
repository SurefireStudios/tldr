# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Because the skill ships in a context window, a change to `skills/tldr/SKILL.md`
is a behaviour change even when no code moved. Those are listed first in every
release.

## [Unreleased]

### Skill

- **Split into a core and a reference.** `skills/tldr/SKILL.md` is now under
  5,000 characters (was 18,000): the contract, the complete never-compress list,
  both render shapes, six one-line rules, the agent-to-agent block and the
  overrides. Everything else — reasoning, bad/good pairs, the depth dial table,
  `/tldr <target>`, the full block field spec, worked examples — moved to
  `skills/tldr/reference.md`, which the core links to and the model opens on
  demand. Always-on harnesses re-send the core on every turn, so this cuts that
  per-turn cost by roughly three quarters (Claude Code hook: 4,279 → 1,213 tokens).
- The never-compress list now sits at 22% of the file instead of 29%, and its
  items lost their bold labels: 2 bold phrases in the core, down from 46.
- Every instruction about whether to act — "write it to a file", "confirm before
  acting", "check the message before reaching for a tool" — is gone from the
  core. The skill shapes what is written; the harness decides what is done. A
  test pins this.
- `full:` in the agent-to-agent block reads "path to the long version, if any";
  every eval trial under the old wording wrote `full: none`.

### Adapters

- The three always-on hooks, the OpenCode plugin and the Pi/OMP extension name
  the absolute path of `reference.md` in their header, since injected text has
  no base directory to resolve a relative link against.
- `scripts/check_mirrors.py` and the mirror-sync workflow cover both files.
- Install routes that copy the skill folder use `cp -r`; the seven rules-file
  routes (Copilot, Zed, Windsurf, Cline, Roo, Aider) note that they carry the
  core only.
- The `/tldr` command files and the Gemini prompt no longer say "write long
  output to a file", and their never-fold lists match the core's eight items.

### Evals

- Resumption is skill-aware: a candidate row is only reused for the exact skill
  text that produced it. Previously, rerunning after editing the skill would
  have skipped every candidate row and reported the old numbers.
- `run_full_eval.sh --out DIR`, so two models can run at once.
- Corrected the record on `verbatim-error`: neither model echoes the exact
  error code in either condition (0 of 12), so it is not a skill defect.

## [0.2.0]

### Skill

- Rule 3, never assert more than you were given: one file shown is not a claim
  about the repository.
- Rule 4 hardened: never fabricate a tool call, its result, or a file that was
  not written.
- The detail continues the TL;DR instead of repeating it; short answers skip
  the scaffolding entirely.
- Every example and comment carried over from prior art replaced with original
  material.

### Evals

- A runnable harness: baseline vs candidate, blind judge with permuted labels,
  weighted rubric, release gate. Six runs published in `evals/RESULTS.md`,
  including the four that failed the gate.
- The skill is injected as a system instruction rather than into the user turn.
- `scripts/measure_duplication.py`.

### Launch

- Self-referential star CTA; demo GIF generated from real eval output.

## [0.1.0]

Initial release.

### Skill

- The core contract: lead with a TL;DR, keep the full detail directly underneath.
  Demote, don't delete.
- Two render shapes: an HTML `<details>` fold where HTML renders, a
  `--- detail ---` divider where it does not.
- A depth dial: `/tldr 0`, `1`, `3` (default), `5`, and `full`.
- `/tldr <target>` as a one-shot verb, with no mode change.
- A never-compress list covering destructive actions, security findings, data
  loss, cost and quota, verbatim error text, diffs, and safety boundaries.
- Agent-to-agent mode: a parseable ```tldr``` block for subagent reports,
  handoffs, commit messages, and PR bodies.

### Harnesses

- Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Zed,
  Windsurf, Cline, Roo Code, Aider, Amp, Qwen Code, Kimi Code CLI, Pi, Oh My Pi,
  and Antigravity.
- Opt-in always-on via a `.tldr-always` flag file, with three implementations
  (Node, POSIX sh, PowerShell) verified to agree byte for byte.
- The flag file optionally carries a default depth.

### Evaluation

- 16 cases across nine categories, weighted toward never-compress traps.
- A five-dimension rubric with **Fidelity** at 25%, to catch responses that look
  better only because they deleted something.
- Structural blinding in the judge: conditions are relabelled and permuted from a
  digest of the group key, so a resumed run reproduces its own labels.
- A release gate scoped to the categories where a blocker is genuinely
  disqualifying, rather than an absolute rule no candidate could ever satisfy.
- Token counting reported beside the quality scores, never instead of them.

### Known gaps

- **No scored eval run has been published yet.** `evals/RESULTS.md` is a
  template, and neither it nor the README carries any performance number. See
  that file for the commands that produce the first run.

[Unreleased]: https://github.com/SurefireStudios/tldr/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/SurefireStudios/tldr/releases/tag/v0.1.0
