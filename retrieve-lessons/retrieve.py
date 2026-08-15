#!/usr/bin/env python
"""Pull the shared rules into a repo -- by reference, pinned, never by copy.

A copied rule drifts silently and nobody notices until it contradicts the source. This links
to the shared repo and records the commit it was read at, so drift becomes detectable instead
of invisible.

    python -X utf8 retrieve.py --repo DIR                      # detect + recommend
    python -X utf8 retrieve.py --repo DIR --write              # write the CLAUDE.md block
    python -X utf8 retrieve.py --repo DIR --check              # exit 1 if the pin is stale
    python -X utf8 retrieve.py --repo DIR --shared DIR --write # use an existing clone

Exit 1 when --check finds drift or a missing block, so it can gate a commit.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SHARED_URL = "https://github.com/surasakcho/agentic-ai-rules-and-skills.git"
SHARED_WEB = "https://github.com/surasakcho/agentic-ai-rules-and-skills/blob"
BEGIN = "<!-- shared-lessons:begin -->"
END = "<!-- shared-lessons:end -->"

# Each category is selected only on evidence. A rule nobody needs is noise, and noise is how
# a CLAUDE.md stops being read.
DETECTORS = {
    "analytics": {
        "why": "produces figures, tables or reported numbers",
        "deps": ("matplotlib", "seaborn", "plotly", "ggplot2", "altair", "bokeh", "d3"),
        "paths": ("figures", "figs", "plots", "charts", "reports"),
        "globs": ("**/*.ipynb",),
    },
    "data-engineering": {
        "why": "ingests or transforms data",
        "deps": ("pandas", "polars", "dbt", "pyarrow", "sqlalchemy", "duckdb", "geopandas"),
        "paths": ("data", "etl", "pipelines", "ingest", "warehouse"),
        "globs": ("**/*.csv", "**/*.parquet", "**/*.sql"),
    },
    "research": {
        "why": "carries research output that must stay reproducible",
        "deps": (),
        "paths": ("research", "papers", "literature", "notebooks"),
        "globs": ("**/*.bib", "**/Q-and-A.md", "**/LESSONS.md"),
    },
    "testing": {
        "why": "has a test suite whose checks must be able to fail",
        "deps": ("pytest", "vitest", "jest", "unittest", "rspec", "junit"),
        "paths": ("tests", "test", "spec", "__tests__"),
        "globs": ("**/test_*.py", "**/*.test.ts", "**/*.spec.ts"),
    },
    "coding": {
        "why": "contains source code that gets changed",
        "deps": (),
        "paths": ("src", "lib", "app", "scripts", "pkg"),
        "globs": ("**/*.py", "**/*.ts", "**/*.js", "**/*.go", "**/*.rs", "**/*.java"),
    },
    "agent-workflow": {
        "why": "is worked on by AI agents",
        "deps": (),
        "paths": (".claude", ".agents"),
        "globs": ("CLAUDE.md", "AGENTS.md", "GEMINI.md"),
    },
}
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next",
        "site-packages", ".mypy_cache", ".pytest_cache"}


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, encoding="utf-8",
                          errors="replace")


def ensure_shared(shared: Path, url: str, offline: bool) -> Path:
    """Clone or refresh the shared repo. A stale cache silently serving old rules is the
    failure this function exists to prevent, so a refresh failure is reported, not swallowed."""
    if shared.exists() and (shared / ".git").exists():
        if not offline:
            r = run("git", "-C", str(shared), "pull", "--ff-only", "--quiet")
            if r.returncode != 0:
                print(f"  WARNING: could not refresh the shared repo, using the cached copy\n"
                      f"           {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''}")
        return shared
    if offline:
        raise SystemExit(f"ERROR: no shared repo at {shared} and --offline was given")
    shared.parent.mkdir(parents=True, exist_ok=True)
    print(f"  cloning {url}")
    r = run("git", "clone", "--quiet", url, str(shared))
    if r.returncode != 0:
        raise SystemExit(f"ERROR: clone failed: {r.stderr.strip()}")
    return shared


def dep_text(repo: Path) -> str:
    """Everything a dependency could be declared in, concatenated and lowercased."""
    names = ("requirements.txt", "pyproject.toml", "setup.py", "environment.yml",
             "package.json", "Gemfile", "go.mod", "Cargo.toml", "DESCRIPTION")
    out = []
    for n in names:
        p = repo / n
        if p.exists():
            out.append(p.read_text(encoding="utf-8", errors="replace").lower())
    return "\n".join(out)


def detect(repo: Path):
    """Return {category: [evidence, ...]} -- only categories with actual evidence."""
    deps = dep_text(repo)
    dirs = {p.name.lower() for p in repo.rglob("*")
            if p.is_dir() and not any(s in p.parts for s in SKIP)}
    found = {}
    for cat, spec in DETECTORS.items():
        evidence = []
        for d in spec["deps"]:
            if re.search(rf"\b{re.escape(d)}\b", deps):
                evidence.append(f"dependency '{d}'")
        for d in spec["paths"]:
            if d.lower() in dirs:
                evidence.append(f"{d}/ directory")
        for g in spec["globs"]:
            hit = next((p for p in repo.glob(g)
                        if not any(s in p.parts for s in SKIP)), None)
            if hit:
                evidence.append(f"{hit.relative_to(repo).as_posix()}")
        if evidence:
            found[cat] = evidence[:3]
    return found


def rules_for(shared: Path, cats):
    """Every rule file under each selected category. Missing category = hard error: it means
    the shared repo moved and this skill is pointing at nothing."""
    out = {}
    for cat in cats:
        d = shared / "rules" / cat
        if not d.exists():
            raise SystemExit(f"ERROR: shared repo has no rules/{cat} -- it has been "
                             f"reorganised and this skill is out of date")
        out[cat] = sorted(p.name for p in d.glob("*.md"))
    return out


def build_block(shared: Path, sha: str, selected, rules):
    lines = [BEGIN,
             "",
             "## Shared working rules",
             "",
             f"Adopted from [agentic-ai-rules-and-skills]({SHARED_WEB.rsplit('/blob', 1)[0]}) "
             f"at `{sha}`. **Linked, not copied** — a copied rule drifts out of agreement with "
             f"its source and nobody notices. Refresh with `/retrieve-lessons`.",
             ""]
    for cat in sorted(rules):
        lines.append(f"**{cat}** — selected because this repo {DETECTORS[cat]['why']} "
                     f"({', '.join(selected[cat])}).")
        lines.append("")
        for name in rules[cat]:
            title = name[:-3].replace("-", " ")
            lines.append(f"- [{title}]({SHARED_WEB}/{sha}/rules/{cat}/{name})")
        lines.append("")
    lines += ["*The pin is the point: if the shared repo has moved on, "
              "`retrieve.py --check` fails and you re-read what changed.*", "", END]
    return "\n".join(lines)


def read_pin(text: str):
    m = re.search(re.escape(BEGIN) + r".*?at `([0-9a-f]{6,40})`", text, re.S)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="the repo adopting the rules")
    ap.add_argument("--shared", help="path to an existing clone (default: a local cache)")
    ap.add_argument("--url", default=SHARED_URL)
    ap.add_argument("--write", action="store_true", help="write the block into CLAUDE.md")
    ap.add_argument("--check", action="store_true", help="exit 1 if the pin is stale/missing")
    ap.add_argument("--offline", action="store_true", help="never touch the network")
    ap.add_argument("--json", action="store_true", help="machine-readable detection output")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"ERROR: no such repo: {repo}")
    shared = Path(args.shared).resolve() if args.shared else \
        Path.home() / ".claude" / "cache" / "agentic-ai-rules-and-skills"
    shared = ensure_shared(shared, args.url, args.offline or bool(args.shared))
    sha = run("git", "-C", str(shared), "rev-parse", "--short", "HEAD").stdout.strip() or "HEAD"

    selected = detect(repo)
    if not selected:
        print("No category matched. Nothing is adopted -- that is a valid outcome, not a bug.")
        return 0
    rules = rules_for(shared, selected)

    if args.json:
        print(json.dumps({"sha": sha, "selected": selected, "rules": rules}, indent=2))
        return 0

    print(f"\nshared repo at {sha}\n")
    for cat in sorted(selected):
        print(f"  {cat:18} {', '.join(selected[cat])}")
        for name in rules[cat]:
            print(f"      - {name}")

    cm = repo / "CLAUDE.md"
    existing = cm.read_text(encoding="utf-8", errors="replace") if cm.exists() else ""
    pin = read_pin(existing)

    if args.check:
        if BEGIN not in existing:
            print(f"\nPROBLEM: no shared-lessons block in {cm.name}. Run --write.")
            return 1
        if pin != sha:
            print(f"\nPROBLEM: pinned at {pin}, shared repo is at {sha}. "
                  f"Re-read what changed, then --write.")
            return 1
        print(f"\nPin is current ({sha}).")
        return 0

    block = build_block(shared, sha, selected, rules)
    if not args.write:
        print(f"\n--- would write into {cm.name} (pass --write) ---\n")
        print(block)
        return 0

    if BEGIN in existing and END in existing:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), block, existing, flags=re.S)
        action = f"refreshed (was {pin})"
    else:
        new = (existing.rstrip() + "\n\n" + block + "\n") if existing else block + "\n"
        action = "added"
    cm.write_text(new, encoding="utf-8")
    print(f"\n{action} the shared-lessons block in {cm} -- pinned at {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
