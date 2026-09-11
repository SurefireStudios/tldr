// SessionStart hook: injects the full tldr ruleset when the user has opted in
// by creating $CLAUDE_CONFIG_DIR/.tldr-always (default ~/.claude/.tldr-always).
//
// Optionally, the flag file may contain a single depth value (0, 1, 3, 5) to set
// the default depth dial for the session. An empty file means depth 3.
//
// Never blocks session start: any failure exits 0.
//
// Runs under Node so it works on macOS, Linux, and Windows. The shared Claude
// Code / Codex hook launches this module from the plugin-root environment rather
// than relying on platform-specific shell expansion for the script path. Native
// sh and PowerShell implementations remain available as fallbacks.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const VALID_DEPTHS = new Set(["0", "1", "3", "5"]);

try {
  const configDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
  const flagPath = path.join(configDir, ".tldr-always");

  // Only fire when the user has opted in.
  if (!fs.existsSync(flagPath)) process.exit(0);

  // Resolve SKILL.md relative to this script's own location, not a trusted env var.
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

  // Strip a leading YAML frontmatter block (--- ... --- at the very top of file).
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
      `delete ${flagPath} to turn always-on off for good.\n\n${body}\n`,
  );
} catch {
  // Never block session start.
  process.exit(0);
}
