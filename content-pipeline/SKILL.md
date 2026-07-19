---
name: content-pipeline
description: Orchestrate a content project's production pipeline — read state, report each item's stage, add new items, and advance an item through its stage graph by dispatching to per-stage skills. Use when running or resuming a content project scaffolded with content-pipeline-init (has project.md + pipeline.md), checking pipeline status, or advancing a content item to its next stage.
---

The conductor for a content project. It does **not** do stage work itself — it
reads the project's stage graph, dispatches each stage to the skill that owns it,
and keeps `pipeline.md` (the dashboard) truthful. Genre- and format-agnostic:
everything project-specific comes from `project.md` and `context.md`, never from
this skill.

## Preconditions

`project.md` and `pipeline.md` must exist in the project. If either is missing,
stop and point the user at `content-pipeline-init` — the project isn't scaffolded
yet.

Before acting, read in this order (later files lose on conflict):
1. `context.md` — decision log + glossary; **overrides everything**.
2. `project.md` — config + the `stages:` graph.
3. `pipeline.md` — current state of every item.

## The stage graph

`project.md` `stages:` is an ordered list of `{ id, skill, gate, exec, model }`.
Advancement follows this order **exactly — never skip a stage**.

Gate values:
- `none` — advance automatically once the stage's skill completes.
- `pr` / `release` — a human gate ends this stage. **Until the gate protocol is
  wired (Phase 3), HALT at the gate:** set the row's Gate + Waiting-on, and tell
  the user a human gate is due here. Never do gated (paid) downstream work before
  a gate clears.

Execution (`exec`, optional — defaults to `inline`):
- `inline` — run the stage in this session on the current model. Required for
  **interactive** stages that interview the user live (a subagent can't hold a
  live back-and-forth).
- `subagent` — spawn a subagent (Agent tool) to run the stage on the `model:`
  named for that stage (`haiku`/`sonnet`/`opus`/`fable`), saving credits on
  mechanical, non-interactive work. The subagent returns its result; you then
  update `pipeline.md`. Never dispatch an interactive stage as a subagent.

## Modes — infer which from the user's request

### Status ("where are we", "what's next")
Report every row in `pipeline.md`: item, current stage, gate, waiting-on, and the
concrete next action. Flag anything blocked at a gate. For "what's next," pick the
most-advanced unblocked item and name its next action.

### New item
1. Derive a slug for the item (ask if not obvious), following any naming
   convention in `context.md` / `project.md`. If the convention is undefined, ask.
2. Create the item's branch and working directory per that convention.
3. Append a row to `pipeline.md` with Stage = the **first** stage id in the graph;
   Gate and Waiting-on blank.
4. Report the item is ready to advance.

### Advance `<item>`
1. Find the item's row; read its current Stage.
2. Look up that stage in `project.md` `stages:` → get its `skill`, `exec`, `model`.
3. **Dispatch** the stage's work (let the stage skill own the craft; if the named
   skill doesn't exist, stop and say so — it may be unbuilt):
   - `exec: inline` (or omitted) → invoke the skill in this session, handing it the
     item's directory and upstream files.
   - `exec: subagent` → spawn a subagent on `model:` and tell it to run the stage
     skill against the item's directory. Wait for its result before continuing.
     Do this only for non-interactive stages.
4. When the stage skill reports done, look at **that stage's** gate:
   - `none` → update the row: Stage = the **next** stage id, clear Waiting-on.
     Continue automatically into the next stage unless the user asked for a single
     step.
   - `pr` / `release` → HALT (see gate rule above).
5. If the finished stage was the **last** in the graph, mark the item complete per
   project convention (e.g. `stockpiled`) and update any stockpile count in
   `pipeline.md`.

## Owning pipeline.md

After every stage transition, rewrite the item's row so a fresh session can resume
from `pipeline.md` alone. Keep the table columns fixed. Never leave a row mid-stage
without a Waiting-on note.

## Rules

- Never skip a stage; never spend gated/paid work before its gate clears.
- Precedence on conflict: `context.md` > `project.md` > this skill.
- Multiple items run in flight at different stages; `pipeline.md` is the single
  source of truth a fresh session reads to resume.
