#!/usr/bin/env bash
# sbx-env.sh — shared constants + the ISOLATION GUARD for the sandbox.
# Source this at the top of every sandbox script:  source "$(dirname "$0")/sbx-env.sh"
#
# SAFETY CONTRACT (why this file exists):
#   The whole point of the sandbox is to develop a session-continuity mechanism that
#   starts/kills/rotates Claude sessions WITHOUT any risk to real sessions (e.g. `ebiz`,
#   the operator's live session). The guarantee is enforced structurally here:
#     * every sandbox session/RC name MUST match ^sbx-[a-z0-9]+$
#     * sbx_assert_target REFUSES any name that is not sbx-* (real sessions can't match the prefix)
#     * a sbx-* session MAY target ITSELF — self-rotation (refresh) is the whole point; the prefix,
#       not a "== current" rule, is the load-bearing guard (a real session can never match sbx-*).
#   => a bug, a typo, or a bad env var can never resolve to a real session name.
#      There is deliberately NO code path that kills a session by pattern, by "all", or by
#      the current session. Only `sbx_kill <sbx-name>` exists, and it calls the guard first.

set -euo pipefail

SBX_PREFIX="sbx-"                                   # reserved namespace — real sessions never start with this

# SBX_REPO is machine-specific and is therefore never a literal here: a path in a shared skill
# publishes a username and a directory layout. Order: environment > <skills-repo>/.env > hard
# failure. There is deliberately NO default — a sandbox rooted at a guessed path is exactly the
# silent mistake this file exists to prevent, and failing loudly costs one command to fix.
SBX_ENV_FILE="${SBX_ENV_FILE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/.env}"
if [ -z "${SBX_REPO:-}" ] && [ -f "$SBX_ENV_FILE" ]; then
  SBX_REPO="$(sed -n 's/^SBX_REPO=//p' "$SBX_ENV_FILE" | head -n1)"
fi
: "${SBX_REPO:?is not set. Export it, or store it once: python lib/skillconfig.py get SBX_REPO --repo <skills-repo> --prompt 'Sandbox repo root'}"
SBX_LOCK="${HOME}/.cache/sandbox-session.lock"      # sandbox-only lock (never the factory lock)
SBX_LOGDIR="${SBX_REPO}/state/logs"
SBX_CRON_TAG="# SANDBOX-CONTINUITY"                 # marker on EVERY sandbox cron line, for surgical add/remove
SBX_MODEL="${SBX_MODEL:-sonnet}"                    # cheap tier — this is infra plumbing, failure is loud

mkdir -p "$(dirname "$SBX_LOCK")" "$SBX_LOGDIR"

sbx_log(){ printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')" "$*" >&2; }

# The current tmux session this script is running inside (empty if not in tmux).
sbx_current_session(){ tmux display-message -p '#S' 2>/dev/null || true; }

# THE GUARD. Exits non-zero (aborting `set -e` callers) unless <name> is a safe sandbox target.
sbx_assert_target(){
  local name="${1:-}"
  if [[ -z "$name" ]]; then
    sbx_log "GUARD: empty target name — refusing."; return 1
  fi
  if [[ ! "$name" =~ ^sbx-[a-z0-9]+$ ]]; then
    sbx_log "GUARD: '$name' is not a sandbox name (must match ^sbx-[a-z0-9]+\$) — REFUSING. Real sessions are unreachable by design."; return 1
  fi
  # A sandbox session targeting ITSELF is ALLOWED — self-rotation (refresh) is intended. The sbx-*
  # prefix above already makes every real session (ebiz, gamelab-os, …) unreachable, so there is
  # deliberately no "refuse == current" rule (it would only ever block the legitimate self-refresh).
  return 0
}

# The ONLY kill path in the sandbox. Guarded.
sbx_kill(){
  local name="${1:-}"
  sbx_assert_target "$name" || return 1
  if tmux has-session -t "$name" 2>/dev/null; then
    tmux kill-session -t "$name"
    sbx_log "killed sandbox session '$name'."
  else
    sbx_log "no session '$name' to kill (already gone)."
  fi
}
