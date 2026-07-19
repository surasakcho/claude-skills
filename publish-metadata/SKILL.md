---
name: publish-metadata
description: Write the publish metadata for a finished content item — title variants, SEO description, tags, chapters, and the finalized pinned/engagement comment. Runs at the publish stage of a content-pipeline project, after the render is approved. Use when completing publish.md for a stockpiled item.
---

Complete `publish.md` for one finished item so it's ready to upload. Metadata
optimizer role: read the final `script.txt` and the charter, then write copy that
earns the click and the comment without over-promising what the video delivers.

## Read first
- Final `script.txt` — the actual content, hook, and payoff.
- `project.md` + `context.md` — niche, voice, the engagement mechanic, any
  title/tag conventions. `context.md` overrides on conflict.
- The draft pinned/engagement comment already in `publish.md` (from the script
  stage) — finalize it, don't start over.

## Write into publish.md
- **Title variants** (2–3) — front-load the hook/curiosity; match the platform's
  length norm; no clickbait the video doesn't pay off.
- **Description** — a tight SEO-aware opener (first line does the work), then any
  standing channel boilerplate the charter specifies.
- **Tags** — drawn from the actual subject/mechanic, not generic filler.
- **Chapters** — only if the format is long enough to warrant them.
- **Finalized engagement comment** — the polarizing question / CTA, tuned against
  the final Trap/payoff.

Upload itself is manual and out of scope. When done, tell the orchestrator the item
is ready to be marked complete (e.g. `stockpiled`); the orchestrator owns
`pipeline.md`.
