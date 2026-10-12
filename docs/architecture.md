# Alert Outlook architecture

`alert-outlook` loads a frozen map snapshot and saved alerts.in.ua pulls, builds causal features, forecasts with three calibrated models, and renders one offline HTML page. All three artifacts are v2 models; Logistic is the first visible panel, and the reader selects LightGBM or CatBoost with the page buttons.

| Module | Interface and responsibility |
|---|---|
| `data` | `saved(paths)` returns normalized history and its common complete cutoff. Source parsing, splice, episode unions and data validation live here. Only `sources.pull_history` performs network requests. |
| `forecasting` | `Forecaster.load(path).predict(rows)` returns `p1/p3/p6`. Feature construction, baselines, purged splits, forward calibration, numerical metrics and revision scoring live here. |
| `experiments` | Explicit workflows own MLflow runs, search resume, training, model publication, prediction logs and evaluation of saved rows. A `Tracking` instance owns one local store; tests use a temporary directory. |
| `presentation` | `render(...)` returns self-contained HTML from supplied tables. History analytics are capped at the map cutoff. Rendering never fetches, trains or recomputes a forecast. |
| CLI and settings | Arguments and printed output; centralized filesystem paths and secret lookup. Set `ALERT_OUTLOOK_HOME` or pass `--root` for another checkout. |

## Data and evaluation contract

The splice is 2026-09-12 00:00 Kyiv. Starts before it use the map; later starts use alerts.in.ua. The map cutoff remains 2026-10-10 19:03 UTC. Only AIR/air_raid records are used. Oblast/raion intervals are unioned, ongoing records are censored at the observation cutoff, and overlapping raion records never multiply alert time. Historical alert levels are final revisions, so red time is an upper bound.

A forecast at T reads minutes before T. Training and calibration use only labels whose horizon has closed at the block start. Search and alarm thresholds use CHOOSE only. The benchmark and the original holdout have already been examined; neither is an independent future test. Bootstrap intervals resample whole Kyiv calendar days. Regional results with fewer than 100 observations are flagged as unverified.

## Storage and failures

`models/` contains exactly three trusted joblib files. Each holds three horizons, their calibrators and metadata. Joblib uses pickle: never load arbitrary downloaded weights. A shared generation identifier prevents consuming a partially published set. Training stages and reload-checks all weights, finishes its MLflow run, then replaces the active files; an ordinary replacement failure restores the preceding files. A process or machine crash during the three replacements is detected as a mixed generation: restore all three snapshots from the same MLflow run before prediction.

`mlruns/tracking.db` stores run metadata and scalar metrics; `mlruns/artifacts/` stores forecast rows, regional tables, calibration tables, search configurations, weights and summaries. Missing/undefined metrics remain null in JSON and are omitted from scalar metrics. New runs never generate Markdown reports. Each search trial completes all three horizons and both calibration windows before becoming resumable. Its fingerprint includes raw file contents, manifests, algorithm code, dependency versions and search settings.

`artifacts/predictions/forecasts.csv` records each `(oblast, T, model, model_sha256)` once. It is replaced atomically. Each prediction run archives the exact weights before writing its journal. Scoring uses those snapshots for old versions, separates live and replay at each horizon, and compares revised forecasts only on rows still clear. The journal supports one CLI writer at a time; do not run concurrent prediction processes against the same checkout.

The page reads logged predictions for the current data and weights, and asks for `predict` if they are missing. An empty MLflow store is supported: quality remains available in README. Unexpected storage failures produce a nonzero exit and an error log.

`logs/operations.jsonl` uses UTC timestamps, rotation, command/model/horizon/run context and redacted errors. Tokens are sent only in Authorization headers, never persisted. `ai_log/` retains the KSE conversation history and its separate export script.

## Redesign provenance

Source commit: `0b983584127bf7a8eb841235a49951770a7db367`. The original v1/v2 artifacts, search tables, reports, research notes and process log were imported into a verified local MLflow migration run before cleanup. The import is idempotent by snapshot checksum. Model migration remapped old Python references only in the conversion process; runtime needs no `alerts` compatibility package. No model was retrained. Historical and latest forecasts were compared before/after conversion with absolute tolerance `1e-12`.

Old imports under `alerts` are replaced by `alert_outlook`. `retrain` becomes `train`; one-off v1 `evaluate`/`holdout` and Markdown `metrics` commands are replaced by `evaluate --run-id ... --period ...`. The short `main.py` entry point remains. The historical artifacts and notes are also preserved in Git history.
