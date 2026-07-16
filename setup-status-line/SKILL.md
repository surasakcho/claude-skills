---
name: setup-status-line
description: Configure Claude Code's or Antigravity's status line to display model name, agent state, context window usage, and rate limits with reset countdowns, without progress bars (e.g. ctx 23% | 5h 12% r:2h3m | wk 4%).
disable-model-invocation: true
---

# Setup Status Line

Configure the status line to display clean usage statistics without progress bars.

## For macOS/Linux (Bash)

Write `~/.claude/statusline.sh` with the script below, make it executable, then update `~/.claude/settings.json`.

```bash
#!/bin/bash
input=$(cat)

# Parse all fields via Python, semicolon-separated on one line.
IFS=';' read -r MODEL MODEL_ABBREV EFFORT CTX_PCT FH_PCT FH_RESET SD_PCT SD_RESET <<< \
  "$(python3 -c "
import json, sys
data = json.loads(sys.argv[1])

def get(obj, *keys, default=''):
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        else:
            return default
    return '' if obj is None else obj

model = get(data, 'model', 'display_name', default='unknown')
parts = model.split()
if len(parts) >= 3:
    abbrev = parts[1][0] + parts[2]
elif len(parts) == 2:
    abbrev = parts[0][0] + parts[1]
else:
    abbrev = model[:6]

print(';'.join([
    model,
    abbrev,
    get(data, 'effort', 'level') or '-',
    str(int(get(data, 'context_window', 'used_percentage', default=0))),
    str(get(data, 'rate_limits', 'five_hour', 'used_percentage')),
    str(get(data, 'rate_limits', 'five_hour', 'resets_at')),
    str(get(data, 'rate_limits', 'seven_day', 'used_percentage')),
    str(get(data, 'rate_limits', 'seven_day', 'resets_at')),
]))
" "$input")"

[ "$EFFORT" = "-" ] && EFFORT=""
CTX_PCT=${CTX_PCT:-0}
FORMAT="${STATUSLINE_FORMAT:-short}"

format_reset_decimal() {
  local reset_at="$1"
  [ -z "$reset_at" ] || [ "$reset_at" = "None" ] && echo "" && return
  local now secs
  now=$(date +%s)
  secs=$(( reset_at - now ))
  [ $secs -le 0 ] && echo "now" && return
  python3 -c "
s=$secs
if s < 86400:
    print(f'{s/3600:.1f}h')
else:
    print(f'{s/86400:.1f}d')
"
}

if [ "$FORMAT" = "short" ]; then
  if [ -n "$EFFORT" ]; then
    EFFORT_ABBREV="${EFFORT:0:1}"
    MODEL_SHORT="${MODEL_ABBREV}(${EFFORT_ABBREV})"
  else
    MODEL_SHORT="${MODEL_ABBREV}"
  fi
  PARTS="${MODEL_SHORT}|ctx:${CTX_PCT}%"
  RL_SEG=""
  if [ -n "$FH_PCT" ] && [ "$FH_PCT" != "None" ]; then
    FH_PCT_INT=$(python3 -c "print(int(float('$FH_PCT')))" 2>/dev/null)
    FH_TIME=$(format_reset_decimal "$FH_RESET")
    [ -n "$FH_TIME" ] && RL_SEG="5h:${FH_PCT_INT}% ${FH_TIME}" || RL_SEG="5h:${FH_PCT_INT}%"
  fi
  if [ -n "$SD_PCT" ] && [ "$SD_PCT" != "None" ]; then
    SD_PCT_INT=$(python3 -c "print(int(float('$SD_PCT')))" 2>/dev/null)
    SD_TIME=$(format_reset_decimal "$SD_RESET")
    [ -n "$SD_TIME" ] && RL_PART="7d:${SD_PCT_INT}% ${SD_TIME}" || RL_PART="7d:${SD_PCT_INT}%"
    [ -n "$RL_SEG" ] && RL_SEG="${RL_SEG}|${RL_PART}" || RL_SEG="$RL_PART"
  fi
  [ -n "$RL_SEG" ] && PARTS="${PARTS}|${RL_SEG}"
  echo "$PARTS"
  exit 0
fi

# Full format
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

PARTS="$MODEL_SEG  |  context:${CTX_PCT}%"

if [ -n "$FH_PCT" ] && [ "$FH_PCT" != "None" ]; then
  FH_PCT_INT=$(python3 -c "print(int(float('$FH_PCT')))" 2>/dev/null)
  FH_TIME=$(format_reset "$FH_RESET")
  [ -n "$FH_TIME" ] && PARTS="$PARTS  |  5h:${FH_PCT_INT}% reset $FH_TIME" || PARTS="$PARTS  |  5h:${FH_PCT_INT}%"
fi

if [ -n "$SD_PCT" ] && [ "$SD_PCT" != "None" ]; then
  SD_PCT_INT=$(python3 -c "print(int(float('$SD_PCT')))" 2>/dev/null)
  SD_TIME=$(format_reset "$SD_RESET")
  [ -n "$SD_TIME" ] && PARTS="$PARTS  |  7d:${SD_PCT_INT}% reset $SD_TIME" || PARTS="$PARTS  |  7d:${SD_PCT_INT}%"
fi

echo "$PARTS"
```

## For Windows (PowerShell - Antigravity)

Write `~/.antigravity/statusline.ps1` with the script below, then update `~/.gemini/antigravity-cli/settings.json`.

```powershell
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$inputJson = $input | Out-String
if (-not $inputJson -or $inputJson.Trim().Length -eq 0) { exit }
try { $data = ConvertFrom-Json $inputJson } catch { exit }

# --- Model (short name) ---
$modelRaw = ""
if ($data.model.display_name)     { $modelRaw = $data.model.display_name }
elseif ($data.model.id)           { $modelRaw = $data.model.id }
elseif ($data.model -is [string]) { $modelRaw = $data.model }

# Shorten known model names
$model = $modelRaw
$model = $model -replace 'Claude ',        ''
$model = $model -replace 'Gemini ',        'Gem '
$model = $model -replace '\(Thinking\)',   '(T)'
$model = $model -replace 'Sonnet',         'Son'
$model = $model -replace 'Haiku',          'Hai'
$model = $model -replace 'Opus',           'Ops'
$model = $model -replace 'Flash',          'Fls'
$model = $model -replace '\(Medium\)',     ''
$model = $model -replace '\(medium\)',     ''
$model = $model -replace 'Medium',         ''
$model = $model -replace 'Preview',        'Prev'
$model = $model -replace '\s{2,}',         ' '
$model = $model.Trim()
if ($model.Length -gt 15) { $model = $model.Substring(0, 14) + "." }

# --- Agent state ---
$agentState = if ($data.agent_state) { $data.agent_state } else { "idle" }

# --- Context window ---
$ctxPct = 0
if ($null -ne $data.context_window.used_percentage) {
    $ctxPct = [int][math]::Round([double]$data.context_window.used_percentage)
}

# --- Quota helper ---
function Get-QuotaInfo($quota, $key) {
    $bucket = $quota.$key
    if ($null -eq $bucket -or $null -eq $bucket.remaining_fraction) { return $null }
    $usedPct = [int][math]::Round((1.0 - [double]$bucket.remaining_fraction) * 100)
    $resetStr = ""
    if ($bucket.reset_in_seconds) {
        $secs = [int]$bucket.reset_in_seconds
        if ($secs -ge 86400) {
            $d = [math]::Floor($secs / 86400)
            $h = [math]::Floor(($secs % 86400) / 3600)
            $resetStr = "${d}d${h}h"
        } elseif ($secs -ge 3600) {
            $h = [math]::Floor($secs / 3600)
            $m = [math]::Floor(($secs % 3600) / 60)
            $resetStr = "${h}h${m}m"
        } else {
            $m = [math]::Floor($secs / 60)
            $resetStr = "${m}m"
        }
    }
    return @{ UsedPct = $usedPct; Reset = $resetStr }
}

# Detect model family
$isGemini = $modelRaw.ToLower().Contains("gemini")
$prefix   = if ($isGemini) { "gemini" } else { "3p" }

$quota5h  = Get-QuotaInfo $data.quota ($prefix + "-5h")
$quotaWk  = Get-QuotaInfo $data.quota ($prefix + "-weekly")

function Bar-Color([int]$pct) {
    if ($pct -ge 90) { return "Red" }
    elseif ($pct -ge 70) { return "Yellow" }
    else { return "Cyan" }
}

$ctxColor = if ($ctxPct -ge 90) { "Red" } elseif ($ctxPct -ge 70) { "Yellow" } else { "Green" }

# State label & color
$stateLabel = switch ($agentState.ToLower()) {
    "idle"     { "RDY" }
    "ready"    { "RDY" }
    "thinking" { "THK" }
    "working"  { "WRK" }
    "tool"     { "TUL" }
    default    { "..." }
}
$stateColor = switch ($agentState.ToLower()) {
    "idle"     { "Green" }
    "ready"    { "Green" }
    "thinking" { "Yellow" }
    "working"  { "Cyan" }
    "tool"     { "Magenta" }
    default    { "White" }
}

# --- Render ---
Write-Host "" -NoNewline
Write-Host " " -NoNewline
Write-Host $stateLabel -ForegroundColor $stateColor -NoNewline
Write-Host " | " -ForegroundColor DarkGray -NoNewline

# Model
Write-Host $model -ForegroundColor Magenta -NoNewline
Write-Host " | " -ForegroundColor DarkGray -NoNewline

# Context
Write-Host "ctx " -ForegroundColor DarkGray -NoNewline
Write-Host "$ctxPct%" -ForegroundColor $ctxColor -NoNewline
Write-Host " | " -ForegroundColor DarkGray -NoNewline

# 5h quota
if ($null -ne $quota5h) {
    $c = Bar-Color $quota5h.UsedPct
    Write-Host "5h " -ForegroundColor DarkGray -NoNewline
    Write-Host "$($quota5h.UsedPct)%" -ForegroundColor $c -NoNewline
    if ($quota5h.Reset) { Write-Host " r:$($quota5h.Reset)" -ForegroundColor DarkGray -NoNewline }
} else {
    Write-Host "5h N/A" -ForegroundColor DarkGray -NoNewline
}
Write-Host " | " -ForegroundColor DarkGray -NoNewline

# Weekly quota
if ($null -ne $quotaWk) {
    $c = Bar-Color $quotaWk.UsedPct
    Write-Host "wk " -ForegroundColor DarkGray -NoNewline
    Write-Host "$($quotaWk.UsedPct)%" -ForegroundColor $c -NoNewline
    if ($quotaWk.Reset) { Write-Host " r:$($quotaWk.Reset)" -ForegroundColor DarkGray -NoNewline }
} else {
    Write-Host "wk N/A" -ForegroundColor DarkGray -NoNewline
}

Write-Host ""
```

## Steps

1. Save the respective script to your local path:
   - macOS/Linux: `~/.claude/statusline.sh`
   - Windows: `~/.antigravity/statusline.ps1`
2. Update the `statusLine` configuration in:
   - macOS/Linux (`~/.claude/settings.json`):
     ```json
     "statusLine": {
       "type": "command",
       "command": "~/.claude/statusline.sh",
       "refreshInterval": 30
     }
     ```
   - Windows (`~/.gemini/antigravity-cli/settings.json`):
     ```json
     "statusLine": {
       "type": "",
       "command": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File <your-home>/.antigravity/statusline.ps1"
     }
     ```
