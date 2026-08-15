---
name: retrieve-lessons
description: Adopt the shared working rules from the agentic-ai-rules-and-skills repo into a repo that does not have them yet — detect what kind of work the repo actually does, select only the rule categories with evidence behind them, and link them from its CLAUDE.md pinned to a commit so drift is detectable. Use when starting work in a new or unfamiliar repo, when a repo's CLAUDE.md has no shared-rules section, when asked to "retrieve/adopt/apply the shared lessons or rules", or to re-check whether an adopted pin has gone stale.
license: MIT
---

# Retrieve Lessons

The consuming half of the cycle. [`lesson-review`](../lesson-review/SKILL.md) publishes what a
project learned; this pulls it into the next repo so the lesson is paid for once.

**Shared repo:** `https://github.com/surasakcho/agentic-ai-rules-and-skills`

```bash
python -X utf8 retrieve.py --repo <target-repo>            # detect + show what it would adopt
python -X utf8 retrieve.py --repo <target-repo> --write    # write the block into CLAUDE.md
python -X utf8 retrieve.py --repo <target-repo> --check     # exit 1 if the pin is stale
```

Paths are arguments, never literals — a machine path in a shared skill publishes a username
and a directory layout.

## The two decisions this encodes

**Link, don't copy.** A copied rule drifts out of agreement with its source and nobody
notices, because a copy looks exactly as authoritative as the original. The block written into
`CLAUDE.md` contains links, not text.

**Pin the commit.** A bare link silently becomes a link to something else. The block records
the shared repo's commit, so `--check` can tell you the rules moved and you can go read *what*
changed. An unpinned reference cannot distinguish "still true" from "nobody looked".

## Select on evidence, never adopt wholesale

`retrieve.py` matches each rule category against real signals — declared dependencies,
directory names, file globs — and adopts only the categories that hit. A repo with no `tests/`
and no test runner does not get the testing rule.

This restraint is the whole point. A `CLAUDE.md` carrying nine rules where two apply teaches
the reader that most of it is skippable, and then the two that mattered get skipped too.
**Adopting nothing is a valid outcome** and the script says so rather than inventing a match.

## The pass, in order

1. **Run it without `--write`** and read what it proposes. The evidence for each category is
   printed next to it — if the evidence looks wrong, the detection is wrong, and adopting on
   top of a bad match is worse than not adopting.
2. **Read the rules it selected.** They are short and each names a real incident. This is the
   step that cannot be automated and the one that makes the adoption real; a linked rule
   nobody has read is a citation, not a practice.
3. **`--write`.** Idempotent — re-running refreshes the block in place and preserves
   everything else in `CLAUDE.md`.
4. **Install the skills the rules mechanise,** where they apply: `verify-outputs` for any repo
   that produces figures, tables or reported numbers. `prose < checklist < test < gate` — a
   rule that can run should be running.
5. **Re-check periodically.** `--check` in a pre-commit hook turns a stale pin into a failing
   commit instead of a rule nobody re-read.

## When the shared repo has moved

`--check` failing is not noise — it means a rule you are relying on may have changed or been
deleted. **A rule contradicted by later experience gets deleted, not hedged**, so a moved pin
can mean something you are currently doing is now known to be wrong. Read the diff, then
`--write` to re-pin.

If the shared repo has been reorganised such that a selected category no longer exists, the
script **errors out** rather than quietly adopting fewer rules. A silent skip is how a repo
ends up believing it has coverage it does not have.
