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
# skill that does the work and the gate that ends it.
#   gate: none    → advance automatically
#   gate: pr      → human gate via GitHub PR (text/storyboard review)
#   gate: release → human gate via GitHub Release asset (render review)
# `skill:` must name an installed skill in claude-skills.
stages:
  - { id: ideate,     skill: concept-interview,      gate: none }
  - { id: script,     skill: showrunner-short,       gate: none }
  - { id: storyboard, skill: draft-asset-prompts,    gate: pr }
  - { id: generate,   skill: run-clips,              gate: none }
  - { id: build,      skill: run-build,              gate: release }
  - { id: publish,    skill: publish-metadata,       gate: none }
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
