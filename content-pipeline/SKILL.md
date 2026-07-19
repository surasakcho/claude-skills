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
- `issue` — a human gate ends this stage. Open the gate and stop (see **Gates**
  below). Never do gated (paid) downstream work before a gate clears.

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
   - `issue` → **open/update the gate** (see **Gates**) and stop. Do not
     auto-advance and do not start the next stage.
5. If the finished stage was the **last** in the graph, mark the item complete per
   project convention (e.g. `stockpiled`) and update any stockpile count in
   `pipeline.md`.

## Gates

A gate is a human checkpoint that ends a stage. The orchestrator opens it, records
it in `pipeline.md`, and **stops** — it resolves the gate only when the user asks
to check or resume.

**One GitHub Issue per item is the review surface** (not PRs). It's created at the
item's first gate and carried through every gate, relabeled for the current gate
stage. The user **comments** to approve or reject. Open Issues are the live
production board; a closed Issue means the item shipped.

### Opening (or updating) a gate
1. Confirm the stage's review artifact exists. If not, the stage isn't really done
   — go back.
2. Ensure the item's review Issue exists: create it at the first gate
   (`gh issue create`, titled for the item); otherwise reuse the same Issue.
3. Relabel it for the current gate stage (e.g. `gate-<stage-id>`), removing the
   previous gate's label.
4. Put the stage's review content in the Issue — text inline; assets embedded or
   linked **per the project's hosting convention** (from `project.md` /
   `context.md`). Asset hosting is project plumbing, not this skill's concern: e.g.
   a private repo whose images won't render on mobile may mirror them to a public
   repo and embed raw URLs, or host a render as a Release-asset link. State in the
   body **how to respond: comment to approve (advance) or reject (name the stage to
   revise from).**
5. In `pipeline.md` set Gate = `<stage-id>`, Review link = Issue URL, Waiting-on =
   `user review Issue #N`. Stop.

### Resolving a gate (user says "check gate" / "resume")
Read the Issue: `gh issue view <n> --json state,comments`.

- **Approve comment → advance.** Move the item to the next stage; clear Waiting-on.
  If this was the **last** gate, **ship** per project convention (e.g. merge the
  item's branch → the default branch, delete any render Release, and **close the
  Issue**). Otherwise relabel the Issue for the next gate and continue the Advance
  loop.
- **Reject comment → revise.** Read which stage to revise from (default: the gate's
  own stage). Set the item's Stage back to that stage, record the reason in Notes,
  and re-run Advance from there — this regenerates downstream artifacts and re-posts
  them to the same Issue.
- **No decision yet.** Report still waiting; change nothing.

### Rules
- No gated/paid downstream work before the gate is approved.
- One review Issue per item; it lives from the first gate until ship.
- Approve/reject is signaled by **comments** — never by closing the Issue (closing
  = shipped).

## Owning pipeline.md

After every stage transition, rewrite the item's row so a fresh session can resume
from `pipeline.md` alone. Keep the table columns fixed. Never leave a row mid-stage
without a Waiting-on note.

## Rules

- Never skip a stage; never spend gated/paid work before its gate clears.
- Precedence on conflict: `context.md` > `project.md` > this skill.
- Multiple items run in flight at different stages; `pipeline.md` is the single
  source of truth a fresh session reads to resume.
