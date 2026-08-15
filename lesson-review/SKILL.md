---
name: lesson-review
description: Run the weekly lesson-harvest pass — sweep project repos for lessons, rules, defect write-ups and repo-agnostic checkers that are stranded in one project, filter for the portable ones, mechanise what can run, verify the existing shared rules still hold, and publish to the shared agentic-ai-rules-and-skills repo. Use when the user asks to review/harvest/share lessons, when a week has passed since the last pass, at the end of a project phase or remediation, or when a task produced a defect write-up or a reusable checker worth sharing.
license: MIT
---

# Lesson Review

The weekly pass that keeps the shared rules repo alive. Full policy in that repo's
`CADENCE.md`; this is how to execute it.

**Shared repo:** `https://github.com/surasakcho/agentic-ai-rules-and-skills`
**Local clone (this machine):** `<your-home>/Repos/agentic-ai-rules-and-skills`

Run `harvest.py` for the mechanical parts, then apply judgement to what it surfaces. The
script finds candidates and checks health; it deliberately does **not** decide what is
portable — that is the part that needs a reader.

```bash
python -X utf8 harvest.py --projects <your-home>/Repos --shared <your-home>/Repos/agentic-ai-rules-and-skills
```

## The pass, in order

**1. Harvest.** The script lists candidates changed since the last pass: `LESSONS.md`,
`DEFECTS.md`, `Q-and-A.md`, `research/*.md`, new numbered rules in project `CLAUDE.md`
files, and scripts that look repo-agnostic (no hardcoded project paths, a CLI, a
`__main__`). Read them. Most stay where they are.

**2. Filter — the hard part, and it is yours.** A lesson belongs in the shared repo only if
it is true outside the project that produced it:

- Would it hold with different data, a different domain, a different language?
- Does it name a **real incident with a cost**? Advice without a scar is opinion.
- Is it already covered? Then **strengthen the existing rule** rather than adding a second
  one that will drift out of agreement with it.

**3. Mechanise what can fail.** `prose < checklist < test < gate`. Before writing a rule as
text, ask whether it can be a check that runs. If it can, it goes to `skills/` as code with
a self-test. Roughly half of what gets harvested can be; be honest about the other half
rather than writing a crude proxy and calling it enforcement.

**4. Verify what is already shared.** `harvest.py --check` runs the health pass: every skill's
self-test executes, every internal link resolves, and every rule is checked for an incident
reference. **A rule later contradicted by experience gets deleted, not hedged** — git keeps
the history, and a hedged rule is one nobody can act on.

**5. Publish.** Commit, push, and append one line to `lessons/_review-log.md` with the date
and what was harvested.

## Recording an empty pass

**A pass that harvests nothing is a valid outcome** and must still be logged. Three empty
passes in a row is a signal worth reading: either the projects are genuinely quiet, or
lessons are not being written down anywhere the sweep can find them — which is a different
and more serious problem.

## What good looks like

A harvested rule reads like this, not like a style guide:

> **The conditional that never fires.** A colour map was registered under
> `if "flag" not in colormaps:` — but `flag` is a library builtin, so the branch never ran
> and 30 figures silently drew inverted. Cost: 30 wrong figures, invisible in code review.
> **Guard:** if you write `if X: do_important_thing`, prove X is ever true.

Mechanism, incident, cost, guard. If you cannot write the cost, you probably do not have a
lesson yet — you have a preference.
