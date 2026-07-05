---
name: link-claude-skills
description: Link a git-tracked skills repo folder with the user's ~/.claude/skills directory (either direction), so skills can be version-controlled. Use when the user wants to link, symlink, or junction their .claude/skills folder to/from a repo, or asks to set up skill version control. Works on Windows and Linux (including Raspberry Pi 4).
---

# Link Claude skills folder to a repo

Connects `<user-home>/.claude/skills` with a folder inside a git repo (e.g.
`claude-skills`), so the skills can be committed and versioned, while Claude
Code keeps reading them from the normal `.claude/skills` location.

One side holds the **real** files; the other side is a **link** to it. Never
have both sides hold independent real content — that's how skills silently
diverge.

## Inputs

Ask or infer:
- `repo_path` — path to the repo's skills folder (e.g. `~/Repos/claude-skills`).
- `home_skills` — the user's skills dir: `~/.claude/skills` (Linux/macOS/Pi4)
  or `%USERPROFILE%\.claude\skills` (Windows).
- `direction`:
  - **`repo-canonical`** (default, recommended for version control): the repo
    folder holds the real files; `.claude/skills` becomes the link.
  - **`home-canonical`**: `.claude/skills` holds the real files; the repo
    folder becomes the link.

## Detect the platform

- Windows: use PowerShell, junctions/symlinks via `New-Item`.
- Linux (including Raspberry Pi 4) or macOS: use `ln -s` — plain symlinks,
  no elevated privileges needed either direction.

## Algorithm (run this logic regardless of OS)

1. Inspect both paths. For each, determine: doesn't exist / exists as a
   link already / exists as a real directory (and if so, whether it has
   content — **check file counts, don't trust an empty-looking listing**,
   some tools truncate output).
2. If the link-side path is **already a link pointing at the canonical
   path** — done, report success, no changes needed.
3. If **both** sides are real directories with content — STOP. Do not merge
   or delete automatically. Report the conflict to the user and ask them
   to reconcile (e.g. `diff -rq` the two, decide which wins) before
   re-running.
4. Otherwise:
   - Ensure the canonical side is a real directory. If it doesn't exist yet
     but the link-side has the real content, **move** that content to the
     canonical path (don't copy-then-delete; move preserves it atomically).
   - Remove the link-side path if it exists (it'll be empty or a stale link
     at this point — safe to remove).
   - Create the link at the link-side path, pointing at the canonical path.
5. Verify: list both paths and confirm they report the same file count and
   the link resolves to the canonical target.

## Windows (PowerShell) commands

```powershell
# Inspect
Get-Item <path> -Force | Select-Object LinkType, Target
(Get-ChildItem <path> -Force).Count

# Remove a junction/symlink itself (does NOT touch target contents)
(Get-Item <linkPath>).Delete()

# Move real content into place (only if canonical dir doesn't exist yet)
Move-Item <oldRealPath> <canonicalPath>

# Create the link — prefer Junction (works without admin/Developer Mode).
# Only try SymbolicLink if the user specifically wants a true symlink and
# has admin rights or Developer Mode enabled.
New-Item -ItemType Junction -Path <linkPath> -Target <canonicalPath>
```

Junctions only work for local directories on the same machine (not UNC/
network paths) — that's fine for this use case.

## Linux / Raspberry Pi 4 (bash) commands

```bash
# Inspect
ls -la <path>          # check if it's a symlink (l...) and where it points
readlink -f <path>
find <path> -mindepth 1 | wc -l   # real content count

# Remove a symlink itself (does NOT touch target contents)
rm <linkPath>          # only if it's confirmed to be a symlink, not a real dir

# Move real content into place (only if canonical dir doesn't exist yet)
mv <oldRealPath> <canonicalPath>

# Create the link
ln -s <canonicalPath> <linkPath>
```

No elevated privileges are needed on Linux for symlinks in the user's own
home directory — this is the same on a Raspberry Pi 4 as any other Linux box.

## Safety notes

- Always run the inspection step first and show the user what you found
  before deleting or moving anything.
- Never use `rm -rf` / `Remove-Item -Recurse` on a path until you've
  confirmed via `ls -la` / `Get-Item` that it's a link and not the real
  directory — deleting a symlink and deleting its target are very
  different operations.
- Default to `repo-canonical` when the goal is "version control my skills"
  — that's the direction that makes the repo the source of truth and lets
  `git status`/`git log` reflect real changes.
