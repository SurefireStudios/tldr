---
{"description": "Lead with a three-line TL;DR and fold the detail, for the rest of this session"}
---

Use the `tldr` skill and apply its contract to every response for the rest of
this session: lead with a three-line TL;DR covering what is true, what to do,
and what it costs, then place the full detail directly underneath — folded in a
`<details>` block where HTML renders, below a `--- detail ---` divider where it
does not.

Demote, don't delete: nothing is discarded, only moved below the summary.
Destructive actions, security findings, data loss, cost, and verbatim error text
are never folded.

When returning output to another agent rather than a human, use the parseable
`tldr` block instead, and write long output to a file rather than piping it
through the context window.

`$ARGUMENTS` may set the depth dial (`0`, `1`, `3`, `5`, or `full`) or name a
single target to compress on demand. These rules persist until I say "stop tldr"
or "normal mode".
