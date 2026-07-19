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
