---
name: draft-asset-prompts
description: Draft or reconcile T2I image prompts and T2V/Flow animation prompts for a marketing short, once concept.txt and style_guide.md are locked (see game-concept-interview). Use when the user needs to write t2i_prompts.txt / flow_prompts.txt from scratch, or to reconcile either file against images/clips that were actually generated (which often diverge from the original prompt through live iteration).
---

Two distinct jobs live under this skill: **drafting** prompts from a locked concept before generation, and **reconciling** prompt files against what was actually kept after the user iterated live in the T2I/T2V tool. Figure out which one the user needs — if they mention pasting a generation-tool transcript, selecting/keeping specific images, or say something like "I updated clip X," that's reconciliation, not drafting.

## Drafting T2I prompts (before generation)

Source the prompt content from `concept.txt` (per-short: mechanic, narrative beat, setting, asset-slot breakdown) and `style_guide.md` (per-game: render style, palette + what each color *means*, camera language, character design, IP-safety constraints). Don't invent details these files don't cover — flag the gap and ask instead.

- One prompt block per asset slot, in the same order as `concept.txt`'s slot list.
- Each shot's palette/UI language must match style_guide.md's *meaning* rules, not just look plausible — e.g. if a color signals a specific game state, the prompt needs to specify the state, not just the color (see "state-accuracy" below).
- If the game has a real dev project as canon, mirror the terminology and any real UI systems (e.g. `BodyStatusUI.cs` existing in the real project justified adding a Health HUD to a shot in a past short) rather than inventing new stats/mechanics wholesale.
- Note Gemini's content-policy behavior if the short involves a young/vulnerable-looking human character: even soft age-signaling words ("teen," "adolescent," "kid") can trigger refusals. Carry vulnerability through body language/expression/framing instead, and phrase the character prompt as an adult-coded frame (established precedent: "fragile young man").

## Drafting Flow/T2V animation prompts (after images are locked)

These come after `t2i_prompts.txt` is finalized against real kept images — animate the *locked* composition, don't redesign it.

- Motion should be small and continuous (drift, flicker, breathing, slow push-in), matched to each shot's dramatic weight — not big new camera moves or added elements.
- Any shot with legible on-screen UI/HUD text needs an explicit "keep this text static, sharp, and unchanged" instruction — generative video is prone to warping on-screen text specifically, more so than T2I is.
- Map each clip's target duration from the locked script (Hook/Twist/Trap timing), so nothing needs re-cutting after generation.
- If a shot is built to loop (e.g. an "idle" shot holding a full script beat alone), say so explicitly and ask for continuous motion with no readable start/end point.
- Flag the known fallback up front rather than waiting for a failure: if a tool can't keep HUD text stable no matter how the prompt is phrased, the fix is animating a HUD-stripped background/character and compositing the static text back on top in the video pipeline (the same way captions get burned in), not endless prompt iteration.
- Tell the user not to worry about ambient sound/music the animation tool bakes into the clip, if the pipeline strips clip audio and rebuilds the soundtrack from narration + music + SFX separately (check the actual pipeline code, e.g. `stitch`'s `audio=False`, before asserting this — don't assume it's true of every pipeline).

### Google Flow specifics (as of this skill's writing — verify against the actual current UI before asserting anything, since generative-video tool UIs change fast)

- **Frames vs. Ingredients input mode:** use Frames (single start image) for animating an already-locked, fully-composed shot. Ingredients is for combining multiple separate reference images into a new composition — wrong mode once the shot is already locked.
- **End frame:** leave blank for ordinary subtle-motion shots. Two legitimate uses for setting it: (a) a shot that needs to loop seamlessly (same image as start and end frame helps it return to the same state), and (b) as a fallback if on-screen text keeps drifting despite the prompt instruction — a matching end frame is an explicit image-based constraint, stronger than a text instruction alone.
- **Aspect ratio/resolution:** set portrait/9:16 at generation time to match the pipeline's target export dimensions directly, rather than relying on a center-crop step to fix a mismatched source. Download the highest resolution available (even above the pipeline's target) — downscaling is clean, upscaling from below-target resolution blurs fine detail, which is worst-case on any shot with on-screen text.
- **Model/quality tier selection:** don't assert specific current model names/tiers/behaviors from training data — ask the user what's listed in their UI right now. As a general decision framework: bias toward the highest-quality tier for shots carrying on-screen text or other high-stakes locked detail; cheaper/faster tiers are more reasonable for simple atmosphere shots with no text and lower failure cost. Mixing tiers across a short's clips has a real tradeoff (cost savings vs. potentially visible inconsistency in motion quality between clips) — worth naming explicitly rather than picking silently.

## Per-clip duration and SFX manifests

If the build pipeline supports it (check for a `clip_durations.txt`/`sfx.txt`-style convention, or propose adding one), don't let a script's differentiated Hook/Twist/Trap timing silently degrade into an even split across clips — verify the actual stitching code respects per-clip durations, not just total duration. Similarly, keep SFX *sound* decoupled from the animation tool itself (SFX gets layered in the video pipeline in post, timed to each clip's actual start position in the final timeline) rather than trying to get the T2V tool to bake in specific sound effects, which is much harder to control precisely than a post-production audio layer.

**VFX (visual) vs. SFX (audio) is a real split, not the same decision.** If the user wants something like gunfire, an explosion, or a flash that's meant to be *seen*, that's VFX and belongs in the Flow/T2V prompt itself — the animation tool is the right place to generate visual effects. The *sound* that accompanies it still goes through the post-production SFX manifest, same as any other SFX. Once split this way, the SFX manifest's offsets are only ever a placeholder guess until the real clip exists — write them as a rough spread across the clip's duration, but flag explicitly (in both the prompt file and the SFX manifest) that they must be re-synced to the actual generated footage's real flash/action timing before the final render, not left as first-guess numbers.

## Reconciling prompt files against actual kept generations

This is the harder, more error-prone half — live iteration in a T2I/T2V tool routinely diverges from the original locked prompt, and silently "fixing" the prompt file to match what was *planned* instead of what was *kept* creates a false record.

- **Ask per-clip, don't assume.** Confirm which image/clip the user is actually keeping before touching any prompt text — a design decision (e.g. a palette rule) can change mid-session, and different clips may or may not have picked up that change.
- **Look at the actual image, not just the user's description of it.** Read the file and check it against the prompt's intent directly — this catches problems the user's own summary might miss (a past case: a "trust breakdown" shot's kept image showed a high, healthy trust percentage, which the user hadn't flagged until asked to look again).
- **Check state-accuracy, not just style-accuracy.** A generated image can nail the art style/palette while still contradicting the narrative beat it's supposed to sell (e.g. a UI readout showing the opposite of the mechanic state the shot exists to demonstrate) — verify what any on-screen numbers/labels actually say against what the beat requires.
- **When a generation reveals a real design decision** (not just an accepted rendering quirk), check whether it should propagate to `style_guide.md`/`design.md` and, if a real dev project is canon for the game, whether it belongs there too — don't let a locked-file rule silently go stale relative to what's actually being produced. Confirm with the user before reversing an established rule (e.g. a signal-color convention); a prompt bug isn't the same as a considered design pivot.
- **Record the iteration history in the prompt file itself**, not just in conversation — a short `NOTE (history): v1 ... v2 ...` block per clip that changed, explaining what was wrong and what fixed it. This is cheap and makes the file self-documenting for the next session, which starts with zero memory of the live back-and-forth.
- **Shot-slot numbering should equal final playback order.** If the locked script needs a different clip order than the shots were originally numbered in, renumber the shot files/prompt entries directly rather than introducing a separate ordering/manifest mechanism — most build pipelines assume filename order is playback order, and matching that keeps the pipeline simple. Renumbering means updating the shot's identity everywhere it's referenced (concept.txt, t2i_prompts.txt, flow_prompts.txt, script.txt) — do all of them in the same pass, don't leave a stale reference.
