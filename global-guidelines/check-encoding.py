#!/usr/bin/env python3
"""Flag text I/O that silently relies on the platform's locale encoding.

Companion to the "Text encoding" rule in SKILL.md. Run it in any project:

    python check-encoding.py [path]     # exit 1 if anything is found

Catches the two constructs that actually cause the bug:
  - builtin `open()` in text mode without `encoding=`
  - `subprocess.run/Popen/check_output(text=True)` without `encoding=`

On Windows these use the locale codec (cp1252, or cp874 on a Thai-locale
machine) instead of UTF-8. The loud failure is a crash printing a non-ASCII
character; the quiet and far worse one is a file written with the locale codec
and read back as UTF-8 on another machine, which corrupts without raising.

WHY AN AST AND NOT GREP: a line-oriented search misses `encoding=` when a call
spans several lines -- reporting a false positive on code that is already
correct -- and matches `Image.open(p)` and `p.open("rb")`, which are not the
builtin. Editing based on that output breaks working code.

DELIBERATE LIMITATION: pathlib's `p.open()` is not resolved. Distinguishing it
from `Image.open()` statically needs type inference, and the false-positive rate
is not worth it. This is a heuristic aid, not a proof -- a clean run means the
common cases are covered, not that the code is encoding-safe.
"""

import ast
import pathlib
import sys

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "build", "dist"}


def issues(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    except (SyntaxError, UnicodeDecodeError) as exc:
        return [(getattr(exc, "lineno", 0) or 0, f"could not parse: {type(exc).__name__}")]

    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        kwargs = {k.arg for k in node.keywords}

        # Builtin open() only: an ast.Name, never Image.open / p.open.
        if isinstance(node.func, ast.Name) and node.func.id == "open" \
                and "encoding" not in kwargs:
            mode = ""
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = node.args[1].value or ""
            if "b" not in mode:
                found.append((node.lineno, "open() without encoding="))

        if isinstance(node.func, ast.Attribute) \
                and node.func.attr in {"run", "Popen", "check_output"} \
                and "encoding" not in kwargs:
            if any(k.arg in {"text", "universal_newlines"}
                   and getattr(k.value, "value", None) is True
                   for k in node.keywords):
                found.append((node.lineno,
                              f"subprocess {node.func.attr}(text=True) without encoding="))
    return found


def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    total = 0
    for path in sorted(root.rglob("*.py")):
        if SKIP_DIRS & set(path.parts):
            continue
        for line, msg in issues(path):
            print(f"{path}:{line}: {msg}")
            total += 1
    print(f"{total} issue(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
