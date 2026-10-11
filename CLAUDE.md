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
- **History:** a frozen snapshot of the official map (map.ukrainealarm.com) in [data/raw/map/](data/raw/map/), covering 2025-10-03 → 2026-10-10. Its provenance is in `MANIFEST.json` there. The site went behind a Cloudflare challenge on 2026-10-11; do not try to bypass it.
- **Fresh and live data:** the alerts.in.ua API. The token lives in `.env` as `ALERTS_IN_UA_TOKEN`. Never print it and never paste it into the chat, because the chat log is submitted.
- **Measured facts and data traps:** [research/feasibility.md](research/feasibility.md) and [research/data-sources.md](research/data-sources.md). The probe code behind those numbers is in [research/probe/](research/probe/).

**Language:** English for code and docs. Chat with the user in Ukrainian.

## Steps

Each step gets its own plan before work starts. Decisions and caught errors go to [PROCESS_LOG.md](PROCESS_LOG.md).

- [ ] 1. **Data.** Build the alert history from the map snapshot plus alerts.in.ua: clean it, build per-oblast alert series, and check the seam between the sources.
- [ ] 2. **Features and baselines.** Forecast-time features computed only from the past, climatology and persistence baselines, and leakage tests.
- [ ] 3. **Model and evaluation.** The calibrated 1/3/6 h forecaster, scored on the latest period against the baselines.
- [ ] 4. **Live forecast.** `predict` from alerts.in.ua, a log of every forecast, and its scoring.
- [ ] 5. **History analytics.** Alert load over time, and the yellow/red levels since the reform.
- [ ] 6. **Outlook page.** One HTML page that combines now, next hours, history and model quality.
- [ ] 7. **Final run.** The untouched holdout and the live-log score; then freeze the results.
- [ ] 8. **Submission.** README, reflection, AI-log export, a fresh-clone check, and the submission itself.

Rough schedule: steps 1–4 on Sunday, so that the live log runs overnight; steps 5–8 on Monday.
