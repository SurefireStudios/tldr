#!/usr/bin/env bash
# Run the whole evaluation pipeline end to end.
#
#   scripts/run_full_eval.sh                        # full run, sonnet, 3 trials
#   scripts/run_full_eval.sh --smoke                # 2 cases, 1 trial, haiku
#   scripts/run_full_eval.sh --runner claude-opus   # the expensive headline run
#   scripts/run_full_eval.sh --trials 5
#
# Every stage is resumable. If a stage fails partway, rerun the same command and
# completed rows are skipped rather than repaid for.

set -u

RUNNER="claude"
TRIALS=3
LIMIT=""
OUT_DIR="evals/results"

while [ $# -gt 0 ]; do
  case "$1" in
    --smoke)  RUNNER="claude-haiku"; TRIALS=1; LIMIT="--limit 2"; shift ;;
    --runner) RUNNER="$2"; shift 2 ;;
    --trials) TRIALS="$2"; shift 2 ;;
    --limit)  LIMIT="--limit $2"; shift 2 ;;
    -h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

RESPONSES="$OUT_DIR/responses.jsonl"
SCORES="$OUT_DIR/scores.jsonl"

PY=python3
command -v $PY >/dev/null 2>&1 || PY=python

say() { printf '\n\033[1m== %s\033[0m\n' "$1"; }

say "Preflight"
$PY scripts/run_evals.py validate || exit 1

# A logged-out CLI produces 144 identical auth failures rather than an eval.
# Catch it once, here, instead of at every call site.
if ! claude auth status 2>/dev/null | grep -q '"loggedIn": *true'; then
  cat >&2 <<'MSG'

  The Claude CLI is not logged in, so every runner call would fail.

  Fix it with ONE of:
    claude login                 # interactive; uses your subscription
    export ANTHROPIC_API_KEY=... # set it in your own shell; bills API credits

  Then rerun this script. Nothing has been spent.
MSG
  exit 1
fi

if [ -z "$LIMIT" ]; then
  say "Plan"
  $PY scripts/run_evals.py plan --trials "$TRIALS"
fi

say "Generating: baseline"
$PY scripts/run_evals.py run \
  --runner "$RUNNER" --condition baseline \
  --trials "$TRIALS" $LIMIT --output "$RESPONSES" || exit 1

say "Generating: candidate"
$PY scripts/run_evals.py run \
  --runner "$RUNNER" --condition candidate \
  --condition-skill skills/tldr/SKILL.md \
  --trials "$TRIALS" $LIMIT --output "$RESPONSES" || exit 1

say "Judging (blind)"
# A judge failure on a few groups is recoverable: judging is resumable, so rerunning
# fills the gaps. Aborting here would throw away a paid-for generation pass over one
# bad group, so warn and carry on to scoring.
$PY scripts/judge.py --runner "$RUNNER" \
  --responses "$RESPONSES" --output "$SCORES" \
  || echo "  judge reported failures; rerun to fill the gaps before trusting the gate" >&2

say "Quality and release gate"
$PY scripts/run_evals.py score "$SCORES"
GATE=$?

say "Token accounting"
$PY scripts/count_tokens.py "$RESPONSES"

# Automated count of fabricated tool calls and results, per condition. The blind
# judge catches most of these as blockers; this catches all of them, and shows
# amplification (baseline vs candidate) at a glance. It is what exposed the fact
# that the earlier ad-hoc detection had undercounted by a third.
say "Fabrication"
$PY scripts/detect_fabrication.py "$RESPONSES"

say "Done"
echo "  responses: $RESPONSES"
echo "  scores:    $SCORES"
echo "  runner:    $RUNNER    trials: $TRIALS"
echo
echo "  Record the runner, model, case count and trial count in evals/RESULTS.md"
echo "  alongside BOTH tables. A token number without the fidelity number is not a result."
[ $GATE -eq 0 ] && echo "  Release gate: PASSED" || echo "  Release gate: FAILED (publish it anyway, with the explanation)"

exit $GATE
