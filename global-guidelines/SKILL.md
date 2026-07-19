---
name: global-guidelines
description: Canonical baseline working rules (subagent delegation policy, session discipline) that should apply to every Claude Code project. Applies these behaviorally on any multi-step engineering task — deciding what to delegate to a subagent, planning before coding, checkpointing commits, keeping changes surgical. Also covers syncing this text into a CLAUDE.md file (global ~/.claude/CLAUDE.md or a project's own) — see sync-claude-md.md — when starting substantive work in a project whose CLAUDE.md doesn't yet reflect these rules, when a project has no CLAUDE.md at all, or when the user asks to add/check/sync/merge these guidelines.
license: MIT
---

# Global Guidelines

Baseline working rules meant to hold across every project, including ones that don't exist
yet. This is the canonical copy — apply it behaviorally in any session, and use it as the
source of truth when syncing into a project's `CLAUDE.md` (see below).

## Model effort / delegation policy

Match effort to failure mode: expensive reasoning for silent failures, cheap execution for
loud ones.

Delegate to a subagent (Sonnet, medium effort) when the task is execution against a known
plan and mistakes surface immediately:
- Writing/running tests, checks, and harnesses
- Authoring content/spec/data files against a locked format
- UI wiring, demo pages, keybindings
- Doc updates, commit message drafting

Do NOT delegate:
- Novel algorithmic/math work (shaders, DSP, sim logic)
- Architectural decisions that span modules or repos
- Choosing WHAT invariants to test — the invariant is named at full effort, the harness is
  built cheap
- Any edit to an existing test's assertions or tolerances

Subagent rules: never weaken an assertion to make a test pass; failures come back up for
diagnosis; diffs get reviewed before commit.

## Session discipline

- State a plan before writing code; wait for approval on non-trivial work
- Checkpoint commit after each verified milestone
- Surgical changes in established codebases; don't restructure working systems without being
  asked

## Syncing into a CLAUDE.md

To check whether a global (`~/.claude/CLAUDE.md`) or project-level `CLAUDE.md` should have
this text added or merged — including creating one from scratch for a brand-new project — see
[sync-claude-md.md](./sync-claude-md.md).
