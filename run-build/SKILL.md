---
name: run-build
description: Build the final render for a content item — narration then stitch/captions/finalize — by running the project's configured build command(s). Thin runner for the build stage of a content-pipeline shorts project. Use when advancing an item whose clips are done and need assembling into the final video.
---

Thin runner for the **build** stage: assemble locked clips into the final render by
running the project's own build script(s). It owns *running and recovering*, not the
engine — the engine lives in the project's scripts, invoked via `project.md`.

## Steps
1. **Run the configured command(s).** Take `commands.build` from `project.md`,
   substitute `{item}` with the item's directory, and run it. It typically chains
   narration → stitch → captions → finalize; run them in the given order. This is
   the authoritative command — don't guess from prose. If `commands.build` is
   missing, stop and ask.
2. **On failure, re-run only the failing subcommand**, not the whole chain — each
   stage's output feeds the next, so a captions failure shouldn't force a re-stitch.
3. **Respect engine conventions in `context.md`** (clip-native vs. stripped audio,
   bgm, logo bumper, caption style, word-timing source). `context.md` overrides on
   conflict — don't assume; check.
4. **Output** the final render plus any QA artifact the charter expects (e.g.
   `qa_checklist.md`) so the render gate has something to attach. Leave `pipeline.md`
   updates to the orchestrator.
