#!/usr/bin/env python
"""Self-test: prove harvest.py's health check can FAIL.

Builds a deliberately unhealthy shared repo (broken link, rule with no incident, skill with
no self-test, missing review log) and asserts each is caught; then builds a healthy one and
asserts it passes.

    python -X utf8 test_self.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
HARVEST = HERE / "harvest.py"


def build_bad(root: Path):
    (root / "rules" / "coding").mkdir(parents=True)
    (root / "skills" / "orphan").mkdir(parents=True)
    (root / "lessons").mkdir(parents=True)
    # A rule that names no incident, and links to a file that does not exist.
    (root / "rules" / "coding" / "vague.md").write_text(
        "# Be careful\n\nAlways write good code. See [the guide](missing-guide.md).\n",
        encoding="utf-8")
    # A skill with a SKILL.md but no self-test.
    (root / "skills" / "orphan" / "SKILL.md").write_text(
        "---\nname: orphan\ndescription: no self-test\n---\n\n# Orphan\n", encoding="utf-8")
    # No lessons/_review-log.md at all.


def build_good(root: Path):
    (root / "rules" / "coding").mkdir(parents=True)
    (root / "skills" / "solid").mkdir(parents=True)
    (root / "lessons").mkdir(parents=True)
    (root / "rules" / "coding" / "real.md").write_text(
        "# A real rule\n\n## The incident\n\nA guard never fired; cost 30 wrong figures.\n",
        encoding="utf-8")
    (root / "skills" / "solid" / "SKILL.md").write_text(
        "---\nname: solid\ndescription: has a self-test\n---\n\n# Solid\n", encoding="utf-8")
    (root / "skills" / "solid" / "test_self.py").write_text(
        "print('ok')\n", encoding="utf-8")
    from datetime import datetime
    (root / "lessons" / "_review-log.md").write_text(
        f"# Review log\n\n## {datetime.now():%Y-%m-%d} · pass\n\nNothing harvested.\n",
        encoding="utf-8")


def run(shared: Path):
    r = subprocess.run([sys.executable, "-X", "utf8", str(HARVEST),
                        "--shared", str(shared), "--check"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def main():
    failures = []
    with tempfile.TemporaryDirectory() as td:
        bad = Path(td) / "bad"; bad.mkdir(); build_bad(bad)
        code, out = run(bad)
        checks = {
            "exits non-zero on an unhealthy repo": code != 0,
            "detects a broken internal link": "broken link" in out,
            "detects a rule with no incident": "names no incident" in out,
            "detects a skill with no self-test": "no self-test" in out,
            "detects a missing review log": "_review-log" in out,
        }
        good = Path(td) / "good"; good.mkdir(); build_good(good)
        code_ok, out_ok = run(good)
        checks["exits zero on a healthy repo"] = code_ok == 0

        for label, ok in checks.items():
            print(f"  [{'ok' if ok else 'MISS'}] {label}")
            if not ok:
                failures.append(label)
        if not checks["exits zero on a healthy repo"]:
            print(out_ok[-700:])

    if failures:
        print("\nSELF-TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nself-test passed: the health check catches every seeded problem, "
          "and clears a healthy repo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
