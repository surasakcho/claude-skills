---
name: run-clips
description: Generate the video clips for a content item by running the project's configured clip-generation command, after animation prompts are drafted. Thin runner for the generate stage of a content-pipeline shorts project. Use when advancing an item whose clips need generating.
---

Thin runner for the **generate** stage: turn locked keyframes into video clips by
running the project's own generation script. It owns *running and recovering*, not
the craft — prompts come from `draft-asset-prompts`, the command from `project.md`.

This stage is usually the **video dollar spend**. It runs only after the upstream
review gate is approved (the orchestrator enforces this) — never generate clips
before that gate clears.

## Steps
1. **Ensure animation prompts exist.** If `flow_prompts.txt` (or the project's
   T2V-prompt file) isn't drafted for the locked keyframes, run `draft-asset-prompts`
   to write it first. Animate the locked composition; don't redesign it.
2. **Gate on animatability before spending.** Confirm every shot passed
   `draft-asset-prompts`' animatability screen. A keyframe with many independently-
   moving components (armies, crowds, players on a field) must be **recomposed**
   before it reaches clip generation — not micromanaged in the prompt. Do not spend
   clip budget on a shot flagged for recomposition; send it back first.
3. **Run the configured command.** Take `commands.generate` from `project.md`,
   substitute `{item}` with the item's directory, and run it. This is the
   authoritative command — don't guess a different one from prose. If
   `commands.generate` is missing, stop and ask for the command.
4. **On failure, re-run only the owning unit** (the failed shot/subcommand), not the
   whole batch — clips cost money. Use any free retry path the charter documents
   before re-spending.
5. **Report** what was produced (clip files in playback order) and the spend if the
   command reports it. Leave `pipeline.md` updates to the orchestrator.

Respect all pipeline conventions in `context.md` (output filenames, playback-order
numbering, 9:16/resolution). `context.md` overrides on conflict.
