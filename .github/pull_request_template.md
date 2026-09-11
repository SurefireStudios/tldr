## What this changes

<!-- One or two lines. The TL;DR of your own PR — this repo would want nothing less. -->

## Type

- [ ] Compression failure fix (tldr dropped something it should have kept)
- [ ] New harness adapter
- [ ] Translation
- [ ] Skill rule change
- [ ] Docs, tooling, or evals
- [ ] Something else

## Why

<!-- What concrete failure does this prevent? A rule that does not prevent a concrete
     failure makes the skill longer for no gain, and every line ships in someone's
     context window on every turn. -->

## What I tested

<!-- Exact commands and results. "Installed on Cursor 2.4, ran /tldr, confirmed the
     fold renders" is reviewable. "Should work" is not. -->

```
```

## Checklist

- [ ] `python3 -m unittest discover -s tests` passes
- [ ] `python3 scripts/check_mirrors.py` passes (if I touched `SKILL.md`)
- [ ] `python3 scripts/run_evals.py validate` passes (if I touched `evals/`)
- [ ] `git diff --check` is clean and the diff contains no unrelated files

### If this changes skill behaviour

- [ ] I ran the evals and reported the runtime, model, cases, trials, and gate result below
- [ ] I did not weaken the never-compress list, or I added an eval case proving the change is safe

<!-- Eval results, if applicable: -->

### If this adds a harness

- [ ] `INSTALL.md` has a section with Install / Verify / Update / Uninstall / Always-on
- [ ] The README supported-agents table has a row linking to it
- [ ] `AGENTS.md` entry-point table updated
- [ ] If the adapter copies `SKILL.md`, the copy is registered in `scripts/check_mirrors.py`

## Agent disclosure

- [ ] An AI agent wrote some or all of this change

<!-- Not disqualifying. It is context for review. -->
