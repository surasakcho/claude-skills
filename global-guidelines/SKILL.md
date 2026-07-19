---
name: global-guidelines
description: Canonical baseline working rules (subagent delegation policy, session discipline, text-encoding correctness) that should apply to every Claude Code project. Applies these behaviorally on any multi-step engineering task — deciding what to delegate to a subagent, planning before coding, checkpointing commits, keeping changes surgical, and passing explicit encodings so Windows locale codecs (cp1252/cp874) don't silently corrupt files read on Linux/CI/Pi. Also covers syncing this text into a CLAUDE.md file (global ~/.claude/CLAUDE.md or a project's own) — see sync-claude-md.md — when starting substantive work in a project whose CLAUDE.md doesn't yet reflect these rules, when a project has no CLAUDE.md at all, or when the user asks to add/check/sync/merge these guidelines.
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

## Text encoding — never rely on the platform default

Windows Python decodes and encodes text using the **locale codec** (cp1252, or cp874 on a
Thai-locale machine); Linux and macOS use UTF-8. Code written on one and run on the other
breaks. Make encoding explicit *as the code is written*, not after a crash:

- `open(...)` → pass `encoding="utf-8"` unless the mode is binary
- `subprocess.run(..., text=True)` → pass `encoding="utf-8"` (usually with
  `errors="replace"`); same for `Popen` and `check_output`
- PowerShell `Set-Content` / `Add-Content` → pass `-Encoding utf8`
- CLI entry points → enable UTF-8 mode (PEP 540) via `-X utf8` / `PYTHONUTF8=1`, so the
  defaults are correct even where an explicit encoding was missed

**The crash is the harmless version.** Failing to print an em dash is loud and gets fixed
immediately. The dangerous version is JSON or Markdown written with the locale codec on
Windows and read back as UTF-8 elsewhere — another machine, CI, a Raspberry Pi. That does
not raise; it corrupts. And once text is mixed encoding, a blanket re-decode makes it worse:
it has to be repaired symbol by symbol.

**Do not audit this with grep.** A line-oriented search misses the keyword when a call spans
lines, and flags `Image.open(p)` and `p.open("rb")` as false positives. Acting on that output
breaks working code. Parse the AST, or read the whole call before editing it.
[check-encoding.py](./check-encoding.py) does this — run it in any project (`python
check-encoding.py [path]`, exit 1 on findings).

## Syncing into a CLAUDE.md

To check whether a global (`~/.claude/CLAUDE.md`) or project-level `CLAUDE.md` should have
this text added or merged — including creating one from scratch for a brand-new project — see
[sync-claude-md.md](./sync-claude-md.md).
