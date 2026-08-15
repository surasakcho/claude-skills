#!/usr/bin/env python
"""Screen rendered figures and tables for the defect classes that survive code review.

Reads the RENDERED artifact -- PNG pixels, CSV values -- never the plotting call, because
that is where the defects live. Every check below corresponds to a defect observed in
production; see SKILL.md for the incidents.

FIGURES (from the image itself):
  blank / low_ink   almost nothing was drawn
  no_signal         one colour covers nearly the whole plot -- what an inverted or
                    unregistered colormap looks like
  dark_dominant     a near-black colour covers most of the plot -- the signature of a
                    colormap whose high end swallowed the map
  washed_out        ink confined to a narrow slice of the colour range: the scale is far
                    wider than the data, so all variation is compressed into a few shades
  tiny              suspiciously small file -- truncated or failed render

TABLES:
  empty, all-null columns, unnamed index column, non-UTF8, single-row

Exit 1 if anything is flagged, so it can gate a commit.

    python -X utf8 verify_outputs.py --figures figs/ --tables out/
    python -X utf8 verify_outputs.py --figures a/ b/ --sample 12

Requires: pillow, numpy, pandas.
"""
import argparse
import io
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

findings = []


def flag(kind, path, detail):
    findings.append((kind, str(path), detail))


def review_image(path, min_bytes=12_000):
    """Pixel-level review. Returns measured properties, appends to `findings`."""
    try:
        from PIL import Image
    except ImportError:
        print("pillow is required: pip install pillow", file=sys.stderr)
        raise
    try:
        im = Image.open(path).convert("RGB")
    except Exception as e:
        flag("unreadable", path, f"{e.__class__.__name__}: {e}")
        return {}
    a = np.asarray(im)
    h, w, _ = a.shape

    # Analyse the middle band only: title and colourbar strips are mostly white and would
    # swamp any ink statistic taken over the whole canvas.
    band = a[int(h * 0.12):int(h * 0.86), :, :].reshape(-1, 3)
    if band.size == 0:
        flag("tiny", path, "image too small to analyse")
        return {}
    is_bg = (band > 245).all(axis=1)
    ink = band[~is_bg]
    ink_frac = len(ink) / len(band)

    if path.stat().st_size < min_bytes:
        flag("tiny", path, f"{path.stat().st_size:,} bytes")
    if ink_frac < 0.005:
        flag("low_ink", path, f"only {ink_frac:.3%} of the plot area carries ink")
        return {"ink_frac": ink_frac}

    # Quantise to 5 bits/channel so anti-aliasing does not shatter the histogram.
    q = (ink >> 3).astype(np.int32)
    keys = (q[:, 0] << 10) | (q[:, 1] << 5) | q[:, 2]
    cnt = Counter(keys.tolist())
    top_share = cnt.most_common(1)[0][1] / len(keys)
    dark_share = float((ink.max(axis=1) < 60).mean())
    distinct = len(cnt)

    if top_share > 0.97:
        flag("no_signal", path, f"a single colour covers {top_share:.1%} of the drawn area")
    if dark_share > 0.55:
        flag("dark_dominant", path,
             f"{dark_share:.1%} of the drawn area is near-black — check the colormap "
             f"direction and whether a custom map actually registered")
    # Few distinct colours over a large inked area means the scale is far wider than the
    # data: everything lands in a couple of shades.
    if distinct < 12 and ink_frac > 0.05 and top_share < 0.97:
        flag("washed_out", path,
             f"only {distinct} distinct colours over {ink_frac:.1%} ink — the colour scale "
             f"is probably much wider than the data range")
    return {"ink_frac": ink_frac, "top_share": top_share, "dark_share": dark_share,
            "distinct": distinct}


def review_table(path):
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    except UnicodeDecodeError as e:
        flag("encoding", path, f"not UTF-8 decodable: {e}")
        return
    except Exception as e:
        flag("unreadable", path, f"{e.__class__.__name__}: {e}")
        return
    if len(df) == 0:
        flag("empty_table", path, "0 rows")
        return
    if len(df) == 1:
        flag("single_row", path, "1 row — intended, or a partial write?")
    allnull = [c for c in df.columns if df[c].isna().all()]
    if allnull:
        flag("all_null_column", path, f"entirely null: {allnull[:6]}")
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed")]
    if unnamed:
        flag("unnamed_column", path,
             f"{unnamed[:4]} — an index was written without a name; set df.index.name")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--figures", nargs="*", default=[], help="directories to scan for PNGs")
    ap.add_argument("--tables", nargs="*", default=[], help="directories to scan for CSVs")
    ap.add_argument("--sample", type=int, default=0,
                    help="also list N artifacts worth eyeballing, chosen at the extremes")
    args = ap.parse_args()
    if not args.figures and not args.tables:
        ap.error("give --figures and/or --tables")

    print("=" * 78)
    print("OUTPUT REVIEW")
    print("=" * 78)

    figs = sorted({p for d in args.figures for p in Path(d).rglob("*.png")})
    stats = []
    if figs:
        print(f"\nfigures: {len(figs)}")
        for i, p in enumerate(figs, 1):
            s = review_image(p)
            s["path"] = p
            stats.append(s)
            if i % 100 == 0:
                print(f"  reviewed {i}/{len(figs)}")
        print(f"  reviewed {len(figs)}/{len(figs)}")

    tables = sorted({p for d in args.tables for p in Path(d).rglob("*.csv")})
    if tables:
        print(f"\ntables: {len(tables)}")
        for p in tables:
            review_table(p)

    if args.sample and stats:
        S = pd.DataFrame([s for s in stats if "top_share" in s])
        if len(S):
            k = max(1, args.sample // 3)
            print(f"\n--- eyeball these ({args.sample}) — extremes are where defects hide ---")
            for lbl, sub in (("most single-coloured", S.nlargest(k, "top_share")),
                             ("least ink", S.nsmallest(k, "ink_frac")),
                             ("darkest", S.nlargest(args.sample - 2 * k, "dark_share"))):
                print(f"  {lbl}:")
                for _, r in sub.iterrows():
                    print(f"    {r['path']}  top={r.top_share:.1%} "
                          f"ink={r.ink_frac:.1%} dark={r.dark_share:.1%}")

    print("\n" + "=" * 78)
    if findings:
        print(f"FLAGGED: {len(findings)}")
        for kind, path, detail in findings:
            print(f"  [{kind}] {path}\n      {detail}")
        return 1
    print(f"All {len(figs)} figure(s) and {len(tables)} table(s) pass the automated screen.")
    print("A SCREEN IS NOT AN EYEBALL. Review a sample by eye, sampling across colour")
    print("policies / norm types / data families rather than at random — defects live in")
    print("shared code and cluster by mechanism. Then say which you eyeballed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
