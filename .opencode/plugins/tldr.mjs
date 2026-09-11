// tldr — OpenCode plugin.
//
// Mirrors the Claude Code / Codex behaviour for OpenCode. The skill in
// `skills/tldr/SKILL.md` is the single source of truth for the ruleset.
//
//   - On demand  — registers the skills directory and a `/tldr` command so the
//                  ruleset applies for the rest of the session.
//   - Always-on  — when the opt-in flag file exists, the full ruleset is appended
//                  to the system prompt every turn (the OpenCode equivalent of the
//                  SessionStart hook in hooks/always-on.mjs).
//
// Opt in to always-on:   touch ~/.config/opencode/.tldr-always
// Set a default depth:   echo 1 > ~/.config/opencode/.tldr-always
// Opt back out:          rm ~/.config/opencode/.tldr-always
//
// Install — add to opencode.json:
//   { "plugin": ["./.opencode/plugins/tldr.mjs"] }

import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillsDir = path.resolve(__dirname, '../../skills');
const skillPath = path.join(skillsDir, 'tldr', 'SKILL.md');
const commandPath = path.join(__dirname, '..', 'command', 'tldr.md');

const VALID_DEPTHS = new Set(['0', '1', '3', '5']);

// JSON is valid YAML frontmatter; share native command metadata without a YAML dependency.
async function commandDefinition() {
  const raw = await fs.promises.readFile(commandPath, 'utf8');
  const match = raw.match(/^---[^\S\r\n]*\r?\n([\s\S]*?)\r?\n---[^\S\r\n]*(?:\r?\n|$)([\s\S]*)$/);
  if (!match) throw new Error('Missing command frontmatter');
  return { ...JSON.parse(match[1]), template: match[2].trim() };
}

// Always-on opt-in flag, mirroring Claude Code's ~/.claude/.tldr-always but under
// OpenCode's config dir so the two tools stay independent.
const flagPath = path.join(
  process.env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config'),
  'opencode',
  '.tldr-always',
);

// Read SKILL.md and strip a leading YAML frontmatter block (--- ... ---).
// The regex and trailing-newline trim match hooks/always-on.mjs so always-on
// injections behave identically across harnesses (see tests/test_always_on_hooks.py).
function rulesetBody() {
  return fs
    .readFileSync(skillPath, 'utf8')
    .replace(/^---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---[^\S\r\n]*(?:\r?\n|$)/, '')
    .replace(/(?:\r?\n)+$/, '');
}

function configuredDepth() {
  try {
    const raw = fs.readFileSync(flagPath, 'utf8').trim();
    if (VALID_DEPTHS.has(raw)) return raw;
  } catch (e) {
    // Unreadable flag file still counts as opted in, at the default depth.
  }
  return '3';
}

export default async () => {
  return {
    // Make the skill discoverable, so the `skill` tool and the /tldr command can load it.
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) config.skills.paths.push(skillsDir);

      // Global installs need a command entry; preserve native or user-defined commands.
      try {
        config.command = config.command || {};
        if (!config.command['tldr']) {
          config.command['tldr'] = await commandDefinition();
        }
      } catch (e) {
        // Missing or malformed command files must not break skill discovery.
      }
    },

    // Always-on: append the ruleset to the system prompt every turn while the flag
    // file exists. "stop tldr" turns it off for the session (the model honours the
    // skill's own Persistence rules); deleting the flag turns always-on off for good.
    'experimental.chat.system.transform': async (_input, output) => {
      let on = false;
      try { on = fs.existsSync(flagPath); } catch (e) {}
      if (!on) return;

      let body;
      try { body = rulesetBody(); } catch (e) { return; }

      const header =
        'TLDR MODE ACTIVE (always-on). The ruleset below applies to every response. ' +
        'Depth dial is set to ' + configuredDepth() + '. ' +
        '"stop tldr" or "normal mode" turns it off for this session; delete ' +
        flagPath + ' to turn always-on off for good.';

      const injected = header + '\n\n' + body;

      if (output.system.length > 0) {
        output.system[output.system.length - 1] += '\n\n' + injected;
      } else {
        output.system.push(injected);
      }
    },
  };
};
