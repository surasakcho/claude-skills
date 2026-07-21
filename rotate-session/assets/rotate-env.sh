#!/usr/bin/env bash
# rotate-env.sh — shared helpers + the SELF-TARGET guard for the rotate-session skill.
# Source at the top of every rotate-* script:  source "$(dirname "$0")/rotate-env.sh"
#
# SAFETY CONTRACT (why this file exists):
#   rotate-session refreshes a LIVE Claude session by killing it and relaunching a same-name
#   successor. The sandbox (session-sandbox) is safe because ONLY sbx-* names are targetable.
#   This skill runs against REAL session names in EVERY repo, so that prefix guard is gone.
#   The guarantee here is SELF-ROTATION ONLY:
#     * the only session you may act on is the one you are running inside
#       (target == `tmux display-message -p '#S'`)
#     * rotate_assert_self REFUSES an empty name, a non-tmux context, or any name != current session
#     * there is deliberately NO kill-by-pattern, NO kill-all, NO kill-by-arbitrary-name path.
#       The ONLY kill is rotate_kill <name>, and it calls the guard first.
#   => a typo, a stale config, or a bad env var can never resolve to ANOTHER repo's session:
#      it will not equal the current session name, so the guard refuses.

set -euo pipefail

ROTATE_LOG(){ printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')" "$*" >&2; }

# Name of the tmux session this script is running inside (empty if not in tmux).
rotate_current_session(){ tmux display-message -p '#S' 2>/dev/null || true; }

# THE GUARD. Non-zero (aborts `set -e` callers) unless <name> is THIS session — self-rotation only.
rotate_assert_self(){
  local name="${1:-}"
  local current; current="$(rotate_current_session)"
  if [[ -z "$name" ]]; then
    ROTATE_LOG "GUARD: empty target name — refusing."; return 1
  fi
  if [[ -z "$current" ]]; then
    ROTATE_LOG "GUARD: not inside a tmux session (no current session) — refusing '$name'."; return 1
  fi
  if [[ "$name" != "$current" ]]; then
    ROTATE_LOG "GUARD: target '$name' is not the current session '$current' — self-rotation ONLY. REFUSING. Other sessions are unreachable by design."; return 1
  fi
  return 0
}

# The ONLY kill path. Guarded.
rotate_kill(){
  local name="${1:-}"
  rotate_assert_self "$name" || return 1
  if tmux has-session -t "$name" 2>/dev/null; then
    tmux kill-session -t "$name"
    ROTATE_LOG "killed session '$name' (self)."
  else
    ROTATE_LOG "no session '$name' to kill (already gone)."
  fi
}

# Per-session launch lock (prevents a duplicate same-name session racing the successor).
rotate_lock_path(){ printf '%s/.cache/claude-rotate-%s.lock' "$HOME" "${1:?name}"; }
