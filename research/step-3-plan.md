# Step 3: model and evaluation

Approved in the previous session on 2026-10-11; recovered from the supplied conversation export.

## Context

Step 3 in CLAUDE.md: "The calibrated 1/3/6 h forecaster, chosen on the `CHOOSE` forward checks (each calibrator sees
only earlier blocks) and scored once on the historical benchmark against the baselines; all 24 oblasts, with
per-oblast counts."

Where we stand:
- Steps 1–2 are done: history, `ForecastTable`, the four baselines, `Split.forward`, the leakage checks (72 tests).
- Wrong #9: the probe's LightGBM gains only about +0.06 / +0.03 / +0.02 over a climatology recounted daily, and the
  7-day `RecentLevel` is as strong. So the honest question of step 3 is whether any model beats these two at all.
- Decision 4 already fixes the step-3 rules: a block's model learns only from its `fit`; its calibrator learns only
  from out-of-fold forecasts of the 14 days before the block; CHOOSE blocks 3–6 are labelled "not independent";
  a pre-registration commit comes before the single benchmark run; all 24 oblasts, n < 100 flagged.

What other teams used (research/prior-solutions-scores.csv, 190 repos, and the cards), checked on 2026-10-11 after the
user asked why only LightGBM:
- Gradient boosting appears in 41 repos, deep models (LSTM, GNN) in 17.
- The deep results that exist are weak or unfinished: a spatio-temporal GNN at AUC 0.61 with no baseline
  (anechytailenko); LSTM lost to XGBoost/CatBoost in goodfrog33's 12-model comparison; LSTM on daily minutes at MAPE
  75–91% (sergkern1); LSTM unfinished (KrafterDen).
- The five strongest onset forecasters (lbgos, maranferij, Ddrakkx, robotheist, Dopplerr24) used LightGBM and/or
  logistic regression. maranferij's logistic regression matched LightGBM on Brier and lost on ranking.
- Teams with strict rate baselines (Ddrakkx `recent_level`, Nazar32's 42-day Markov chain) often could not beat them.
- The numbers across teams are not comparable (different targets and windows, often a frozen climatology). So the choice
  must come from our own CHOOSE blocks, and the candidates must include more than one model type.

Measured on 2026-10-11 (CHOOSE window only, no scores computed): the table builds in 0.6 s (267,283 rows), one
LightGBM fit takes 2.5 s on 228k rows, the daily clim28 takes 5 s. Python 3.11.9 on arm64; catboost 1.2.10 has a cp311
macOS wheel (29 MB). Smallest oblasts on CHOOSE blocks 3–6 at H = 6: Donetska 48, Dnipropetrovska 49, Kharkivska 66
rows, so these will be flagged "quality not verified".

## Decisions (with the user, 2026-10-11)

1. **Five candidates, three model types**, all at fixed settings with no tuning, on the same 19 forecast-time features:
   - **A** `gbm`: LightGBM at the probe's settings.
   - **B** `gbm_clim`: A plus the daily clim28 rate as a feature (Decision 3 left this input for step 3).
   - **C** `gbm_recent`: A with recency weights, half-life 60 days (Wrong #10 left this for step 3; lbgos's value).
   - **D** `catboost` (the user): boosted trees too, but with a different design: ordered boosting against
     overfitting, native handling of the oblast category, and strong defaults. Library defaults, seed 0.
   - **E** `logistic`: logistic regression, a linear model (Ddrakkx, maranferij). Oblast and weekday are one-hot, the
     hour is sin/cos, and counts and minutes are log1p and standardised. sklearn defaults.
   More candidates make the CHOOSE winner look better than it is; the benchmark is the honest check of it.
2. **LSTM: considered and deferred**, logged with its reasons:
   - no evidence in the survey of a deep model beating a strong baseline on this task;
   - our inputs are tabular features, where boosted trees usually win (Grinsztajn et al., NeurIPS 2022; LightGBM won M5);
   - the data are short (about one year, about 26k alerts) and the regime shifted;
   - it would need PyTorch and architecture tuning, about one day before the deadline.
3. **No stacking or blending now** (the user): combining forecasts only makes sense if their errors differ, and that has
   not been measured. The CHOOSE report shows the correlation of errors (y − p) between the candidates and the
   baselines. Any blend after that is a new logged decision before the pre-registration, made by the user.
4. **Platt is calibration, not a stack**: it rescales one model's probabilities (logistic regression on its logit,
   ported from `research/probe/model.py:57-59`). The CHOOSE report shows raw vs calibrated Brier for each candidate.
5. **Choice rule, set before any score**: the candidate with the highest mean Brier skill against the daily clim28
   over H = 1, 3, 6, on CHOOSE blocks 3–6 pooled. One candidate serves all three horizons.
6. **The bar, strict** (the user): the chosen forecaster passes if its Brier skill against the daily clim28 AND against
   `RecentLevel` has a 95% day-block bootstrap CI with the lower bound above 0, on at least 2 of 3 horizons, pooled
   over all 24 oblasts on the benchmark. The bar decides only the claim in the README; the tool uses the chosen
   forecaster whatever the result (switching models on the benchmark would be tuning on it).
7. **Saving the models and forecasts** (the user):
   - `models/<chosen>.joblib`: the forecaster the tool will use. For each H, the model is fitted on everything known
     at the map cutoff, and its Platt on the last 14 days of benchmark forecasts. The file also stores its metadata:
     fit window, rows, features, library versions and the git commit. Step 4's live `predict` loads it. Step 7 scores
     exactly this file on the holdout; its SHA-256 goes into PROCESS_LOG before the holdout is opened.
   - `results/choose_forecasts.csv.gz` and `results/benchmark_forecasts.csv.gz`: every row's forecasts (raw and
     calibrated) with the baselines and labels. Every number in the reports can be rechecked without retraining, and
     step 6 can draw from them.
   - joblib comes with scikit-learn; requirements.txt pins the library versions, so loading is reproducible.
   - The per-block models are not saved: they come back from the code, the data and the fixed seeds.
8. **CLAUDE.md claim** (the user): fix "Why this framing" now (beat a *frozen* clim28 in the probe; whether it beats a
   daily one and `RecentLevel` is step 3's question, Wrong #9); write the measured result after the benchmark.

## What gets built

### `alerts/model.py` (new)
- `CALIBRATION = 14 days`; `CHOSEN = None`, set only by the pre-registration commit.
- Candidates share one interface: `fit(rows, hours, asof)` on rows known at `asof`, then `predict(rows)` gives the raw
  probability.
  - `Boosting(clim=False, half_life=None)`: LightGBM with `AdversarialValidation.SETTINGS`, the probe's settings,
    reused rather than copied. `obl` is categorical; the features are `Features.NAMES`, plus `clim28_<H>` if `clim`.
    `weights(ts, asof)` = 0.5 ** ((asof − T) / half_life).
  - `CatBoost`: library defaults, `random_seed=0`, `cat_features=["obl"]`.
  - `Logistic`: a sklearn `Pipeline` with a `ColumnTransformer` and `LogisticRegression(max_iter=1000)`.
- `Platt`: `fit(p, y)` / `predict(p)`; logistic regression (C = 100) on logit(p clipped at 1e-4).
- `ForwardRun(candidates, split=DECISION, window=CALIBRATION)`:
  1. For each range (CHOOSE, then BENCHMARK if asked) and each block from `split.forward`, every candidate makes raw
     forecasts for the held rows from a fresh model fitted on `fit` only.
  2. For each block start s, `window(raw, s, hours)` holds the earlier raw-forecast rows with s − 14 d ≤ T and
     T + H ≤ s. A `Platt` fitted on them calibrates the block. A block whose window starts before the first raw
     forecast is a warm-up block and is not scored; this gives exactly CHOOSE 1–2. The first benchmark block calibrates
     on CHOOSE 5–6 (val), as Decision 4 says.
  3. `run` returns the held rows with `block`, `scored`, `raw_<name>` and `<name>`.
  4. `final(rows, raw, hours, asof)` fits the model on everything known at `asof` and its Platt on `window(raw, asof)`.
     This is what gets saved.

### `alerts/evaluate.py` (new)
- `Scores(rows, hours)`:
  - `brier(col)`;
  - `skill(col, ref)` → the point value and a 95% CI by a Kyiv-day block bootstrap (1,000 resamples, seed 0; ported
    from the probe's `skill_ci`, `research/probe/model.py:62-70`);
  - `per_oblast(col)` → n, base rate, Brier, skill vs clim28 and vs recent7, and the flag "quality not verified" when
    n < 100;
  - `reliability(col)` → 10 bins of mean forecast vs observed rate, with n;
  - `error_correlation(cols)` → the correlation matrix of y − p.
- `bar(skills)`: pass/fail per horizon and the overall verdict (≥ 2 of 3), as decision 6 states.

### `main.py evaluate {choose,benchmark}`
- The baseline columns are computed once per table: `Climatology(28)` daily, `Climatology(None)`, `RecentLevel`,
  `Persistence`.
- `choose`:
  - builds the table **only up to the test start**, so no label from the benchmark can enter;
  - runs A–E over CHOOSE;
  - writes `results/choose_report.md`, headed "these scores chose the model; not independent", with the pooled Brier
    and skills with CIs per horizon, raw vs calibrated, per-block Brier, the error correlations, the per-oblast table
    and the choice by the rule;
  - also writes `results/choose_forecasts.csv.gz`.
- `benchmark`:
  - refuses while `CHOSEN` is None;
  - builds the table up to `MAP_CUTOFF`, so the holdout is never read;
  - runs the chosen candidate over CHOOSE + BENCHMARK and scores BENCHMARK blocks 1–4 against the baselines;
  - writes `results/benchmark_report.md`, headed "historical benchmark, seen by the feasibility probe", with the bar
    verdict, per-block scores, the per-oblast table and the reliability table;
  - also writes `results/benchmark_forecasts.csv.gz` and `models/<chosen>.joblib`; the report gives the SHA-256.
- `requirements.txt`: add `catboost==1.2.10`, which also pulls in matplotlib, plotly, graphviz and six.
- Expected runtime: choose ≈ 2.5 min for LightGBM, ≈ 1.5 min for logistic, and CatBoost unmeasured (an estimate of
  5–10 min, measured on its first fit). Benchmark ≈ 30 fits plus the final one.

## Tests (TDD: agree these seams first, one red test at a time, worked examples)

`tests/test_model.py`
1. Platt maps each of two raw values to its observed rate (e.g. 0.2 → 0.1 and 0.6 → 0.5, on 100 rows each).
2. Recency weights halve every half-life (T = s, s − 60 d, s − 120 d → 1, 0.5, 0.25); no half-life → no weights.
3. A block is calibrated only on the window before it. The test uses synthetic rows and a stub candidate with a
   constant raw forecast, so Platt returns the window's base rate and shows which rows each calibrator used. It checks:
   - the 14-day window;
   - the T + H ≤ s purge;
   - that warm-up blocks are not scored;
   - that the first block of the next range uses the previous range's last blocks.
4. A saved forecaster gives the same forecasts after loading, and its metadata holds the fit window.

`tests/test_leakage.py`
5. End to end, for **every candidate type** (LightGBM, CatBoost, logistic): the calibrated forecast at T is identical
   from all records and from records known at T (`TruncationCheck`, synthetic world). Planted leak: a window without the
   T + H ≤ s purge is caught.
6. Real data (`need_api`), with a stub candidate so it runs in seconds and computes no score:
   - on CHOOSE and BENCHMARK, every calibration window obeys Decision 4 for H = 1/3/6;
   - the scored blocks are CHOOSE 3–6 and BENCHMARK 1–4;
   - all 24 oblasts appear.

`tests/test_evaluate.py`
7. Skill = 1 − sum(loss) / sum(ref loss), and the bootstrap resamples whole **Kyiv** days: a 21:30 UTC row belongs to
   the next Kyiv day, and a two-day worked example gives CI [−0.5, 0.5].
8. The per-oblast table flags 99 rows and not 100.
9. The bar passes with both lower bounds > 0 on 2 of 3 horizons, and fails when one reference fails on 2 horizons.

A test that passes at once gets a mutation check (`PYTHONDONTWRITEBYTECODE=1`, green state staged first).

## Order of work (branch `step-3-model`, one logical change per commit)

1. PROCESS_LOG **Decision 5** (decisions 1–8 above, written before any score) + the CLAUDE.md claim fix.
2. `Platt` + the three candidate types + catboost in requirements (tests 1–2).
3. `ForwardRun` with `final` and the save/load (tests 3–6).
4. `Scores` + `bar` (tests 7–9).
5. `main.py evaluate` with both stages. The benchmark code is committed before the choice is made.
6. Run `evaluate choose`; commit the report, the forecasts and a PROCESS_LOG entry with the choice.
   **Stop here: the user reviews the error correlations and the choice.**
7. Pre-registration commit: `CHOSEN = "<name>"` and the bar restated in PROCESS_LOG.
8. Run `evaluate benchmark` once, then commit:
   - the report, the forecasts and the model file;
   - PROCESS_LOG results, with the pre-registration hash and the model's SHA-256;
   - CLAUDE.md: step 3 ticked, the measured claim, and `model.py` / `evaluate.py` / `evaluate` / `models/` in the Code
     section.
9. Merge into `main`.

## Verification

- `.venv/bin/pytest`: the 72 old tests and the new ones pass.
- `python main.py evaluate choose`: the report covers blocks 3–6 and all 24 oblasts with n each; Donetska,
  Dnipropetrovska and Kharkivska are flagged at H = 6.
- `git log --oneline`: the pre-registration commit comes before the benchmark report.
- `python main.py evaluate benchmark`: 4 blocks, 24 oblasts, the bar verdict per horizon. `models/<chosen>.joblib`
  loads in a fresh Python and reproduces the last block's forecasts.
- `python main.py check` still writes the same data report.

## Not in this step

- LSTM and other deep models: deferred with reasons (decision 2).
- Blends and stacks: only after the error correlations, as a separate decision.
- Hyperparameter search: none; every candidate keeps fixed settings.
- AUC, feature importance, plots: step 6, if the page needs them.

## Resumed scope

The user requested completion of step 3 only. Steps 4–8 and the untouched holdout remain outside this work. Continue with the registered choice rule, without adding blends, model families or tuning. The benchmark code and rule are committed before selection; the selected name is committed before benchmark scoring. Existing frozen artifacts are never overwritten.

The save/load check compares the final forecaster before and after serialization. The final model is refitted at the cutoff, so its predictions need not equal those of the last weekly block model.
