---
name: data-analyst
description: Guidelines for data analytics tasks — visualization, summary statistics, data scoping, regression analysis, and econometrics. Invoke when starting any analysis, building charts, computing summary stats, fitting regression models, or applying econometric methods.
---

## Data Analyst Guidelines

Apply these rules for every visualization and every summary statistic produced in this session.

---

## 1. Before producing any visualization or statistic — ask these two questions explicitly

Before writing any plotting or aggregation code, ask the user:

**Q1 — Observation scope:**
> "Should this include **all observations**, or do you want to drop outliers first? If dropping, which method — IQR, percentile cap (e.g. p99), or a specific threshold?"

**Q2 — Statistic base:**
> "Should mean/median/std and other statistics be computed on the **raw (unclipped) data**, or on the **clipped/outlier-dropped** series?"

**Default answers (use these unless the user says otherwise):**
- Q1 default: **include all observations** — do not drop any rows
- Q2 default: **compute statistics from raw, unclipped data**

If the user says "use defaults" or doesn't answer, proceed with both defaults.

---

## 2. Clipping is for visualization only

When you clip data (e.g. `series.clip(upper=p99)`) to set axis limits or bin ranges for a histogram:

- Use the **clipped** variable **only** for the histogram bins / `sns.histplot` / axis range
- Compute mean, median, std, and all other statistics from the **unclipped original series**
- When placing a reference line (`axvline`) for a stat that falls outside the display range, clip the **position** to the display cap so the line stays visible, but the **label** must show the true unclipped value

```python
# RIGHT
_raw = df['delay_hours']                         # full series, no clip
_vis = _raw.clip(upper=p99)                      # visualization only
ax.hist(_vis, bins=_bins)
ax.axvline(min(_raw.median(), p99), label=f'Median: {_raw.median():.1f}h')

# WRONG — never do this
_vis = _raw.clip(upper=p99)
ax.axvline(_vis.median(), label=f'Median: {_vis.median():.1f}h')  # biased!
```

---

## 3. Always surface the scope clearly in the figure

Every figure annotation (text box, legend, title) must state:
- `n = X,XXX` — the number of observations the statistic is based on (always unclipped count)
- If outliers were dropped by user request: add "(outliers excluded)" to the annotation

---

## 4. Stat lines on histograms must use unclipped series

Any `axvline` or annotation that shows mean or median must be computed from the unclipped source series, even when the histogram itself is trimmed for display.

---

## 5. When the user changes defaults mid-session

If the user says "clip the stats too" or "drop outliers for this one", apply only to that specific figure. Ask again for the next one — do not carry the override forward silently.
