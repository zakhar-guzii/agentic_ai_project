# Alert Outlook

Submission for the KSE Agentic AI School, Stage 2: *Time Series Analysis of air raid alerts in Ukraine* ([brief](research/brief.md)).

For every oblast of Ukraine (23 oblasts + Kyiv City) it shows:
- **Now:** where an air-raid alert is on, and its level (🟡 drones / 🔴 missiles or massed strike);
- **Next hours:** the probability that a new alert starts within 1, 3 or 6 hours, from a calibrated logistic regression;
- **History:** the weekly alert load, including since the yellow/red level reform of 2026-09-07.

It is a CLI that prints a table and writes one self-contained HTML page, [results/outlook.html](results/outlook.html). Every forecast is logged and scored once its window has passed.

## Results

Brier skill of the frozen model against two honest references: **clim28**, a 28-day oblast × hour climatology recounted daily, and **recent7**, the last 7 days' rate. Brackets are 95% Kyiv-day bootstrap intervals.

| period | | 1 h | 3 h | 6 h |
|---|---|---|---|---|
| historical benchmark (4 blocks) | vs clim28 | +7.5% | +7.9% | +6.7% |
| | vs recent7 | +5.5% | +4.8% | +2.8% (uncertain) |
| untouched holdout (41.7 h after the map cutoff, very high load) | vs clim28 | +7% [+6, +25] | +20% [+11, +60] | +32% [+29, +51] |
| | vs recent7 | +0.9% [+0.2, +9] | −3.6% [−18, +30] | −15.8% [−64, +7] |

- The registered bar (both lower bounds > 0 on at least two horizons) **passes** on the benchmark and **fails** on the holdout. On the holdout the model is level with recent7 at 1 h and worse at 3 and 6 h.
- The benchmark was already seen by the feasibility probe, so it is not an independent check. The holdout was opened once, as pre-registered.
- Why it fails under high load: [research/weak-spots.md](research/weak-spots.md).
- v2, a search for maximum F1 over LightGBM, CatBoost and logistic regression, does not move F1. v1 stays the registered model ([results/v2/report.md](results/v2/report.md)).
- Reports: [benchmark](results/benchmark_report.md), [holdout](results/holdout_report.md), [classification metrics](results/metrics_report.md), [history](results/history_report.md), [data and seam check](results/data_report.md).

## Quick start

Python 3.11.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest                      # unit tests, plus the acceptance checks on the real data
.venv/bin/python main.py predict      # forecast where the saved data end; prints the table, logs it
.venv/bin/python main.py page         # writes results/outlook.html
```

Everything except `fetch` runs offline from the data committed in `data/raw/`. To pull fresh data, put an [alerts.in.ua](https://alerts.in.ua) token in `.env` (see `.env.example`) and run `main.py fetch` (about 13 min: the API allows 2 requests per minute).

| command | what it does |
|---|---|
| `fetch` | pull the alerts.in.ua 30-day history for all regions (network, resumable) |
| `check` | seam, splice and drift checks → `results/data_report.md` |
| `predict` / `score` | forecast at the end of the saved data and log it / score logged forecasts whose windows closed |
| `history` | weekly load and the reform comparison → `results/history_report.md` |
| `page` | the outlook page → `results/outlook.html` |
| `metrics` | precision / recall / F1 / AP / AUC of the frozen forecasts → `results/metrics_report.md` |
| `evaluate choose\|benchmark`, `holdout`, `tune`, `retrain` | the one-off frozen runs; they refuse to overwrite their results |

### Use the saved model

```python
from alerts.model import Forecaster

model = Forecaster.load("models/logistic.joblib")  # trusted repo artifact only: joblib uses pickle
print(model.meta)  # fit cutoff, counts, the 19 feature names, versions, source commit
# rows_at_T: the 19 Features.NAMES columns, built only from history before T
# model.predict(rows_at_T) -> columns p1, p3, p6
```

## Data

- **Before 2026-09-12 00:00 Kyiv:** a frozen snapshot of the official map (map.ukrainealarm.com), 2025-10-03 → 2026-10-10 19:03 UTC, in `data/raw/map/` with its `MANIFEST.json`.
- **After, and live:** the alerts.in.ua API; raw pulls in `data/raw/alerts_in_ua/<UTC stamp>/`.
- The seam between the sources agrees at minute-level Jaccard 0.9994. Alerts are counted as per-oblast union episodes, because the map keeps overlapping raion records.
- **No leakage:** a forecast at time T reads only minutes before T. This is tested by truncation on 30 real moments (`tests/test_leakage.py`).

## Layout

- `alerts/`: the package: `data` (load, splice, episodes), `features`, `splits`, `baselines`, `model`, `evaluate`, `live`, `page`, `api`, `checks`.
- `main.py`: the CLI. `tests/`: pytest, one file per seam.
- `models/`: the frozen v1 forecaster and the three v2 models.
- `results/`: frozen forecasts, reports, the forecast log and the page.
- `research/`: the brief, data sources, the feasibility probe, the survey of other submissions, weak spots.
- [PROCESS_LOG.md](PROCESS_LOG.md): every decision and every caught error ("Wrong #1–23").
- [ai_log/](ai_log/): the full AI conversation log (Claude Code and Codex), with an index of the prompts.

## Reflection

AI was the engineering tool here, and my job was to keep it honest. It was fastest at research and plumbing: surveying 115 other submissions, finding data traps, writing test-first code. Its most dangerous errors were confident ones. The first model "beat climatology" only because the climatology was frozen (Wrong #9). A weak guard once opened the holdout early (Wrong #21). Pre-registering every bar before scoring, and logging each mistake, turned these from hidden flaws into findings. The result is modest: a calibrated forecast that beats climatology but not a 7-day recent rate under heavy load. I would rather submit that than a number I cannot defend.
