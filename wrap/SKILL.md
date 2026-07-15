---
name: wrap
description: End-of-session ritual — summarize the session, update project logs, commit and push, then write next-session handoff notes into a committed project file. Use when the user says "wrap", "wrap up", "hand off", or otherwise signals they're closing out for now.
---

Close out the current session. Steps run in order; never save session notes to OS temp or claude memory — everything must end up committed and pushed.

## 1. Check for a project-defined wrap convention first

Check this project's `CLAUDE.md` for a custom `wrap` ritual. If one is defined, follow it exactly instead of the steps below.

## 2. Check for anything to wrap

Run `git status` and `git diff`. If there are no staged/unstaged changes and nothing meaningful happened this session, say so and stop — don't manufacture a commit.

## 3. Summarize the session

Write a short summary (a few sentences) of what was done this session: what changed and why. Scoped to this conversation's work, not a general changelog.

## 4. Update project-specific logs, only if they already exist

Look for established conventions — a changelog, worklog, ADR directory, TODO/DONE tracker, `.changeset/` in JS repos. If one exists, update it consistent with its existing format.

If new conventions were established this session that `CLAUDE.md` doesn't capture yet, update `CLAUDE.md` too.

Do not invent a new log file just because none exists — that's the project owner's call.

## 5. Commit and push work

Stage the relevant files (never a blanket `git add -A`) and commit, following this repo's existing commit message style. Push to the current branch's upstream.

## 6. Write handoff notes (always)

Ask the user: "Anything specific to note for next session?" If they give input, use it. If they say no or don't respond, write a brief note based on what you know needs doing next.

Then follow the `handoff` skill exactly:
- Find or create the handoff target file (`CONTEXT.md` → `HANDOFF.md` → `TODO.md`, in that order; create `HANDOFF.md` if none exist)
- Add or update a `## Next Session` section with: what was done, what to do next, known bugs/blockers, suggested skills
- Commit only the handoff file with message `docs: handoff notes for next session`
- Push

Never write handoff notes to OS temp or claude memory — they must be in a committed, pushed file so they're available on any machine.

## 7. Report back

One short summary: what was committed, whether any project logs were updated, and confirmation it pushed — with the remote/branch.
