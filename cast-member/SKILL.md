---
name: cast-member
description: Create or revise a locked cast/mascot reference sheet — a recurring character rendered consistently across views so shots can reuse it by name. Use when adding a new character/mascot to a project's cast library, or revising an existing one's look. Built for multi-view consistency and easy iteration.
---

Produce and maintain **locked reference images** for recurring characters — the
reusable asset library that content items pull from by name (e.g. a `REFS:` line in
a shot's prompts). A cast member is **create-once, freeze-as-canon,
reference-forever** — a different lifecycle from a content item that ships, so it's
a library asset, not something tracked on the pipeline dashboard.

Two jobs: **create** a new member and **revise** an existing one. Revision is
first-class — cast members drift and get tweaked, so the **saved prompt is the
starting point** and you regenerate only what changed.

## Read first
- `project.md` / `context.md` — the project's cast conventions: where the library
  lives (e.g. `branding/cast/`), the reference-name/`REFS:` system, the image-
  generation command, IP/style constraints. `context.md` overrides. Ask if undefined.
- The project's `style_guide.md` — render style, palette *meaning*, silhouette
  language the character must fit.
- For a mascot counterpart or a character meant to echo an existing one, read what
  it echoes — a change that breaks the resemblance is a regression, not an edit.

## Consistency is the whole point
A cast member is only useful if it renders **identically** every time it's
referenced; the enemy is multi-view drift. Bake consistency in:
- **Single-pass character sheet** — generate all views (front/side/back/top) in ONE
  image where the tool allows, so the model holds one design across views instead of
  four independent generations that drift apart.
- **Symmetrize** features with no reason to differ left/right — asymmetry multiplies
  drift across views.
- **Neutral pose, even lighting, orthographic character-sheet framing** — no dramatic
  angles that hide or reinterpret the design.
- Lock a clear **silhouette + 2–3 signature identifiers** (color, headgear, one prop)
  that must appear identically in every view and every future shot.

## Create a new member
1. **Design** — run a focused character-design pass (reuse `game-concept-interview`'s
   character/unit-design questions): silhouette, signature identifiers, palette
   meaning, what makes it legible in a still. Produce a short spec.
2. **Draft the sheet prompt** as a single-pass multi-view character sheet applying the
   consistency rules above (lean on `draft-asset-prompts` for tool/T2I phrasing and
   content-policy behavior). **Save it to `<name>.txt` in the member's folder — this
   is what every future revision starts from.**
3. **Generate** — run the project's image-generation command for cast.
   - **Ask how many variants** before spending; **default 1**. On a first-ever run of
     a prompt, prefer 1 regardless: if it trips a content filter or comes back
     malformed, three identical failures teach nothing that one does.
   - **Dry-run first, always.** Show what will be generated and the estimated cost,
     and wait for an explicit go-ahead. Never spend on an assumption.
   - **Every output must be traceable** to the exact prompt that produced it — store
     the prompt verbatim, not just the file it came from, since prompt files are
     edited between rounds. Round-number the outputs so a later round cannot
     overwrite an earlier one's variants; comparing them is the point.
4. **Review before locking** — present the sheet; if the project uses Issue gates and
   you want mobile review, post it to an Issue (same mechanism as short gates).
   Approve → lock; reject → revise (below).
   - **Show the currently locked images alongside the candidates.** A reviewer cannot
     tell an intended change from drift without seeing the canon being matched.
   - Feedback given in conversation must be **relayed into the review thread
     verbatim**, or the thread becomes an incomplete record and a later session sees
     a change with no stated reason. Keep reviewer wording and your own analysis
     clearly distinguished — never let reasoning read as something that was asked for.
5. **Lock** — save the approved image(s) into the library folder (e.g.
   `branding/cast/archetypes/<name>/<name>.png` + per-view files), keep `<name>.txt`
   beside them, and register the `REFS:` name per the project's convention. If it's a
   mascot counterpart or must-echo character, note it in the style guide.

## Revise an existing member (keep this easy)
1. **Locate by name** → the member's folder + its saved `<name>.txt`. Start from the
   saved prompt, never from scratch.
2. **Scope the change** — one view (fix the back) or design-wide (bigger crown
   everywhere)? **Regenerate only what changed:**
   - one view → regenerate just that view, matched to the locked others;
   - design-wide → re-run the single-pass sheet with the edited prompt.
   **Vague feedback ("the horns look wrong") never goes straight to a regeneration.**
   Translate it into a concrete prompt diff and get that approved first — otherwise
   you are spending money on your interpretation of what was meant.
   Before blaming wording, consider whether the trait is even *resolvable* at the
   size it is being judged: fine material detail can fail to render on a multi-pose
   sheet while being perfectly well specified. Test at full frame before rewriting.
3. **Edit `<name>.txt`**, regenerate, review (as above).
4. **Re-lock** — replace the image(s) and append a short `NOTE (history):` line to
   `<name>.txt` (what changed and why) so iterations are traceable and the next
   session doesn't mistake drift for a decision. Preserve the prior version if it
   might be wanted.
   **Keep the decision log in the repo, not only in the review thread.** A thread
   on a hosting service is not in a fresh clone; feedback and selections belong
   beside the prompt they changed, so `git log` on the member's folder tells the
   whole story. If the review tool has a "current canon" panel, refresh it on every
   lock — a stale panel silently invites judging candidates against the wrong thing.
5. **Propagate** — if the change breaks a mascot counterpart's resemblance or a
   style-guide rule, flag it before locking.

## Output
- Locked image(s) in the cast library + the saved `<name>.txt` prompt beside them.
- The `REFS:` name registered so shots can pull it.
- No pipeline-dashboard updates — cast members are library assets, not tracked items.
