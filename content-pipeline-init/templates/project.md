---
# ── Project identity ────────────────────────────────────────────────
project: PROJECT_SLUG          # short machine name, e.g. my-channel
niche: "ONE_LINE_NICHE"        # what this project makes
format: short                  # short | long → selects the creative skill family
voice: "ONE_LINE_VOICE"        # narration/style, e.g. "two-host dialogue"
personas:                      # recurring hosts/characters (optional; delete if none)
  - "NAME — one-line description"

# ── Budget rails ────────────────────────────────────────────────────
budget:
  per_item: 5                  # USD ceiling per content item
  total: 200                   # USD ceiling for the whole project

# ── Stage graph ─────────────────────────────────────────────────────
# The /content-pipeline orchestrator runs these in order. Each stage names the
# skill that does the work, the gate that ends it, and how it runs.
#   gate: none  → advance automatically
#   gate: issue → human gate: pause for review on the project's SINGLE GitHub
#                 Issue (one per item, labeled by this stage). Advance on an
#                 approve comment, revise on a reject comment. Gate spend early —
#                 put a gate before each costly stage.
#   exec: inline  → run in-session on the session model (DEFAULT if omitted;
#                   required for interactive stages that interview the user live)
#   exec: subagent + model: → run as a subagent on the named model
#                   (haiku|sonnet|opus|fable) to save credits on mechanical work
# `skill:` must name an installed skill in claude-skills.
stages:
  - { id: ideate,     skill: concept-interview,   gate: none,  exec: inline }
  - { id: script,     skill: showrunner-short,    gate: issue, exec: inline }                  # gate: text (before asset work)
  - { id: storyboard, skill: draft-asset-prompts, gate: issue, exec: inline }                  # gate: assets (before video spend)
  - { id: generate,   skill: run-clips,           gate: none,  exec: subagent, model: haiku }
  - { id: build,      skill: run-build,           gate: issue, exec: subagent, model: haiku }  # gate: render
  - { id: publish,    skill: publish-metadata,    gate: none,  exec: inline }
---

# PROJECT_NAME — charter

Free-form direction the creative skills read: tone, hard constraints
(IP rules, content policy), format specifics, and anything a stage skill must
honor. The frontmatter above is the machine-readable part the orchestrator
reads; this prose is for the creative stages.

## Constraints

- (e.g. never use real game/IP assets; use original stand-in units)

## Format notes

- (e.g. shorts are 30s, structured Hook 0–5s / Twist 5–20s / Trap 20–30s)
