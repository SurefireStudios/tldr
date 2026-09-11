// tldr — OpenCode plugin.
//
// OpenCode has no SessionStart hook, so this plugin reproduces the two behaviours
// that hooks/always-on.mjs gives Claude Code and Codex. Either way the ruleset is
// read from skills/tldr/SKILL.md, which stays the only copy that matters.
//
//   On demand   Registers the skills directory plus a `/tldr` command, so a user
//               can switch the contract on for the rest of a session.
//
//   Always-on   While the opt-in flag file exists, the ruleset is appended to the
//               system prompt on every turn. OpenCode rebuilds that prompt per
//               request, which is why this hangs off a transform rather than
//               firing once at startup.
//
// Turn always-on on:     touch ~/.config/opencode/.tldr-always
// Pick a start depth:    echo 1 > ~/.config/opencode/.tldr-always
// Turn it back off:      rm ~/.config/opencode/.tldr-always
//
// Wire it up in opencode.json:
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

// The command file's frontmatter is written as JSON, which is also valid YAML.
// That lets both loaders share one file without pulling in a YAML parser.
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

// Read the skill and drop its frontmatter. The regex and the trailing-newline trim
// are deliberately identical to hooks/always-on.mjs: an OpenCode user and a Claude
// Code user must receive the same bytes, which tests/test_always_on_hooks.py
// asserts directly.
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

      // A global install has no project-local command to discover, so register one -
        // but never clobber a command the user or OpenCode already defined.
      try {
        config.command = config.command || {};
        if (!config.command['tldr']) {
          config.command['tldr'] = await commandDefinition();
        }
      } catch (e) {
        // A bad command file costs the user the slash command, not the whole skill.
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
        '"stop tldr" or "normal mode" turns it off for this session; remove ' +
        flagPath + ' to stop it loading at startup.';

      const injected = header + '\n\n' + body;

      if (output.system.length > 0) {
        output.system[output.system.length - 1] += '\n\n' + injected;
      } else {
        output.system.push(injected);
      }
    },
  };
};
