"""How much better is each v2 model than v1? F1 difference with a paired whole-Kyiv-day bootstrap (1,000, seed 0), from
results/v2/forecasts.csv.gz and the thresholds in results/v2/summary.json. Descriptive, post hoc."""
import json
import sys

import numpy as np
import pandas as pd

root = sys.argv[1] if len(sys.argv) > 1 else "."  # the repository root; run: python research/v2_compare.py
f = pd.read_csv(f"{root}/results/v2/forecasts.csv.gz", parse_dates=["ts"])
s = json.load(open(f"{root}/results/v2/summary.json"))
thr = {(r["forecast"], r["horizon"]): r["threshold"] for r in s["pooled"] if r["period"] == "choose"}
f1 = lambda c: 2 * c[..., 0] / (2 * c[..., 0] + c[..., 1] + c[..., 2])
out = []
for period in ("choose", "benchmark", "holdout"):
    for h in (1, 3, 6):
        part = f[(f.period == period) & (f.hours == h)]
        day = part.ts.dt.tz_convert("Europe/Kyiv").dt.date
        y = part.y.to_numpy() == 1

        def counts(col):
            a = part[col].to_numpy() >= thr[(col, h)]
            return pd.DataFrame({"tp": a & y, "fp": a & ~y, "fn": ~a & y}).groupby(day.to_numpy()).sum().to_numpy()

        base = counts("v1")
        idx = np.random.default_rng(0).integers(0, len(base), (1000, len(base)))
        for m in ("logistic", "gbm", "catboost", "recent7"):
            c = counts(m)
            d = f1(c[idx].sum(1)) - f1(base[idx].sum(1))
            lo, hi = np.percentile(d, [2.5, 97.5])
            out.append(dict(period=period, h=h, model=m, days=len(base), f1_v1=f1(base.sum(0)), f1=f1(c.sum(0)),
                            diff=f1(c.sum(0)) - f1(base.sum(0)), lo=lo, hi=hi))
print(pd.DataFrame(out).round(4).to_string(index=False))
