# Sync into CLAUDE.md

Companion behavior for `karpathy-guidelines`: keep the guideline text present in
a project's own `CLAUDE.md`, not just applied in-session.

## When to run this

- The user asks to add/sync/check Karpathy guidelines in a project's `CLAUDE.md`.
- You're starting substantive work in a project (reading its `CLAUDE.md` to
  orient) and notice the file exists but doesn't contain these guidelines.
- Don't run it just because you invoked `karpathy-guidelines` behaviorally in
  the current turn — only when the project's own docs are in view.

## Process

1. Locate `CLAUDE.md` at the project root (the one you'd normally read for
   project context — not this skills repo's own `CLAUDE.md`).
2. Check whether it already contains the guidelines (look for a section
   matching this content, e.g. headed "Karpathy Guidelines" or covering the
   same four principles). If present, do nothing — don't duplicate.
3. If missing, insert a section reproducing the full text from
   `skills/karpathy-guidelines/SKILL.md` (the four sections: Think Before
   Coding, Simplicity First, Surgical Changes, Goal-Driven Execution),
   verbatim, under a heading like `## Karpathy Guidelines`. If the file doesn't
   exist yet, create it with just this section.
4. Touch nothing else in the file — insertion only, surgical.
5. Tell the user what you added and where, in one line. If nothing changed,
   say so briefly rather than staying silent.
