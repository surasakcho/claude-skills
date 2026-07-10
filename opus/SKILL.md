---
name: opus
description: Switch the active Claude model to Opus with medium effort. Use when the user types /opus.
---

Edit `~/.claude/settings.json` and set:
- `"model"` to `"opus"`
- `"effortLevel"` to `"medium"`

Preserve all other keys exactly as they are. Then tell the user: "Switched to Opus — effort: medium."
