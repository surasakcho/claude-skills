#!/usr/bin/env python
"""Mechanical half of the weekly lesson-review pass.

Finds candidates and checks health. Deliberately does NOT judge what is portable -- that
needs a reader, and a script that guessed would either miss the good ones or flood you with
the rest.

    python -X utf8 harvest.py --projects DIR --shared DIR      # harvest candidates
    python -X utf8 harvest.py --shared DIR --check             # health-check the shared repo
    python -X utf8 harvest.py --shared DIR --check --deny acme-internal,jsmith
    python -X utf8 harvest.py --projects DIR --shared DIR --since 2026-08-01

Exit 1 if the health check finds problems, so it can gate a commit.
"""
import argparse
import io
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Files that carry lessons rather than pipeline state.
LESSON_FILES = ("LESSONS.md", "DEFECTS.md", "Q-and-A.md", "POSTMORTEM.md", "RETRO.md")
LESSON_GLOBS = ("research/*.md", "docs/lessons/*.md")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "site-packages",
             ".claude", "dist", "build", ".next"}

# Text the shared repo is scanned for before publishing. A `<placeholder>` segment is how you
# write a path in shared docs, so it is deliberately not a hit.
LEAK_PATTERNS = [
    (r"[A-Za-z]:[\\/]Users[\\/](?!<)[^\s'\"`)\]]+", "machine path (publishes a username)"),
    (r"/(?:home|Users)/(?!<)[A-Za-z0-9._-]+/[^\s'\"`)\]]*", "machine path (publishes a username)"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "email address"),
]
SCAN_SUFFIXES = {".md", ".py", ".sh", ".txt", ".json", ".yml", ".yaml", ".toml"}
# A self-test that seeds fake leaks must contain fake leaks. Exempt it explicitly, by marker,
# and report the count -- an exemption nobody can see is a hole, not an exemption.
# Assembled from two pieces so this file does not exempt ITSELF by merely defining the marker.
LEAK_EXEMPT_MARKER = "leak-scan" + ": fixtures"

problems = []


def log_problem(msg):
    problems.append(msg)


def repos_under(root: Path):
    """Every git working tree directly under `root`."""
    for p in sorted(root.iterdir()):
        if p.is_dir() and (p / ".git").exists():
            yield p


def changed_since(repo: Path, since: str):
    """Paths changed in `repo` since a date, via git. Empty list if git is unavailable."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", f"--since={since}", "--name-only",
             "--pretty=format:"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        return {l.strip() for l in out.stdout.splitlines() if l.strip()}
    except Exception:
        return set()


def looks_portable(script: Path) -> tuple[bool, str]:
    """A script is a candidate if it could plausibly run outside its own repo."""
    try:
        src = script.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False, ""
    if "__main__" not in src:
        return False, ""
    has_cli = "argparse" in src or "sys.argv" in src
    # Hardcoded absolute paths, or a project-root walk, mean it is wired to one repo.
    hardcoded = bool(re.search(r'["\']([A-Za-z]:[\\/]|/(home|Users|mnt)/)', src))
    parent_walk = "Path(__file__).parent.parent" in src
    if has_cli and not hardcoded and not parent_walk:
        return True, "has a CLI, no hardcoded paths"
    return False, ""


def harvest(projects: Path, since: str):
    print("=" * 76)
    print(f"HARVEST  — candidates changed since {since}")
    print("=" * 76)
    found = 0
    for repo in repos_under(projects):
        touched = changed_since(repo, since)
        hits, scripts = [], []
        for name in LESSON_FILES:
            for p in repo.rglob(name):
                if any(s in p.parts for s in SKIP_DIRS):
                    continue
                rel = p.relative_to(repo).as_posix()
                hits.append((rel, rel in touched))
        for pat in LESSON_GLOBS:
            for p in repo.glob(f"**/{pat}"):
                if any(s in p.parts for s in SKIP_DIRS):
                    continue
                rel = p.relative_to(repo).as_posix()
                hits.append((rel, rel in touched))
        for p in repo.rglob("*.py"):
            if any(s in p.parts for s in SKIP_DIRS):
                continue
            ok, why = looks_portable(p)
            if ok:
                rel = p.relative_to(repo).as_posix()
                scripts.append((rel, why, rel in touched))

        # New numbered rules in a project CLAUDE.md
        rules = []
        cm = repo / "CLAUDE.md"
        if cm.exists():
            txt = cm.read_text(encoding="utf-8", errors="replace")
            rules = re.findall(r"^#{2,4}\s*(\d+)\.\s*(.+)$", txt, re.M)

        if not (hits or scripts or rules):
            continue
        found += 1
        print(f"\n{repo.name}")
        for rel, recent in sorted(set(hits)):
            print(f"   {'*' if recent else ' '} lesson doc   {rel}")
        for rel, why, recent in sorted(set(scripts)):
            print(f"   {'*' if recent else ' '} portable?    {rel}   ({why})")
        if rules:
            print(f"     {len(rules)} numbered rule(s) in CLAUDE.md: "
                  f"{', '.join(n for n, _ in rules[:12])}"
                  f"{' ...' if len(rules) > 12 else ''}")
    print(f"\n{found} repo(s) with candidates.  '*' = changed since {since}.")
    print("\nNow READ them and decide what is portable. The test is whether the lesson")
    print("holds with different data, a different domain, a different language -- and")
    print("whether it names a real incident with a cost.")


def scan_leaks(shared: Path, deny: list):
    """What must not leave a private context: people, places, paths.

    The fourth category -- findings -- is not here on purpose. Only a reader can tell whether
    a number is a defect count or somebody's unpublished result.
    """
    hits = 0
    exempt = []
    files = [p for p in shared.rglob("*")
             if p.is_file() and p.suffix.lower() in SCAN_SUFFIXES
             and not any(s in p.parts for s in SKIP_DIRS)]
    for p in files:
        txt = p.read_text(encoding="utf-8", errors="replace")
        rel = p.relative_to(shared).as_posix()
        if LEAK_EXEMPT_MARKER in txt:
            exempt.append(rel)
            continue
        for pattern, label in LEAK_PATTERNS:
            for m in re.findall(pattern, txt):
                log_problem(f"{label} in {rel}: {m}")
                hits += 1
        for term in deny:
            if term and term.lower() in txt.lower():
                log_problem(f"denylisted term '{term}' in {rel}")
                hits += 1
    print(f"  scanned {len(files) - len(exempt)} file(s) for leaks; hits: {hits}")
    for rel in exempt:
        print(f"    exempt (declared fixtures): {rel}")
    if not deny:
        print("    (no --deny terms given: private repo names and collaborator names "
              "are not being checked)")


def health(shared: Path, deny=()):
    print("\n" + "=" * 76)
    print("HEALTH CHECK — the shared repo")
    print("=" * 76)
    if not shared.exists():
        log_problem(f"shared repo not found at {shared}")
        print(f"  MISSING: {shared}")
        return

    md = [p for p in shared.rglob("*.md") if ".git" not in p.parts]
    print(f"  {len(md)} markdown file(s)")

    scan_leaks(shared, list(deny))

    # Internal links must resolve -- and must resolve INSIDE the repo. A link that walks out
    # of the root can pass an existence check by hitting a file on the author's machine, which
    # is both a broken link for every other reader and a disclosure of the local layout.
    root = shared.resolve()
    broken = escaped = 0
    for p in md:
        txt = p.read_text(encoding="utf-8", errors="replace")
        for target in re.findall(r"\]\(([^)#:]+?)(?:#[^)]*)?\)", txt):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            dest = (p.parent / target).resolve()
            if not dest.exists():
                log_problem(f"broken link in {p.relative_to(shared)}: {target}")
                broken += 1
            elif root not in dest.parents and dest != root:
                log_problem(f"link escapes the repo in {p.relative_to(shared)}: {target}")
                escaped += 1
    print(f"  broken internal links: {broken}; links escaping the repo: {escaped}")

    # Every rule should name an incident. A rule without a scar is an opinion.
    rules = [p for p in (shared / "rules").rglob("*.md")] if (shared / "rules").exists() else []
    no_incident = [p.relative_to(shared).as_posix() for p in rules
                   if not re.search(r"(?i)incident|cost|what happened|earned from",
                                    p.read_text(encoding="utf-8", errors="replace"))]
    print(f"  rules: {len(rules)}; without a named incident: {len(no_incident)}")
    for r in no_incident:
        log_problem(f"rule names no incident: {r}")

    # Every skill must carry a self-test and it must pass.
    skills = [d for d in (shared / "skills").iterdir()
              if d.is_dir()] if (shared / "skills").exists() else []
    print(f"  skills: {len(skills)}")
    for s in skills:
        if not (s / "SKILL.md").exists():
            log_problem(f"skill has no SKILL.md: {s.name}")
            continue
        tests = list(s.glob("*self_test*.py")) + list(s.glob("test_*.py"))
        if not tests:
            log_problem(f"skill has no self-test: {s.name} "
                        f"(a check you have never seen fail is untested)")
            continue
        for t in tests:
            r = subprocess.run([sys.executable, "-X", "utf8", str(t)],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=300)
            # Exit 2 means the test could not run at all (missing dependencies). That is
            # still a problem -- a self-test that never executes is not a green check --
            # but it is a different problem from a checker that behaved wrongly.
            state = {0: "PASS", 2: "CANNOT RUN"}.get(r.returncode, "FAIL")
            print(f"    self-test {s.name}/{t.name}: {state}")
            if r.returncode == 2:
                log_problem(f"self-test could not run: {s.name}/{t.name} — "
                            f"{r.stdout.strip().splitlines()[0] if r.stdout.strip() else 'no output'}")
            elif r.returncode != 0:
                log_problem(f"self-test failed: {s.name}/{t.name}\n{r.stdout[-800:]}")

    # Shared library code carries self-tests too. Without this the lib tests exist but never
    # run in the gate, which is the same as not having them.
    lib = shared / "lib"
    if lib.exists():
        for t in sorted(list(lib.glob("test_*.py")) + list(lib.glob("*self_test*.py"))):
            r = subprocess.run([sys.executable, "-X", "utf8", str(t)],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=300)
            state = {0: "PASS", 2: "CANNOT RUN"}.get(r.returncode, "FAIL")
            print(f"    self-test lib/{t.name}: {state}")
            if r.returncode != 0:
                log_problem(f"lib self-test {'could not run' if r.returncode == 2 else 'failed'}"
                            f": lib/{t.name}\n{r.stdout[-800:]}")

    # Review cadence.
    logp = shared / "lessons" / "_review-log.md"
    if not logp.exists():
        log_problem("no lessons/_review-log.md — the cadence is not being recorded")
    else:
        dates = re.findall(r"(\d{4}-\d{2}-\d{2})",
                           logp.read_text(encoding="utf-8", errors="replace"))
        if dates:
            last = max(datetime.strptime(d, "%Y-%m-%d") for d in dates)
            age = (datetime.now() - last).days
            print(f"  last recorded pass: {last:%Y-%m-%d} ({age} days ago)")
            if age > 7:
                log_problem(f"last review pass was {age} days ago; the cadence is weekly")
        else:
            log_problem("_review-log.md has no dated entries")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projects", help="directory containing project repos")
    ap.add_argument("--shared", required=True, help="the shared rules repo")
    ap.add_argument("--since", default=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
    ap.add_argument("--check", action="store_true", help="health check only")
    ap.add_argument("--deny", default="",
                    help="comma-separated terms that must not appear in the shared repo "
                         "(private repo names, collaborator names, internal hostnames)")
    args = ap.parse_args()

    if args.projects and not args.check:
        harvest(Path(args.projects), args.since)
    health(Path(args.shared), [t.strip() for t in args.deny.split(",") if t.strip()])

    print("\n" + "=" * 76)
    if problems:
        print(f"PROBLEMS: {len(problems)}")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("Shared repo is healthy.")
    print("Remember: log this pass in lessons/_review-log.md, even if it harvested nothing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
