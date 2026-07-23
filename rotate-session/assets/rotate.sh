#!/usr/bin/env bash
# rotate.sh --preflight          -> run all safety checks, print PASS/FAIL, take NO action
# rotate.sh <predecessor_sha>    -> schedule same-name successor (detached) then guarded self-kill
#
# The Claude-driven steps (/handoff -> /wrap) run BEFORE this script, from SKILL.md. This script is
# ONLY the irreversible mechanical half.
#
# ORDER IS THE CORRECTNESS GUARANTEE (from sbx-rotate.sh): schedule the successor — detached into the
# user systemd manager, so it survives this process (and the whole session) dying — BEFORE the
# self-kill. If scheduling fails, the predecessor is NOT killed, so there is never a coverage gap.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/rotate-env.sh"

REPO_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CONF="$REPO_DIR/.claude/rotate.conf"
CURRENT="$(rotate_current_session)"

fail(){ ROTATE_LOG "PREFLIGHT FAIL: $*"; exit 1; }

# --- activation gate: a committed .claude/rotate.conf is what activates a repo ---
[[ -f "$CONF" ]] || fail "no .claude/rotate.conf in $REPO_DIR — rotation NOT activated for this repo (only activated repos rotate)."
# shellcheck disable=SC1090
source "$CONF"
: "${SESSION:?rotate.conf missing SESSION}"
MODEL="${MODEL:-}"; EFFORT="${EFFORT:-}"; RC_NAME="${RC_NAME:-$SESSION}"
PERMISSION_MODE="${PERMISSION_MODE:-}"; DELAY="${DELAY:-60}"; BOOTSTRAP_EXTRA="${BOOTSTRAP_EXTRA:-}"
REPO_DIR="${REPO_DIR_OVERRIDE:-$REPO_DIR}"

# --- THE GUARD: the config's SESSION must be THIS live session (self-rotation only) ---
rotate_assert_self "$SESSION" || fail "config SESSION='$SESSION' is not the current session '$CURRENT' — refusing."
[[ "$DELAY" =~ ^[0-9]+$ ]] || fail "DELAY '$DELAY' is not an integer."
command -v tmux >/dev/null 2>&1        || fail "tmux missing."
command -v systemd-run >/dev/null 2>&1 || fail "systemd-run missing (needed to detach the successor)."

if [[ "${1:-}" == "--preflight" ]]; then
  tmux has-session -t "$SESSION" 2>/dev/null || ROTATE_LOG "note: 'tmux has-session $SESSION' false (unexpected while inside it)."
  loginctl show-user "$USER" 2>/dev/null | grep -q 'Linger=yes' \
    || ROTATE_LOG "WARN: user linger is OFF — a successor scheduled near logout may not fire (loginctl enable-linger $USER)."
  ROTATE_LOG "PREFLIGHT PASS: self-rotation of '$SESSION' permitted (repo=$REPO_DIR, delay=${DELAY}s, rc=$RC_NAME)."
  exit 0
fi

SHA="${1:-unknown}"

# 1. Successor bootstrap — SHA dual-check per e-biz-factory/docs/auto-resume-design.md.
BOOTSTRAP="You are the REFRESHED successor for session '$SESSION'. Read the committed handoff note (CONTEXT.md or HANDOFF.md '## Next Session', or TODO.md). Run 'git fetch' and CONFIRM predecessor commit $SHA is present before proceeding. Then reply in ONE short line confirming you are the fresh successor and stating the next step. Do nothing else until instructed.${BOOTSTRAP_EXTRA:+ $BOOTSTRAP_EXTRA}"

# 2. Schedule the successor (detached; survives our death, incl. self-rotation). Pass PATH through.
LAUNCH="$HERE/rotate-launch.sh"
UNIT="claude-rotate-succ-${SESSION}-$(date +%s)"
if systemd-run --user --setenv=PATH="$PATH" --on-active="${DELAY}s" --unit="$UNIT" \
     "$LAUNCH" "$SESSION" "$REPO_DIR" "$MODEL" "$EFFORT" "$RC_NAME" "$PERMISSION_MODE" "$BOOTSTRAP" >/dev/null 2>&1; then
  ROTATE_LOG "successor scheduled: unit '$UNIT' fires in ${DELAY}s -> rotate-launch '$SESSION'."
else
  ROTATE_LOG "FATAL: could not schedule successor (systemd --user / linger?) — NOT killing predecessor."
  exit 1
fi

# 3. Guarded self-kill LAST (irreversible). Successor already queued above.
ROTATE_LOG "killing predecessor '$SESSION' now (successor appears in ~${DELAY}s)."
rotate_kill "$SESSION"
ROTATE_LOG "rotation initiated. Watch: claude.ai/code -> '$SESSION' reappears fresh in ~${DELAY}s."
