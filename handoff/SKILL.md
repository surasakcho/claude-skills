---
name: handoff
description: Summarise the session and write next-session notes into a committed project file, then commit and push so the handoff is available on any machine.
argument-hint: "What should the next session focus on?"
disable-model-invocation: true
---

Close out the current session by writing a handoff note into a tracked project file and pushing it. The note must travel with the repo — never save it to OS temp or claude memory.

## 1. Find or create the handoff target file

Look for an existing file to append to, in this order:
- `CONTEXT.md` (preferred if it exists)
- `HANDOFF.md`
- `TODO.md`

If none exist, create `HANDOFF.md` in the project root.

## 2. Write the handoff note

Add or update a `## Next Session` section at the top of the file (after any title/header). Keep it concise — bullets, not prose. Include:

- **What was done this session** — one sentence max, just enough context.
- **What to do next** — specific actionable items, ordered by priority.
- **Known bugs or blockers** — anything that will bite the next session immediately.
- **Suggested skills** — if a specific Claude Code skill would help (e.g. `/run`, `/tdd`), name it.

Do not duplicate content already captured in commits, PRDs, or ADRs — reference them by path or URL instead.

Redact any sensitive information (API keys, passwords, PII).

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the note accordingly.

## 3. Commit and push

Stage only the handoff file. Commit with a short message like `docs: handoff notes for next session`. Push to the current branch's upstream.

## 4. Report back

Confirm: what file was written, what was committed, and that it pushed — so the user knows the notes are safe on the remote.
