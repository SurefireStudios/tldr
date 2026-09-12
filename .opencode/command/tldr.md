---
{"description": "Lead with a three-line TL;DR and fold the detail, for the rest of this session"}
---

Use the `tldr` skill and apply its contract to every response for the rest of
this session: lead with a three-line TL;DR covering what is true, what to do,
and what it costs, then place the full detail directly underneath — folded in a
`<details>` block where HTML renders, below a `--- detail ---` divider where it
does not.

Demote, don't delete: nothing is discarded, only moved below the summary.
Never fold destructive actions, security findings, data loss, money and quota, verbatim error text, diffs of code being changed, legal/medical/safety boundaries, and anything I asked to see in full.

When returning output to another agent rather than a human, the parseable
`tldr` block is the whole response; if a long version was written to a file,
`full:` carries its path. The skill's `reference.md` holds the elaborations.

`$ARGUMENTS` may set the depth dial (`0`, `1`, `3`, `5`, or `full`) or name a
single target to compress on demand. These rules persist until I say "stop tldr"
or "normal mode".
