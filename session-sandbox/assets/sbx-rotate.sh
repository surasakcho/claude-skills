#!/usr/bin/env bash
# sbx-rotate.sh <sbx-name> [delay_seconds] [successor_prompt]
# REFRESH a sandbox session: write a breadcrumb, schedule a SAME-NAME successor (detached, so it
# survives this process dying), then guarded self-kill of the predecessor. From claude.ai the session
# named <sbx-name> drops, then reappears fresh after ~delay with the breadcrumb available.
#
# ORDER IS THE CORRECTNESS GUARANTEE (like the factory handoff): schedule the successor BEFORE the
# kill. The successor is dispatched into the user systemd manager (detached from our process tree,
# linger on), so even if the kill also ends the caller (self-rotation from inside the session), the
# successor is already queued.
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/sbx-env.sh"

NAME="${1:-}"
DELAY="${2:-60}"                                   # seconds until the successor launches
sbx_assert_target "$NAME"                          # refuses anything not sbx-* (self-target IS allowed: refresh)
[[ "$DELAY" =~ ^[0-9]+$ ]] || { sbx_log "FATAL: delay '$DELAY' not an integer."; exit 1; }

DEFAULT_PROMPT="You are the REFRESHED successor for sandbox session '$NAME'. Read state/${NAME}.handoff.md, then reply in ONE short line confirming you are the fresh successor and stating the next step. Do nothing else until instructed."
PROMPT="${3:-$DEFAULT_PROMPT}"

command -v systemd-run >/dev/null 2>&1 || { sbx_log "FATAL: systemd-run missing (needed to detach the successor)."; exit 1; }
tmux has-session -t "$NAME" 2>/dev/null || sbx_log "note: '$NAME' not currently running — scheduling a successor anyway."

# 1. Breadcrumb — the successor reconstructs continuity from this (repo-as-memory).
BC="${SBX_REPO}/state/${NAME}.handoff.md"
pred_pid="$(pgrep -f -- "remote-control $NAME" | head -1)"
{
  echo "# HANDOFF breadcrumb — ${NAME}"
  echo
  echo "- Written: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "- Predecessor claude pid: ${pred_pid:-unknown} (rotated out to refresh context)"
  echo "- You are the fresh same-name successor. Reconstruct state from this repo, not chat."
  echo "- Next step: (test rotation — no work item; confirm you read this and are steerable)."
} > "$BC"
sbx_log "breadcrumb written: $BC"

# 2. Schedule the successor (detached, survives our death). Pass PATH so it finds claude/tmux/flock.
LAUNCH="${SBX_REPO}/bin/sbx-launch.sh"
UNIT="sbx-succ-${NAME}-$(date +%s)"
if systemd-run --user --setenv=PATH="$PATH" --on-active="${DELAY}s" --unit="$UNIT" \
     "$LAUNCH" "$NAME" "$PROMPT" >/dev/null 2>&1; then
  sbx_log "successor scheduled: unit '$UNIT' fires in ${DELAY}s -> sbx-launch '$NAME'."
else
  sbx_log "FATAL: could not schedule successor (systemd --user / linger?) — NOT killing predecessor."
  exit 1
fi

# 3. Guarded self-kill LAST (irreversible for the predecessor). Successor already queued above.
sbx_log "killing predecessor '$NAME' now (successor will appear in ~${DELAY}s)."
sbx_kill "$NAME"
sbx_log "rotation initiated. Watch: claude.ai/code -> '$NAME' reappears fresh in ~${DELAY}s."
