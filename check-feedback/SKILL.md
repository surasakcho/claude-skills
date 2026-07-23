---
name: check-feedback
description: Check the CURRENT repo's GitHub issues for feedback the owner left, then act on it by following that repo's own feedback pipeline. Use when the user tells the repo's CEO/manager to "check the issues", "check for feedback", or see whether the owner replied on any issue — or when a CEO/manager session should look for owner feedback and process it per the repo's pipeline.
---

Go see whether the owner left feedback on this repo's GitHub issues, then handle it by following **this repo's own feedback pipeline**. This skill only points you at the issues and at the pipeline — it deliberately does not define the pipeline. The repo does.

Operate on the **current repo only**. One invocation = one repo.

## 1. Confirm context

Confirm the current directory is a git repo with a GitHub remote and `gh` is authenticated:

```
gh repo view --json nameWithOwner -q .nameWithOwner
```

If this fails (not a repo, no GitHub remote, or `gh` not authed), say so and stop — there are no issues to check.

## 2. Find this repo's feedback pipeline — it is authoritative

The process for interpreting and acting on feedback lives in the repo, not here. Locate it before touching any issue:

- Read this repo's `CLAUDE.md` first — the pipeline (or a pointer to it) is usually there.
- If it points to a dedicated doc (e.g. a `pipeline.md`, `feedback.md`, or a file under `docs/`), read that too.

If you cannot find any documented feedback pipeline, **stop and ask the owner where it's defined** rather than inventing one. Everything below follows that doc, not this skill.

## 3. Check the issues

List the open issues and read the ones that may carry owner feedback, including their comment threads:

```
gh issue list --state open
gh issue view <number> --comments
```

Don't pre-filter with assumptions about labels or markers — surface what the owner actually wrote and let the repo's pipeline decide what counts as actionable feedback.

## 4. Act per the repo's pipeline

For each issue where the owner left feedback, do exactly what this repo's pipeline prescribes — respond, relabel, move a stage, open the next piece of work, close it, whatever the pipeline defines. This skill intentionally does not spell out those steps; the repo's doc from step 2 does.

## 5. Report back

One short summary: which issues had owner feedback, what you did with each per the pipeline, and anything now waiting back on the owner.
