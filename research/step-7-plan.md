# Step 7: the final run — the untouched holdout and the live-log score

Approved by the user on 2026-10-12.

## Context

CLAUDE.md step 7: "The untouched holdout and the live-log score; then freeze the results." Earlier steps already promised the following:

- **Decision 4.5.** A pre-registration commit comes before the holdout is opened.
- **Step 3, PROCESS_LOG.** Step 7 scores exactly `models/logistic.joblib` (SHA-256 `ffbce213…`), with no refit and no recalibration.
- **Decision 4, late revisions.** The fresh pull is compared with the 2026-10-11 pull for records with the same id whose start or end changed.
- **Decision 6.4–6.6.** The live log is scored for the first time here, and replays are reported apart from live forecasts. This is done since the step-6 review (Wrong #20).
- **The user, 2026-10-12.** Do one `fetch` in step 7. The live log then holds only the 2026-10-11 replay. The new moment T2 is logged but none of its windows closes, so no live forecast is scored. The report says so.

**Time.** It is 15:40 Kyiv. Step 7 should finish by about 17:15. After it come the serve and the map (with the cut at 19:00) and step 8.

**Holdout** = everything after MAP_CUTOFF (2026-10-10 19:03 UTC) up to `api_asof` of the new pull: about 41 h, 3 Kyiv days (the first and the last partial).

## Pre-registration (Decision 10; committed before `fetch`)

1. **Model.** `models/logistic.joblib`, SHA-256 `ffbce213…`. No refit, no recalibration, no tuning. Whatever the result, the logistic model is kept.
2. **Rows.** As in the benchmark:
   - 30-min moments on the :00 and :30 grid, regions clear at T, all 24 regions;
   - T in [MAP_CUTOFF, END), where END = `api_asof` of the step-7 pull;
   - for horizon H, only rows with T + H ≤ END (closed windows).
3. **References.** Daily clim28 (counted at 00:00 Kyiv) and recent7, computed exactly as for the benchmark.
4. **Scoring.**
   - Brier for the model, clim28 and recent7;
   - skill with the registered Kyiv-day bootstrap (1,000 resamples, seed 0);
   - the strict bar computed as registered;
   - a per-Kyiv-day table of skills;
   - per region: n, with ⚠ where n < 100;
   - reliability.
   - **Expected:** with 3 days the day-bootstrap is wide and probably inconclusive. That is reported as it is, with no claim beyond what it shows, and no method changed afterwards.
5. **Live log.** `live.summary` separately for live and replay. The 2026-10-11 moment is a replay. T2 is not scored: its windows are still open.
6. **Late revisions.** Fresh pull vs `20261011T1247Z`, same `id`:
   - records with a changed `started_at`;
   - records with a changed `finished_at` that was not null in the old pull;
   - a changed `alert_level`;
   - counts, and how many start before MAP_CUTOFF (those touch the benchmark).
7. **Freeze.** `holdout` runs once. It refuses to overwrite its artifacts, as `evaluate` does. After it, no more `predict` before submission.

## Code (branch `step-7-final`)

**`alerts/live.py` → `holdout(records, lo, hi, model)`**, about 10 lines:
- `ForecastTable(records, start, hi)`, where start = Kyiv midnight of `lo − 29 D`. This puts the moments on the :00/:30 grid and gives clim28 its 28 days.
- Add `Climatology(28).predict(rows)` and `RecentLevel().predict(rows)`, then keep `ts ≥ lo`, then add `model.predict(rows)`.
- Set `y{h}` = NaN where T + H > hi, as `score` does.
- Reuses only existing classes: `ForecastTable` and `AlertGrid` (alerts/features.py), the `Climatology` and `RecentLevel` baselines (alerts/baselines.py), and `Forecaster.predict` (alerts/model.py).

**`main.py holdout`**: offline. It writes:
- `results/holdout_report.md`;
- `results/holdout_forecasts.csv.gz` (gzip with mtime=0);
- `results/holdout_summary.json`, with the model SHA, END, n per horizon, skills and CIs, the bar, the revision counts and the SHA-256 of the pull MANIFEST.

Details:
- It refuses if the artifacts exist, or if the model SHA ≠ `ffbce213…`.
- Scoring reuses `Scores` (`brier`, `skill`, `per_oblast`, `reliability`) and `bar` from alerts/evaluate.py.
- The revision check loads both pulls through `_frozen_api(dir)` (main.py).
- The live-log section uses `live.summary(live.score(...))` and `live.NOTE`.

**Page** (`main.py outlook`):
- In Model quality, add an "Untouched holdout" table from `holdout_summary.json`, only when the file exists. It is the same shape as the benchmark table.
- The intro text no longer says "is scored in step 7".
- The page stays deterministic.

**Tests (TDD)**
1. Synthetic, `tests/test_live.py`: one Volyn start at 14:00, lo = 12:00, hi = 18:00.
   - Rows only at T ≥ lo, on :00/:30.
   - `y6` is set only at T = 12:00; at T = 12:30 it is NaN.
   - `y3` = 1 for Volyn at T = 12:00 and NaN for T > 15:00.
   - Every clear row has p1/p3/p6, clim28 and recent7.
2. Real data, frozen pull, before the fetch: `holdout(records, lo, hi=MAP_CUTOFF, MODEL)` over the last benchmark week reproduces `clim28` and `recent7` of `benchmark_forecasts.csv.gz` on the same (obl, ts) to 1e-12. This proves the holdout path builds rows and references as the benchmark did, without touching the holdout.
3. Mutations (`PYTHONDONTWRITEBYTECODE=1`, caught on the assertion):
   - `T + H < hi` instead of `≤`;
   - the table start without the 29-day lead, which test 2 catches through clim28.

## Order of work

1. Save the plan as `research/step-7-plan.md`, and add PROCESS_LOG **Decision 10** (the pre-registration above). Commit: this is the registration commit, and its hash goes into the report.
2. Write `live.holdout` + `main.py holdout`, test-first. Tests 1–2 pass on the old data. Commit.
3. **Then** `.venv/bin/python main.py fetch`, in the background, about 13 min. Check the token count in the saved files: `fetch` prints it, and it must be 0. Commit the raw pull with its MANIFEST.
4. `predict` logs T2. Made about 25 min after T2, so it is live, but no window closes. Commit `forecast_log.csv`.
5. `main.py holdout` runs once, plus `main.py score`. Commit the artifacts.
6. `main.py history` and `page`.
   - The history report may move slightly from late revisions before the cutoff. The diff is checked and logged, not hidden.
   - `check`'s data report is the step-1 artifact and is not regenerated.
7. Docs, then merge into `main`:
   - PROCESS_LOG: step-7 result, with the numbers as they are;
   - CLAUDE.md: tick step 7, the holdout results in "Why this framing", `holdout` in the Code section.

## Verification

- `.venv/bin/pytest`: everything passes after the fetch. Real-data tests that pin pull-specific values are checked, not loosened silently.
- `holdout` run a second time refuses. `shasum` of `outlook.html` is stable across two `page` runs.
- Cross-check: recompute the holdout Brier from `holdout_forecasts.csv.gz` with plain NumPy; it must equal the report.
- `score` shows only `replay` rows, from the 10-11 moment, at 1, 3 and 6 h.
- `git grep` finds no token. Nothing under `data/raw/map/` changed.

## Not in this step

- A second fetch or a live forecast scored: the user chose one fetch. The T2 forecast stays logged for whoever scores it later.
- Serve, the real map and step 8: as in [research/step-6-review-plan.md](step-6-review-plan.md).
