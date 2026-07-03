---
name: game-concept-interview
description: Structured, staged interview to turn a rough game/marketing-short idea into a locked visual + narrative spec (game style guide + short concept). Use when the user wants to develop a game concept into T2I/animation-ready prompts, define or extend a game's visual identity, or plan a marketing short's narrative beat before scripting.
---

Interview the user one question at a time to build a concrete, T2I-ready spec — for a marketing short, a piece of game concept art, or general game design exploration. Never ask multiple questions at once. For each question, give a recommended answer with reasoning, and let the user confirm, redirect, or push back before moving to the next question. If the user pushes back with a real concern (e.g. "does this fit the mechanic?", "is this an IP risk?"), stop and reason it through explicitly before resuming — don't just re-ask.

Explore the codebase/project first (existing game design docs, prior shorts, an existing style guide) before asking anything that's already answered there.

## Two-tier output structure

Keep visual/narrative continuity across multiple shorts of the *same* game separate from per-short specifics:

- **Per-game `style_guide.md`** (create once, update whenever a new short establishes a new visual element): art medium/render style, color palette (and what each color *means*, not just what it looks like), camera/lens language, character/unit design, established locations, IP-safety notes for anything genre-adjacent to existing media.
- **Per-short `concept.txt`**: which mechanic/system this short demonstrates and why, the concrete narrative beat (a specific, visualizable action — not an abstract system description), setting for this specific scene, and a breakdown of what each asset slot (per the project's asset budget) needs to show.

If no style guide exists yet for this game, the interview is establishing the baseline — treat every art/style question as locking in precedent for all future shorts of that game, and say so explicitly when asking.

## Question sequence (adapt order to what's already known; skip anything already answered)

1. **Mechanic/system focus** — which one concrete mechanic does this concept/short center on? Recommend the option that's most *visually dramatic and legible in a single still frame* over one that's mechanically important but visually abstract (e.g. an internal stat vs. a unit visibly disobeying).
2. **Art medium/render style** — concrete rendering technique (e.g. stylized 3D cinematic vs. flat illustration vs. photoreal), tied to the actual dev stack where relevant (an engine-rendered look reads as "real game footage").
3. **Color palette** — not just colors, but what each signal color *means* mechanically (e.g. one accent color = stable/good state, another = danger/failure state), so palette choices double as legible in-universe signals.
4. **Camera/lens language** — may need to split by shot *purpose*: cinematic/dramatic framing for mood-setting shots vs. mechanically-accurate framing (e.g. real gameplay UI/perspective) for any shot whose job is to *prove* a mechanic is real, not just imply mood. If the user pushes back that a stylistic choice risks misrepresenting the actual game, this is the right moment to work through that tension explicitly rather than picking one blanket rule.
5. **Character/unit design** — silhouette, and critically: does the design make the mechanic being demonstrated *visually legible in a still frame* (e.g. a physical indicator light/marker tied to the stat in question)? If the user references an existing IP/genre aesthetic for inspiration, separate what's safe (genre convention, mood, generic silhouette elements) from what isn't (specific insignia, named characters, unique gear mechanisms) — state the split explicitly, don't just avoid the topic.
6. **Setting/environment** — concrete location, not generic. Push toward something that reinforces the mechanic's stakes rather than a neutral backdrop.
7. **Lighting/time-of-day/mood** — tie back to the palette's signal colors: make sure "meaningful" colors (danger states, mechanic indicators) stay reserved for their meaning and aren't diluted by ambient scene lighting using the same hue decoratively.
8. **Concrete narrative beat** — the specific action/moment to depict. Prefer beats that are easy to stage as a clean still/short loop over complex multi-stage action, and that serve whatever comes next in the pipeline (e.g. a script's Hook/Twist/Trap structure, or a marketing dilemma/CTA).
9. **Asset-slot breakdown** — map the locked narrative beat onto the project's actual asset budget/slots, assigning each slot a specific shot description (subject, camera language from Q4, what beat/moment it captures).

## Wrapping up

Once the sequence is exhausted (or the user says to move on), write/update the two output files immediately — don't leave the locked decisions only in conversation. If a `style_guide.md` for this game already existed, only append/amend the parts that changed or that this short newly established; don't regenerate the whole file from scratch.
