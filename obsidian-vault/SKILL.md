---
name: obsidian-vault
description: Search, create, and manage notes in the Obsidian vault with wikilinks and index notes. Use when user wants to find, create, or organize notes in Obsidian.
---

# Obsidian Vault

## Vault location

Machine-specific, so it is never hardcoded here. Read it once and reuse it for the session:

```bash
VAULT="$(python lib/skillconfig.py get OBSIDIAN_VAULT --repo <skills-repo> --prompt 'Obsidian vault path')"
```

First use prompts and stores it in the repo's gitignored `.env`; later uses read it back. If
it is not set and nothing can prompt, **stop and ask** — do not guess a vault path.

Mostly flat at root level.

## Naming conventions

- **Index notes**: aggregate related topics (e.g., `Ralph Wiggum Index.md`, `Skills Index.md`, `RAG Index.md`)
- **Title case** for all note names
- No folders for organization - use links and index notes instead

## Linking

- Use Obsidian `[[wikilinks]]` syntax: `[[Note Title]]`
- Notes link to dependencies/related notes at the bottom
- Index notes are just lists of `[[wikilinks]]`

## Workflows

### Search for notes

```bash
# Search by filename
find "$VAULT" -name "*.md" | grep -i "keyword"

# Search by content
grep -rl "keyword" "$VAULT" --include="*.md"
```

Or use Grep/Glob tools directly on the vault path.

### Create a new note

1. Use **Title Case** for filename
2. Write content as a unit of learning (per vault rules)
3. Add `[[wikilinks]]` to related notes at the bottom
4. If part of a numbered sequence, use the hierarchical numbering scheme

### Find related notes

Search for `[[Note Title]]` across the vault to find backlinks:

```bash
grep -rl "\\[\\[Note Title\\]\\]" "$VAULT"
```

### Find index notes

```bash
find "$VAULT" -name "*Index*"
```
