---
name: game-concept-interview
description: Structured, staged interview to turn a rough game/marketing-short idea into a locked visual + narrative spec (game style guide + short concept). Use when the user wants to develop a game concept into T2I/animation-ready prompts, define or extend a game's visual identity, or plan a marketing short's narrative beat before scripting.
---

Interview the user one question at a time to build a concrete, T2I-ready spec — for a marketing short, a piece of game concept art, or general game design exploration. Never ask multiple questions at once. For each question, give a recommended answer with reasoning, and let the user confirm, redirect, or push back before moving to the next question. If the user pushes back with a real concern (e.g. "does this fit the mechanic?", "is this an IP risk?"), stop and reason it through explicitly before resuming — don't just re-ask.

Explore the codebase/project first (existing game design docs, prior shorts, an existing style guide) before asking anything that's already answered there.

**Inside a content-pipeline project:** if the project has a `project.md` (pipeline config — niche, format, budget) and `context.md` (decision log + glossary), read both before interviewing — `context.md` **overrides on conflict**. They carry project-level direction and constraints this stage must honor, alongside the game canon (`style_guide.md` / the real dev project) you already use.

## Step 0 — check for a real dev project BEFORE asking anything

Before any interview question, check whether this game has a real development project already (a Unity/Unreal/Godot project folder, a game repo — ask the user if it's not obvious, e.g. "is there a dev project for this game yet, and if so where?"). This determines who owns canon:

- **A real dev project exists:** its design docs (CLAUDE.md, design specs, README, whatever it has) are the source of truth for mechanics, visual style, and terminology — not this interview. Read them first. The interview's job becomes *translating* that canon into marketing/concept-art terms (e.g. "the game is pixel-sprite HD-2D, but concept art can still be cinematic 3D since it's not gameplay capture — what specifically needs to stay accurate vs. what has creative license?"), not inventing a fresh identity. Skip/reframe any question below that the real project already answers, and flag explicitly which answers come from canon vs. are new marketing-only choices. If a `style_guide.md`/`design.md` in this repo already exists and predates the check, diff it against the real project's current docs — direction can drift as the real project evolves, and stale assumptions (wrong terminology, wrong signal colors, wrong render style) are expensive to unwind after prompts/assets are already built on them.
- **No real dev project yet (concept-only):** this repo's `games/{slug}/` files ARE canon, same as before — proceed with the full interview below.

When a game's status flips from concept-only to "has a real dev project," the existing `style_guide.md`/`design.md` needs a reconciliation pass against the new canon (don't just leave it stale) — treat this the same as a normal interview session: walk through what changed, one topic at a time, get confirmation, and preserve any solid-but-now-superseded direction in `games/_reusable-styles/` rather than deleting it, since it may fit a different game later.

## Two-tier output structure

Keep visual/narrative continuity across multiple shorts of the *same* game separate from per-short specifics:

- **Per-game `style_guide.md`** (create once, update whenever a new short establishes a new visual element): art medium/render style, color palette (and what each color *means*, not just what it looks like), camera/lens language, character/unit design, established locations, IP-safety notes for anything genre-adjacent to existing media. If a real dev project is canon, open with a pointer to it and a note that this file is a derived translation, not the source of truth.
- **Per-game `design.md`** (only when a real dev project exists): a thin pointer to the real design docs plus narrative/tone notes established through short production — deliberately does NOT duplicate exact numeric formulas/mechanics from the real project, since those will drift out of sync as development continues.
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

Once the sequence is exhausted (or the user says to move on), write/update the output files immediately — don't leave the locked decisions only in conversation. If a `style_guide.md` for this game already existed, only append/amend the parts that changed or that this short newly established; don't regenerate the whole file from scratch. If a real dev project is canon for this game, make sure `style_guide.md`'s opening lines name its path explicitly, so the next session (which starts with zero memory of this one) knows immediately to check it before trusting anything else in the file.
