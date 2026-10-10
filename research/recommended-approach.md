# Recommended approach: what I would build

_Written 2026-10-10 (Saturday evening). Deadline: **Monday 2026-10-12, 23:59 Kyiv**. This is my recommendation, built on [feasibility.md](feasibility.md) (our measurements), [prior-solutions-survey.md](prior-solutions-survey.md) (what 115 other repos did), [data-sources.md](data-sources.md) and [brief.md](brief.md). It is a plan, not a commitment; the user decides._

## 1. The project in one sentence

**A calibrated per-oblast forecast of "will a new air-raid alert start here in the next 1 / 3 / 6 hours?", built on data fresh to the hour, evaluated once on the latest weeks against honest baselines, with tests showing it cannot see the future.**

Why this framing:
- It is the only target that measurably beats a strong baseline on the latest period. Brier skill vs a 28-day climatology is +0.12 / +0.15 / +0.18 at 1 / 3 / 6 h, on 2026-09-13 → 10-10, and all confidence intervals exclude zero ([feasibility.md §3](feasibility.md)).
- "Alert tonight" and "daily alert-minutes" do not reliably beat climatology. They go in as an honest baselines section only.
- It answers the brief literally: the most recent data, evaluation on the latest period, no leakage.
- The October competitors also forecast onsets. **What none of them has** is listed in §2 ([prior-solutions-survey.md §5](prior-solutions-survey.md)).

## 2. What makes it different

1. **Data that runs past the 2026-09-07 freeze of the official file, with a validated seam.** We use the official map's ranged history, which matches the frozen file at Jaccard 0.994 and alerts.in.ua at 0.998. Every other repo either stops at the freeze or falls back to the volunteer feed, which covers only about 30% of official alert time.
2. **A data-trap and regime story.** Each item is backed by a number:
   - the `level=='oblast'` trap, and the "feed died" myth it causes;
   - duplicates;
   - the 08-29 → 09-02 outage, where Vadimkin shows 0 starts against 500 on the map;
   - the freeze;
   - standing hromada alerts that make whole oblasts look permanently under alert;
   - volunteer under-coverage;
   - the late-August escalation, which makes a full-history climatology 20–40% worse than a 28-day one;
   - the yellow/red reform.

   This is KSE's "verify facts, handle errors" criterion, shown with data.
3. **Proof of no leakage.**
   - A truncation test: rebuild features from data cut at T and assert they are equal (the idea from maranferij, Ddrakkx and olehm208, written ourselves).
   - Purged splits.
   - Model and calibration choices made on a dev window, then a single final test.
4. **An honest text ablation.**
   - Feature: @kpszsu per-oblast threat-post counts, keyed on post time.
   - Expected result: about −2% Brier, i.e. a small gain. The report says it is small and why: the channel's lead time is minutes, and alert history already carries most of the information.
5. **A small live artifact.** `python -m alerts predict` fetches the map and prints next-6 h probabilities per oblast. It also appends each prediction to a log, so it can be scored later.

## 3. Scope

**In:**
- the core forecaster (target a: start within 1 / 3 / 6 h, for oblasts not under alert);
- data assembly with seam checks;
- the data-trap and regime write-up;
- the text ablation;
- the live CLI;
- tonight and daily-minutes as a short "baselines-only" section.

**Out:**
- raion-level forecasting;
- yellow/red levels as features, since there are only about 5 weeks of data; we describe them instead;
- weather;
- ISW;
- dashboards, Docker and an API;
- hyperparameter search;
- a zoo of models.

Each of these is either too costly for the deadline or adds no measured value. The README says so in one line each.

## 4. Pipeline

### 4.1 Data (`data.py`)

1. **Fetch.**
   - Map ranged history, 2025-10-03 → now: one request per oblast per 31 days, 1 s apart, about 351 requests and about 12 min ([feasibility.md §1](feasibility.md)).
   - **Cache the raw JSON** under `data/raw/` with a manifest: URL, time fetched, SHA-256. The endpoint is undocumented, so the snapshot keeps the results reproducible.
2. **Clean.**
   - Drop hromada-level units, which carry standing alerts.
   - Treat `isContinue=true` alerts as ongoing, censored at the snapshot time.
   - Store every timestamp in UTC; derive calendar features in `Europe/Kyiv`.
3. **Series.** For each oblast, the union of raion- and oblast-level intervals ("some part of the oblast is under alert"). An episode start is a clear → alert transition.
4. **Exclusions,** decided on training data only:
   - Luhansk and Crimea, which are under permanent alert;
   - Donetsk, Kharkiv and Dnipropetrovsk, which were under alert at least 80% of the training time. These are reported separately, not hidden.
5. **Optional long history.** The Vadimkin official file for 2022 → 2025-10, deduplicated. It is only used for the descriptive story; the model trains from 2025-11.
6. **Seam check script.** Reproduces the overlap table: Jaccard, start matches, the outage window.

### 4.2 Features and targets (`features.py`)

**Grid:** one row per oblast every 30 minutes, at forecast time T.

**Features.** Everything uses events strictly before T.
- Own recency:
  - minutes since the last alert end and since the last start;
  - starts in the last 3 h and 24 h;
  - alert-minutes in the last 24 h and 7 d.
- Neighbours:
  - the share of neighbouring oblasts under alert now;
  - their starts in the last 1 h and 3 h;
  - minutes since a neighbour last started.
- National:
  - the number of oblasts under alert now and 1 h ago;
  - national starts in the last 1 h and 3 h.
- Calendar: Kyiv hour, day of week, oblast id.

**Label:** a start in [T, T+H), only for rows where the oblast is clear at T.

### 4.3 Baselines (`baselines.py`)

1. **Climatology over the last 28 days** (oblast × Kyiv hour, Laplace-smoothed). This is the main bar, and already scores AUC 0.82–0.90.
2. **Climatology over the full training period,** to show the regime cost.
3. **Recent level:** the oblast's start rate over the last 7 days, scaled to H.
4. **Binary persistence:** a known-weak sanity line.

### 4.4 Model (`model.py`)

- One LightGBM per horizon, at the settings from the probe (300 trees, 31 leaves, `min_child_samples` 200).
- Platt scaling fitted on the dev window.
- No tuning beyond that. The README says so.

### 4.5 Evaluation (`evaluate.py`)

1. **Splits.** Purged chronological splits, so no label window crosses a boundary.
   - train: 2025-11 → dev start;
   - dev: about 2 weeks, used for calibration and every decision;
   - **final test: the last about 4 weeks up to the data cutoff, run once.**
   - Plus two earlier rolling folds, shifted back by 30 and 60 days, to show the effect of the regime.
2. **A pre-registered skill bar.** Written in `PROCESS_LOG.md` *before* the final run: "the model passes if Brier skill vs the 28-day climatology > 0 with the 95% CI excluding 0 at ≥ 2 of 3 horizons".
3. **Metrics.**
   - Brier, and Brier skill vs each baseline;
   - AUC, both pooled and **within-oblast**, so that differences between oblasts don't inflate it;
   - a reliability diagram;
   - confidence intervals from a day-block bootstrap.
4. **Leakage tests** (`test_leakage.py`, plain asserts, runnable with pytest):
   - **truncation:** features at T computed on the full data equal features computed on data cut at T, for random (oblast, T) pairs;
   - **planted leak:** a positive control. Add a feature that peeks at the future; the test must fail and the score must jump;
   - **label purge:** no training label window reaches into dev or test.
5. **Slices.**
   - before and after 2026-09-07 (the level reform);
   - calm and escalation folds;
   - excluded frontline oblasts, scored separately and shown as a limitation.

### 4.6 Text ablation (`text.py`)

- **Collection.** Scrape @kpszsu through the public `t.me/s/` preview for the full train + dev + test span. That is about 20 pages per day, so around 4–5 hours for a year. Alternatively, limit the text experiment to the window since about 08-27 that is already collected (6 weeks).
- **Feature.** The per-oblast count of threat posts in (T − N, T], using each post's **original publication time**.
- **Edits.** Only the latest version of an edited post is visible. Report how many posts are edited (2% for @kpszsu), and run a variant that drops edited posts.
- **Report.** ΔBrier with a CI: the stack with text against the same stack without it.

### 4.7 Live CLI (`main.py`)

- `fetch`: update the cache.
- `evaluate`: run the full evaluation and write `results/`.
- `predict`: fetch the map now, print next-1 / 3 / 6 h probabilities per oblast, and append to `results/live_predictions.jsonl`.
- `score-live`: score the logged predictions once their windows have closed. If there is time on Monday, include the first live score in the README.

## 5. Repo layout (minimal)

```
README.md              # question, data, method, results table, limitations, how to run
PROCESS_LOG.md         # decisions, "Wrong #n" entries with before/after numbers, pre-registration
main.py                # CLI: fetch / evaluate / predict / score-live
alerts/data.py features.py baselines.py model.py evaluate.py text.py
tests/test_leakage.py  # truncation + planted-leak + purge
research/              # this folder: the research trail behind the decisions
results/               # metrics tables, reliability plot, live log
requirements.txt
```

No Docker, no API, no dashboard. The passer's lesson is a working, honest artifact, not infrastructure.

## 6. Timeline

| When | What | Done when |
|---|---|---|
| Sat night (now) | Agree on the plan. Skeleton repo, `requirements.txt`, `PROCESS_LOG.md` started. | the plan is approved |
| Sun morning | `data.py` (fetch + cache + clean + union) + seam check | seam table reproduces Jaccard ≈ 0.99 |
| Sun midday | `features.py`, `baselines.py`, `tests/test_leakage.py` (written **before** the model) | truncation test passes, planted leak fails as expected |
| Sun afternoon | `model.py` + `evaluate.py` on the dev and earlier folds; write the pre-registered skill bar | the fold table exists |
| Sun evening | Text ablation; data-trap and regime figures | ablation table, 3–4 figures |
| Mon morning | **Single final test run.** Live `predict` started and logging. | `results/` frozen |
| Mon afternoon | README, limitations, reflection draft, export the AI log | a fresh-clone run works |
| Mon by about 20:00 | Submit, keeping a buffer before 23:59 | form sent |

Fallbacks, if Sunday slips: drop the text ablation first, then the live CLI. The core forecaster, the leakage tests and the data story are the minimum.

## 7. Process: the AI log is the primary signal

- **Keep this Claude Code conversation as the main log** and export it at the end. It already shows the research trail.
- In the log, keep doing what KSE asks for, visibly:
  - challenge claims and ask for evidence;
  - ask for raw samples before trusting a schema;
  - catch and correct errors.
- Real moments from this session to mention in the reflection:
  - the "official feed died" myth, versus the raion reform;
  - a subagent misreporting the sign of robotheist's text result, caught by re-checking the README;
  - the automatic repo score failing to rank the confirmed passer (81st of 190), which led to rejecting it as a pass predictor;
  - a subagent hitting the rate limit and being resumed.
- **`PROCESS_LOG.md`.** Every decision follows proposal → risk → check → result → adjustment, and every error gets a "Wrong #n" entry with before/after numbers. The skill bar is pre-registered before the final run.
- **Reflection** (~100 words): what went wrong, how we adjusted, why the final version is better. Drafted from `PROCESS_LOG.md` on Monday.

## 8. Risks

| Risk | Mitigation |
|---|---|
| The map endpoint changes or blocks us | Cache the raw JSON on Sunday morning and commit it if small enough, otherwise its SHA-256 plus a fetch script. Fallback: Vadimkin up to 08-29 + JustJimer from 09-06, with the 08-29 → 09-06 gap documented. |
| The map's terms of use are unclear | Use it for non-commercial research only, cite it, don't hammer it (1 req/s), and say so in the README. |
| The final test window is a calm regime, so skill is about 0 | That is a valid result. The pre-registered bar plus the fold table make a null honest, not a failure. |
| Text leakage from edited posts | Report the edited share, and run the variant without edited posts. |
| Time overrun | Drop the text ablation and the live CLI; keep the core, the leakage tests and the data story. |
| Copying from other repos | Borrow ideas with credit in the README ("inspired by …"); write all code ourselves. KSE reads the log, and the log has to show our own work. |

## 9. Open decisions for the user

1. **Approve the framing:** "new alert within 1 / 3 / 6 h", or prefer something else?
2. **Text ablation:** include it (+0.5 day), or drop it now to save time?
3. **Live CLI:** include it (+0.5 day)?
4. **Language** of the README and reflection: English, to match the brief, or Ukrainian?
