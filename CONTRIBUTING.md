# Contributing

Three kinds of contribution are worth more than the rest. In order:

1. **A case where `tldr` dropped something it should have kept.** This is the highest-value contribution to the project, and it is worth more as a failing eval case than as a bug report. See [Reporting a compression failure](#reporting-a-compression-failure).
2. **A new harness adapter.** Every agent that can run `tldr` is a community that can find it. See [Adding a harness](#adding-a-harness).
3. **A translation.** See [Translations](#translations).

## Ground rules

- `skills/tldr/` is the single source of truth: `SKILL.md` is the core the model reads every time (kept under 5,000 characters, enforced by a test), `reference.md` is the long form it opens on demand. Change them first, then sync the mirrors.
- The never-compress list is load-bearing. Do not weaken it without an eval case proving the change is safe.
- Keep the skill readable in two minutes. Its whole trust model is that a person can audit it before installing.
- No runtime dependencies in the skill itself. It is markdown, and it stays markdown.

## Reporting a compression failure

If `tldr` compressed something you needed, that is a bug, not a preference.

Open an issue with:

- The exact prompt.
- The response you got.
- What was missing, and what you would have done differently if you had seen it.
- The harness and model.

Then, if you can, add it to [`evals/cases.jsonl`](evals/cases.jsonl):

```json
{"id":"your-case-id","category":"never-compress","prompt":"...","risk":"high","criteria":["States X above the fold.","Does not paraphrase Y."]}
```

A blocking finding in the `never-compress` or `safety` category disqualifies a release. That is the point: the case you add becomes a permanent guard.

Run `python3 scripts/run_evals.py validate` after editing.

## Adding a harness

1. Add the adapter — a manifest, a plugin file, or a documented copy path.
2. Add an `## Agent Name` section to [`INSTALL.md`](INSTALL.md) with Install / Verify / Update / Uninstall / Always-on subsections, matching the existing ones.
3. Add a row to the supported-agents table in [`README.md`](README.md), with an anchor link to your INSTALL.md section.
4. Add the runtime to the entry-point table in [`AGENTS.md`](AGENTS.md).
5. If the adapter copies the skill rather than reading it, add the copy's directory to `MIRROR_DIRS` in [`scripts/check_mirrors.py`](scripts/check_mirrors.py) so neither file can drift.

`tests/test_repo_contract.py` checks that README links resolve to real INSTALL.md headings, so step 3 is enforced.

**State what you tested.** "Installed on Cursor 2.4, ran `/tldr`, confirmed the fold renders" is a reviewable claim. "Should work" is not.

## Translations

Translated READMEs live in `.github/readme/README.<locale>.md`, translated install guides in `.github/install/INSTALL.<locale>.md`.

- Translate the prose. Do **not** translate command names, file paths, flag names, or the `tldr` block keys.
- Keep the language switcher at the top in sync across every translated file.
- Add your locale to the switcher in the English `README.md` too.

`skills/tldr/SKILL.md` itself stays in English: it is injected into a model's context, and maintaining behavioural parity across translated rulesets is not something this project can honestly promise.

## Changing the skill

The skill is the product, so changes to it get the most scrutiny.

1. Edit `skills/tldr/SKILL.md` (the core) or `skills/tldr/reference.md` (the elaborations). A rule the model needs on every turn goes in the core; a reason, an example or a rarely used feature goes in the reference.
2. Sync the mirrors: `cp skills/tldr/SKILL.md skills/tldr/reference.md .cursor/skills/tldr/`
3. Run the tests: `python3 -m unittest discover -s tests -v`
4. For anything that changes behaviour, run the evals and report the numbers.

State in the PR which rule you changed and what failure mode it addresses. A rule that does not prevent a concrete failure is a rule that makes the skill longer for no gain, and length is a real cost here — every line ships in someone's context window on every turn.

## Running the checks

```bash
python3 -m unittest discover -s tests -v   # 38 tests, no network
python3 scripts/check_mirrors.py           # mirrors match the canonical skill
python3 scripts/run_evals.py validate      # cases, rubric, and runners are well formed
```

All three run in CI on Linux, macOS, and Windows. The Windows run is not decorative: the PowerShell hook is the implementation most likely to break on encoding.

For behaviour changes, also:

```bash
python3 scripts/run_evals.py plan --trials 3
# ... run, judge, then:
python3 scripts/run_evals.py score evals/results/scores.jsonl
python3 scripts/count_tokens.py evals/results/responses.jsonl
```

Report the runtime, model, case count, trial count, rubric, and release-gate result. Publish the numbers whether or not they flatter the change.

## Pull requests

- One concern per PR.
- Run `git diff --check` before submitting, and check the diff for unrelated files.
- Fill in the [PR template](.github/pull_request_template.md).
- If an agent wrote the change, say so. It is not disqualifying; it is context for review.

## Code of conduct

Be straightforward and assume good faith. Critique the change, not the person. Maintainers may close discussions that stop being about the work.
