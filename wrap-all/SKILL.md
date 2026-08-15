---
name: wrap-all
description: End-of-session ritual across EVERY repo on this machine — for each git repo under the scan root with uncommitted or unpushed work, run the full wrap ritual (summarize, commit, push, handoff). Use when the user says "wrap all", "wrap everything", "/wrap-all", or wants to close out every repo at once. NOTE — a skill runs only in the current session; it cannot drive other live Claude Code sessions, it wraps repos on disk.
---

Wrap every repo on this machine that has outstanding work. A skill runs inside the current
session only — it cannot reach into other running Claude Code sessions. What it does instead
is walk the repos on disk and wrap each one. Never save notes to OS temp or claude memory —
everything ends up committed and pushed.

## Scan root

If the user named a root, use that. Otherwise read `SCAN_ROOT` from this skills repo's `.env`,
prompting for it on first use and storing the answer — a scan root is machine-specific, so it
is never hardcoded here:

```bash
SCAN_ROOT="$(python lib/skillconfig.py get SCAN_ROOT --repo <skills-repo> --prompt 'Repo scan root')"
```

Each immediate subfolder of that root containing a `.git` is a repo.

## 1. Enumerate repos with outstanding work

List every git repo directly under the scan root. For each, check:
- uncommitted changes (`git status --porcelain` non-empty), and/or
- unpushed commits (`git log @{u}.. ` non-empty, when an upstream exists).

Build the working set = repos that have either. Skip clean+pushed repos silently.

**Report the working set to the user before acting** — a short list of repos and why each is
included (dirty / unpushed / both). This is the plan.

## 2. Set aside repos that need a human

Do NOT auto-wrap a repo that is mid-operation or can't safely push. Instead list it separately
for the user to handle manually:
- an in-progress merge/rebase/cherry-pick (`.git/MERGE_HEAD`, `rebase-*` dirs),
- detached HEAD,
- no upstream / no remote configured,
- the current branch is the default branch AND the repo's own `CLAUDE.md` says branch-first
  (respect each repo's rules).

## 3. Wrap each remaining repo, one at a time

For each repo in the working set, run its wrap ritual **from that repo's directory**:

1. **Honor the repo's own convention first.** If that repo's `CLAUDE.md` defines a custom
   `wrap` ritual, follow it exactly for that repo instead of the steps below.
2. **Summarize.** For the repo you actually worked in this session, summarize from the
   conversation. For the others, recover context from that repo's saved session transcripts
   before falling back to the diff:
   - Transcripts live at `~/.claude/projects/<enc>/<session-uuid>.jsonl`, where `<enc>` is the
     repo's absolute path with **every non-alphanumeric char replaced by `-`**
     (e.g. `D:\Work\my-project` → `D--Work-my-project`). If several
     project folders could match, pick the one with the most recent `.jsonl`.
   - Read the **newest** `.jsonl` (these can be multi-MB — tail it / extract the last user+
     assistant turns rather than loading the whole file) to see what that session was doing.
   - These are *persisted* transcripts, not the live memory of a still-running session, so the
     final turns of an active session may not be flushed yet. Note that if it matters.
   - If no transcript is found or it's unreadable, summarize honestly from `git diff` / `git log`
     and say the wrap was a bulk close-out (don't invent intent).
3. **Update existing logs only** (changelog / worklog / TODO-DONE / ADR / `.changeset/`),
   consistent with that repo's format. Do not create a new log file.
4. **Commit.** Stage intentionally by inspecting `git status` — never a blanket `git add -A`.
   Match the repo's existing commit-message style. If changes look half-finished or
   experimental, still commit (that's the point of a wrap) but say so in the message body.
   Follow this repo's commit trailer/signing rules if it has them.
5. **Push** to the current branch's upstream. Never force-push, never `--no-verify` unless the
   repo's rules explicitly allow it.
6. **Handoff, as a separate commit.** Find/create the handoff file
   (`CONTEXT.md` → `HANDOFF.md` → `TODO.md`, in that order; create `HANDOFF.md` if none exist).
   Update a `## Next Session` section (what changed, what's next, blockers, suggested skills).
   Commit only that file with message `docs: handoff notes for next session`, then push
   immediately.

Keep going even if one repo fails — record the failure and move on.

## 4. Report back

One compact table: repo → what was committed → pushed? (remote/branch) → handoff pushed?
Plus the set-aside repos from step 2 with the reason each needs manual attention. If nothing
had outstanding work, say so plainly.
