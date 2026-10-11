# Step 3: saved model and results

Step 3 is complete. The approved plan is in [step-3-plan.md](../research/step-3-plan.md), the selection comparison in [choose_report.md](choose_report.md), and the historical evaluation in [benchmark_report.md](benchmark_report.md). The latter was seen by the feasibility probe; it is not the untouched holdout.

The winner is calibrated logistic regression. The strict registered bar passed at 1 and 3 h, with both daily clim28 and recent7 lower confidence bounds above zero. At 6 h, improvement against recent7 is uncertain. Results are pooled over 24 modeled regions; each report also contains regional counts and the n < 100 flag.

## Load the model

Use the project's Python 3.11 environment and pinned `requirements.txt`. Load only the trusted repository artifact; joblib uses pickle.

```python
from alerts.model import Forecaster

model = Forecaster.load("models/logistic.joblib")
print(model.meta)  # fit cutoff, counts, 19 feature names, versions, source commit
# rows_at_T must contain the 19 Features.NAMES columns, built only from history before T.
# Supply clear-region rows at or after the model fit cutoff, not earlier training rows.
# probabilities = model.predict(rows_at_T)  # columns: p1, p3, p6
```

This file contains all three fitted pipelines and their separate Platt calibrators. Its cutoff is 2026-10-10 19:03 UTC and SHA-256 is `ffbce213e5e203c6246c2c2e8f4bfb4461349a5837545e487467973b18219243`. Live data acquisition and forecast logging are step 4; they are not part of this artifact's evaluation.

## Recheck scores without retraining

Run the following from the repository root with `.venv/bin/python`. Forecast CSVs are in long format: one row per region, forecast time and horizon, with a binary `y`, baseline probabilities, raw/calibrated model probabilities, block start and `scored` flag. Both files include unscored CHOOSE warm-up rows; benchmark scoring additionally requires the benchmark start filter.

```python
import pandas as pd
from alerts.evaluate import Scores
from alerts.splits import BENCHMARK

rows = pd.read_csv("results/benchmark_forecasts.csv.gz", parse_dates=["ts"])
rows = rows[rows.scored & (rows.ts >= BENCHMARK[0])]
for h, part in rows.groupby("hours"):
    part = part.rename(columns={"y": f"y{h}"})
    score = Scores(part, h)
    print(h, len(part), score.brier("logistic"))
    print("clim28 skill, 95% CI:", score.skill("logistic", "clim28"))
    print("recent7 skill, 95% CI:", score.skill("logistic", "recent7"))
```

The model was registered at commit `30cb39a1c08edd62ecc7f67a7d1c49b47fe1d12a` before the single benchmark run. Summaries contain source-manifest and output hashes. `main.py evaluate choose|benchmark` refuses to overwrite these frozen artifacts. The untouched post-cutoff holdout remains for step 7; no holdout results are reported here.
