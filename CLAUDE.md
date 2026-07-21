Skills are organized into bucket folders under `skills/`:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools
- `misc/` — kept around but rarely used
- `personal/` — tied to my own setup, not promoted
- `in-progress/` — drafts not yet ready to ship
- `deprecated/` — no longer used

Every skill in `engineering/`, `productivity/`, or `misc/` must have a reference in the top-level `README.md` and an entry in `.claude-plugin/plugin.json`. Skills in `personal/`, `in-progress/`, and `deprecated/` must not appear in either.

Each skill entry in the top-level `README.md` must link the skill name to its `SKILL.md`.

Each bucket folder has a `README.md` that lists every skill in the bucket with a one-line description, with the skill name linked to its `SKILL.md`. Bucket `README.md`s and the top-level `README.md` group entries into **User-invoked** and **Model-invoked**.

Every `SKILL.md` is either user-invoked (`disable-model-invocation: true`, reachable only by the human) or model-invoked (model- or user-reachable). For the full definitions, description conventions, and why a user-invoked skill can invoke model-invoked skills but never another user-invoked one, see [docs/invocation.md](./docs/invocation.md).

## How skills are actually loaded — and a known misalignment (read before "fixing" paths)

This repo is symlinked into `~/.claude/skills` (`~/.claude/skills` → repo root, via `<sandbox-root>/repos` → `<mount-root>/USB`). Claude Code **discovers skills by scanning the folders directly under `~/.claude/skills`, i.e. the repo root**. So a skill is available purely because its `<name>/SKILL.md` sits at the top level of this repo — automatically, with no registration step. `.claude-plugin/plugin.json` does **not** drive local discovery; it's a separate distribution manifest.

Known, deliberate misalignment — **do not "fix" it unless explicitly asked**:
- On disk the skills are **flat top-level folders** (`rotate-session/`, `wrap/`, …). There is **no `skills/` directory**.
- The bucket structure described above, and most `./skills/<bucket>/…` paths in `README.md` and `plugin.json`, refer to that intended-but-not-yet-realized layout. Many of those paths therefore don't resolve on disk. That's pre-existing and left as-is on purpose.
- When registering a **new** skill in `README.md`/`plugin.json`, use the **flat path that actually resolves** (`./rotate-session/SKILL.md`, `"./rotate-session"`). Do not rewrite the existing bucketed entries to match, and do not move existing folders into a `skills/` tree.

## After a pull

When you pull this repo, or when the user says they just pulled (including pulls done outside Claude Code), check for skill changes:

```
git diff ORIG_HEAD..HEAD --name-only
```

Filter the output for files that are inside a skill directory (any `.md` file one or two levels deep that is not a top-level file, README, or doc). This covers `SKILL.md` and companion files like `sync-claude-md.md`.

For each changed skill:
- Name the skill (folder name) and which file(s) changed.
- Note whether it is user-invoked (`disable-model-invocation: true`) or model-invoked.
- If the skill has setup or config effects — it writes to `CLAUDE.md`, configures tools, or installs something — suggest the user re-invoke it.
- If the change is purely a definition or description update, just note it; no action needed.

If `ORIG_HEAD` is not set or equals `HEAD`, skip this check silently.
