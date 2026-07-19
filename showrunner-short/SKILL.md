---
name: showrunner-short
description: Write the dialogue/voiceover script for a short-form video (≤~60s) from a locked concept, honoring the project's beat structure, hosts, and per-beat timing. Use at the script stage of a content-pipeline shorts project, once concept.txt exists and before asset prompts.
---

Write `script.txt` for one short from its locked `concept.txt`. This is the
shorts-family script skill — it encodes short-form craft but takes the *specific*
beat structure, hosts/personas, duration, and voice from the project charter, so
it works for any shorts channel, not one.

## Read first (don't invent what these define)
- `concept.txt` — what this short depicts (mechanic/subject, narrative beat, setting).
- `project.md` + `context.md` — the charter: format/duration, **beat structure and
  per-beat timing**, host personas + their voices, the engagement mechanic (comment
  bait / CTA), IP/content constraints. `context.md` **overrides on conflict**.
- Any per-project `style_guide.md` for tone. If the charter doesn't define a beat
  structure or hosts, ask — don't default to a structure the project didn't set.

## Short-form craft (generic — applies whatever the structure)
- **Front-load the hook.** The first 1–2 seconds must land in media res — no
  intros, no "hey guys," no throat-clearing. Open on the most arresting moment.
- **Honor the charter's beat structure and timing exactly.** Write each beat inside
  its time block; don't let a beat run long. Tag every line with its speaker and
  its timing.
- **Write for the voice(s) the charter names.** If multi-host, give each a distinct
  cadence/role; keep turns short and punchy for spoken delivery.
- **Write for TTS delivery** — natural spoken phrasing, no unpronounceable markup in
  the spoken text; keep any delivery notes separate from the words to be voiced
  (follow the project's TTS convention in `context.md`).
- **End on the engagement mechanic** the charter defines (a polarizing dilemma, a
  question, a CTA) — draft it together with the final beat.

## Output
- `script.txt` — speaker-tagged lines with per-line/per-beat timing.
- Draft the engagement mechanic (e.g. pinned comment) into `publish.md`.
- Apply the beat dependencies internally (hook → middle → payoff); don't interview
  the user beat by beat unless they ask.
