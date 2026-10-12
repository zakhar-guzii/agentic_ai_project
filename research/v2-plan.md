# v2: retrain LightGBM, CatBoost and logistic for maximum F1, save all three, and let the user switch models on the page

Approved by the user on 2026-10-12.

## Context

- v1 (calibrated logistic regression, `models/logistic.joblib`) failed the registered bar on the untouched holdout. At 1 h it was level with recent7; at 3 h and 6 h it was worse. `research/weak-spots.md` explains why. Under high load its level lags behind the real rate. It has one global calibration. Within a region it ranks moments poorly.
- **The user, 2026-10-12:**
  - retrain, changing every parameter that matters, so as to **maximise F1**;
  - save the weights of LightGBM, CatBoost and logistic regression;
  - on the page, a button lets the user choose a v2 model;
  - do v2 first, then step 8.
- **One rule does not move.** The F1 we report must come from weeks that the tuning never saw.
  - The search sees only the CHOOSE weeks, up to 2026-09-12.
  - The benchmark and the holdout are the check. Both were seen before (by the probe and the weak-spot analysis), so the report labels them "seen, not used for tuning".
  - If we tuned on the holdout, its F1 would mean nothing, and that would break the brief's no-leakage rule.
- **v1 stays untouched**, with all its frozen files: `models/logistic.joblib`, `results/*_forecasts.csv.gz`, `results/*_summary.json` and `results/forecast_log.csv`.
- Branch: `v2-retrain`. This plan is copied to `research/v2-plan.md`.

## Decision 12 (PROCESS_LOG; committed before the search starts)

1. **Families.** Three: logistic, LightGBM (`gbm`) and CatBoost.
2. **Search.**
   - The search space is below.
   - Configs run in a fixed random order (seed 0). Each family runs in its own process and gets a **45-minute box**.
   - A family uses the configs it finishes inside its box. Every config tried is saved, with its scores.
3. **Score of one config.** It is scored the way v1 was chosen:
   - forward blocks over CHOOSE: each block is fitted on the past only and calibrated with a Platt on the window before it;
   - **pooled F1** over the 24 regions on the scored blocks 3–6, at the config's max-F1 threshold (grid .01–.99).
4. **Winner.** For each family and each horizon, the config with the highest F1 wins. Its threshold is then fixed.
5. **Check.**
   - The winners are run forward again over BENCHMARK and over the holdout (10-10 19:03 → 10-12 12:43 UTC).
   - The report shows precision, recall and F1 at the CHOOSE threshold, the F1 of always saying yes, AP, AUC and Brier.
   - v1, clim28 and recent7 appear alongside, their thresholds also taken from CHOOSE.
   - Both periods are labelled seen.
6. **Final models.**
   - Each family's winners are refitted on every label known at 10-12 12:43 UTC (the newest saved data, holdout included), with a Platt on the window before that moment.
   - They are saved as `models/v2/{logistic,gbm,catboost}.joblib` with their SHA-256. The meta records the config and threshold of each horizon.
7. **Untouched check (after the submission).**
   - The data are everything after 10-12 12:43 UTC. Nothing after that moment is fetched until the v2 models are committed.
   - v1 and the three v2 models are scored on the same rows with these thresholds.

## Search space

| family | parameter | values |
|---|---|---|
| all | inputs | the 19 features; the 19 plus `clim28_H` and `recent7_H` (the two references as inputs) |
| all | recency weights, half-life | none, 30, 60, 120 days |
| all | Platt window | 7, 14 days (the same raw forecasts are recalibrated; no refit) |
| logistic | `C` / `class_weight` | 0.01, 0.1, 1, 10 / none, balanced |
| gbm | `n_estimators` × `learning_rate` | 200, 400, 800 × 0.02, 0.05, 0.1 |
| gbm | `num_leaves` / `min_child_samples` | 15, 31, 63, 127 / 50, 200, 1000 |
| gbm | `subsample` / `colsample_bytree` / `reg_lambda` | 0.7, 1 / 0.6, 0.8, 1 / 0, 1, 10 |
| catboost | `iterations` / `learning_rate` | 300, 600, 1000 / 0.03, 0.1 |
| catboost | `depth` / `l2_leaf_reg` | 4, 6 / 1, 3, 10 |

**Measured on 249k rows, one fit:** logistic 1.3 s; gbm 2.5 s (300 trees); catboost 20 s (1,000 iterations).
- One config is 18 fits: 6 blocks × 3 horizons.
- In 45 min: logistic covers all its 64 configs, gbm about 15–30, catboost about 8–10.
- Depth 8 is left out: it takes about 80 s per fit.

**Threads:** 14 cores, split as gbm `n_jobs=6` (plus `deterministic=True`), catboost `thread_count=7`, logistic 1. These values stay fixed, so a refit reproduces the search.

## Code (smallest diff; reuse what exists)

**`alerts/model.py`**
- `recency(ts, asof, half_life)` gives the weights. `Boosting.weights` calls it, so its existing test stays.
- `Boosting`, `CatBoost` and `Logistic` all take:
  - `half_life`, passed to the fit as `sample_weight`;
  - `refs`, the reference columns used as inputs (`Boosting(clim=True)` stays as it is);
  - `params`, the hyperparameters, merged over the current settings;
  - `name`.
- `Logistic` puts the reference inputs through logit, then standardises them.
- Defaults are set at class level, so the pickled v1 predicts byte for byte as before.
- `ForwardRun.calibrate(raw, hours)` is the calibration half of `run`, split out. `run` calls it. The search uses it to recalibrate the same raw forecasts with 7 and with 14 days.
- `SPACE` and `configs(family, seed=0)`: the shuffled product of the space. `best(search)` picks the winner per family and horizon.

**`alerts/live.py` `forecast`:** compute clim28 and recent7 first, then pass them to the model. v1 ignores them, so its output is unchanged.

**`main.py`**
- `tune <family> [--minutes 45]`:
  - builds the table up to the end of CHOOSE only, starting 29 days early so that clim28 is complete (the pattern of `live.holdout`);
  - runs the configs in seeded order and appends each finished one to `results/v2/search_<family>.csv`;
  - resumes after a crash.
- `retrain`:
  - reads the winners;
  - runs them forward over CHOOSE, BENCHMARK and the holdout;
  - **asserts** that each winner's CHOOSE F1 equals the search's, and that v1's rows, labels and references equal the frozen CSVs;
  - writes `results/v2/{report.md, forecasts.csv.gz, summary.json}`;
  - makes the final fit and writes `models/v2/*.joblib`;
  - refuses to overwrite existing files.
  - Reuses `Scores.threshold`, `Scores.classes`, `ForwardRun.final` (once per horizon, merged into one `Forecaster` per family), `md` and `_names`.

**`alerts/page.py` `switch(panels)`:** radio buttons and panels, in CSS only. The page stays without script, self-contained and deterministic.

## Page: the model button

- Buttons: **v1 logistic (registered) · v2 logistic · v2 LightGBM · v2 CatBoost**. The default is v1, a one-line change if a v2 model should be the default.
- Each button shows that model's tiles and forecast table at T, 10-12 12:43 UTC.
  - v2 forecasts are computed when the page is rendered, from the saved data, so they are a replay.
  - The "now" state is the same for all four.
- **Model quality** gets a table: F1, precision and recall per model and horizon, on the benchmark and the holdout. Its note: "v2 was tuned after the holdout; untouched check pending".
- Without `results/v2/`, the page is as today.

## Order and time boxes (Kyiv)

| # | Part | Box |
|---|---|---|
| 1 | Branch; `research/v2-plan.md`; PROCESS_LOG Decision 12; commit (the registration) | 17:40–17:55 |
| 2 | TDD: the v1 guard, `model.py`, `live.py`, `tune` | 17:55–18:45 |
| 3 | Search: 3 background processes, 45 min | 18:45–19:30 |
| 3′ | While it runs, TDD: `retrain` and the page switch | 18:45–19:30 |
| 4 | `retrain` (≈15 min, catboost dominates), `page`, checks | 19:30–19:55 |
| 5 | PROCESS_LOG result, CLAUDE.md (steps, code), merge into `main` | 19:55–20:15 |
| 6 | Step 8 | 20:15–21:45 |

**Cut rule.**
- If the search has not started by 19:00, its box shrinks to 30 min.
- If v2 is not merged by 21:00, stop and go to step 8. Write down what is unfinished.

## Tests (TDD, one red test at a time; mutation-check any test that passes at once)

1. **v1 guard (first, `test_real_data.py`).** `models/logistic.joblib` on the holdout rows reproduces `results/holdout_forecasts.csv.gz` to 1e-12.
2. **Recency weights.** In a worked example, `Logistic(half_life=60)` with y = 1 at s and y = 0 at s − 60 d predicts 2/3.
3. **Reference inputs.** In a worked example where y follows `recent7_1` alone, `Logistic(refs=…)` ranks by it.
4. **Leakage.** The truncation check in `test_leakage.py` runs on v2-style candidates of all three families (refs, half-life, non-default params). Its helper also joins recent7.
5. **`live.forecast`.** A model with refs gets clim28 and recent7 at T and stays truncation-clean.
6. **`calibrate`.** `calibrate(raw, window=W)` equals a run with window W.
7. **Search.** `configs` is deterministic and has no duplicates. `best` takes the highest F1 per family and horizon (worked example).
8. **Save and load.** A round trip for all three v2 families gives equal forecasts.
9. **Page.** `switch` renders one checked radio and one panel per model, and the acceptance test still finds no `<script`.
10. **`retrain`.** It refuses to overwrite, like `test_evaluate_cli.py`.

## Verification

- `.venv/bin/pytest`: all green, the existing tests and the new ones.
- The frozen v1 files are unchanged: `git diff main --stat -- models/logistic.joblib results/*_forecasts.csv.gz results/*_summary.json results/forecast_log.csv` is empty.
- `retrain`'s own asserts pass: the search is reproduced, the v1 rows equal the frozen CSVs, and v1's F1 equals `results/metrics.json`.
- In a fresh process, each `models/v2/*.joblib` loads and forecasts at T; all p are in [0, 1].
- `python main.py page` run twice gives the same bytes. In a browser, the four buttons switch the tiles and the table.

## Not in v2

- Per-region calibration or thresholds, and daily recalibration inside `predict`. These come next if the v2 report still shows region bias.
- `predict` and `forecast_log.csv` stay on v1 (they are frozen for the submission).
- Threat type and raion-level features: `threats` is not in the history.
