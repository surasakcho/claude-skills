---
name: content-pipeline-init
description: Scaffold the content-pipeline OS into a project — writes project.md (config + stage graph), an empty pipeline.md dashboard, and a context.md stub. Use when starting a new content project that will run on the /content-pipeline orchestrator, or when the user says scaffold/init/set up the pipeline for a project.
---

Scaffold the content-pipeline OS into the current project. This is the one-time
setup that lets the `/content-pipeline` orchestrator run the project afterward. Genre-
and format-agnostic: the project's specifics live in `project.md`, never in the
skills.

## Step 0 — don't clobber an existing pipeline

Check whether the project already has `pipeline.md` or `project.md`. If either
exists, STOP and ask — this project may already be scaffolded. Never overwrite a
populated dashboard.

## Step 1 — gather the minimum direction (one question at a time)

Ask only what the config needs, one question at a time, each with a recommended
answer. Don't over-interview — deep creative direction belongs to the stage
skills later, not here. Collect:

1. **project slug** — short machine name (e.g. `my-channel`).
2. **niche** — one line: what this project makes.
3. **format** — `short` or `long`. This selects the creative skill family the
   orchestrator dispatches to; if the needed family skills don't exist yet, note
   that and proceed (they can be built later).
4. **budget rails** — per-item and total USD ceilings (recommend $5 / $200).
5. **stage graph** — start from the template's default graph; adjust stage ids,
   the `skill:` for each, and `gate:` values (`none`/`pr`/`release`) to match
   this project. Confirm which stages need a human gate.

## Step 2 — write the three files

Copy the templates from this skill's `templates/` directory into the project
root, filling placeholders:

- `project.md` — replace `PROJECT_SLUG`, `PROJECT_NAME`, `ONE_LINE_NICHE`,
  `ONE_LINE_VOICE`, personas, budget, and the `stages:` graph with the confirmed
  values. Keep the frontmatter valid YAML (the `stages` entries are flow
  mappings: `{ id: ..., skill: ..., gate: ... }`). Fill `commands.*` with the real
  shell command for every `run-*` stage (`{item}` = the item's directory), or
  delete keys for stages the project doesn't have.
- `pipeline.md` — replace `PROJECT_SLUG`, set `STAGE_SEQUENCE` to a human-
  readable arrow chain of the stage ids with gates marked (e.g.
  `ideate → script(GATE) → storyboard(GATE) → generate → build(GATE) → publish`),
  and set `THRESHOLD` (stockpile launch target). Leave the table empty — the
  orchestrator adds rows as items enter the pipeline.
- `context.md` — copy as-is unless the user already has decisions to record.

## Step 3 — verify

- `project.md` frontmatter parses as YAML. Sanity-check by reading it back;
  every `stages` entry must have `id`, `skill`, and `gate`.
- `pipeline.md`'s stage sequence matches the ids in `project.md` `stages`.
- No placeholder tokens (ALL_CAPS_UNDERSCORE) remain in any of the three files.

Report the three files written and tell the user the next step: run `/content-pipeline`
to add the first content item and start advancing stages.
