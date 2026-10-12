# Step 6: the outlook page

Approved by the user on 2026-10-12.

## Context

CLAUDE.md step 6: "One HTML page that combines now, next hours, history and model quality." Decision 1: a CLI plus one self-contained HTML page, no server, no Streamlit.

- **The user, 2026-10-12:** "now" as a schematic tile map plus the table; the page comes from a separate `main.py page` command, and `predict` keeps its behaviour.

- **Every input already exists; step 6 only renders.**
  - Now + next hours: `results/forecast_log.csv`, newest moment T = 2026-10-11 12:46 UTC (15:46 Kyiv), 24 rows: 13 under alert (5 red, 8 yellow), 11 clear with p1/p3/p6. Made 20.3 h after T, so it is a replay (Decision 6).
  - History: `data.daily` and the tables `main.py history` builds (step 5), up to MAP_CUTOFF.
  - Model quality: `results/benchmark_summary.json` (skills, 95% CIs, bar per horizon) and `results/benchmark_forecasts.csv.gz` (Brier, reliability, regional n). Reading and scoring it takes 0.3 s.
  - Live score: `live.summary(live.score(...))` (step 4). The saved data end at T, so it is empty.
- **Measured while planning (nothing new scored):**
  - The CSV recomputes the report: Brier logistic / clim28 / recent7 = 0.1246 / 0.1348 / 0.1318 at 1 h, 0.1333 / 0.1448 / 0.1400 at 3 h, 0.1235 / 0.1323 / 0.1271 at 6 h.
  - The CSV renames the references to `clim28` / `recent7`; `Scores.per_oblast` needs `clim28_{h}` / `recent7_{h}`, so the page renames them back.
  - Benchmark n < 100 at every horizon: Dnipropetrovska (9) and Donetska (28) only.
  - `api_asof` = the log's newest T = 2026-10-11 12:46 UTC.
- **No new dependency.** Step 5's plan already said no matplotlib; there is no plotting library in `requirements.txt`. Charts are inline SVG built with f-strings, tables come from `DataFrame.to_html`.
- **Time.** It is 2026-10-12 ~14:30 Kyiv; steps 6–8 must be done by ~20:00. Step 6 gets about 1.5 h.

## Decisions (logged as Decision 8 in PROCESS_LOG)

1. **`main.py page`, offline**, writes `results/outlook.html`.
   - Now / next hours show the newest moment in the log: exactly what was logged and will be scored. No forecast is recomputed.
   - It refuses when the saved data end after the log's newest moment ("run `python main.py predict` first"), so the page is never staler than the data.
   - Flow: `fetch` → `predict` → `page`. `predict` prints and logs as before; only its table code moves to a shared helper.
2. **Self-contained and deterministic.** Inline CSS and SVG, no JavaScript, nothing loaded from outside. The page carries T and the log's `made_at`, never the wall clock, so a rerun writes the same bytes.
3. **The page says what each number is.**
   - Now is the state at T, where the saved data end. A forecast made more than 6 h after T is labelled a replay.
   - Model quality is the historical benchmark: seen by the probe, not the untouched holdout; pooled over 24 regions, not a guarantee for each region. Regions with benchmark n < 100 get a ⚠ next to their forecast.
   - The live log shows how many moments are logged and their score; until step 7 it reads "nothing scored yet".
   - History stops at MAP_CUTOFF, as the history report does. Marker weeks are markers, not causes; the red share is an upper bound.
4. **English text, Ukrainian region names**, as in `predict` and the reports.

## The page, top to bottom

1. **Header.** Alert Outlook; "data as of 2026-10-11 15:46 Kyiv (12:46 UTC), where the saved alerts.in.ua pull ends"; "made 20.3 h after T: a replay, not a live forecast".
2. **Now and next hours.**
   - A schematic tile map of Ukraine: 24 equal tiles placed roughly where the regions are (CSS grid, no geodata). Tile colour = 🔴 / 🟡 / clear; a clear tile shows P(a new alert within 3 h).
   - The `predict` table below it: region | now | 1 h | 3 h | 6 h, plus ⚠ for n < 100. "Under alert: no forecast; the model forecasts a new start for clear regions only."
3. **History, 2025-10-04 → map cutoff.**
   - One SVG chart, one bar per Kyiv week: the share of time under alert (24-region mean), split into red / yellow since the splice and grey (no level known) before it. Dashed markers at 2025-12-15 (raion-level alerting) and 2026-09-07 (yellow/red levels). Each bar has an SVG `<title>`, so hovering shows its numbers.
   - The headline numbers that `history` prints: year share, 28 d before / after the reform, red share since the splice.
   - Per region (in `<details>`): share year / 28 d before / after / after − before, red share since 09-12.
4. **Model quality.**
   - A table per horizon: n, base rate, Brier of model / clim28 / recent7, skill vs clim28 and vs recent7 with 95% CI, bar passed. Verdict line: "Strict bar: PASS (1 h and 3 h); at 6 h the gain vs recent7 is uncertain."
   - An SVG reliability chart: mean forecast vs observed per bin for 1/3/6 h, with the diagonal.
   - Live log: moments logged; the `live.summary` table, or "nothing scored yet: no logged window closes inside the saved data; the first live score is step 7".
5. **Footer.** Sources and the splice, the model SHA-256, links to the markdown reports, and the commands that regenerate the page.

## What gets built

**`alerts/page.py`** (new, about 70 lines): pure rendering, no data loading.
- `TILES`: region id → (row, col) on the schematic map, 6 columns × 5 rows, west to east and north to south:

  | row | 0 | 1 | 2 | 3 | 4 | 5 |
  |---|---|---|---|---|---|---|
  | 0 | Volynska 8 | Rivnenska 5 | Zhytomyrska 10 | Kyiv City 31 | Chernihivska 25 | Sumska 20 |
  | 1 | Lvivska 27 | Ternopilska 21 | Khmelnytska 3 | Kyivska 14 | Poltavska 19 | Kharkivska 22 |
  | 2 | Zakarpatska 11 | Ivano-Frankivska 13 | Vinnytska 4 | Cherkaska 24 | Dnipropetrovska 9 | Donetska 28 |
  | 3 | | Chernivetska 26 | Odeska 18 | Kirovohradska 15 | Zaporizka 12 | |
  | 4 | | | | Mykolaivska 17 | Khersonska 23 | |

- `tiles(rows, names)`: the tile map as HTML. A tile's label is the region name without " область"; long names wrap. If they are unreadable at phone width, the labels get short forms.
- `bars(weeks, notes)`: SVG stacked weekly bars from per-week red / yellow / grey shares.
- `reliability(tables)`: SVG of `Scores.reliability` for each horizon.
- `CSS`: colour tokens, a dark-mode media query, phone width with a 16 px gutter.

**`main.py`**
- `_table(rows, names)`: the now / 1 / 3 / 6 h table, moved out of `predict`. `predict` prints `md(_table(...))` as before; the page uses `.to_html()`.
- `_history()`: the computation part of `history` (the daily table, the weekly, per-region and level tables), moved out unchanged; `history` keeps the markdown. The report must stay byte-identical.
- `outlook()`: returns the page as a string.
  - log → newest moment; refuse if `D.api_asof(OBLAST_UIDS)` is later;
  - `_history()` → weekly red / yellow / grey shares (one groupby on `daily`), the per-region table, the headline numbers;
  - benchmark rows filtered as in `results/model_usage.md` (`scored & ts >= BENCHMARK[0]`) → `Scores.brier`, `reliability`, `per_oblast` n; skills, CIs and verdict from `benchmark_summary.json`;
  - `live.summary(live.score(log, history, asof, model))`.
- `page(args)`: writes `results/outlook.html`, prints one line. A `page` subparser.

## Tests (`tests/test_page.py`, TDD: one red test at a time, worked examples)

1. **Bars.** Week A: grey 0.25; week B: red 0.10 and yellow 0.30. The y-axis tops at the next 0.1 at or above the tallest bar, here 0.4, so on a plot of height H: A's grey rect is 0.625 H, B's red 0.25 H and its yellow 0.75 H, stacked on the red. A week with no level has no red or yellow rect.
2. **Reliability.** A bin with forecast 0.3 and observed 0.3 sits on the diagonal: at 0.3 of the width and 0.7 of the height from the top.
3. **Tiles.** `TILES` covers the 24 `OBLASTS` in distinct cells. With Volyn red, Rivne yellow and Lviv clear at p3 = 0.344: 24 tiles; Volyn's is red, Rivne's yellow, Lviv's shows "34%".
4. **Real data** (`test_real_data.py`, `need_api`), on `main.outlook()`. Every check must still hold after step 7's new pull:
   - nothing is loaded from outside: no `<script`, `src=`, `<link`, `@import` or `url(`;
   - all 24 region names, and the log's newest T in Kyiv time;
   - the last weekly bar is the map-cutoff week (2026-10-05): nothing from the holdout.

The guard "data newer than the log" is a one-line comparison and gets no test.

A test that passes at once gets a mutation check (`PYTHONDONTWRITEBYTECODE=1`, green state staged first). It counts only when the failure is the test's assertion (Wrong #18). For example: drop the grey part; flip the y-axis of the reliability chart; let the history run to the data end.

## Order of work (branch `step-6-page`, one logical change per commit)

1. Save this plan as `research/step-6-plan.md`, and add PROCESS_LOG **Decision 8**.
2. Move `_table` out of `predict` and `_history` out of `history`. Check: the history report is byte-identical, `predict` prints the same table and "already in" the log, and 108 tests pass.
3. `alerts/page.py` (tests 1–3). Load the `dataviz` skill before writing chart code.
4. `main.py page` + test 4; run it and commit `results/outlook.html`.
5. Docs, then merge into `main`:
   - PROCESS_LOG: the step-6 result;
   - CLAUDE.md: tick step 6; add `alerts/page.py` and `page` to the Code section.

Stage files by name. The untracked `research/reports/` is not part of this step.

## Verification

- `.venv/bin/pytest`: the 108 old tests and the new ones pass.
- `.venv/bin/python main.py page` twice gives the same `shasum`.
- `git diff results/history_report.md` is empty after `main.py history`; `predict` reports the moment as already logged and prints the same table.
- Cross-checks on the page: the weekly bar totals equal the history report's `share under alert`; the quality table equals `benchmark_report.md`; 13 regions under alert (5 red, 8 yellow) and 11 clear, as logged; the live section reads "nothing scored yet".
- `open results/outlook.html`: light and dark mode, and phone width (≤ 400 px) with no page-wide horizontal scroll.
- No `fetch` in this step: nothing under `data/` changes, and `score` still has nothing to score. The holdout stays unscored.

## Not in this step

- Real oblast borders: the map is schematic and needs no geodata.
- JavaScript, a server, auto-refresh or a scheduler.
- Threat types (live only), raion-level views, hour-of-day profiles.
- The holdout and live-log scores: step 7 runs them, then reruns `page`.
- Hosting the page (GitHub Pages); step 8 may link it from the README.
