#!/usr/bin/env bash
# rotate-launch.sh <name> <repo_dir> <model> <effort> <rc_name> <permission_mode> [bootstrap]
# Launch ONE Claude session (remote-control) in a detached tmux session, on a REAL TTY.
#
# KEY FIX (from sbx-launch.sh): claude runs as the pane command so its stdout/stdin stay on the
# pane's REAL TTY. We log with `tmux pipe-pane` — NOT `| tee`, which moves stdout onto a pipe
# (stdout.isTTY == false) and stops the interactive TUI + remote-control from initialising.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/rotate-env.sh"

NAME="${1:?name}"; REPO_DIR="${2:?repo_dir}"; MODEL="${3:-}"; EFFORT="${4:-}"
RC_NAME="${5:-$NAME}"; PERMISSION_MODE="${6:-}"; BOOTSTRAP="${7:-}"

command -v tmux >/dev/null 2>&1 || { ROTATE_LOG "FATAL: tmux missing."; exit 1; }
if tmux has-session -t "$NAME" 2>/dev/null; then
  ROTATE_LOG "session '$NAME' already running — no-op. (attach: tmux attach -t $NAME)"; exit 0
fi

LOCK="$(rotate_lock_path "$NAME")"; mkdir -p "$(dirname "$LOCK")"
LOGDIR="${HOME}/.cache/claude-rotate-logs"; mkdir -p "$LOGDIR"     # OUTSIDE the repo — never committed
LOG="${LOGDIR}/${NAME}.log"

# Assemble the claude invocation for the tmux pane. flock -n serialises same-name launches.
cmd="flock -n '$LOCK' claude --remote-control '$RC_NAME'"
[[ -n "$MODEL" ]]            && cmd="$cmd --model '$MODEL'"
[[ -n "$EFFORT" ]]          && cmd="$cmd --effort '$EFFORT'"
[[ -n "$PERMISSION_MODE" ]] && cmd="$cmd --permission-mode '$PERMISSION_MODE'"
[[ -n "$BOOTSTRAP" ]]       && cmd="$cmd '$BOOTSTRAP'"

tmux new-session -d -s "$NAME" -c "$REPO_DIR" "$cmd"
# Log the pane WITHOUT disturbing the TTY (the tee-bug fix).
tmux pipe-pane -o -t "$NAME" "cat >> '$LOG'" 2>/dev/null || ROTATE_LOG "WARN: pipe-pane logging unavailable."
ROTATE_LOG "started '$NAME' -> claude --remote-control '$RC_NAME' (dir=$REPO_DIR). log: $LOG"
ROTATE_LOG "  attach: tmux attach -t $NAME   |   remote: claude.ai/code -> '$RC_NAME'"
