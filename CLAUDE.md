# CLAUDE.md

## Project

**Alert Outlook** is our submission for the KSE Agentic AI School, Stage 2: "Time Series Analysis of air raid alerts in Ukraine". The full brief is in [research/brief.md](research/brief.md).

It is a Python tool that shows, for every oblast of Ukraine:
- **Now:** where an air-raid alert is on, and at which level (🟡 drones / 🔴 missiles or massed strike). Live data from alerts.in.ua.
- **Next hours:** the probability that a new alert starts within 1, 3 or 6 hours. It comes from a calibrated model trained on alert history.
- **History:** how the alert load has changed, including since the yellow/red level reform of 2026-09-07.

It runs as a CLI that prints a table and writes a single HTML page. Every forecast is logged and scored once its window has passed.

**Why this framing.** In the feasibility probe, "a new alert within 1–6 h" was the only target that beat a frozen 28-day climatology; daily and "tonight" targets did not (Wrong #9). Step 3 compared five candidates and selected calibrated logistic regression. On the historical benchmark, Brier skill versus daily clim28 is +7.5% / +7.9% / +6.7%, and versus recent7 is +5.5% / +4.8% / +2.8% for 1/3/6 h. Both reference comparisons have positive 95% Kyiv-day bootstrap lower bounds at 1 and 3 h, passing the registered bar; at 6 h the gain against recent7 is uncertain. These are pooled results across 24 modeled regions, not a guarantee for each region. The benchmark was already seen by the probe; the untouched holdout remains for step 7.

**Brief requirements:**
- use the most recent data;
- evaluate on the latest period;
- no leakage: nothing the model uses at forecast time T may come from after T.

Text and Telegram data are optional in the brief. We leave them out, because the probe measured only a small gain from them.

**Submission.** Deadline: Mon 2026-10-12 23:59 Kyiv; aim for 20:00. We submit:
- the GitHub repo with working code;
- the full AI conversation log (all Claude Code sessions);
- a reflection of about 100 words.

KSE grades the process. The AI log is their primary signal.

**Data (as of 2026-10-11):**
- **History before the splice:** a frozen snapshot of the official map (map.ukrainealarm.com) in [data/raw/map/](data/raw/map/).
  - It covers 2025-10-03 → 2026-10-10 19:03 UTC (the map cutoff), and its provenance is in `MANIFEST.json`.
  - The site went behind a Cloudflare challenge on 2026-10-11; do not try to bypass it.
- **From the splice on, and live:** the alerts.in.ua API.
  - Raw `month_ago` pulls, gzipped with a MANIFEST, are committed under `data/raw/alerts_in_ua/<UTC stamp>/`.
  - `month_ago` is a rolling 30-day window, limited to 2 requests per minute; a full pull of 24 regions takes about 13 min.
  - History has no `threats` field and carries only the final `alert_level` of each record.
- **Splice:** alerts that start before 2026-09-12 00:00 Kyiv (`SPLICE`, 09-11 21:00 UTC) come from the map; later ones come from alerts.in.ua.
- **Untouched holdout:** everything after the map cutoff. It is the final check; make no decisions on it before step 7.
- **Token:** it lives in `.env` as `ALERTS_IN_UA_TOKEN`.
  - Never print it and never paste it into the chat, because the chat log is submitted.
  - Send it only in the `Authorization` header.
- **Data traps:** the measured ones are in [research/feasibility.md](research/feasibility.md), [research/data-sources.md](research/data-sources.md) and PROCESS_LOG ("Wrong #n"). The ones that matter most:
  - the map is not AIR-only;
  - `location_oblast_uid` is not the oblast id;
  - the map marks ongoing alerts with the end sentinel `0001-01-01`;
  - since the level reform the map keeps overlapping records for one raion, so count union episodes, never records.

**Code:**
- `alerts/api.py`: the alerts.in.ua client, with a paced, resumable history pull.
- `alerts/data.py`: `load_map`, `load_api` → `history` (the splice) → `episodes` (per-oblast union, censored at `asof`) → `minute_grid`. Also `compare`, `daily_agreement` and `unmatched` for the seam checks.
- `alerts/features.py`: `AlertGrid` (per-oblast minute grid; a query for T reads minutes before T only) → `Features` → `ForecastTable` (30-min rows where the oblast is clear at T, labels `y1`/`y3`/`y6`).
- `alerts/splits.py`: `Split` with the purge; `DECISION` = train / val / test, where test is a historical benchmark (seen by the probe). `forward()` gives the sequential forecast checks: blocks of unique moments, each fitted only on labels known at its start. `CHOOSE` and `BENCHMARK` are step 3's ranges; the step-3 contract is in PROCESS_LOG, Decision 4.
- `alerts/baselines.py`: `Climatology(28 | None)` (recounted daily), `RecentLevel`, `Persistence`. Nothing is trained.
- `alerts/checks.py`: `TruncationCheck` (leakage) and `AdversarialValidation` (drift: time blocks with a 7-day gap; not a check of forecasting).
- `alerts/model.py`: five fixed candidates, sequential OOF calibration, final fitting and trusted joblib persistence. `CHOSEN = "logistic"` was committed before benchmark scoring.
- `alerts/evaluate.py`: Brier scores, 1,000-resample Kyiv-day bootstrap, regional counts/flags, reliability, error correlations and the registered bar.
- `main.py`: the CLI. `fetch` pulls history (network). `check` writes the data report (offline). `evaluate choose|benchmark` writes frozen forecasts, reports and summaries; it refuses to overwrite existing artifacts.
- `models/logistic.joblib`: the frozen final 1/3/6 h forecaster, fitted at MAP_CUTOFF. Usage and result-reading examples: `results/model_usage.md`.
- `tests/`: pytest. There is one file per seam; `test_real_data.py` holds the acceptance bar on the real data.
- The probe in [research/probe/](research/probe/) is a frozen research record. Do not edit it.

**How we work:**
- **Environment.** Use the venv in `.venv/` (`python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`). Run everything through `.venv/bin/python` and `.venv/bin/pytest`.
- **Tests first** (the /tdd skill):
  - agree the seams before writing tests;
  - write one red test, then the minimal code, then repeat;
  - expected values come from worked examples;
  - a test that passes at once must be checked by a mutation, run with `PYTHONDONTWRITEBYTECODE=1` (a stale `.pyc` once faked a failure).
- **Commits** go on a step branch (for example `step-1-data`), one logical change per commit, with plain English messages. Merge into `main` once the step is done.

**Language:** English for code and docs. Chat with the user in Ukrainian.

## Steps

Each step gets its own plan before work starts. Decisions and caught errors go to [PROCESS_LOG.md](PROCESS_LOG.md).

- [x] 1. **Data.** Build the alert history from the map snapshot plus alerts.in.ua: clean it, build per-oblast alert series, and check the seam between the sources. Seam Jaccard 0.9994; report in `results/data_report.md`.
- [x] 2. **Features and baselines.** Forecast-time features computed only from the past, climatology and persistence baselines, and leakage tests. Probe reproduced; leakage tests pass on 30 real moments. Wrong #9: against a daily-recounted 28-day climatology the probe's model gains only about +0.02 to +0.06, and the 7-day recent level is as strong (PROCESS_LOG). Split fix (Decision 4): rows sorted by time, sequential forecast checks, time-blocked AV (train vs test AUC 0.944, not 0.9995), all 24 oblasts. Review fixes: Wrong #11 (count every start), Wrong #12 (AV never fits held rows).
- [x] 3. **Model and evaluation.** Calibrated logistic regression selected from five candidates on `CHOOSE` blocks 3–6 and scored once on four historical benchmark blocks. All 24 modeled regions (23 oblasts + Kyiv City), with regional counts/flags. Registered strict bar passes at 1 and 3 h; 6 h versus recent7 remains uncertain. Final model and forecast rows saved; see `results/benchmark_report.md`.
- [ ] 4. **Live forecast.** `predict` from alerts.in.ua, a log of every forecast, and its scoring.
- [ ] 5. **History analytics.** Alert load over time, and the yellow/red levels since the reform.
- [ ] 6. **Outlook page.** One HTML page that combines now, next hours, history and model quality.
- [ ] 7. **Final run.** The untouched holdout and the live-log score; then freeze the results.
- [ ] 8. **Submission.** README, reflection, AI-log export, a fresh-clone check, and the submission itself.

