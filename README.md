# Alert Outlook

Air-raid alert history and calibrated probabilities of a new alert within **1, 3 or 6 hours** for 23 oblasts and Kyiv City. The offline HTML page has three buttons: **Logistic**, **LightGBM**, **CatBoost**. Each file in `models/` contains all three horizons and their calibrators.

## Quick start

Python 3.11 or 3.12 (the pinned numpy and pandas have no wheels for 3.13+). Run from the repository root:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest -q
.venv/bin/alert-outlook predict
.venv/bin/alert-outlook page
open artifacts/outlook.html  # Linux: xdg-open, Windows: start
```

`python main.py ...` and `python -m alert_outlook ...` use the same commands. `--root PATH` or `ALERT_OUTLOOK_HOME` selects another checkout. Everything except `fetch` works offline from committed raw data and the three committed models.

| Command | Result |
|---|---|
| `fetch [--into PATH]` | Paced, resumable alerts.in.ua history pull; needs `ALERTS_IN_UA_TOKEN` in `.env` or environment. A full pull takes about 13 minutes. |
| `check` | Source agreement, splice completeness and time-blocked drift checks in MLflow. |
| `predict` | Forecast and journal all three models at the saved data cutoff; identical versions/moments are recorded once. |
| `score` | Score closed windows, separately by model/version and live/replay, including revision checks. |
| `history` | Historical load and level tables in MLflow. |
| `page` | Generate `artifacts/outlook.html` from logged predictions; run `predict` after data or weights change. |
| `tune logistic\|lightgbm\|catboost [--minutes 45]` | Resume CHOOSE-only search from completed MLflow trials with matching data and settings. |
| `train` | Fit each family's CHOOSE winners, log forward evaluations and publish three validated weights. Requires searches for all families. |
| `evaluate --run-id ID --period choose\|benchmark\|holdout` | Score a completed training/import run's saved forecast rows, without training. |

## Historical model quality

F1 and Brier are pooled across modeled regions. Values within each cell follow **1 h / 3 h / 6 h**; lower Brier is better. Alarm thresholds were selected on CHOOSE and then fixed. These values describe the original v2 forward runs, not in-sample scores of the final fitted weights.

| Model | Period | F1: 1 / 3 / 6 h | Brier: 1 / 3 / 6 h |
|---|---|---|---|
| Logistic | Benchmark | 0.6394 / 0.7871 / 0.8315 | 0.1245 / 0.1337 / 0.1240 |
| LightGBM | Benchmark | 0.6363 / 0.7843 / 0.8338 | 0.1248 / 0.1341 / 0.1253 |
| CatBoost | Benchmark | 0.6314 / 0.7825 / 0.8273 | 0.1255 / 0.1349 / 0.1269 |
| Logistic | Holdout | 0.6486 / 0.8299 / 0.8917 | 0.1794 / 0.1574 / 0.1216 |
| LightGBM | Holdout | 0.6417 / 0.8163 / 0.8948 | 0.1748 / 0.1622 / 0.1103 |
| CatBoost | Holdout | 0.6341 / 0.8236 / 0.8842 | 0.1755 / 0.1658 / 0.1178 |

The benchmark had been seen by the feasibility probe, and the short high-load holdout had been examined before v2 work. Both are **historical checks, not independent future validation**. High F1 alone does not establish improvement over recent alert rates; regional quality can differ. The redesign migrated existing weights without retraining or changing numerical forecasts.

## MLflow and logs

Runs, scalar metrics and experiment artifacts are stored locally in `mlruns/`. View them with:

```bash
.venv/bin/mlflow ui --backend-store-uri "sqlite:///$PWD/mlruns/tracking.db" --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000`. The URI uses the same SQLite store as the CLI; artifacts are stored under `mlruns/artifacts/`. Training/evaluation write parameters, metrics, thresholds, bootstrap intervals and tables explicitly. Undefined metrics are omitted from scalar metrics and retained as null in JSON.

Back up **all of `mlruns/`**, including SQLite and artifacts, with writers stopped. Artifact locations in the database are absolute: restore to the same project path. MLflow history is not committed to Git. A new clone needs no imported history for `predict` or `page`; the quality table above is sufficient. Historical runs were migrated in the original workspace and remain there.

Operational logs go to stderr and rotating `logs/operations.jsonl`. The forecast journal is `artifacts/predictions/forecasts.csv`; HTML and journals are also outside Git. Scoring retains exact weight snapshots in MLflow, so keep the store when replacing weights. Run one prediction writer per checkout.

## Layout and saved models

- `src/alert_outlook/`: data, forecasting, experiments, presentation, CLI, settings and logging.
- `models/`: exactly `logistic.joblib`, `lightgbm.joblib`, `catboost.joblib`.
- `data/raw/`: original map snapshot and alerts.in.ua pulls with provenance manifests.
- `tests/`: numerical, leakage, storage and workflow checks.
- `docs/`: [architecture and contracts](docs/architecture.md), [KSE brief](docs/brief.md).
- `ai_log/`: required AI conversation history; export with `python ai_log/export.py`.

```python
from alert_outlook.forecasting.model import Forecaster
model = Forecaster.load("models/logistic.joblib")
# rows include the feature columns and any reference inputs listed in model.meta["horizons"].
probabilities = model.predict(rows)  # p1, p3, p6
```

Load only trusted project joblib files: they use pickle. Data parsing keeps AIR/air_raid records and unions overlapping oblast/raion episodes. Features read only history before forecast time T; historical levels keep final API revisions. See the architecture document for cutoffs, evaluation limits and failure recovery.
