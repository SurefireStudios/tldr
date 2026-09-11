#!/usr/bin/env sh
# SessionStart hook (POSIX fallback): injects the full tldr ruleset when the user
# has opted in by creating $CLAUDE_CONFIG_DIR/.tldr-always (default ~/.claude).
#
# The Node implementation in always-on.mjs is the primary path and works on all
# three platforms. This script exists for environments without Node on PATH.
#
# Never blocks session start: always exits 0.

set -u

CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
FLAG_PATH="$CONFIG_DIR/.tldr-always"

[ -f "$FLAG_PATH" ] || exit 0

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd) || exit 0
SKILL_PATH="$SCRIPT_DIR/../skills/tldr/SKILL.md"

[ -f "$SKILL_PATH" ] || exit 0

DEPTH=$(tr -d ' \t\r\n' < "$FLAG_PATH" 2>/dev/null || echo '')
case "$DEPTH" in
  0|1|3|5) ;;
  *) DEPTH=3 ;;
esac

printf 'TLDR MODE ACTIVE (always-on). The ruleset below applies to every response. '
printf 'Depth dial is set to %s. ' "$DEPTH"
printf '"stop tldr" or "normal mode" turns it off for this session; '
printf 'remove %s to stop it loading at startup.\n\n' "$FLAG_PATH"

# Strip a leading YAML frontmatter block (--- ... --- at the very top of file).
awk '
  NR == 1 && $0 ~ /^---[ \t]*$/ { in_fm = 1; next }
  in_fm && $0 ~ /^---[ \t]*$/   { in_fm = 0; started = 1; next }
  in_fm                          { next }
  { print }
' "$SKILL_PATH" 2>/dev/null || exit 0

exit 0
