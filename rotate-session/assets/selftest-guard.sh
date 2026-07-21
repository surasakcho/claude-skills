#!/usr/bin/env bash
# selftest-guard.sh — prove the self-target guard accepts ONLY the current session.
# Safe: it only exercises rotate_assert_self (which returns a status); it NEVER kills anything.
# Run from inside any tmux session. Exit 0 = all assertions held; exit 1 = a guard failure.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/rotate-env.sh"

CUR="$(rotate_current_session)"
if [[ -z "$CUR" ]]; then echo "SKIP: not inside a tmux session; cannot self-test the guard here."; exit 0; fi

fails=0
ok(){ printf 'PASS  %s\n' "$1"; }
bad(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

# ACCEPT: the current session name (the one legitimate self-rotation target).
if rotate_assert_self "$CUR" 2>/dev/null; then ok "accept current session '$CUR'"; else bad "should ACCEPT current '$CUR'"; fi

# REFUSE: every OTHER live tmux session, plus synthetic edge cases. Any candidate that happens to
# equal the current session is skipped (it would be a legitimate accept, not a refuse case).
others="$(tmux ls -F '#{session_name}' 2>/dev/null | grep -vxF "$CUR" || true)"
for bogus in $others "" "SBX-1" "${CUR}x" "x${CUR}" "$CUR; rm -rf /" "*" "nonexistent-repo"; do
  [[ "$bogus" == "$CUR" ]] && continue
  if rotate_assert_self "$bogus" 2>/dev/null; then bad "should REFUSE '$bogus'"; else ok "refuse '$bogus'"; fi
done

echo "----"
if [[ "$fails" -eq 0 ]]; then echo "GUARD OK — self-rotation only."; exit 0
else echo "GUARD BROKEN — $fails assertion(s) failed."; exit 1; fi
