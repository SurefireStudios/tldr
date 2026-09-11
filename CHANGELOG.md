# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Because the skill ships in a context window, a change to `skills/tldr/SKILL.md`
is a behaviour change even when no code moved. Those are listed first in every
release.

## [Unreleased]

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
