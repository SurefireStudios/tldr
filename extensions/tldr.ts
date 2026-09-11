import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  getAgentDir,
  type ExtensionAPI,
  type ExtensionContext,
} from "@earendil-works/pi-coding-agent";

const EXTENSION_DIR = dirname(fileURLToPath(import.meta.url));
const SKILL_PATH = join(EXTENSION_DIR, "..", "skills", "tldr", "SKILL.md");

const STATE_ENTRY_TYPE = "tldr-state";
const RULES_MESSAGE_TYPE = "tldr-rules";
const DISABLED_MESSAGE_TYPE = "tldr-disabled";
const STATUS_KEY = "tldr";

const DISABLE_CONFIRMATION = "TLDR mode off.";
const STOP_PHRASES = new Set(["stop tldr", "tldr off", "normal mode"]);
const VALID_DEPTHS = ["0", "1", "3", "5"] as const;

type Depth = (typeof VALID_DEPTHS)[number];

const DISABLED_NOTICE =
  "TLDR MODE OFF. Ignore the tldr ruleset injected earlier in this conversation and return to your default response style.";

type TldrModeState = {
  enabled: boolean;
  depth: Depth;
};

type TldrConfig = {
  alwaysOn?: boolean;
  depth?: Depth;
  hideStatus?: boolean;
};

function isDepth(value: string): value is Depth {
  return (VALID_DEPTHS as readonly string[]).includes(value);
}

function loadConfig(): TldrConfig {
  try {
    return JSON.parse(readFileSync(join(getAgentDir(), "tldr.json"), "utf8"));
  } catch {
    return {};
  }
}

function stripFrontmatter(content: string): string {
  return content
    .replace(/^---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---[^\S\r\n]*(?:\r?\n|$)/, "")
    .trim();
}

function loadRules(): string {
  let content: string;

  try {
    content = readFileSync(SKILL_PATH, "utf8");
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new Error(`Unable to load tldr rules from ${SKILL_PATH}: ${reason}`);
  }

  const rules = stripFrontmatter(content);
  if (!rules) {
    throw new Error(`The tldr rules file is empty: ${SKILL_PATH}`);
  }

  return rules;
}

function rulesHeader(depth: Depth): string {
  const dial =
    depth === "0"
      ? "Depth dial is set to 0: headline only, no detail section."
      : `Depth dial is set to ${depth}: ${depth} summary line(s), then the full detail.`;

  return `TLDR MODE ACTIVE. The ruleset below applies to every response until turned off. ${dial} "stop tldr" or "normal mode" turns it off for this session.`;
}

function getSavedState(ctx: ExtensionContext): Partial<TldrModeState> | undefined {
  let savedState: Partial<TldrModeState> | undefined;

  for (const entry of ctx.sessionManager.getBranch()) {
    if (entry.type !== "custom" || entry.customType !== STATE_ENTRY_TYPE) {
      continue;
    }

    const data = entry.data as Partial<TldrModeState> | undefined;
    if (data && typeof data.enabled === "boolean") {
      savedState = data;
    }
  }

  return savedState;
}

/**
 * Whether the rules are still live in the context the model actually receives.
 *
 * Only the newest marker counts: a later "disabled" notice cancels an earlier
 * ruleset, and compaction drops summarized entries so the ruleset has to be
 * injected again.
 */
function rulesAreInContext(ctx: ExtensionContext): boolean {
  let active = false;

  for (const entry of ctx.sessionManager.getBranch()) {
    if (entry.type !== "custom") continue;
    if (entry.customType === RULES_MESSAGE_TYPE) active = true;
    else if (entry.customType === DISABLED_MESSAGE_TYPE) active = false;
  }

  return active;
}

export default function tldrExtension(pi: ExtensionAPI) {
  const rules = loadRules();
  const alwaysOnFlag = join(getAgentDir(), ".tldr-always");
  const config = loadConfig();

  let enabled = false;
  let depth: Depth = config.depth && isDepth(config.depth) ? config.depth : "3";

  const updateStatus = (ctx: ExtensionContext): void => {
    if (!enabled || config.hideStatus) {
      ctx.ui.setStatus(STATUS_KEY, undefined);
      return;
    }

    const dot = ctx.ui.theme.fg("success", "●");
    const label = ctx.ui.theme.fg("accent", `TLDR ${depth}`);
    ctx.ui.setStatus(STATUS_KEY, `${dot} ${label}`);
  };

  /**
   * Keep the conversation in sync with the current mode, the way the Claude Code
   * SessionStart hook does: inject the ruleset once, never per request.
   */
  const syncContext = (ctx: ExtensionContext): void => {
    const injected = rulesAreInContext(ctx);

    if (enabled && !injected) {
      pi.sendMessage(
        {
          customType: RULES_MESSAGE_TYPE,
          content: `${rulesHeader(depth)}\n\n${rules}`,
          display: false,
        },
        { triggerTurn: false },
      );
      return;
    }

    if (!enabled && injected) {
      pi.sendMessage(
        {
          customType: DISABLED_MESSAGE_TYPE,
          content: DISABLED_NOTICE,
          display: false,
        },
        { triggerTurn: false },
      );
    }
  };

  const restoreState = (ctx: ExtensionContext): void => {
    const savedState = getSavedState(ctx);
    const enabledByDefault =
      pi.getFlag("tldr") === true ||
      config.alwaysOn === true ||
      existsSync(alwaysOnFlag);

    enabled = savedState?.enabled ?? enabledByDefault;
    if (savedState?.depth && isDepth(savedState.depth)) depth = savedState.depth;

    updateStatus(ctx);
    syncContext(ctx);
  };

  const setState = (
    nextEnabled: boolean,
    nextDepth: Depth,
    ctx: ExtensionContext,
  ): void => {
    const depthChanged = nextDepth !== depth;
    enabled = nextEnabled;
    depth = nextDepth;

    pi.appendEntry(STATE_ENTRY_TYPE, { enabled, depth } satisfies TldrModeState);
    updateStatus(ctx);

    // A depth change has to re-inject: the header carries the dial value.
    if (depthChanged && enabled && rulesAreInContext(ctx)) {
      pi.sendMessage(
        {
          customType: DISABLED_MESSAGE_TYPE,
          content: DISABLED_NOTICE,
          display: false,
        },
        { triggerTurn: false },
      );
    }

    syncContext(ctx);
    ctx.ui.notify(
      enabled ? `TLDR mode on (depth ${depth})` : "TLDR mode off",
      "info",
    );
  };

  pi.registerFlag("tldr", {
    description: "Start with TL;DR output enabled",
    type: "boolean",
    default: false,
  });

  pi.registerCommand("tldr", {
    description: "Toggle TL;DR output for this session, or set the depth dial",
    handler: async (args, ctx) => {
      const argument = args.trim().toLowerCase();

      if (argument === "") {
        setState(!enabled, depth, ctx);
        return;
      }

      if (argument === "on") {
        setState(true, depth, ctx);
        return;
      }

      if (argument === "off" || argument === "stop" || argument === "full") {
        setState(false, depth, ctx);
        return;
      }

      if (isDepth(argument)) {
        setState(true, argument, ctx);
        return;
      }

      ctx.ui.notify("Usage: /tldr [on|off|full|0|1|3|5]", "warning");
    },
  });

  pi.on("input", async (event, ctx) => {
    const input = event.text.trim().toLowerCase();

    // Keep the built-in skill command working as an alias without letting Pi
    // expand a second copy of the same rules into the conversation.
    if (input === "/skill:tldr") {
      setState(true, depth, ctx);
      return { action: "handled" };
    }

    if (enabled && STOP_PHRASES.has(input)) {
      setState(false, depth, ctx);

      if (ctx.hasUI) {
        return { action: "handled" };
      }

      return {
        action: "transform",
        text: `Reply with exactly: ${DISABLE_CONFIRMATION}`,
      };
    }

    return { action: "continue" };
  });

  pi.on("session_start", async (_event, ctx) => restoreState(ctx));
  pi.on("session_tree", async (_event, ctx) => restoreState(ctx));
  pi.on("session_compact", async (_event, ctx) => syncContext(ctx));
}
