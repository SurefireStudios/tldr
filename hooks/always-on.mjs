// SessionStart hook. Prints the tldr ruleset into a new session, but only for
// users who asked for it by creating $CLAUDE_CONFIG_DIR/.tldr-always
// (default ~/.claude/.tldr-always).
//
// That flag file may hold a single digit - 0, 1, 3 or 5 - to pick a starting
// depth. Empty means depth 3.
//
// Node is the primary implementation because one file then covers macOS, Linux
// and Windows. The declaration in hooks.json launches it from the plugin root, so
// no shell has to expand the path itself. always-on.sh and always-on.ps1 exist
// for machines without Node on PATH.
//
// Every failure here is silent and exits 0. A hook that shapes output must never
// be the reason somebody cannot open a session.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const VALID_DEPTHS = new Set(["0", "1", "3", "5"]);

try {
  const configDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
  const flagPath = path.join(configDir, ".tldr-always");

  // No flag, nothing to say.
  if (!fs.existsSync(flagPath)) process.exit(0);

  // Find the skill from this file's own path. An env var could point anywhere.
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const skillPath = path.join(scriptDir, "..", "skills", "tldr", "SKILL.md");
  if (!fs.existsSync(skillPath)) process.exit(0);

  // An optional depth value in the flag file overrides the default dial.
  let depth = "3";
  try {
    const raw = fs.readFileSync(flagPath, "utf8").trim();
    if (VALID_DEPTHS.has(raw)) depth = raw;
  } catch {
    // Unreadable flag file still counts as opted in, at the default depth.
  }

  // Drop the frontmatter. It is harness metadata, not instructions for a model.
  const body = fs
    .readFileSync(skillPath, "utf8")
    .replace(/^---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---[^\S\r\n]*(?:\r?\n|$)/, "")
    .replace(/(?:\r?\n)+$/, "");

  const depthNote =
    depth === "0"
      ? "Depth dial is set to 0: headline only, no detail section."
      : `Depth dial is set to ${depth}: ${depth} summary line(s), then the full detail.`;

  process.stdout.write(
    "TLDR MODE ACTIVE (always-on). The ruleset below applies to every response. " +
      `${depthNote} ` +
      '"stop tldr" or "normal mode" turns it off for this session; ' +
      `remove ${flagPath} to stop it loading at startup.\n\n${body}\n`,
  );
} catch {
  // Swallow everything; see the note at the top of this file.
  process.exit(0);
}
