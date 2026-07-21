---
name: session-sandbox
description: Safely develop and test automation that starts/kills Claude or tmux sessions, installs cron/systemd timers, or touches live sessions — inside an isolated, guard-enforced sandbox where only sbx-* names can be targeted, so real sessions are structurally unreachable (a sandbox session may still refresh itself). Use before building any session-continuity / rotation / auto-launch / auto-resume mechanism, or any script that could kill a session, install a cron job, or change global config. Prevents the "it ran on my live session and broke it" failure.
---

# session-sandbox — develop live-session automation without blast radius

Any automation that **starts, kills, or rotates Claude/tmux sessions**, **installs cron/systemd
timers**, or **edits global config** can damage a *real* running session (e.g. the operator's live
session) if a name, env var, or pattern resolves wrong. This skill develops such automation in an
**isolated sandbox** where a single guard makes non-sandbox targets impossible to hit — then promotes
it only once proven.

## The one rule that makes it safe
Everything the sandbox can act on lives in a reserved namespace: names MUST match `^sbx-[a-z0-9]+$`.
A single guard (`sbx_assert_target`) refuses any name that isn't `sbx-*`. **There is no kill-by-pattern
and no kill-all code path** — the only kill is `sbx_kill <sbx-name>`, and it calls the guard first. A
typo or bad env var can therefore never resolve to a real session name (real sessions can't match the
prefix). A `sbx-*` session **may target itself** — self-rotation (refresh) is the whole point, and the
prefix, not a "== current" rule, is what keeps real sessions safe.

## Workflow (do in order — prove the guard BEFORE any live action)
1. **Record the current live session** (`tmux display-message -p '#S'`) and state plainly: this is
   never a target. It is protected by the guard, not by care.
2. **Scaffold** from `assets/` into a sandbox repo (default `~/repos/sandbox`): copy `sbx-env.sh`
   (the guard + constants), `sbx-launch.sh` (TTY-clean launcher), `sbx-status.sh` (read-only checks).
   Adjust `SBX_REPO`/`SBX_MODEL` if needed. Keep the `sbx-` prefix, the `${HOME}/.cache/…` sandbox lock,
   and the `# SANDBOX-CONTINUITY` cron tag.
3. **PROVE the guard first.** Run `sbx_assert_target` against the real session names on the box AND a
   couple of `sbx-*` names. Real names (and `""`, uppercase, injection strings) MUST all REFUSE; only
   `sbx-*` ACCEPT. Do not launch anything until this passes.
4. **Develop & test in isolation.** Launch `sbx-1`, `sbx-2`, … Verify each with `sbx-status.sh`:
   claude on a real TTY (`/dev/pts/*`) and relay-connected (established conn to Anthropic
   `160.79.104.0/22`). After every run, confirm the real session is untouched (pid + `has-session`).
5. **Cron/timer tests** go through the tagged helpers only — every sandbox cron line carries
   `# SANDBOX-CONTINUITY`, so it can be added/removed surgically without touching other crontab entries
   (`crontab -l | grep -v 'SANDBOX-CONTINUITY' | crontab -` to clear only sandbox lines).
6. **Promote only when certain.** Once the mechanism is proven in the sandbox, adapt it for the real
   target — parameterize the project dir, keep the guard, and (if it becomes a global `~/.claude` skill
   or edits global config) file the FYI issue your project requires.

## Hard-won gotchas (bake these into whatever you build)
- **Never `| tee` a session's launch command.** Piping claude's stdout moves it off the TTY
  (`stdout.isTTY == false`) → the interactive TUI and **remote control never initialise**. Log with
  `tmux pipe-pane -o -t <name> "cat >> log"` instead — it captures pane output without touching the TTY.
- **Never `rm -f` a live flock file.** It unlinks the entry but the held lock stays on the old inode; a
  new open+flock succeeds on a different inode and defeats the mutex. Release by killing the holder.
- **Self-destruct needs an actual exit.** An interactive session that hits the credit limit idles alive
  (does not exit → does not self-clean). One-shot (`-p`) ticks exit and self-clean; long interactive
  sessions are managed singletons — guard duplicates with `has-session`.
- **`claude -p` cannot be remote-controlled** (headless ⊥ interactive). If it must be steerable, it must
  be interactive `--remote-control`.
- **Duplicate RC names collide on claude.ai.** A dead session that registered a name can shadow a live
  one of the same name. Ensure the predecessor is fully dead before a successor claims the name.

## Refresh (session rotation) — the proven mechanism
`assets/sbx-rotate.sh <sbx-name> [delay_s]` refreshes a session in place: writes a breadcrumb,
schedules a **same-name** successor (detached via `systemd-run --user`, so it survives the caller
dying — needs `loginctl enable-linger`), then guarded self-kill. From claude.ai the named session
drops, then reappears fresh after `delay_s` with the breadcrumb available. **Schedule the successor
BEFORE the kill** — that ordering, not a timer, is what guarantees no gap in coverage. Works as
self-rotation (run from inside the session) *or* driven from another session.

## Assets
- `assets/sbx-env.sh` — constants + the isolation guard (`sbx_assert_target`, `sbx_kill`). Source first.
- `assets/sbx-launch.sh` — launch one `sbx-*` remote-control session on a real TTY (pipe-pane logging).
- `assets/sbx-rotate.sh` — refresh/rotate a `sbx-*` session (breadcrumb + same-name successor + self-kill).
- `assets/sbx-status.sh` — read-only: per `sbx-*` session, on-TTY? relay-connected?
