#!/usr/bin/env python
"""Self-test: prove verify_outputs.py can FAIL.

A checker you have never seen fail is an untested checker. This builds deliberately broken
figures and tables, runs the screen over them, and asserts each defect class is caught --
then builds a clean pair and asserts they pass.

    python -X utf8 test_self.py        # exit 0 if the checker behaves
"""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
CHECKER = HERE / "verify_outputs.py"


def build(tmp: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    bad_f, good_f = tmp / "bad_figs", tmp / "good_figs"
    bad_t, good_t = tmp / "bad_tabs", tmp / "good_tabs"
    for d in (bad_f, good_f, bad_t, good_t):
        d.mkdir(parents=True)

    # blank
    fig, ax = plt.subplots(figsize=(4, 3)); ax.set_axis_off()
    fig.savefig(bad_f / "blank.png", dpi=110); plt.close(fig)
    # a single flat colour covering everything
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(np.ones((80, 80)), cmap="Greys", vmin=0, vmax=1); ax.set_axis_off()
    fig.savefig(bad_f / "flat.png", dpi=110); plt.close(fig)

    # a genuinely informative figure
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.imshow(rng.random((120, 120)), cmap="viridis")
    ax.set_title("structured signal"); fig.savefig(good_f / "ok.png", dpi=120); plt.close(fig)

    pd.DataFrame({"a": []}).to_csv(bad_t / "empty.csv", index=False)
    pd.DataFrame({"a": [1, 2], "b": [None, None]}).to_csv(bad_t / "allnull.csv", index=False)
    pd.DataFrame({"x": [1, 2]}, index=["p", "q"]).to_csv(bad_t / "unnamed.csv")
    pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]}).to_csv(good_t / "fine.csv", index=False)
    return bad_f, good_f, bad_t, good_t


def run(figs, tabs):
    r = subprocess.run([sys.executable, "-X", "utf8", str(CHECKER),
                        "--figures", str(figs), "--tables", str(tabs)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        bad_f, good_f, bad_t, good_t = build(tmp)

        code, out = run(bad_f, bad_t)
        failures = []
        if code == 0:
            failures.append("checker PASSED known-bad input — it cannot fail")
        for kind in ("low_ink", "no_signal", "empty_table", "all_null_column",
                     "unnamed_column"):
            if kind not in out:
                failures.append(f"did not detect '{kind}'")

        code_ok, out_ok = run(good_f, good_t)
        if code_ok != 0:
            failures.append(f"checker FAILED known-good input:\n{out_ok[-600:]}")

        for k in ("low_ink", "no_signal", "empty_table", "all_null_column", "unnamed_column"):
            print(f"  [{'ok' if k in out else 'MISS'}] detects {k}")
        print(f"  [{'ok' if code != 0 else 'MISS'}] exits non-zero on bad input")
        print(f"  [{'ok' if code_ok == 0 else 'MISS'}] exits zero on good input")

        if failures:
            print("\nSELF-TEST FAILED:")
            for f in failures:
                print(f"  - {f}")
            return 1
        print("\nself-test passed: the checker detects every seeded defect class, "
              "and clears clean input.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
