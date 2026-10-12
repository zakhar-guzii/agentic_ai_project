# Step 5: history analytics

Approved by the user on 2026-10-12.

## Context

CLAUDE.md step 5: "Alert load over time, and the yellow/red levels since the reform." Decision 1 put both in scope. Decision 3 says levels are described, not forecast. Step 6 shows them on the page, so step 5 builds the data layer and a markdown report. The HTML and the charts are step 6.

- **Time.** It is 2026-10-12 ~13:05 Kyiv, and steps 5–8 must be done by ~20:00. Step 5 gets about 1 h.
- **The user, 2026-10-12:** the minimal scope: weekly load, the reform windows and the red share. No hour-of-day profile.
- **Data facts (measured while planning, nothing modelled):**
  - The spliced history covers 2025-10-03 → MAP_CUTOFF. Levels exist only in alerts.in.ua records, which means from SPLICE (2026-09-12 00:00 Kyiv). The map has no levels, so 09-07 → 09-11 is unlabelled.
  - History keeps only each record's **final** level, because yellow → red is an in-place update. "Red minutes" is therefore an upper bound on red time, and yellow is a lower bound.
  - Since the reform the map keeps overlapping records for one raion (+10–13% records). Count union episodes, never records (step 1, Wrong #5).
  - National monthly load: share under alert 0.24 (2025-10) → 0.32 (2026-08) → 0.41 (2026-09/10); starts per region-day 2.0 → 3.5 → 4.9–5.5. feasibility.md says the rise began in late August, *before* the reform, so a before/after difference is not the reform's effect.
  - Red share of alert minutes, SPLICE → MAP_CUTOFF: 0.46 overall, 0.66 on 09-12 and 0.22–0.31 on 10-08 → 10-10.
- **Holdout.** The analytics stop at MAP_CUTOFF, as `check`'s per-oblast table does. The ~18 h after it stay untouched until step 7.

## Decisions (logged as Decision 7 in PROCESS_LOG)

1. **One data function, `data.daily(records, lo, hi)`.** For each (Kyiv calendar day, region) on [lo, hi), it returns:
   - `minutes`: the minutes of that day inside the window (1380/1440/1500 on DST days, partial at the edges);
   - `alert`: minutes under alert (the union of oblast and raion records, i.e. `episodes` + `minute_grid`, as `daily_agreement` does);
   - `starts`: episode starts (clear → alert, restarts count, as in Wrong #11);
   - `red`: minutes under a red record, by the same union rule as `live.forecast`'s level. It is NaN for days before SPLICE, where no level exists.

   Weeks, months and reform windows are pandas groupbys on this table. No second aggregator.
2. **Reform windows:** 28 days on each side of `REFORM = 2026-09-07 00:00 Kyiv`. The same length removes the day-count bias. Both sides come from the map plus the splice; the seam Jaccard is 0.9994.
3. **Markers, not causes.** The report marks 2025-12-15 (raion-level alerting) and 2026-09-07 (levels). It states the late-August rise, so the before/after table is read as a description only.

## What gets built

**`alerts/data.py`**
- `REFORM` constant next to `SPLICE`.
- `daily(records, lo, hi, oblasts=…)`. It reuses `episodes`, `minute_grid` and the Kyiv-day binning of `daily_agreement`. It is about 15 lines.

**`main.py history`** (offline) writes `results/history_report.md`:
1. **Load over time.** A national weekly table (Kyiv weeks Mon–Sun) with the share of time under alert (mean over 24 regions) and starts per region-day. The two marker weeks are flagged.
2. **Per region.** Share under alert and starts/day for the whole year, the 28 d before REFORM and the 28 d after, plus the after/before ratio.
3. **Levels since the reform** (SPLICE → MAP_CUTOFF):
   - per region: alert hours and the red share;
   - national weekly red share;
   - the final-level caveat.
4. A header with the window, the sources and the holdout note, in the style of `check`.

The report is deterministic: a rerun writes the same bytes.

## Tests (`tests/test_daily.py`, TDD: one red test at a time, worked examples)

1. **Kyiv-day bins.** An alert 2026-09-20 20:30–21:30 UTC (23:30–00:30 Kyiv) gives 09-20: 30 min and 1 start; 09-21: 30 min and 0 starts. UTC bins would give 60 on 09-20.
2. **Overlap counts once.** Raion records 10:00–11:00 and 10:30–11:30 of one oblast give 90 min and 1 start, not 120 and 2.
3. **Restart counts.** 10:00–10:30 and then 10:31–11:00 give 2 starts.
4. **Red.**
   - A yellow raion record 10:00–12:00 plus a red raion record 11:00–11:30 give alert 120 and red 30.
   - A day before SPLICE has `red` NaN.
5. **Edges.**
   - 2026-03-29 (DST) has `minutes` = 1380.
   - An alert still on at `hi` is censored there.
   - A region with no alert gets rows of zeros, not missing rows.
6. **Real data** (`test_real_data.py`, `need_api`):
   - per region, the `starts` sum on [lo, MAP_CUTOFF) equals the `episodes` count of `check`'s table;
   - `red ≤ alert` everywhere;
   - `alert ≤ minutes` everywhere.

A test that passes at once gets a mutation check (`PYTHONDONTWRITEBYTECODE=1`, green state staged first). For example: bin by UTC date, count records instead of episodes, or fill red with 0 before SPLICE.

## Order of work (branch `step-5-history`, one logical change per commit)

1. Save this plan as `research/step-5-plan.md`, and add PROCESS_LOG **Decision 7**.
2. `data.daily` + `REFORM` (tests 1–5).
3. `main.py history` + test 6; run it and commit `results/history_report.md`.
4. Docs, then merge into `main`:
   - PROCESS_LOG: the step-5 result, with the measured findings;
   - CLAUDE.md: tick step 5; add `daily`, `REFORM` and `history` to the Code section.

Stage files by name. The untracked `research/reports/` is not part of this step.

## Verification

- `.venv/bin/pytest`: all 100 old tests and the new ones pass.
- `.venv/bin/python main.py history` writes the report. A second run gives the same bytes (`shasum`).
- Cross-check in pandas: the monthly national share recomputed straight from `minute_grid` matches the planning numbers above (0.24 / 0.32 / 0.41).
- `main.py check` still writes the same data report, `predict` reports the moment as already logged, and nothing after MAP_CUTOFF appears in the history report.

## Not in this step

- HTML and charts (step 6). No matplotlib is added; step 6 draws from `daily`.
- Levels as features (Decision 3), and threat types (live only).
- Any use of the holdout (step 7).
- Raion-level analytics.
- An hour-of-day profile by level (the user chose the minimal scope).
