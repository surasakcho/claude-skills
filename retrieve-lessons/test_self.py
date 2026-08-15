#!/usr/bin/env python
"""Self-test: prove retrieve.py detects, discriminates, and can FAIL.

The interesting property is not that it finds categories -- it is that it does NOT find the
ones with no evidence. A detector that selects everything is the same as no detector.

    python -X utf8 test_self.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SCRIPT = HERE / "retrieve.py"


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          encoding="utf-8", errors="replace")


def build_shared(root: Path):
    """A miniature of the shared repo, as a real git repo so --shared can be pinned."""
    for cat in ("analytics", "testing", "coding", "research", "data-engineering",
                "agent-workflow"):
        d = root / "rules" / cat
        d.mkdir(parents=True)
        (d / f"{cat}-rule.md").write_text(f"# {cat}\n\n## The incident\n\nCost: real.\n",
                                          encoding="utf-8")
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@t.t")
    git(root, "config", "user.name", "t")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "seed")
    return root


def build_target(root: Path):
    """A repo that plots and tests, but does NO research and has NO data pipeline."""
    (root / "src").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "figures").mkdir(parents=True)
    (root / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    (root / "tests" / "test_app.py").write_text("def test_x(): assert True\n", encoding="utf-8")
    (root / "requirements.txt").write_text("matplotlib\npytest\n", encoding="utf-8")
    return root


def run(target, shared, *extra):
    r = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), "--repo", str(target),
                        "--shared", str(shared), *extra],
                       capture_output=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def main():
    failures = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        shared = build_shared(tmp / "shared")
        target = build_target(tmp / "target")

        code, out = run(target, shared, "--json")
        try:
            data = json.loads(out)
        except Exception:
            print(out[-800:])
            print("\nSELF-TEST FAILED: --json did not produce JSON")
            return 1
        sel = set(data["selected"])

        checks = {
            "selects analytics from matplotlib + figures/": "analytics" in sel,
            "selects testing from pytest + tests/": "testing" in sel,
            "selects coding from src/": "coding" in sel,
            "does NOT select research (no evidence)": "research" not in sel,
            "does NOT select data-engineering (no evidence)": "data-engineering" not in sel,
            "records a pin": bool(data["sha"]),
        }

        # --check must FAIL before anything is written.
        code, _ = run(target, shared, "--check")
        checks["--check fails when no block exists"] = code == 1

        code, _ = run(target, shared, "--write")
        cm = (target / "CLAUDE.md").read_text(encoding="utf-8")
        checks["--write creates the block"] = "shared-lessons:begin" in cm
        checks["links point at the shared repo"] = "rules/analytics/analytics-rule.md" in cm
        checks["does not link an unselected category"] = "rules/research/" not in cm

        code, _ = run(target, shared, "--check")
        checks["--check passes once pinned"] = code == 0

        # Idempotent: writing twice must not duplicate the block.
        run(target, shared, "--write")
        cm2 = (target / "CLAUDE.md").read_text(encoding="utf-8")
        checks["--write is idempotent"] = cm2.count("shared-lessons:begin") == 1

        # Move the shared repo on: the pin is now stale and --check must say so.
        (shared / "rules" / "coding" / "another.md").write_text(
            "# another\n\n## The incident\n\nCost: real.\n", encoding="utf-8")
        git(shared, "add", "-A")
        git(shared, "commit", "-q", "-m", "move on")
        code, out = run(target, shared, "--check")
        checks["--check detects a stale pin"] = code == 1 and "pinned at" in out

        # Preserves surrounding content.
        (target / "CLAUDE.md").write_text(
            "# My rules\n\nKeep me.\n\n" + cm2, encoding="utf-8")
        run(target, shared, "--write")
        cm3 = (target / "CLAUDE.md").read_text(encoding="utf-8")
        checks["--write preserves existing CLAUDE.md content"] = "Keep me." in cm3

        # A shared repo missing a category must be a hard error, not a silent skip.
        import shutil
        shutil.rmtree(shared / "rules" / "analytics")
        git(shared, "add", "-A")
        git(shared, "commit", "-q", "-m", "drop analytics")
        code, out = run(target, shared, "--write")
        checks["errors when the shared repo drops a category"] = (
            code != 0 and "no rules/analytics" in out)

        for label, ok in checks.items():
            print(f"  [{'ok' if ok else 'MISS'}] {label}")
            if not ok:
                failures.append(label)

    if failures:
        print("\nSELF-TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nself-test passed: detection discriminates, the pin catches drift, "
          "and a reorganised shared repo fails loudly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
