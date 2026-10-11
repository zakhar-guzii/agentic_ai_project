# CLAUDE.md

## Project

**Alert Outlook** is our submission for the KSE Agentic AI School, Stage 2: "Time Series Analysis of air raid alerts in Ukraine". The full brief is in [research/brief.md](research/brief.md).

It is a Python tool that shows, for every oblast of Ukraine:
- **Now:** where an air-raid alert is on, and at which level (🟡 drones / 🔴 missiles or massed strike). Live data from alerts.in.ua.
- **Next hours:** the probability that a new alert starts within 1, 3 or 6 hours. It comes from a calibrated model trained on alert history.
- **History:** how the alert load has changed, including since the yellow/red level reform of 2026-09-07.

It runs as a CLI that prints a table and writes a single HTML page. Every forecast is logged and scored once its window has passed.

**Why this framing.** Our research ([research/](research/)) shows that "a new alert within 1–6 h" is the only target that beats a 28-day climatology on the latest weeks. Daily and "tonight" targets do not beat it. KSE also asks for a usable artifact.

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
- **Untouched holdout:** everything after the map cutoff. Make no decisions on it before step 7.
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
- `main.py`: the CLI. `fetch` pulls history (network). `check` builds the history and writes `results/data_report.md` (offline).
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
- [ ] 2. **Features and baselines.** Forecast-time features computed only from the past, climatology and persistence baselines, and leakage tests.
- [ ] 3. **Model and evaluation.** The calibrated 1/3/6 h forecaster, scored on the latest period against the baselines.
- [ ] 4. **Live forecast.** `predict` from alerts.in.ua, a log of every forecast, and its scoring.
- [ ] 5. **History analytics.** Alert load over time, and the yellow/red levels since the reform.
- [ ] 6. **Outlook page.** One HTML page that combines now, next hours, history and model quality.
- [ ] 7. **Final run.** The untouched holdout and the live-log score; then freeze the results.
- [ ] 8. **Submission.** README, reflection, AI-log export, a fresh-clone check, and the submission itself.

Rough schedule: steps 1–4 on Sunday, so that the live log runs overnight; steps 5–8 on Monday.
