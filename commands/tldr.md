---
description: Lead with a three-line TL;DR and fold the detail, for the rest of this session
argument-hint: "[0|1|3|5|full] or a target to compress"
---

Use the `tldr` skill (`skills/tldr/SKILL.md`) and apply its contract to every
response for the rest of this session.

**The contract — demote, don't delete:**

1. Lead with a TL;DR: what is true, what to do, what it costs.
2. Put the full detail directly underneath — a `<details>` fold where HTML
   renders, a `--- detail ---` divider where it does not.
3. Never thin the detail because the summary exists.

**Never fold:** destructive actions, security findings, data loss,
money and quota, verbatim error text, diffs of code being changed, and anything
I explicitly asked to see in full.

**Agent-to-agent:** when output goes to another agent rather than to me, return
the parseable ```tldr``` block instead and write long output to a file.

**Arguments:** `$ARGUMENTS`

- If it is `0`, `1`, `3`, `5`, or `full`, set the depth dial to that value and
  confirm in one line.
- If it names something (`this file`, `that error`, `the last 20 commits`,
  `your last answer`), compress that one thing in the TL;DR shape and then
  return to the style that was already active. One-shot, no mode change.
- If it is empty, turn the mode on at depth 3 and confirm in one line.

These rules persist until I say "stop tldr", "tldr off", or "normal mode".
