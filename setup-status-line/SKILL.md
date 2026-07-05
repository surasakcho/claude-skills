---
name: setup-status-line
description: Configure Claude Code's status line to display model name, effort level, context window usage, and 5-hour/7-day rate limit usage with reset countdowns. Writes ~/.claude/statusline.sh and updates ~/.claude/settings.json automatically.
disable-model-invocation: true
---

# Setup Status Line

Write `~/.claude/statusline.sh` with the script below, make it executable, then update `~/.claude/settings.json` to wire it in.

**Note:** The script uses Python 3 (not `jq`) for JSON parsing — `jq` is often not installed.

## Script to write at `~/.claude/statusline.sh`

```bash
#!/bin/bash
input=$(cat)

# Parse all fields via Python in one call, newline-separated
IFS=$'\n' read -r -d '' MODEL EFFORT CTX_PCT FH_PCT FH_RESET SD_PCT SD_RESET < <(python3 -c "
import json, sys
data = json.loads(sys.argv[1])

def get(obj, *keys, default=''):
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        else:
            return default
    return '' if obj is None else obj

print(get(data, 'model', 'display_name', default='unknown'))
print(get(data, 'effort', 'level'))
print(int(get(data, 'context_window', 'used_percentage', default=0)))
print(get(data, 'rate_limits', 'five_hour', 'used_percentage'))
print(get(data, 'rate_limits', 'five_hour', 'resets_at'))
print(get(data, 'rate_limits', 'seven_day', 'used_percentage'))
print(get(data, 'rate_limits', 'seven_day', 'resets_at'))
" "$input"; printf '\0')

# Build 10-char context bar
CTX_PCT=${CTX_PCT:-0}
filled=$(( CTX_PCT / 10 ))
[ $filled -gt 10 ] && filled=10
empty=$(( 10 - filled ))
bar=""
for i in $(seq 1 $filled); do bar="${bar}#"; done
for i in $(seq 1 $empty);  do bar="${bar}-"; done

format_reset() {
  local reset_at="$1"
  [ -z "$reset_at" ] && echo "" && return
  local now secs days hours mins
  now=$(date +%s)
  secs=$(( reset_at - now ))
  [ $secs -le 0 ] && echo "now" && return
  days=$(( secs / 86400 ))
  hours=$(( (secs % 86400) / 3600 ))
  mins=$(( (secs % 3600) / 60 ))
  if [ $days -gt 0 ]; then echo "${days}d${hours}h"
  elif [ $hours -gt 0 ]; then echo "${hours}h${mins}m"
  else echo "${mins}m"; fi
}

if [ -n "$EFFORT" ]; then
  MODEL_SEG="[$MODEL ($EFFORT)]"
else
  MODEL_SEG="[$MODEL]"
fi

PARTS="$MODEL_SEG  |  context:${CTX_PCT}% [${bar}]"

if [ -n "$FH_PCT" ]; then
  FH_PCT_INT=$(python3 -c "print(int(float('$FH_PCT')))" 2>/dev/null)
  FH_TIME=$(format_reset "$FH_RESET")
  [ -n "$FH_TIME" ] && PARTS="$PARTS  |  5h:${FH_PCT_INT}% reset $FH_TIME" || PARTS="$PARTS  |  5h:${FH_PCT_INT}%"
fi

if [ -n "$SD_PCT" ]; then
  SD_PCT_INT=$(python3 -c "print(int(float('$SD_PCT')))" 2>/dev/null)
  SD_TIME=$(format_reset "$SD_RESET")
  [ -n "$SD_TIME" ] && PARTS="$PARTS  |  7d:${SD_PCT_INT}% reset $SD_TIME" || PARTS="$PARTS  |  7d:${SD_PCT_INT}%"
fi

echo "$PARTS"
```

## Steps

1. Write the script above to `~/.claude/statusline.sh`.
2. Run `chmod +x ~/.claude/statusline.sh` to make it executable.
3. Read `~/.claude/settings.json`, then add or update the `statusLine` key:

```json
"statusLine": {
  "type": "command",
  "command": "~/.claude/statusline.sh",
  "refreshInterval": 30
}
```

   Merge it into the existing JSON — do not overwrite other settings.

4. Confirm to the user that the status line is configured and will appear at the bottom of Claude Code after the next interaction. Mention that `5h` and `7d` segments only appear for Claude.ai Pro/Max subscribers after the first API response.
