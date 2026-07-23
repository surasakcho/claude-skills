---
name: launch-session
description: Start a new detached tmux session, cd into a repo under ~/repos/, and launch Claude Code with a given model and remote-control name. Requires 4 parameters from the user — repo, model, tmux session name, and remote-control session name. Use when the user says "launch session", "start a claude session", "open a tmux claude session", or similar.
---

# launch-session

Ask the user for any of these 4 parameters not already provided in the args:

1. **repo** — repo name under `~/repos/` (e.g. `e-biz-factory`)
2. **model** — Claude model to use: `sonnet`, `opus`, `haiku`, or `fable`
3. **tmux** — tmux session name to create (e.g. `ebiz`, `gamelab`)
4. **rc** — remote-control session name that will appear on claude.ai (e.g. `ebiz-main`)

Once all four are confirmed, run exactly this bash command (substituting the four values):

```bash
tmux new-session -d -s "<tmux>" -c "$HOME/repos/<repo>" \
  "claude --model <model> --remote-control '<rc>'"
```

After the command succeeds, tell the user:

- Attach command: `tmux attach -t <tmux>`
- Remote-control: go to claude.ai/code → select session **`<rc>`**
- Repo: `~/repos/<repo>`
- Model: `<model>`

If the tmux session name is already taken (`tmux has-session -t <tmux>` exits 0), warn the user before proceeding — do not overwrite a live session without explicit confirmation.
