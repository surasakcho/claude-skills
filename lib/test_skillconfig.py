#!/usr/bin/env python
"""Self-test: prove skillconfig.py stores safely and FAILS when it cannot.

The properties that matter are the refusals, not the happy path: it must never invent a
default, never write a real value into the committed example, and never store into a repo
where .env is already tracked.

    python -X utf8 test_skillconfig.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SC = HERE / "skillconfig.py"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          encoding="utf-8", errors="replace")


def run(repo, *args, stdin=""):
    return subprocess.run([sys.executable, "-X", "utf8", str(SC), "--repo", str(repo), *args],
                          input=stdin, capture_output=True, encoding="utf-8", errors="replace")


def run_after(repo, *args, stdin=""):
    """--repo AFTER the subcommand -- the order the docs show, and the one that was broken."""
    return subprocess.run([sys.executable, "-X", "utf8", str(SC), *args, "--repo", str(repo)],
                          input=stdin, capture_output=True, encoding="utf-8", errors="replace")


def new_repo(root: Path, name: str) -> Path:
    r = root / name
    r.mkdir(parents=True)
    git(r, "init", "-q", "-b", "main")
    git(r, "config", "user.email", "t@t.t")
    git(r, "config", "user.name", "t")
    return r


def main():
    checks = {}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # --- first use: prompts, stores, echoes only the value on stdout ---
        repo = new_repo(tmp, "a")
        r = run(repo, "get", "SBX_REPO", "--prompt", "Sandbox root", stdin="/srv/sandbox\n")
        checks["first use stores the answer"] = r.returncode == 0
        checks["value goes to stdout, prompt does not"] = (
            r.stdout.strip() == "/srv/sandbox" and "Sandbox root" in r.stderr)
        env = (repo / ".env").read_text(encoding="utf-8")
        checks["writes the value into .env"] = "SBX_REPO=/srv/sandbox" in env

        # --- .env must be gitignored, and must NOT be committable ---
        gi = (repo / ".gitignore").read_text(encoding="utf-8")
        checks[".env added to .gitignore"] = any(
            l.strip() == ".env" for l in gi.splitlines())
        git(repo, "add", "-A")
        tracked = git(repo, "ls-files").stdout.split()
        checks["git add -A does not stage .env"] = ".env" not in tracked

        # --- the committed example records the KEY but never the VALUE ---
        ex = (repo / ".env.example").read_text(encoding="utf-8")
        checks[".env.example records the key"] = "SBX_REPO=" in ex
        checks[".env.example does NOT contain the real value"] = "/srv/sandbox" not in ex

        # --- second use: reads back, never prompts (stdin is empty and it must not fail) ---
        r = run(repo, "get", "SBX_REPO", "--prompt", "Sandbox root", stdin="")
        checks["second use returns the stored value without asking"] = (
            r.returncode == 0 and r.stdout.strip() == "/srv/sandbox"
            and "Sandbox root" not in r.stderr)

        # --- nobody to ask: must fail loudly, never invent a default ---
        repo2 = new_repo(tmp, "b")
        r = run(repo2, "get", "MACHINE_NAME", "--prompt", "Machine", stdin="")
        checks["EOF fails with exit 2 rather than guessing"] = r.returncode == 2
        checks["EOF explains how to set it"] = "skillconfig.py set" in r.stderr
        checks["EOF writes no .env"] = not (repo2 / ".env").exists()

        # --- an empty answer is not an answer ---
        r = run(repo2, "get", "MACHINE_NAME", "--prompt", "Machine", stdin="\n\n\n")
        checks["blank answers are rejected"] = r.returncode == 2
        checks["blank answer stores nothing"] = "MACHINE_NAME" not in (
            (repo2 / ".env").read_text(encoding="utf-8") if (repo2 / ".env").exists() else "")

        # --- refuse a repo where .env is already tracked ---
        repo3 = new_repo(tmp, "c")
        (repo3 / ".env").write_text("OLD=1\n", encoding="utf-8")
        git(repo3, "add", "-f", ".env")
        git(repo3, "commit", "-q", "-m", "oops")
        r = run(repo3, "set", "USERNAME", "someone")
        checks["refuses to write when .env is git-tracked"] = (
            r.returncode == 1 and "REFUSING" in r.stderr)
        checks["refusal names the fix"] = "rm --cached" in r.stderr
        r = run(repo3, "check")
        checks["check fails on a tracked .env"] = r.returncode == 1

        # --- check passes on a healthy repo ---
        r = run(repo, "check")
        checks["check passes on a safe repo"] = r.returncode == 0

        # --- check catches a real value leaking into the committed example ---
        (repo / ".env.example").write_text("SBX_REPO=/srv/sandbox\n", encoding="utf-8")
        r = run(repo, "check")
        checks["check catches a real value in .env.example"] = (
            r.returncode == 1 and "REAL value" in r.stderr)

        # --- values survive spaces and '=' ---
        repo4 = new_repo(tmp, "d")
        run(repo4, "set", "SCAN_ROOT", "C:/Program Files/My Repos")
        r = run(repo4, "get", "SCAN_ROOT", stdin="")
        checks["values with spaces round-trip"] = r.stdout.strip() == "C:/Program Files/My Repos"

        # --- the documented argument order must actually work ---
        # Every example in the docstring, the rule and the skills puts --repo AFTER the
        # subcommand. argparse rejected exactly that, and the suite never noticed because it
        # only ever called the other order. A usage nobody executes is a usage nobody verified.
        repo5 = new_repo(tmp, "e")
        r = run_after(repo5, "set", "MACHINE_NAME", "beta")
        checks["--repo works AFTER the subcommand (set)"] = r.returncode == 0
        r = run_after(repo5, "get", "MACHINE_NAME", stdin="")
        checks["--repo works AFTER the subcommand (get)"] = (
            r.returncode == 0 and r.stdout.strip() == "beta")
        r = run_after(repo5, "check")
        checks["--repo works AFTER the subcommand (check)"] = r.returncode == 0
        r = run_after(repo5, "list")
        checks["--repo works AFTER the subcommand (list)"] = "MACHINE_NAME=beta" in r.stdout
        # ...and the order before it must keep working.
        r = run(repo5, "get", "MACHINE_NAME", stdin="")
        checks["--repo still works BEFORE the subcommand"] = r.stdout.strip() == "beta"

    failures = [k for k, ok in checks.items() if not ok]
    for k, ok in checks.items():
        print(f"  [{'ok' if ok else 'MISS'}] {k}")
    if failures:
        print("\nSELF-TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nself-test passed: stores once, reads back, refuses to guess, and refuses to "
          "write where the value could be committed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
