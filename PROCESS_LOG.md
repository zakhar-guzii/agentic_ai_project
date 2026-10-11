# Process log

Decisions and caught errors, newest last.
- A decision is written as: proposal → check → result → adjustment.
- An error gets a "Wrong #n" entry with before/after facts.

## 2026-10-10: research

The research trail is in [research/](research/):
- [brief.md](research/brief.md): the task;
- [data-sources.md](research/data-sources.md): sources, freshness and leakage traps;
- [prior-solutions-survey.md](research/prior-solutions-survey.md): what 115 other repos did;
- [feasibility.md](research/feasibility.md): our own measurements.

Main measurement: on 2026-09-13 → 10-10, a LightGBM + Platt forecaster of "a new alert starts within H" beats a 28-day oblast × hour climatology.

| | 1 h | 3 h | 6 h |
|---|---|---|---|
| Brier skill vs 28-day climatology | +0.12 | +0.15 | +0.18 |

All 95% CIs exclude 0. "Alert tonight" and "daily alert-minutes" did not reliably beat climatology.

## 2026-10-11

### Decision 1: concept and scope

- **Proposal.** Combine the "forecast + live tool" option with the "product dashboard" option, as **Alert Outlook**: what is happening now, the forecast for the next hours, and history, per oblast.
- **Form.** A CLI plus one self-contained HTML page. No server and no Streamlit.
- **Extras in scope:**
  - a live log of every forecast, scored once its window closes;
  - the yellow/red alert levels since the 2026-09-07 reform.
- **Dropped: the text ablation.** The probe measured only a small gain:
  - a per-oblast count of @kpszsu posts cut Brier by just 1.8–2.5% at 3 h;
  - national post counts and @radar_raketaa added nothing;
  - the brief makes text optional.
- **Language:** English for code and docs.
- **Planning.** CLAUDE.md holds the project description and 8 steps. Each step gets its own plan before work starts.

### Wrong #1: "the map endpoint is a reliable keyless source"

- **Before.** feasibility.md recommended map.ukrainealarm.com's ranged-history endpoint as the main source: no key, fresh to the minute, 351 requests without an error on 2026-10-10.
- **Check, 2026-10-11 11:18 UTC.**
  - The map page returns HTTP 403 with `cf-mitigated: challenge` (Cloudflare "Just a moment…"). This happens with curl and with Python urllib, and with any User-Agent.
  - The API path itself answers 400 without a token. Tokens come only from the challenged page, so scripted fetching is no longer possible.
- **Adjustment.**
  - We do not try to bypass the challenge.
  - Yesterday's raw responses existed only in a temporary scratchpad. They are now copied to [data/raw/map/](data/raw/map/), with per-file SHA-256 in `MANIFEST.json`:
    - 351 files, 124,688 records;
    - `startDate` from 2025-10-03 01:36 to 2026-10-10 19:06 UTC;
    - fetched 19:02–19:15 UTC.
  - This frozen snapshot is the training and evaluation history. Everything after it comes from alerts.in.ua.
- **Lesson.** Caching raw responses on day one is what keeps the project reproducible. The official Telegram channel froze on 09-07, and now the map is closed too.

### Wrong #2: "an alerts.in.ua key is unlikely before the deadline"

- **Before.** feasibility.md §5 assumed the form-based key would not arrive in time, so nothing was planned around it.
- **Check.** The key arrived on 2026-10-11.
- **Adjustment.** alerts.in.ua becomes the source for everything after the snapshot and for the live page. It also provides the yellow/red levels and threat types.

Limits from the API documentation:
- history: 2 requests per minute;
- overall: soft limit 8–10 requests per minute, hard limit 12.

The token lives only in `.env`, which is git-ignored. It is never printed or pasted into the chat, because this chat log is submitted.

### Note for step 3: test disclosure

The feasibility probe has already scored the window 2026-09-13 → 10-10. That window therefore counts as **seen**:
- we report it as such;
- we do not tune anything on it.

The honest tests are two:
- the untouched days after 2026-10-10 19:00 UTC, run once after a pre-registration commit;
- the live forecast log.

### Open questions for step 1

Check these with raw alerts.in.ua samples before writing any parser:
- Does `month_ago` history return `threats[]`? In the JustJimer copy of the history the field is empty in all 18,146 rows.
- What is the exact `month_ago` window? Does it include standing alerts that started earlier?
- How does a yellow → red change appear: as an updated record, or as a new one?
- Do the `location_type` values and the region IDs match the probe's mapping (ukrainealarm state IDs)?
