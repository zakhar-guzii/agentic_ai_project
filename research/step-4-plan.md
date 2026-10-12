# Step 4: live forecast

Approved by the user on 2026-10-12.

## Context

CLAUDE.md step 4: "`predict` from alerts.in.ua, a log of every forecast, and its scoring."

- Step 3 froze `models/logistic.joblib` (fitted at MAP_CUTOFF, SHA-256 `ffbce213…`). Under Decision 5, step 4 loads this file and step 7 scores exactly this file.
- Decision 3: the live log stores the current alert levels with every forecast.
- Decision 4: the log keeps what the API showed at T. Scoring compares those features with features recomputed from the final history, which shows the effect of late API revisions.
- **The user, 2026-10-12:**
  - Plan on the data we already have.
  - `predict` must not re-download history: a full `month_ago` pull takes about 13 min at 2 requests/min.
  - The saved data are refreshed only by `fetch` (daily).
  - Forecast as of the time the saved data reach.
- **Saved data: one pull, `20261011T1247Z`.**
  - Its regions were fetched 12:47:56–13:13:07 UTC.
  - The server's `meta.last_updated_at` reads 12:46:28–13:12:39. It is always earlier than the fetch, and regions fetched minutes apart share it, so it is the server's snapshot time.
  - So every region is complete up to **2026-10-11 12:46 UTC** (15:46 Kyiv).
- **Time.** It is 2026-10-12 11:34 Kyiv, and steps 4–8 remain before about 20:00. Step 4 gets about 2 h.

## Decisions (logged as Decision 6 in PROCESS_LOG)

1. **T is where the saved data end, not the wall clock.**
   - For each of the 24 regions, take its newest saved `last_updated_at`. T is the earliest of these, floored to the minute.
   - `predict` makes no network call and trains nothing. It prints how old the data are.
   - Each `fetch` gives one new forecast moment.
   - Data trap: `fetched_utc` can be about 1.5 min later than the server snapshot. Using it would show a start inside that gap as "clear".
   - A pull takes about 25 min, so the regions fetched later hold records after T. They are cut the way `TruncationCheck.known_at` cuts records: starts at or after T are dropped, and ends after T are treated as unknown.
2. **24 rows per T.**
   - A region under alert in the minute before T (`under`, as defined in `Features`) gets a `level`: red if any oblast or raion record covering that minute is red, otherwise yellow. It gets no probability, because the model forecasts a new start for a clear region only.
   - A clear region gets the model's `p1/p3/p6`, plus the two registered references:
     - `clim28`, counted at 00:00 Kyiv of T's day, as in the benchmark;
     - `recent7`.

     This lets the live score be read the same way as the benchmark.
3. **Threats are not logged.** History has no `threats` field, and T is not "now". The levels from Decision 3 stay.
4. **The log is `results/forecast_log.csv`.** It is append-only and committed.
   - Columns: `ts`, `made_at`, `obl`, `under`, `level`, `p1/p3/p6`, `clim28_*`, `recent7_*`, the 19 features, and `model_sha256`.
   - A T that is already in the log is not appended again; the forecast is deterministic.
   - `made_at` > T + H marks a replay from the saved pull rather than a live forecast. Step 7 reports the two separately.
5. **Scoring runs on demand and stores nothing.**
   - A logged clear row is scored for horizon H once T + H ≤ the data's own T. Its label y_H is 1 if an episode starts in [T, T + H) in the current history.
   - Per horizon: n, and the Brier score of the model, clim28 and recent7.
   - Decision 4's revision check: the forecast at T is recomputed from the current history. Report the rows whose features changed, and the model's Brier on the recomputed features.
   - No bootstrap CI: by the deadline the log holds one forecast moment per pull.
6. **Holdout rule.**
   - Every T falls after MAP_CUTOFF, so the outcomes belong to the untouched holdout.
   - In step 4, `score` runs only in synthetic tests. Its first real run is in step 7, after that step's pre-registration.
   - Until a newer pull exists, no logged window closes inside the saved data anyway.

## What gets built

**`alerts/data.py`**
- `api_asof(uids, api_dir=API_DIR)` computes decision 1 from the MANIFESTs that `load_api` already globs.
- A uid that was never fetched raises a `KeyError`.

**`alerts/live.py`** (new, about 50 lines). It reuses existing code:
- `forecast(records, T, model)` returns 24 rows:
  - features: `Features(AlertGrid(known, T − 8 d, T)).at([T])`, with `known = records[records.start < T]`;
  - model probabilities: `model.predict(clear)` (`Forecaster`);
  - recent7: `RecentLevel().predict(clear)`;
  - clim28: `Climatology(28).predict(past + clear, asof=Kyiv midnight)`, where `past = ForecastTable(known, midnight − 28 d, T).rows`;
  - `level`: from oblast and raion records with `start < T` whose end is missing or later than T − 1 min.
- `log(rows, path)` appends unless `rows.ts` is already in the file, and returns whether it appended.
- `score(log, records, asof, model)` returns the logged clear rows with:
  - `y1/y3/y6` from `AlertGrid.start_within`, NaN while T + H > asof;
  - `revised`;
  - `final_p1/p3/p6` from `forecast(records, T, model)`.

**`main.py`**
- `predict`:
  1. Builds the history with `D.history(D.load_map(), D.load_api())`.
  2. Sets `T = D.api_asof(OBLAST_UIDS)`.
  3. Loads the model with `Forecaster.load("models/logistic.joblib")` and calls `live.forecast`, then adds `made_at` and `model_sha256`.
  4. Prints a table: the region name (from regions.json), its state now (🔴/🟡 alert, or clear), and 1/3/6 h in %, plus "data as of T (Kyiv), N h old".
  5. Logs the rows with `live.log` to `results/forecast_log.csv`.
- `score`:
  - takes the same inputs plus the log;
  - prints, per horizon and with `md()`: n; the Brier score of the model, clim28, recent7 and the model on recomputed features; and the number of revised rows;
  - if no window has closed yet, prints "nothing to score before <T>" instead.

## Tests (`tests/test_live.py`, TDD: one red test at a time, worked examples)

Unless a test says otherwise, it uses a synthetic world at T = 2026-10-01 12:00 UTC. Where a model is needed, it uses the real frozen model.

1. **`api_asof`.**
   - Setup: pull 1 has uid 3 updated at 12:46:28 and uid 4 updated at 12:48:30; pull 2, a day later, has uid 3 only.
   - Expect 12:48: uid 4 pins it.
   - `api_asof([3, 4, 5])` raises.
2. **`forecast`, the state now.**
   - Volyn has a yellow raion alert still on and a red one that ended at 11:59:30 → under alert, red.
   - Rivne has a yellow alert still on → under alert, yellow.
   - Lviv's alert ended at 10:20, and a red one starts at 12:05 → clear, no level.
3. **`forecast`, the probabilities.** `p*`, `clim28_*` and `recent7_*` are in [0, 1] for exactly the 22 clear regions, and NaN for Volyn and Rivne.
4. **Leakage.** `TruncationCheck(world).mismatches(forecast at m, moments) == []`, on a random world with alerts still on at the end (as in test_leakage).
5. **`log`.** Logging twice with the same T leaves one copy of the 24 rows, and `ts` reads back as the same UTC moment.
6. **`score`, the labels.**
   - Setup: Volyn starts an alert at T + 2 h; asof is T + 4 h.
   - Volyn's y1/y3/y6 = 0/1/NaN, and Lviv's = 0/0/NaN.
   - Regions under alert at T are not scored.
7. **`score`, the revisions.** Lviv's alert end is revised from 09:00 to 09:30 after the log was written. Expect `revised` for exactly Lviv and its 5 neighbours (through `nb_alert_min_24h`).
8. **Real data (`need_api`).** `forecast` at the saved T gives 24 rows, with a level for every region under alert and a finite p for every clear one.

A test that passes at once gets a mutation check (`PYTHONDONTWRITEBYTECODE=1`, green state staged first). For example, for test 4: count levels from records that start after T.

## Order of work (branch `step-4-live`, one logical change per commit)

1. Save this plan as `research/step-4-plan.md`, and add PROCESS_LOG **Decision 6** (the decisions above).
2. `api_asof` (test 1).
3. `live.forecast` (tests 2–4).
4. `live.log` and `live.score` (tests 5–7).
5. `main.py predict` and `score`, plus test 8.
6. Run `predict` on the saved pull, and commit `results/forecast_log.csv`.
7. Update the docs, then merge into `main`:
   - PROCESS_LOG: the step-4 result;
   - CLAUDE.md: tick step 4 and reword it ("from the saved alerts.in.ua pulls"); add `live.py`, `predict`, `score` and the log to the Code section.

Stage files by name. The untracked `research/reports/` is not part of this step.

## Verification

- `.venv/bin/pytest`: all old and new tests pass.
- `.venv/bin/python main.py predict`:
  - shows 24 regions as of 2026-10-11 12:46 UTC (15:46 Kyiv), with the data age;
  - the log then holds 24 rows, and a second run adds none.
- Cross-check in pandas: the regions shown under alert are exactly the regions with an oblast or raion record covering 12:45–12:46 in the pull.
- `.venv/bin/python main.py score` prints "nothing to score", because no window has closed inside the saved data. The holdout stays unscored.
- `main.py check` writes the same data report, and `evaluate` still refuses to overwrite its artifacts.

## Not in this step

- Network calls or retraining in `predict` (the user's rule). A forecast for the real next hours needs a `fetch` first (about 13 min).
- A scheduler for a daily `fetch` + `predict`.
- Threat types: they exist only live, in `active.json`.
- The real live-log score and its report: step 7.
- The HTML page: step 6.
