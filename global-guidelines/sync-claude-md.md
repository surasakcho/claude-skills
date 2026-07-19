# Sync into CLAUDE.md

Companion behavior for `global-guidelines`: keep this guideline text present in a `CLAUDE.md`
file — the global one (`~/.claude/CLAUDE.md`) or a project's own — not just applied in-session.

## The global CLAUDE.md is deliberately not version-controlled

`~/.claude/CLAUDE.md` lives outside any repo on purpose — don't propose putting it in one.
This skill IS the canonical copy and the backup; re-running the sync on a new machine
recreates it. More importantly, machines are *expected* to diverge: one may be unable to run
what another can (blocked APIs, no GPU, different OS), so its global rules should differ.
A shared repo would force uniformity that is wrong here.

That is also why the alignment check below is semantic rather than a byte-diff, and why
step 5 stops to ask instead of overwriting: a difference is as likely to be a deliberate
local decision as it is to be drift.

## When to run this

- The user asks to add/sync/check/merge the global guidelines into a `CLAUDE.md`.
- You're starting substantive work in a project (reading its `CLAUDE.md` to orient) and notice
  the file exists but doesn't reflect these rules, or the file doesn't exist at all —
  including a brand-new project with no `CLAUDE.md` yet.
- Don't run it just because you invoked `global-guidelines` behaviorally in the current turn —
  only when a `CLAUDE.md` (global or project) is actually in view or being created.

## Process

1. **Identify the target**: the global `~/.claude/CLAUDE.md`, or the project root `CLAUDE.md`
   you'd normally read for project context. Don't confuse the two — they're synced
   independently.

2. **No file yet** (new project, or global file missing): create it with a `## Global Working
   Rules` section reproducing the full text from `global-guidelines/SKILL.md` (both sections:
   Model effort / delegation policy, Session discipline), verbatim. Tell the user what you
   created and where. Done — skip the steps below.

3. **File exists — check alignment**: read the existing content and compare it against the
   canonical text in `global-guidelines/SKILL.md`. This is a semantic check, not a byte-diff —
   wording may differ slightly. Judge alignment on substance:
   - Same delegate / don't-delegate boundaries?
   - Same subagent rules (never weaken assertions, failures escalate, diffs reviewed)?
   - Same three session-discipline rules (plan-first, checkpoint commits, surgical changes)?

4. **Aligned**: do nothing. Optionally note in one line that it already matches — don't
   restate the content back at the user.

5. **Not aligned (missing, partial, or conflicting)**: stop and ask before touching the file.
   Tell the user, concretely:
   - What's missing or different (e.g. "your CLAUDE.md has session discipline rules but
     nothing on subagent delegation" or "your delegation list conflicts with the canonical one
     on X").
   - Exactly how you'd merge it (new section appended vs. interleaved with existing content,
     which existing lines would be kept/replaced/reworded).
   Only proceed once the user confirms. Never silently overwrite project-specific rules that
   don't literally match the canonical text — a project may have deliberately customized them.

6. **Touch nothing else in the file** — insertion/merge only, surgical. Report what changed
   and where in one line.
