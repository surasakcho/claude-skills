---
name: rotate-session
description: Refresh (rotate) the CURRENT Claude session in place — hand off, wrap, then drop and relaunch a fresh same-name successor with an empty context window. Only rotates the session you are inside, and only in a repo that has opted in with a committed .claude/rotate.conf.
argument-hint: "What should the next (fresh) session focus on?"
disable-model-invocation: true
---

# rotate-session — refresh the current session in place

Rotate the **current** Claude session: preserve continuity to disk, then replace this
session with a fresh same-name successor (empty context window). Continuity is
reconstructed from committed, pushed files — not from the discarded conversation.

This is the promoted, every-repo version of the sandbox `session-sandbox` mechanism. The
sandbox is safe because only `sbx-*` names are targetable; here the guard is **self-rotation
only** — the sole session this skill can ever kill is the one it is running inside
(`target == tmux display-message -p '#S'`). A typo or bad config cannot reach another repo's
session.

## Activation (why it may refuse)

A repo rotates **only** if it contains a committed `.claude/rotate.conf` whose `SESSION`
equals the live session name. Absent that file, the skill hard-refuses. This is the gate:
the skill is installed in every repo but active only where a config has been added. Until the
mechanism is verified in the sandbox, **only the sandbox repo carries a `rotate.conf`.**

`.claude/rotate.conf` fields:

```sh
SESSION=ebiz               # REQUIRED: the tmux session name this repo runs under
MODEL=opus                 # optional: --model for the successor
EFFORT=high                # optional: --effort for the successor
RC_NAME=Factory-$(hostname) # optional: --remote-control name (default: SESSION)
PERMISSION_MODE=acceptEdits # optional: --permission-mode for the successor
DELAY=60                   # optional: seconds until the successor launches (default 60)
```

## Steps (run in this order)

Run from **inside** the session you want to refresh.

1. **Preflight — refuse early if not permitted.** Run
   `assets/rotate.sh --preflight`. It verifies: inside tmux; `.claude/rotate.conf` present;
   its `SESSION` equals the current session (the self-target guard); `systemd-run` available.
   On `PREFLIGHT FAIL`, print the reason and STOP — change nothing.
2. **Handoff note (inlined).** Write the deliberate `## Next Session` note (from the focus
   argument) into the repo's committed handoff file (CONTEXT.md / HANDOFF.md / TODO.md) and
   commit + push just that file. This is the `/handoff` action performed **inline**: `handoff`
   is a user-invoked skill and, per this repo's `docs/invocation.md`, a user-invoked skill
   (this one) can never invoke another user-invoked skill — so do the note yourself rather
   than calling `/handoff`.
3. **`/wrap`** — invoke the `/wrap` skill (it is model-invoked, so this user-invoked skill may
   call it). It summarises, updates project logs, and commits **and pushes** everything.
   Capture the resulting commit SHA (the successor verifies it). If `/wrap` does not push
   cleanly, **ABORT**: do not schedule a successor, do not kill. The session stays alive with
   work intact. `/wrap`'s successful push is the hard gate on the irreversible kill.
4. **Rotate** — run `assets/rotate.sh <pushed_sha>`. It schedules the same-name successor
   (detached via `systemd-run --user`, so it survives this session dying) **then** does the
   guarded self-kill. Scheduling happens before the kill, so a scheduling failure leaves the
   predecessor alive — never a coverage gap.
5. **Report** — the session drops now and reappears fresh under the same name in ~`DELAY`s;
   the successor reads the committed handoff and confirms the predecessor SHA before acting.

## Assets

- `assets/rotate-env.sh` — the self-target guard (`rotate_assert_self`, `rotate_kill`). Source first.
- `assets/rotate.sh` — `--preflight` checks; else schedule-before-kill (the mechanical half).
- `assets/rotate-launch.sh` — launch a same-name successor on a real TTY (`tmux pipe-pane` logging).
- `assets/rotate-status.sh` — read-only: is a session on a TTY and relay-connected?
- `assets/selftest-guard.sh` — proves the guard accepts only the current session; run it anywhere.

## Notes

- Adding this skill is a global `~/.claude` change → file the FYI issue your project requires.
- v1 is manual only. Auto-firing at a context ceiling (~30%) is a separate, later change.
- The sandbox `sbx-*` scripts are NOT modified — they remain the isolated dev harness.
