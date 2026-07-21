#!/usr/bin/env bash
# rotate-status.sh [session]   (default: the current tmux session)
# Read-only: is claude on a real TTY, and does it hold an established Anthropic relay connection
# (160.79.104.0/22)? Never kills or changes anything.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/rotate-env.sh"

s="${1:-$(rotate_current_session)}"
[[ -n "$s" ]] || { echo "(no session given and not inside tmux)"; exit 0; }
tmux has-session -t "$s" 2>/dev/null || { echo "$s (not running)"; exit 0; }

pane_pid="$(tmux list-panes -t "$s" -F '#{pane_pid}' 2>/dev/null | head -1)"
cl_pid="$(pgrep -P "$pane_pid" -f 'claude' 2>/dev/null | head -1)"
[[ -z "$cl_pid" ]] && cl_pid="$(pgrep -f -- "remote-control $s" 2>/dev/null | head -1)"
tty="$(readlink /proc/${cl_pid:-0}/fd/1 2>/dev/null || true)"
is_tty="no"; [[ "$tty" == /dev/pts/* ]] && is_tty="YES"
# Count established relay connections. grep -c exits 1 on zero matches, so tolerate it under pipefail.
relay=0
if [[ -n "$cl_pid" ]]; then
  relay="$(ss -tnp 2>/dev/null | { grep -w "pid=${cl_pid}" || true; } | { grep ESTAB || true; } | grep -Ec '160\.79\.10[4-7]\.' || true)"
  [[ -z "$relay" ]] && relay=0
fi
printf "%-16s claude_pid=%-8s on_TTY=%-3s relay_conns=%s\n" "$s" "${cl_pid:-none}" "$is_tty" "$relay"
