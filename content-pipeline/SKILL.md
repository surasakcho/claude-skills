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
- `pr` / `release` — a human gate ends this stage. Open the gate and stop (see
  **Gates** below). Never do gated (paid) downstream work before a gate clears.

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
   - `pr` / `release` → **open the gate** (see **Gates**) and stop. Do not
     auto-advance and do not start the next stage.
5. If the finished stage was the **last** in the graph, mark the item complete per
   project convention (e.g. `stockpiled`) and update any stockpile count in
   `pipeline.md`.

## Gates

A gate is a human checkpoint that ends a stage. The orchestrator opens it, records
it in `pipeline.md`, and **stops** — it resolves the gate only when the user asks
to check or resume. Two gate shapes (set per stage by `gate:`):

- `pr` — text/storyboard review on a GitHub **PR**.
- `release` — render review via a GitHub **Release** asset (mobile-friendly,
  full-res) linked from a PR.

Gate branches/tags are named per item **and** stage so multiple gates never
collide: branch `<item>_gate_<stage-id>`, release tag `<item>-<stage-id>`.

### Opening a `pr` gate
1. Confirm the stage's review artifact exists (e.g. `storyboard.md` plus every
   asset it references). If not, the stage isn't really done — go back.
2. Create branch `<item>_gate_<stage-id>` off the item's branch; commit the review
   artifact(s); push.
3. `gh pr create --base <project's default branch> --head <gate branch>`, titled
   with the item + stage, body stating **how to respond: merge = approve; a
   comment naming a stage = reject and revise from that stage** (default: this
   stage).
4. In `pipeline.md` set Gate = `<stage-id>`, Review link = PR URL, Waiting-on =
   `user review PR #N`. Stop.

### Opening a `release` gate
1. Confirm the render/output artifact exists.
2. Publish it as a prerelease asset:
   `gh release create <item>-<stage-id> <artifact> --prerelease --title "..."`.
3. Open a PR carrying the QA artifact (e.g. `qa_checklist.md`) that links the
   release asset; same approve/reject convention in the body.
4. Record Gate / Review link / Waiting-on as above. Stop.

### Resolving a gate (user says "check gate" / "resume")
Read PR state: `gh pr view <n> --json state,mergedAt,comments,reviews`.

- **Merged → approved.** Advance the item to the next stage; clear Gate +
  Waiting-on. For a `release` gate, delete the release (`gh release delete
  <item>-<stage-id>`) and the gate branch. Then continue the Advance loop.
- **Open with a rejecting comment/review → rejected.** Read the comment for which
  stage to revise from (default: the gate's own stage). Set the item's Stage back
  to that stage, clear the gate, record the reason in Notes, and re-run Advance
  from there — this regenerates downstream artifacts and re-opens the gate.
- **Open, no decision yet.** Report still waiting; change nothing.

### Rules
- No gated/paid downstream work before the gate is approved.
- One open gate per item at a time.

## Owning pipeline.md

After every stage transition, rewrite the item's row so a fresh session can resume
from `pipeline.md` alone. Keep the table columns fixed. Never leave a row mid-stage
without a Waiting-on note.

## Rules

- Never skip a stage; never spend gated/paid work before its gate clears.
- Precedence on conflict: `context.md` > `project.md` > this skill.
- Multiple items run in flight at different stages; `pipeline.md` is the single
  source of truth a fresh session reads to resume.
