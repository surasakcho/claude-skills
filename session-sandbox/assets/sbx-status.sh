#!/usr/bin/env bash
# sbx-status.sh — report every sandbox (sbx-*) session: is claude on a real TTY, and does it
# hold an established connection to Anthropic's remote relay (160.79.104.0/22)?
# Read-only. Never touches non-sandbox sessions.
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/sbx-env.sh"

sessions="$(tmux ls -F '#{session_name}' 2>/dev/null | grep -E '^sbx-' || true)"
if [[ -z "$sessions" ]]; then echo "(no sbx-* sessions running)"; exit 0; fi

while read -r s; do
  [[ -z "$s" ]] && continue
  pane_pid="$(tmux list-panes -t "$s" -F '#{pane_pid}' 2>/dev/null | head -1)"
  cl_pid="$(pgrep -P "$pane_pid" -f 'claude' 2>/dev/null | head -1)"
  [[ -z "$cl_pid" ]] && cl_pid="$(pgrep -f -- "remote-control $s" 2>/dev/null | head -1)"
  tty="$(readlink /proc/${cl_pid:-0}/fd/1 2>/dev/null || true)"
  is_tty="no"; [[ "$tty" == /dev/pts/* ]] && is_tty="YES"
  relay="$(ss -tnp 2>/dev/null | grep -w "pid=${cl_pid:-x}" | grep ESTAB | grep -E '160\.79\.10[4-7]\.' | wc -l)"
  printf "%-12s claude_pid=%-8s on_TTY=%-3s relay_conns=%s\n" "$s" "${cl_pid:-none}" "$is_tty" "$relay"
done <<< "$sessions"
