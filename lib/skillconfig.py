#!/usr/bin/env python
"""Ask once, store locally, never hardcode.

Anything machine-specific -- a username, a hostname, a path to a repo or a sandbox -- must not
be a literal in a shared rule or skill. It gets prompted for on first use and stored in the
consuming repo's `.env`, which is gitignored. The shared artifact stays portable; the value
stays on the machine it describes.

The prompt goes to STDERR and only the value goes to STDOUT, so shell skills can do:

    SBX_REPO="$(python skillconfig.py get SBX_REPO --repo . --prompt 'Sandbox repo root')"

    python skillconfig.py get KEY --repo DIR --prompt TEXT [--example PLACEHOLDER]
    python skillconfig.py set KEY VALUE --repo DIR
    python skillconfig.py list --repo DIR
    python skillconfig.py check --repo DIR      # .env gitignored and untracked?

Exit codes: 0 ok, 1 unsafe/failed check, 2 value needed but nobody could be asked.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ENV = ".env"
EXAMPLE = ".env.example"
HEADER = ("# Machine-specific values, written by skillconfig.py. Never committed.\n"
          "# Keys and placeholders are in .env.example, which IS committed.\n")


def err(*a):
    print(*a, file=sys.stderr)


def read_env(repo: Path) -> dict:
    p = repo / ENV
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def write_env(repo: Path, values: dict):
    body = HEADER + "".join(f"{k}={v}\n" for k, v in sorted(values.items()))
    (repo / ENV).write_text(body, encoding="utf-8")


def is_tracked(repo: Path, name: str) -> bool:
    """True if git already tracks the file. Being tracked is the dangerous state: the next
    `git add -A` publishes it, which is the whole failure this module exists to prevent."""
    r = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", name],
                       capture_output=True, encoding="utf-8", errors="replace")
    return r.returncode == 0


def ensure_ignored(repo: Path) -> bool:
    """Add `.env` to .gitignore if absent. Returns True if it had to be added."""
    gi = repo / ".gitignore"
    lines = gi.read_text(encoding="utf-8", errors="replace").splitlines() if gi.exists() else []
    if any(l.strip() in (ENV, f"/{ENV}") for l in lines):
        return False
    body = ("\n".join(lines) + "\n" if lines else "")
    body += f"\n# Machine-specific values (skillconfig.py). Must never be committed.\n{ENV}\n"
    gi.write_text(body, encoding="utf-8")
    return True


def update_example(repo: Path, key: str, placeholder: str):
    """Record the KEY -- never the value -- in a committed file, so the required config is
    discoverable and reviewable without anyone's machine leaking into the repo."""
    p = repo / EXAMPLE
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines() if p.exists() else [
        "# Required machine-specific values. Copy to .env and fill in, or let a skill",
        "# prompt you on first run. Real values never belong in this file.",
    ]
    if any(l.split("=", 1)[0].strip() == key for l in lines if "=" in l):
        return
    lines.append(f"{key}={placeholder}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def guard(repo: Path) -> int:
    """Refuse to store anything into a repo where .env would be committed."""
    if is_tracked(repo, ENV):
        err(f"REFUSING: {ENV} is tracked by git in {repo}.")
        err(f"  The next 'git add -A' would publish it. Fix first:")
        err(f"    git -C {repo} rm --cached {ENV}")
        return 1
    if ensure_ignored(repo):
        err(f"  added {ENV} to .gitignore")
    return 0


def cmd_get(args, repo: Path):
    values = read_env(repo)
    if args.key in values and values[args.key]:
        print(values[args.key])
        return 0
    if guard(repo):
        return 1

    prompt = args.prompt or f"Value for {args.key}"
    for attempt in range(3):
        err(f"\n{prompt}")
        err(f"  (stored in {repo / ENV}, which is gitignored — asked once, then remembered)")
        err("  > ", )
        line = sys.stdin.readline()
        if line == "":  # EOF: nobody is there to ask.
            err(f"\nERROR: {args.key} is not set and there is no one to prompt.")
            err(f"  Set it explicitly:")
            err(f"    python skillconfig.py set {args.key} <value> --repo {repo}")
            return 2
        val = line.strip()
        if val:
            values[args.key] = val
            write_env(repo, values)
            update_example(repo, args.key, args.example or f"<{args.key.lower()}>")
            err(f"  stored {args.key} in {ENV}")
            print(val)
            return 0
        err("  empty — a machine-specific value has no safe default.")
    err(f"ERROR: no value given for {args.key} after 3 attempts.")
    return 2


def cmd_set(args, repo: Path):
    if guard(repo):
        return 1
    values = read_env(repo)
    values[args.key] = args.value
    write_env(repo, values)
    update_example(repo, args.key, f"<{args.key.lower()}>")
    err(f"stored {args.key} in {repo / ENV}")
    return 0


def cmd_list(args, repo: Path):
    values = read_env(repo)
    if not values:
        err(f"no {ENV} in {repo}")
        return 0
    for k, v in sorted(values.items()):
        print(f"{k}={v}")
    return 0


def cmd_check(args, repo: Path):
    problems = []
    if is_tracked(repo, ENV):
        problems.append(f"{ENV} is TRACKED by git — it will be published on the next commit")
    gi = repo / ".gitignore"
    ignored = gi.exists() and any(
        l.strip() in (ENV, f"/{ENV}")
        for l in gi.read_text(encoding="utf-8", errors="replace").splitlines())
    if (repo / ENV).exists() and not ignored:
        problems.append(f"{ENV} exists but is not in .gitignore")
    ex = repo / EXAMPLE
    if ex.exists():
        real = read_env(repo)
        for line in ex.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                if v.strip() and real.get(k.strip()) == v.strip():
                    problems.append(f"{EXAMPLE} contains the REAL value for {k.strip()}")
    for p in problems:
        err(f"  PROBLEM: {p}")
    if problems:
        return 1
    err(f"  {repo}: config storage is safe")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repo whose .env holds the values")
    # --repo must work on BOTH sides of the subcommand. argparse only accepts it before the
    # subcommand unless every subparser also declares it, and SUPPRESS is what stops the
    # subparser's default from clobbering a value given before it.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", default=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get", parents=[common]); g.add_argument("key")
    g.add_argument("--prompt"); g.add_argument("--example")
    s = sub.add_parser("set", parents=[common]); s.add_argument("key"); s.add_argument("value")
    sub.add_parser("list", parents=[common])
    sub.add_parser("check", parents=[common])
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        err(f"ERROR: no such repo: {repo}")
        return 1
    return {"get": cmd_get, "set": cmd_set, "list": cmd_list, "check": cmd_check}[args.cmd](
        args, repo)


if __name__ == "__main__":
    raise SystemExit(main())
