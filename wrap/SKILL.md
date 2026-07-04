---
name: wrap
description: End-of-session ritual — summarize the session, update whatever project-specific logs/trackers already exist, then commit and push. Defers to a project's own `wrap` convention if its CLAUDE.md defines one. Use when the user says "wrap", "wrap up", "wrap this session", or otherwise signals they're closing out for now.
---

Close out the current session: summarize the work, update whatever project-specific record-keeping already exists, then commit and push.

## 1. Check for a project-defined wrap convention first

Some projects already define their own `wrap` ritual in their `CLAUDE.md` (e.g. a numbered list of session-end steps, a specific commit message format, a dashboard/build step to re-run). Check this project's `CLAUDE.md` for one.

If it defines one: follow it exactly, in order, instead of the steps below.

If it doesn't: fall back to the generic ritual in steps 2-6.

## 2. Check for anything to wrap

Run `git status` and `git diff`. If there are no staged/unstaged changes and nothing meaningful happened this session, say so and stop — don't manufacture a commit.

## 3. Summarize the session

Write a short summary (a few sentences, not a document) of what was actually done this session: what changed and why. This is scoped to this conversation's work, not a general changelog of the repo.

## 4. Update project-specific logs, only if they already exist

Look for established conventions in *this* project before touching anything — a changelog, worklog, decision log, ADR directory, TODO/DONE tracker, research-log index, or a changeset tool (e.g. `.changeset/` in JS repos). If one exists, update it consistent with its existing format and level of detail (mark completed items, add an entry for this session, etc).

If new conventions were established this session (a pattern the user asked you to follow going forward), and this project's `CLAUDE.md` doesn't capture them yet, update `CLAUDE.md` too.

Do not invent a new log file or document just because none exists — that's the project owner's call, not something to introduce as a side effect of wrapping up.

## 5. Commit and push

Stage the relevant files (never a blanket `git add -A`) and commit, following this repo's existing commit message style (check `git log` for tone/format, unless the project's own wrap convention specifies one). The commit message should capture the *why*, per this session's summary.

Push the current branch. If it has no upstream yet, set one (`git push -u origin <branch>`). Do not force-push, skip hooks, or bypass signing.

## 6. Report back

One short summary: what was committed, whether any project logs were updated (and which), and confirmation it pushed — with the remote/branch.
