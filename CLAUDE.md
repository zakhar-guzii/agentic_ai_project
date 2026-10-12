# Alert Outlook

Python 3.11 package for the KSE air-raid alert time-series assignment. See [README](README.md), [architecture](docs/architecture.md) and [brief](docs/brief.md). Use English for code/docs and Ukrainian in chat.

- Run through `.venv/bin/python`, `.venv/bin/pytest` and `.venv/bin/alert-outlook`; install with `pip install -e '.[dev]'`.
- The runtime lives in `src/alert_outlook/`: data, forecasting, experiments and presentation have separate responsibilities. Reuse existing algorithms; do not add pass-through abstractions.
- Preserve causal features, label maturity, purged time splits, CHOOSE-only selection/thresholds, and forward OOF calibration. The existing benchmark and holdout are historical, not untouched validation.
- Use explicit MLflow runs for metrics and experiment artifacts. Operational events use standard logging. Never generate metric reports in Markdown.
- `models/` has exactly Logistic, LightGBM and CatBoost joblib files. Snapshot weights in MLflow before replacement; publication failures must preserve active files. Load only trusted artifacts.
- Keep `data/raw/` and its manifests intact. Do not bypass the map site's Cloudflare challenge. alerts.in.ua history allows two requests per minute; the client supports paced resume.
- Never print/persist tokens or Authorization. `.env` remains ignored. AI conversation logs are required by KSE and must be preserved.
- Test through module interfaces. For new behavior, write one failing test, then the minimal implementation. The approved seams include storage, model persistence, prediction/scoring and HTML. Retain data/leakage acceptance checks.
- No automatic fetch, tuning, retraining, commit or publication during a structural cleanup.
