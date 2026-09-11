# Security

## What this project runs on your machine

By default: nothing. The skill is a markdown file that gets read into a model's context.

Two optional components execute code, and both are opt-in:

| Component | When it runs | What it does |
| --- | --- | --- |
| `hooks/always-on.*` | Session start, only if you created the `.tldr-always` flag file | Reads `SKILL.md`, strips the frontmatter, prints it. No network, no writes. |
| `.opencode/plugins/tldr.mjs`, `extensions/tldr.ts` | Inside OpenCode / Pi, if installed | Registers a command and injects the ruleset into the session. No network. |

None of these make network requests, write files, read anything outside the plugin directory and the single flag file, or collect telemetry. Read them yourself; together they are under 250 lines.

## Threat model

`tldr` shapes model output. It does not gate tool use, approve actions, or sit in any security boundary. It cannot grant an agent a permission it did not already have.

The one risk specific to this project is **hiding information that should have been seen**. A summary that omits a security finding, or folds a destructive action out of sight, is a real harm even though no code did anything unsafe.

That risk is addressed in the skill's never-compress list and enforced by the `never-compress` and `safety` eval categories, where a blocking finding disqualifies a release outright.

**If you find a prompt where `tldr` hid something consequential, please report it.** That is a security issue for this project, not a style complaint.

## Reporting a vulnerability

For anything that executes code, exfiltrates data, or escalates privileges, use GitHub's [private vulnerability reporting](https://github.com/SurefireStudios/tldr/security/advisories/new) rather than a public issue.

For a compression failure that hid something important, a public issue is fine and preferred — the case becomes an eval case, and that is better done in the open.

Expect an initial response within 7 days.

## Supply chain

- No runtime dependencies. `package.json` declares no `dependencies` or `devDependencies`.
- The eval scripts use only the Python standard library. `tiktoken` is optional and only affects token-count precision.
- Pin what you install: fork the repo if you need a frozen copy, rather than tracking `main`.
