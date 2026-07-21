#!/usr/bin/env bash
# sbx-launch.sh <sbx-name> [bootstrap-prompt]
# Launch ONE sandbox Claude session, remote-control enabled, inside a detached tmux session.
#
# KEY FIX vs the factory launcher: claude runs directly as the tmux pane command, so its
# stdout/stdin stay on the pane's REAL TTY. The factory launcher wrapped claude in
# `... | tee logfile`, which moves claude's stdout onto a pipe -> stdout.isTTY == false ->
# the interactive TUI (and thus remote-control) never initialises properly. We log with
# `tmux pipe-pane` INSTEAD, which copies pane output to a file WITHOUT taking claude off the TTY.
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/sbx-env.sh"

NAME="${1:-}"
PROMPT="${2:-}"                     # empty => idle interactive session (0 tokens until steered)
sbx_assert_target "$NAME"          # <-- refuses anything not sbx-* (real sessions unreachable)

command -v tmux >/dev/null 2>&1 || { sbx_log "FATAL: tmux missing."; exit 1; }

if tmux has-session -t "$NAME" 2>/dev/null; then
  sbx_log "session '$NAME' already running — no-op. (attach: tmux attach -t $NAME)"; exit 0
fi

LOG="${SBX_LOGDIR}/${NAME}.log"
# claude as the pane command => stays on the pane TTY. RC name == session name (sandbox-scoped).
if [[ -n "$PROMPT" ]]; then
  tmux new-session -d -s "$NAME" -c "$SBX_REPO" \
    "flock -n '$SBX_LOCK' claude --model $SBX_MODEL --remote-control '$NAME' '$PROMPT'"
else
  tmux new-session -d -s "$NAME" -c "$SBX_REPO" \
    "flock -n '$SBX_LOCK' claude --model $SBX_MODEL --remote-control '$NAME'"
fi
# Log the pane WITHOUT disturbing the TTY (the tee-bug fix).
tmux pipe-pane -o -t "$NAME" "cat >> '$LOG'" 2>/dev/null || sbx_log "WARN: pipe-pane logging unavailable."
sbx_log "started '$NAME' -> claude --remote-control '$NAME' ($SBX_MODEL). log: $LOG"
sbx_log "  attach: tmux attach -t $NAME   |   remote: claude.ai/code -> '$NAME'"
