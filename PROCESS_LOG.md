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

## 2026-10-11: step 1 (data)

### Resource check before planning (11:50–12:30 UTC)

- **map.ukrainealarm.com:** still HTTP 403 with `cf-mitigated: challenge`.
- **Map snapshot:**
  - 351 files (27 query ids × 13 chunks), and all SHA-256 hashes match `MANIFEST.json`;
  - the Luhansk query returned 0 rows;
  - the last chunks were fetched 19:03:18–19:15:09 UTC, so the **map cutoff is 2026-10-10 19:03 UTC**.
- **alerts.in.ua:** the token is valid.
  - `active.json`: 50 active alerts, with `alert_level`, and `threats[]` filled in for 42 of them.
  - `month_ago` for Kyivska: 1,465 records, starting 2026-09-11 12:21 UTC.
- **Seam pre-check, real API vs map**, 2026-09-11 → 10-10 19:02:

  | Oblast | Jaccard | Starts (map / API) |
  |---|---|---|
  | Kyivska | 0.9995 | 228 / 228 |
  | Kyiv City | 0.9984 | 212 / 211 |

### Answers to the four open questions (measured)

1. **Does `month_ago` return `threats[]`?** No. History has no `threats` field at all, for either oblast checked. Threat types exist only in `active.json`.
2. **What is the window?** A rolling 30 days, plus standing alerts that started earlier. For example, Vovchanska hromada has been under alert since 2024-05-20.
3. **How does yellow → red appear?** As an in-place update of the same record. History keeps only the *final* level.
   - In JustJimer, no records of the same unit overlap with different levels.
   - Back-to-back pairs (gap ≤ 60 s) are rare (~1%), and their level pairs are mixed.
4. **IDs.**
   - Raion uids match `regions.json`, but the names differ (Берестинський vs Красноградський, apostrophe variants). Join on uid.
   - **`location_oblast_uid` is not the oblast id:** it holds raion or hromada ids such as 124 and 1293. The oblast must come from the `location_oblast` name.
   - Kyiv City has `location_type = oblast`.
   - Kharkiv city is uid 6293, which is not in `regions.json`.

### Wrong #3: "the map endpoint returns AIR alerts only"

- **Before.** data-sources.md §2 and §3.4 say the map returns AIR alerts only.
- **Check.** Profiling the snapshot found other types:

  | Type | Rows | Level |
  |---|---|---|
  | ARTILLERY | 3,203 | all hromada |
  | NUCLEAR | 12 | 10 raion, 2 hromada |
  | URBAN_FIGHTS | 3 | hromada |

  The probe's `load_map` never filtered on type, so the 10 raion-level NUCLEAR rows leaked into its oblast union. The effect is negligible, but it is a bug.
- **Adjustment.** Keep only `alertType == "AIR"`.

### Other data traps found

- **End sentinel.** Ongoing map alerts have the end `0001-01-01T00:00:00`, which overflows pandas unless it is coerced.
- **Duplicates in the map.** 4,095 duplicate `(unit, start)` rows, all identical. They come from:
  - 59 ongoing alerts repeated in all 13 chunks;
  - chunk-boundary days that appear in two files.
- **Unit levels.** The probe classified unit levels with a regex on names. Use the State/District/Community tree in `regions.json` instead.
- **Records are final versions.** History records carry the final level and late-filled ends: 60 of 2,371 Kharkiv records were updated more than 1 min after finishing.
  - Features at T must truncate at T.
  - Level features may only use alerts that finished before T.

### Decision 2: the data path

- **Proposal.**
  - Splice at **2026-09-12 00:00 Kyiv (09-11 21:00 UTC)**: map for starts before it, alerts.in.ua for starts after it.
  - This is better than splicing at the map cutoff:
    - no map alert that starts before the splice is still open at the cutoff, since the longest is 87.8 h;
    - the API supplies real levels for the whole post-splice period;
    - the 29-day overlap is used only for the seam check.
- **Deduplication at three levels:**
  - map: on `(unit_id, start)`;
  - API pulls: on `id`, keeping the latest pull;
  - between sources: by the splice time.
- **Storage.** Raw API pulls are saved gzipped, with a MANIFEST (sha256, fetch time, no token). Everything else is rebuilt from raw.
- **Code.** Written test-first (TDD), at four agreed seams: loaders, splice, episodes, and seam + api.
- **User decisions:**
  - commit the raw API pulls;
  - no Vadimkin 2022–2025 long history, since one year of map data covers the raion reform, the escalation and the level reform.
- **Acceptance bar, set before running:**
  - overall seam Jaccard ≥ 0.99;
  - starts matched within ±2 min ≥ 98% in both directions;
  - per-oblast Jaccard ≥ 0.97;
  - splice completeness: no lost or doubled records, ≥ 99% unit-level match after the splice, and Jaccard ≥ 0.99 in the window splice ± 12 h.

### Corrections during implementation

- **Wrong #4 (mine, in the plan): "25 oblast series" should be 24.**
  - The plan counted 24 oblasts + Kyiv City. Without Luhansk (permanent alert, not fetched) the true count is 23 oblasts + Kyiv City = 24.
  - feasibility.md and the probe's `OBL` table had it right.
  - The acceptance bar now reads 24 series and 24/24 API responses.
- **Zero-length blips.** `load_map` on the real snapshot found 2 records with `end < start`, by 0.7 s and 4.2 s:
  - Zvenyhorodskyi raion, 2025-10-28;
  - Rozdilnianskyi raion, 2026-08-13.

  They look like alerts cancelled at once, recorded with clock jitter. `episodes()` drops intervals with length ≤ 0. The bar now reads "`end ≥ start`, except 2 blips under 10 s".
- **Tests that passed on first run.** Several splice and episode tests passed at once, because the behaviour already followed from the splice rule or the ported `union`.
  - To show they can fail, each was checked by a mutation, and every mutation was caught:
    - `>=` → `>` at the splice;
    - dropping the level filter;
    - dropping the censoring clip;
    - `tol_min` 2 → 0.
  - One mutation looked like a false failure after the code was restored. The cause was a stale `__pycache__`: the mutant was the same size and was written in the same second as the original. Mutation runs now use `PYTHONDONTWRITEBYTECODE=1`.
- **The minute grid biases the per-oblast seam for quiet oblasts.** The user asked which "shingle" size the Jaccard uses.
  - It uses (oblast, minute) cells: a minute counts if any part of it is under alert.
  - On the partial pull, Zakarpattia scored 0.956 on minutes, below the 0.97 bar. It has only 3 alerts and 65 alert-minutes.
  - The exact overlap in seconds is **0.990**. The API records all-clears 8–17 s later than the map, which pushes ends into the next minute.
  - **Adjustment.** `compare` now also reports `jaccard_s`, the exact overlap in seconds, which was added test-first. The per-oblast bar (≥ 0.97) is applied to the exact value, and the minute-grid value stays in the report for comparison with feasibility.md. The threshold itself did not change; only the measurement did.

### Step 1 result (2026-10-11 ~13:25 UTC)

- **API pull.** `data/raw/alerts_in_ua/20261011T1247Z`: 24/24 regions returned HTTP 200, 16,574 raw rows, and 0 files contain the token.
  - The pull broke twice on transient network errors: `IncompleteRead` on the 15th region, then `URLError` on Kherson for about 1 min.
  - Fix: `get()` now retries dropped connections. This was written test-first. The pull was resumed from the same directory.
- **Seam, map vs alerts.in.ua**, 2026-09-11 21:00 → 10-10 19:03 UTC. Every bar is met:

  | Metric | Result | Bar |
  |---|---|---|
  | Jaccard, overall (minute grid / exact) | 0.9994 / 0.9994 | ≥ 0.99 |
  | Jaccard, per oblast: minimum on the minute grid | 0.956 (Zakarpattia, see above) | – |
  | Jaccard, per oblast: minimum exact | 0.990 | ≥ 0.97 |
  | Starts matched within ±2 min (map → API / API → map) | 99.8% / 99.8% | ≥ 98% |
  | Daily alert-minutes per (oblast, Kyiv day) | correlation 1.0000, MAE 0.3 min | – |

- **Splice completeness.** Every bar is met:
  - 117,276 records = 101,198 from the map + 16,078 from the API;
  - in the window splice ± 12 h: Jaccard 0.9998, minimum per oblast 0.9965, starts 110 vs 110;
  - all 24 oblasts have records on both sides of the splice;
  - there are 0 six-hour bins without a national start.
- **Wrong #5 (my metric): "unit-level match = a start within 60 s".**
  - **Before.** 1,791 map raion records had no API record with a start within 60 s, failing the ≤ 1% bar. The API side had 1 such record.
  - **Check.** 1,780 of the 1,791 lie *inside* an API record of the same raion.
    - Since the level reform, the map stores overlapping records for one raion. 10% of its raion records in Sep 2026 and 13% in Oct start while an earlier record of the same raion is still open. Before September the share rounds to 0% (the first is on 2025-11-10).
    - alerts.in.ua keeps one record for the same alert.
  - **Adjustment.** `unmatched()` also counts a covering record as a match; this was written test-first.
  - **After.** 11 of 15,474 map raion records have no counterpart (0.07%), and 0 of 13,526 API records lack one. The 11 are listed in the data report: 6 blips of 1–9 s, and 5 stretches of 1–10 h that the API starts later.
  - **For step 5.** On the map, record counts after the reform are inflated by about 10–13%. Count union episodes, never records.
- **Manual spot check.** 3 random API raion records were found in the raw map JSON: starts within 1 s, ends within 0.4 s to 2 min.
- **Tests.** 36 pass: 30 written test-first, plus the acceptance tests in `test_real_data.py`.
- **For step 2.** 6.3% of episodes (1,651 of 26,128) restart within 5 min of an all-clear.

### Code review of step 1 (2026-10-11)

A review of 6e980e0..HEAD found three P2 bugs. All 36 tests passed, and none covered them. Each was reproduced on a worked example and then fixed test-first.

- **Wrong #6: the token was masked after the error body was cut to 300 chars.**
  - **Before.** When the token crossed char 300, its first chars stayed in the error message: a body of 295 chars + the token left `secre` behind.
  - **After.** `get()` masks the token first and then cuts the body.
- **Wrong #7 (my metric): "starts matched within ±2 min" was counted on the minute grid.**
  - **Before.** Binning to minutes widened the tolerance to almost 3 min: starts 2 min 30 s apart counted as a match. Starts in the same minute were also counted as one.
  - **After.** `compare` matches exact episode start times with `merge_asof`, as `unmatched` already does. It also counts episodes rather than minutes.
  - **Seam, before → after:**
    - starts (map / API): 3,726 / 3,722 → 3,727 / 3,723;
    - matched: 99.76% / 99.84% → 99.73% / 99.84%.

    The ≥ 98% bar still holds, and the splice window ± 12 h is unchanged (110 vs 110). Only Odeska (18) and Chernihivska (25) changed; Chernihivska map → API went from 0.989 to 0.983.
- **Wrong #8: `episodes()` crashed when no oblast or raion record was left** (`pd.concat` of nothing).
  - **After.** It returns an empty table with the same columns and types, so callers can still use `.dt`.
- **Tests.** 40 pass. Two assertions passed at once, and both were checked by a mutation that was caught:
  - "exactly 2 min still matches" fails when the tolerance is made strict;
  - the dtype check fails when the empty result is an untyped table.

## 2026-10-11: step 2 (features, baselines, splits)

### Decision 3: what step 2 builds

- **Rows.** One per (oblast, T) every 30 min from 2025-10-10 to the map cutoff, only where the oblast is clear at T (no alert in the minute before). Labels `y1`/`y3`/`y6`: an episode start in [T, T + H); NaN when T + H is past the data end.
- **"The past" means minutes before T.** A record known at T started before T; an end after T is unknown.
  - Limitation: ends that the server filled in late cannot be checked (60 of 2,371 Kharkiv records were updated more than 1 min after the all-clear).
- **Restarts within 5 min of an all-clear** (6.3% of episodes) stay separate starts: people hear a new siren. `min_since_alert` carries their risk.
- **Features: the probe's 18 plus `starts_7d`**, ranked by evidence from research/:
  1. oblast × Kyiv hour (climatology alone: AUC 0.82–0.90; lbgos "time + oblast" = 0.162 of 0.278 skill);
  2. own load and recency (lbgos +0.055; top gain in the probe);
  3. neighbours (lbgos +0.036; a neighbour siren preceded 94% of episodes);
  4. the national wave (lbgos +0.001), kept because it is in the probe's set.

  The 28-day climatology at T is a candidate input; step 3 decides it on val. Out: text (Decision 1), yellow/red levels (below), weather, holidays, ISW.
- **Yellow/red levels (user's decision): logged, not forecast.** Levels exist only since the splice (about 30 days), the map has none, and history keeps only each record's final level. The forecast is "any alert"; the live log in step 4 stores the current levels and threats with every forecast.
- **Baselines** (`alerts/baselines.py`). Nothing is trained; each counts rates from rows whose label window had closed:
  - `Climatology(28)`: oblast × Kyiv hour over the last 28 days, shrunk to the oblast mean with 10 pseudo-rows, recounted every day at 00:00 Kyiv. The main bar.
  - `Climatology(None)`: the same over all history, to show the cost of a regime change.
  - `RecentLevel`: a constant hazard from the last 7 days (starts / clear minutes), i.e. the two-state Markov chain.
  - `Persistence`: 1 if a start came in the last H hours.
- **Splits** (`alerts/splits.py`, `DECISION`), Kyiv dates. A row belongs to a part [a, b) only if a ≤ T and T + H ≤ b (purge).

  | Part | Window | Role |
  |---|---|---|
  | train | 2025-11-15 → 2026-08-29 | fitting; starts after raion-level alerts reached every oblast |
  | val | 2026-08-29 → 2026-09-13 | every step-3 decision and the calibration |
  | test | 2026-09-13 → map cutoff | reported as seen by the probe; nothing is tuned on it |

  The holdout after the map cutoff is step 7.
- **Code as classes** (user's decision), new code only: `AlertGrid`, `Features`, `ForecastTable`, `Split`, `Baseline` and its three kinds, `TruncationCheck`, `AdversarialValidation`. Step-1 code stays as functions.

### Why leakage is tested by truncation and not by adversarial validation

The user asked why. Adversarial validation (AV) trains a classifier to tell two sets of rows apart; it measures drift between their feature distributions. A feature that sees the future can have the same distribution in both sets, so AV can pass it. `TruncationCheck` tests the brief's rule directly: it computes a quantity from all records and from the records as known at T, and requires exact equality. A planted leak (features at T + 1 min) is caught, and so is a climatology that counts a row before its label window closed. AV stays as a drift diagnostic (below).

### Wrong #9: "the model beats a 28-day climatology by +0.12 / +0.15 / +0.18"

- **Before.** feasibility.md §3 and CLAUDE.md: LightGBM + Platt has Brier skill +0.12 / +0.15 / +0.18 against a 28-day climatology on 2026-09-13 → 10-10.
- **Check.** In the probe the climatology is counted once, at the test start, and then frozen for 27 days (`research/probe/model.py:162-163`). By the end of the window it is up to 55 days old, while the alert load kept rising.
- **Result** on the same window and the same 21 oblasts (Brier; skill against the daily climatology):

  | H | Base rate | Persistence | Clim. 28 d frozen (probe) | **Clim. 28 d daily** | Clim. all history | Recent level 7 d | Probe's LightGBM + Platt |
  |---|---|---|---|---|---|---|---|
  | 1 h | 0.235 | 0.2366 | 0.1439 (−0.07) | **0.1346** | 0.1703 (−0.27) | 0.1318 (+0.02) | 0.127 |
  | 3 h | 0.414 | 0.2703 | 0.1652 (−0.13) | **0.1458** | 0.2175 (−0.49) | 0.1413 (+0.03) | 0.141 |
  | 6 h | 0.531 | 0.2491 | 0.1598 (−0.19) | **0.1339** | 0.2153 (−0.61) | 0.1285 (+0.04) | 0.131 |

  - Against a climatology recounted daily, the probe's model is only about +0.06 / +0.03 / +0.02 (its numbers come from the probe's own run, so this is approximate).
  - The 7-day recent level, which has no model at all, is as good as the probe's model at 3 h and better at 6 h.
- **Adjustment.**
  - The honest bar is the daily climatology, and the recent level must be reported next to it.
  - The step-3 pre-registered bar has to name the bar explicitly.
  - The claim in CLAUDE.md ("beats a 28-day climatology") needs the user's decision before step 3.

### Step 2 result (2026-10-11 ~17:30 Kyiv)

- **Reproduction of the probe** (acceptance test, bar set in the plan before the run). Every bar is met:

  | | Probe | Ours | Bar |
  |---|---|---|---|
  | Clear rows | 18,214 | 18,209 | ±1% |
  | Base rate 1 / 3 / 6 h | 0.234 / 0.414 / 0.531 | 0.235 / 0.414 / 0.531 | ±0.005 |
  | Brier persistence | 0.237 / 0.270 / 0.249 | 0.237 / 0.270 / 0.249 | ±0.005 |
  | Brier clim. 28 d, frozen | 0.144 / 0.165 / 0.160 | 0.144 / 0.165 / 0.160 | ±0.003 |

- **Leakage on the real history.** Features and the 28-day climatology are identical with the data cut at T, at 30 moments. These are 23 random moments, plus:
  - an episode start;
  - 1 and 2 min after an all-clear;
  - inside an alert longer than 24 h;
  - both DST switches;
  - the splice.

  No train label window reaches val, and no val window reaches test, for any H.
- **Is the test window adequate?** Size and regime per part (21 oblasts, H = 6 h purge for the row counts):

  | Part | Rows | Base rate 1 / 3 / 6 h | Share of time under alert | Starts per oblast-day |
  |---|---|---|---|---|
  | train | 232,474 | 0.102 / 0.224 / 0.329 | 0.194 | 2.53 |
  | val | 10,459 | 0.193 / 0.363 / 0.465 | 0.301 | 4.53 |
  | test | 18,209 | 0.236 / 0.415 / 0.531 | 0.343 | 5.58 |

  Test is the latest and most intense regime, as the brief asks. It is almost entirely alerts.in.ua data, which step 1 validated on this very window (Jaccard 0.9994).
- **Adversarial validation** (LightGBM, 5-fold, features only):
  - train vs val: AUC **0.999**; top drifting features `starts_7d`, `alert_min_7d`, `obl`, `nat_starts_3h`;
  - train vs test: AUC **1.000**; top features `nat_starts_3h`, `starts_7d`, `obl`, `alert_min_7d`.

  These random-fold scores combine real load drift with temporal dependence between fitting and held rows. The follow-up audit below finds substantial inflation: they do not prove independent-period separability or that every model trained on all history without weights will lag. Recency weighting remains a step-3 hypothesis to compare on chronological val.
- **Corrections during implementation.** During a mutation run, `git checkout` restored a file from an index that did not hold the latest edit (the `asof` guard). The `asof` test failed at once, and the edit was redone. Mutation runs now stage the green state first.
- **Tests.** 65 pass: 40 from step 1 plus 25 new. Every test that passed at once was checked by a mutation that was caught:
  - the minute-before rule;
  - the purge;
  - the label-maturity rule (×2);
  - the refit at midnight;
  - the 28-day window;
  - `known_at` cutting at T.

## 2026-10-11: leakage and AV follow-up requested by the user

### Wrong #10: interpreting near-perfect random-fold AV as independent-period drift

- **Question.** Check whether train/val AV 0.999 and train/test AV 1.000 come from data leakage, and identify the cause.
- **Reproduction.** Fixed step-2 settings and 21 oblasts reproduce AUC 0.999400 / 0.999501. The latter rounds to 1.000; it is not exact perfect classification.
- **Cause.** Individual random folds mix strongly dependent temporal context: 99.993% of held rows share a timestamp with fit, and about 93.5–93.7% have a same-oblast ±30-minute neighbour in fit. Rolling load and national wave features provide a fingerprint of the recorded interval. Grouping timestamps still gives 0.998031 / 0.998459; removing only the two 7-day features still gives 0.992471 / 0.993831. The dependence extends to shorter windows and national aggregates.
- **Countercheck.** Holding first/last complete 3-day blocks of each compared period gives pooled AV 0.849 / 0.911 without a gap and 0.749 / 0.892 with a 7-day gap. These are sensitivity diagnostics over the same endpoint rows, not full-period OOF scores or forward forecast metrics. The gap also reduces fit size; individual fold scores and limits are in the report.
- **Other hypotheses.** Event-time feature/climatology truncation and horizon purges pass; the planted future-feature leak is caught. Using the map throughout gives train/test AV 0.999515, so the source splice is not necessary for the effect. Only oblast/hour/weekday gives 0.515 / 0.542.
- **Residual risk.** Final history versions do not establish field availability at T. Of 13,885 completed API AIR oblast/raion records before cutoff (all 24 oblasts), 183 were updated >60 s after finishing. This marks a publication/revision risk, not proof that each update changed an end. `known_at` cannot check it without timestamped live/version snapshots.
- **Adjusted conclusion.** Rising load is confirmed independently (starts per oblast-day 2.53 → 4.53 → 5.58), but the AV scores overstate evidence of generalization difficulty. Whether a particular all-history model lags, and whether recency weights help, must be tested on chronological val. No model choice was made on test; the post-cutoff holdout was not scored.
- **Artifacts.** [Full report](results/leakage_report.md), [offline reproduction](results/audit_leakage.py), [exact results](results/leakage_audit.json). Existing diagnostic tests: **9 passed**, one joblib CPU-detection warning. Forecast implementation unchanged.

### Follow-up: which split actually mixes time, and why these dates and oblasts?

- **Primary split.** `Split.rows` filters by T and `T + H <= boundary`, with shared dates for all oblasts. Real checks over all 24 series find no shared timestamps between parts and no label-window crossings for 1/3/6 h. Synthetic split checks: **2 passed**. This split already satisfies chronological membership.
- **Random folds.** The auxiliary AV uses shuffled stratified row folds over the two periods. Its fits can include later times than a held row. The previous endpoint experiments also permit later fitted dates and are sensitivity diagnostics, not forward forecast validation. Turning off shuffle alone does not fix either protocol.
- **Order.** `ForecastTable` is oblast-major; each part is not globally sorted by time. Its existing timestamp filters remain correct. Future index-based chronological CV must sort by `(ts, obl)` and keep equal timestamps together.
- **Dates.** The snapshot's last first-observed raion series is Ternopilska on 2025-11-06 09:07 UTC, supporting the November-15 start and full trailing windows. August-29/September-13 come from the probe's hard-coded test start and its 15-day dev interval; they are not geographic balancing rules.
- **Geography.** Train-only `>=80%` alert-time exclusion recomputes to IDs 9/22/28 (Dnipropetrovska 89.29%, Kharkivska 81.92%, Donetska 88.47%). Their clear H=6 h val rows number only 21/30/29. Exclusion is a population choice, not an oblast split. Reported 21-region metrics cannot establish accuracy for the promised 24-region tool; the model/evaluation scope must be explicit and consistent.
- **Seen test.** The September/October period already informed the feasibility research and project scope. It remains a chronological historical benchmark, not an untouched final test. This was disclosed earlier and needs to remain explicit. Val's short duration and combined selection/calibration role also constrain step-3 evaluation; calibrator-fit loss must not be presented as independent validation performance.
- **Artifacts.** [Clear split review](results/split_report.md), [exact membership/geography checks](results/split_audit.json). No forecast implementation or split dates changed.

## 2026-10-11: split fix requested by the user

### Decision 4: forecast checks in time order, time-blocked AV, all 24 oblasts

- **Request.** The user: the split must be by time, and time must not be mixed. The review above found the primary split already chronological; the AV folds were what mixed time. Four more gaps:
  - the table was oblast-major;
  - there were no sequential forecast checks;
  - one 15-day val was to choose the model and also fit the calibrator;
  - the reported metrics covered 21 of the 24 regions the tool promises.
- **Proposal and the user's corrections.** I first proposed replacing `Split` with weekly walk-forward windows. The user kept `Split`, because it is already chronological and purges label windows, and set these rules:
  - sort by `(ts, obl)` before any time CV, and cut blocks from unique timestamps so the oblasts of a moment stay together;
  - use separate protocols: sequential checks (train on the past, score the next period) for the forecast, time blocks for AV. `TimeSeriesSplit` cannot be dropped into AV, because its early fits hold one class only;
  - do not read the endpoint AV (0.749 / 0.892) as a corrected forecast estimate: some of its fits held later dates;
  - evaluate every region the tool promises, each with its own counts;
  - keep test as a historical benchmark; the final check is later data after the decisions are frozen. One val for choice and calibration is acceptable, but not as an independent estimate, and calibrated models are compared only on blocks their calibrator did not see;
  - add no 7-day gap between the main parts: past history in the rolling features is legitimate. The risk of late API revisions is a separate check.
- **What changed.**
  - `ForecastTable.rows` is sorted by `(ts, obl)`.
  - `Split.forward(rows, H, a, b, blocks)` cuts the unique moments in [a, b) into consecutive blocks. A block's fit holds only rows with T + H ≤ its start; its held rows have T + H ≤ b.
  - `CHOOSE` is six weekly blocks, 2026-08-02 → 09-13; the first two only warm the calibrator up. `BENCHMARK` is four weekly blocks of test.
  - `AdversarialValidation` cuts each set into 4 time blocks; fold j holds block j of both sets. No fitted row lies within 7 days (`WEEK`, the longest feature window) of a held moment. It reports the AUC per fold and refuses a fold whose fit has under 1,000 rows of a set.
  - `main.py check` reports AV train vs test.
- **Contract for step 3**, also in the `forward` docstring:
  1. A block's model learns only from its `fit`.
  2. A block's calibrator learns only from out-of-fold forecasts of the 14 days before the block start s, with T + H ≤ s. For the first benchmark block, those are the val forecasts.
  3. Calibrated candidates are compared only on blocks their calibrator did not see. A calibrator's loss on its own rows is never reported.
  4. Scores on `CHOOSE` blocks 3–6 (late train and all of val) chose the model, and are labelled as not independent.
  5. A pre-registration commit (the candidate, and the bar against the daily 28-day climatology and `RecentLevel`) comes before the single benchmark run. Another one comes before the holdout in step 7.
  6. All 24 oblasts, no exclusions. Every window gets a per-oblast table with n, marked "quality not verified" below n = 100; this rule is set now, before any score.
- **Results.**
  - **Tests.** 70 pass. Every test that passed at once was checked by a mutation, and every mutation was caught:
    - no purge in `forward`'s fit (the real-data test);
    - `<=` → `<` at the block start;
    - held labels leaving [a, b);
    - random AV blocks;
    - a shift the model cannot see;
    - `>` → `>=` at the gap edge;
    - a zero gap.
  - **Forward blocks on the real rows** (H = 6): 4,310–5,750 held rows each, all 24 oblasts. On 2026-08-04 at 20:30 Kyiv every oblast was under alert, so that moment has no row. The `CHOOSE` blocks after it therefore start at 00:30, not midnight.
  - **Time-blocked AV, train vs test, 24 oblasts:** AUC **0.946** (folds 0.953 / 0.986 / 0.909 / 0.937). Top features: `nat_starts_3h`, `starts_7d`, `obl`, `alert_min_7d`.
    - The drift is real, but it is not 0.9995. This is a drift diagnostic, not a forecast estimate.
    - Train vs val is refused: 15 days cannot hold a block plus a 7-day gap on both sides.
  - **Frozen audit.** It still reproduces its parts (232,474 / 10,459 / 18,209 rows) in its original oblast-major order.
- **Separate check: late API revisions.** No split removes this risk: history holds the final record versions, and the truncation checks work on event times.
  - Step 4: the live log keeps what the API showed at T. When a forecast is scored, features from that snapshot are compared with features from the final history at the same T: the share of differing rows and the effect on Brier.
  - Step 7: the fresh holdout pull is compared with the 2026-10-11 pull, the only one so far, for records with the same id whose start or end changed.
  - Until then it stays an open limitation: 183 of 13,885 records were updated more than 60 s after their all-clear.

### Code review of step 2 (2026-10-11)

A review found two P2 bugs. Both were reproduced on the data and fixed test-first, and each new test failed before its fix.

- **Wrong #11: the start counters counted minutes with a start, not starts.**
  - **Before.** `minute_grid` returns the number of starts in each minute, but `AlertGrid` added up `starts > 0`. So two starts of one oblast in one minute (a blip shorter than a minute, then a new alert) counted once.
    - This contradicts Decision 3: restarts are separate starts, because people hear a new siren.
    - The probe had the same flag (`cumsum(ST > 0)`); the probe stays frozen.
  - **Measured.** 19 of 26,128 starts were merged, in 19 oblast-minutes across 12 oblasts (5 of them in Odeska).
    - Of 267,283 forecast rows, `starts_7d` was too low in 3,059 (1.14%), `starts_3h` in 43, and `nat_starts_3h` in 1,744 (0.65%).
    - `RecentLevel` reads `starts_7d`, so its rate was too low in the same rows.
  - **After.** `AlertGrid` adds up the counts and now sees all 26,128 starts. These do not change:
    - the labels (`> 0`), `min_since_start` and `Persistence`;
    - the clear rows and the climatology.

    The probe reproduction and the truncation checks still pass.
  - **Effect on the numbers.**
    - `RecentLevel` Brier on the Wrong #9 window: 0.1318 / 0.1413 / 0.1285, unchanged to four decimals.
    - Time-blocked AV, train vs test: AUC 0.946 → **0.944** (folds 0.951 / 0.987 / 0.905 / 0.935).
    - The frozen leakage audit was computed with the merged starts. Its row counts do not depend on them, but a re-run can differ in the last digits of its AUCs.
- **Wrong #12: AV with gap = 0 fitted on held rows.**
  - **Before.** `folds()` left out the rows strictly inside (first held moment − gap, last held moment + gap). With gap = 0, the first and last moments of a held block fell outside that zone, so they were both fitted and held: 4 rows in every fold of the test example.
  - **After.** The fit leaves out the held rows explicitly, whatever the gap. The default 7-day gap already covered them (0 such rows), so the reported AUC was not affected.
- **Tests.** 72 pass: 70 before, plus the two new tests.

## 2026-10-11: step 3 (model and evaluation)

### Wrong #13 (mine, in the plan): "the candidates" were one model type, taken by default

- **Before.** My first step-3 plan compared three variants of the probe's LightGBM plus a blend of clim28 and `RecentLevel`. I presented them as evidence-based, but I had not weighed other model types at all: LightGBM came from the probe, where it was the default.
- **The user's challenges.**
  - "Why only LightGBM, without LSTM? Did you weigh what could be best, or pick at random?"
  - A blend is stacking, and stacking before the correlation of the errors is measured is premature.
  - CatBoost is worth a look too, and the plan did not save the model weights.
- **Check** against the survey (research/prior-solutions-scores.csv, 190 repos, and the cards):
  - gradient boosting appears in 41 repos, deep models (LSTM, GNN) in 17;
  - the deep results that exist are weak or unfinished: a spatio-temporal GNN at AUC 0.61 with no baseline (anechytailenko); LSTM lost to XGBoost/CatBoost in goodfrog33's 12-model comparison; LSTM on daily minutes at MAPE 75–91% (sergkern1); LSTM unfinished (KrafterDen);
  - the five strongest onset forecasters (lbgos, maranferij, Ddrakkx, robotheist, Dopplerr24) used LightGBM and/or logistic regression; maranferij's logistic regression matched LightGBM on Brier and lost on ranking;
  - the numbers across teams are not comparable (targets, windows, often a frozen climatology), so the choice must come from our own CHOOSE blocks, with more than one model type.
- **After.** Decision 5 below: five candidates of three model types, no blend now, LSTM deferred with its reasons, and the chosen model saved.

### Decision 5: what step 3 compares, how it chooses, and the bar (set before any score)

- **Candidates.** Five, of three model types. Every candidate has fixed settings (no tuning) and uses the same 19 forecast-time features:

  | | Name | Model | Why |
  |---|---|---|---|
  | A | `gbm` | LightGBM, the probe's settings | the probe's model |
  | B | `gbm_clim` | A + the daily clim28 rate as a feature | Decision 3 left this input to step 3 |
  | C | `gbm_recent` | A with recency weights, half-life 60 days | Wrong #10 left this to step 3; 60 d is lbgos's value, not tuned by us |
  | D | `catboost` | CatBoost, library defaults, seed 0 | the user: boosted trees of another design (ordered boosting, native categories, strong defaults) |
  | E | `logistic` | logistic regression; one-hot oblast and weekday, sin/cos hour, log1p and standardised counts | a linear model (Ddrakkx, maranferij) |

  More candidates make the CHOOSE winner look better than it is; the benchmark checks it.
- **LSTM: considered and deferred.**
  - No deep model in the survey beat a strong baseline on this task.
  - Our inputs are tabular features, where boosted trees usually win (Grinsztajn et al., NeurIPS 2022; LightGBM won M5).
  - About one year and 26k alerts, with a regime shift, is little for a sequence model.
  - PyTorch and architecture tuning would take the one day left before the deadline.
- **No stacking or blending now (the user).** A blend helps only if the forecasts err differently, and that has not been measured. The CHOOSE report shows the correlation of the errors (y − p) between the candidates and the baselines. Any blend after that is a new decision, taken before the pre-registration.
- **Calibration.** Platt (logistic regression on the logit of one forecast, as in the probe) rescales a single model, so it is not a stack. Each block's calibrator follows Decision 4. The report shows raw and calibrated Brier side by side.
- **Choice rule.** The candidate with the highest mean Brier skill against the daily clim28 over H = 1, 3, 6, on CHOOSE blocks 3–6 pooled. One candidate serves all three horizons.
- **The bar (the user chose the strict one).**
  - On the benchmark, the chosen forecaster passes if its Brier skill against the daily clim28 **and** against `RecentLevel` has a 95% Kyiv-day block bootstrap CI above 0, on at least 2 of 3 horizons, pooled over all 24 oblasts.
  - The bar decides only what we claim. The tool keeps the chosen forecaster whatever the result, because switching models on the benchmark would be tuning on it.
- **Saved artifacts (the user).**
  - `models/<chosen>.joblib` holds the forecaster the tool will use. For each H:
    - the model is fitted on everything known at the map cutoff;
    - its Platt is fitted on the last 14 days of benchmark forecasts.
  - Step 4 loads this file. Step 7 scores exactly this file, and its SHA-256 is logged before the holdout is opened.
  - Every row's forecasts go to `results/{choose,benchmark}_forecasts.csv.gz`, so each reported number can be rechecked without retraining.
- **Framing claim (the user).** CLAUDE.md said the target "beats a 28-day climatology"; Wrong #9 showed this holds only against a frozen one. CLAUDE.md now says so, and gets the measured result after the benchmark.


### Step-3 continuation (2026-10-11)

- The previous session stopped after writing the serialization test, before implementing `Forecaster`. Its test failed at import; it also constructed an invalid date (`2026-09-028`). Corrected that date, then implemented `ForwardRun.final` and trusted-artifact joblib save/load. Horizons own separate fitted models and OOF calibrators; metadata includes counts, feature names, versions, cutoff and the code commit.
- Recovered the approved plan into `research/step-3-plan.md`. The user explicitly limited the resumed scope to step 3. No live features, page, new candidates, blend, tuning or holdout scoring is included.
- The registered choice and strict benchmark bar from Decision 5 are unchanged. Completion uses the fixed choice rule; no new discretionary blend is introduced after viewing correlations.
- Added `Scores`, Kyiv-day block bootstrap (1,000 resamples, seed 0), per-region counts, reliability, error correlations and the strict bar. Worked examples tested: daily skills -0.5/+0.5 give CI [-0.5,+0.5]; 99 rows are flagged, 100 are not; both references must have lower CI > 0 on at least two horizons. Zero-reference-loss or undefined intervals cannot count as a pass.
- Added the offline `evaluate choose|benchmark` CLI. Benchmark refuses before pre-registration; either stage refuses to overwrite frozen reports/forecasts/summary. Data use is pinned to the first API pull and the frozen map; later pulls cannot change this evaluation. Source-manifest and output SHA-256 hashes are recorded.
- **Wrong #14: "CatBoost defaults" do not imply ordered boosting.** The original plan described ordered boosting as if it were the default here. Kept the approved library defaults, corrected the code docstring, and disabled only auxiliary training-file output. The effective mode will be inspected rather than inferred.
- **Test correction:** the first final-calibration test passed even after removing the completed-label purge, because its raw-forecast table already ended at the fit cutoff. Extended the worked example with later rows. The mutation now fails (14 calibration rows instead of the expected 9); the code was restored. Final fit uses 14 completed rows, and the calibrated constant forecast is 4/9.
- The saved final model is refitted at the cutoff. Serialization must reproduce this final model's forecasts, not the last block model's forecasts (the latter has a different training window).
- **Verification before any model score:** 89 tests passed, including all five candidates’ end-to-end truncation checks and planted-leak controls. The strengthened final-calibration test also passes after restoration. Existing SciPy deprecation warnings are covered by the existing SciPy < 1.18 pin.


### CHOOSE results (selection evidence, not independent)

- Run code: `e789a3fd1bdbee1612dcdcec6e42ac921729fb71`; `evaluate choose` used only rows before 2026-09-12 21:00 UTC. Six sequential blocks, first two calibration warm-up, last four scored. No benchmark or post-map-cutoff outcomes were scored.
- All 24 modeled regions (23 oblasts plus Kyiv City); scored n = 20,607 / 20,566 / 20,501 for H = 1/3/6. At H = 6 the three smallest regions are Donetska 48, Dnipropetrovska 49, Kharkivska 66, all flagged "quality not verified".
- Mean calibrated Brier skill versus daily clim28, by the registered rule:

  | Candidate | Mean skill |
  |---|---:|
  | logistic | 0.106779 |
  | gbm_clim | 0.092946 |
  | gbm_recent | 0.090746 |
  | gbm | 0.087297 |
  | catboost | 0.048026 |

- **Winner: logistic**, serving all three horizons. Brier 0.0997 / 0.1112 / 0.1098 (raw 0.1013 / 0.1147 / 0.1120). LightGBM wins H = 1 individually; logistic wins the registered three-horizon average. This is why the strongest survey teams’ model family is not itself a choice rule.
- The clim28 feature and 60-day recency weights gave small mean gains over unweighted GBM on CHOOSE; neither beat logistic. These comparisons were used for selection and are not independent claims.
- Candidate error correlations are high (about 0.936–0.996 across distinct candidates). No blend or tuning is introduced. This does not prove that no blend could help; it keeps the approved scope and choice rule.
- Saved `results/choose_report.md`, `results/choose_summary.json`, `results/choose_forecasts.csv.gz`. Forecast-file SHA-256: `73230d47236c8978da5052ea3e8f6001057cf1e009c0317f64362462c986a726`. An independent NumPy calculation from the CSV reproduces all five mean skills and the winner to < 1e-12; all rows satisfy T + H <= the CHOOSE cutoff.
- Additional mutation checks caught UTC-day grouping, flagging n = 100, and accepting CI lower bound = 0; all code restored. `python main.py check` reproduces the existing data report byte for byte.


### Benchmark pre-registration (before any benchmark score)

- **CHOSEN = "logistic"**, determined solely by Decision 5's fixed CHOOSE rule. No stacking, new candidate, tuning or benchmark-driven substitution.
- Score this candidate once on the four BENCHMARK forward blocks, 2026-09-12 21:00 UTC through 2026-10-10 19:03 UTC. The historical benchmark was already seen by the feasibility probe and must be described that way.
- **Strict bar unchanged:** both daily clim28 AND recent7 95% Kyiv-day bootstrap CI lower bounds must be strictly > 0 on the same horizon, on at least 2 of H = 1/3/6. Use 1,000 resamples, seed 0, all 24 modeled regions, flag regional n < 100.
- Keep logistic whatever the verdict; the verdict controls the claim. Fit the final models on labels completed at MAP_CUTOFF and their Platt calibrators on the preceding 14 days of OOF forecasts. Save `models/logistic.joblib` and its SHA-256. That exact artifact is reserved for step 7's untouched holdout, which remains unscored here.


### Benchmark results and step-3 completion

- **Pre-registration commit:** `30cb39a1c08edd62ecc7f67a7d1c49b47fe1d12a`, recorded before the single `evaluate benchmark` run. No candidate or setting changed after selection. The same logistic CHOOSE raw forecasts were regenerated exactly, checked against the frozen CHOOSE CSV.
- Four sequential benchmark blocks for each horizon, all 24 modeled regions, completed labels only. Pooled results:

  | H | n | Logistic Brier | Skill vs daily clim28 (95% CI) | Skill vs recent7 (95% CI) | Both lower bounds > 0 |
  |---|---:|---:|---|---|---|
  | 1 h | 18,538 | 0.12460149 | +0.0753 [+0.0535, +0.0995] | +0.0547 [+0.0353, +0.0743] | yes |
  | 3 h | 18,492 | 0.13334334 | +0.0789 [+0.0399, +0.1233] | +0.0476 [+0.0087, +0.0821] | yes |
  | 6 h | 18,419 | 0.12350017 | +0.0667 [+0.0201, +0.1156] | +0.0280 [-0.0272, +0.0783] | no |

- **Registered bar: PASS (2 of 3).** The historical benchmark supports a pooled improvement against both strong references at 1 and 3 h. At 6 h the point gain versus recent7 is positive but its interval crosses zero. This is not evidence for every region, or an untouched-holdout claim.
- **Frozen final artifact:** `models/logistic.joblib`, SHA-256 `ffbce213e5e203c6246c2c2e8f4bfb4461349a5837545e487467973b18219243`. Final training counts = 267,259 / 267,213 / 267,140; OOF calibration counts = 9,202 / 9,156 / 9,083. Fit cutoff 2026-10-10 19:03 UTC; calibration window 14 days. Metadata records the pre-registration commit and pinned library versions.
- **Forecast rows:** `results/benchmark_forecasts.csv.gz`, SHA-256 `19db7e3d0d064c47c50c1ff81d3edfcff411fd3b58a421e76b3b1bc4ceffd155`. Independent NumPy arithmetic from the CSV reproduces all point skills to < 1e-12. Boundaries, four blocks and all 24 regions verified for each horizon. Full report and machine-readable summary are committed alongside it.
- **Fresh-process load verified.** Loaded the saved artifact, computed features at its cutoff for 12 clear regions, checked all three probabilities are finite and in [0,1], then saved/loaded it again and obtained exact prediction equality. Those cutoff features also match features from records truncated to what was event-time-known then. No post-cutoff outcomes were used for this check.
- **Freeze protection verified:** repeat CLI calls refuse existing CHOOSE and benchmark artifacts before training. Both output hashes still match. Metric/CLI tests pass after pre-registration; 89 tests passed before scoring, and the strengthened final-calibration test passed separately after its mutation correction. `check` remains byte-identical.
- Preserved the previous session's generated `catboost_info/` directory and added it to `.gitignore`; new CatBoost fits suppress auxiliary files.
- **Open limitation:** final API record revisions are not publication-time snapshots. The historical event-time checks do not remove this risk; live snapshot comparison and the untouched holdout are reserved for later steps. Steps 4–8 are not implemented in this continuation.

## 2026-10-12: step 4 (live forecast)

### Decision 6: the live forecast runs on the saved data

- **The user.** Plan on the data we already have.
  - `predict` does not re-download history: a full `month_ago` pull takes about 13 min at 2 requests per minute.
  - The saved data are refreshed only by `fetch` (daily).
  - The forecast is made as of the time the saved data reach.
- **Check: where do the saved data end?**
  - The only pull, `20261011T1247Z`, fetched its regions 12:47:56–13:13:07 UTC.
  - The server's `meta.last_updated_at` reads 12:46:28–13:12:39. It is always earlier than the fetch, and regions fetched minutes apart share it, so it is the server's snapshot time.
  - **Data trap:** `fetched_utc` can be about 1.5 min later than the snapshot. A start inside that gap would look "clear".
- **Decisions.**
  1. **T is where the saved data end, not the wall clock.**
     - For each of the 24 regions take its newest `last_updated_at`. T is the earliest of these, floored to the minute; for this pull, 2026-10-11 12:46 UTC.
     - `predict` makes no network call and trains nothing: it loads `models/logistic.joblib` (Decision 5). It prints how old the data are.
     - Each `fetch` gives one new forecast moment.
     - A pull takes about 25 min, so the regions fetched later hold records after T. They are cut as `TruncationCheck.known_at` cuts records: starts at or after T are dropped, and ends after T are unknown.
  2. **24 rows per T.**
     - A region under alert in the minute before T gets a level: red if any oblast or raion record covering that minute is red, otherwise yellow. It gets no probability: the model forecasts a new start for a clear region only.
     - A clear region gets `p1/p3/p6` and the two registered references: `clim28`, counted at 00:00 Kyiv of T's day as in the benchmark, and `recent7`.
  3. **Threats are not logged.** History has no `threats` field, and T is not "now". The levels from Decision 3 stay.
  4. **The log** is `results/forecast_log.csv`, append-only and committed.
     - Columns: T, `made_at`, the region, `under`, the level, the three forecasts and references, the 19 features and the model's SHA-256.
     - A T already in the log is not appended again; the forecast is deterministic.
     - A row with `made_at` > T + H is a replay from the saved pull, not a live forecast. Step 7 reports the two separately.
  5. **Scoring runs on demand and stores nothing.**
     - A logged clear row is scored at H once T + H is inside the saved data. Its label is an episode start in [T, T + H) in the current history.
     - Per horizon: n and the Brier score of the model, clim28 and recent7.
     - Decision 4's revision check: the forecast at T is recomputed from the current history. The rows whose features changed and the model's Brier on them are reported.
     - No bootstrap CI: by the deadline the log holds one moment per pull.
  6. **Holdout rule.** Every T falls after MAP_CUTOFF, so its outcomes are the untouched holdout. In step 4 `score` runs only in synthetic tests; its first real run is step 7, after that step's pre-registration.
- **Plan:** [research/step-4-plan.md](research/step-4-plan.md).

### Step 4 result (2026-10-12 ~12:08 Kyiv)

- **Code.**
  - `data.api_asof`: where the saved history ends.
  - `alerts/live.py`:
    - `forecast`: 24 regions at T, from records known at T;
    - `log`: append-only, once per T;
    - `score`: outcomes once a window closes, plus the revision check.
  - `main.py predict | score`: offline; `predict` takes about 2 s.
- **First forecast moment: T = 2026-10-11 12:46 UTC (15:46 Kyiv).**
  - It was made 20.3 h after T, so all its windows had already closed. It is a replay from the saved pull, not a live forecast; `made_at` records this.
  - At T, 13 regions were under alert (5 red, 8 yellow) and 11 were clear.
  - An independent check straight from the records (oblast and raion records covering 12:45–12:46) gives the same regions and levels.
  - Every row carries the registered model SHA-256, `ffbce213…`.
- **Nothing was scored.** `score` reports that no logged window closes before 12:46, where the saved data end. The holdout stays unscored.
- **Tests.** 97 pass: 89 old plus 8 new. Each new test either failed first, or was checked by a mutation; every mutation was caught:
  - an alert ending at 11:59:30 counts in the minute before T (mutation: `end > T`);
  - clim28 is counted at 00:00 Kyiv (mutation: counted at T);
  - levels come only from records known at T (mutation: from all records, caught at 6 of 11 moments by `TruncationCheck`);
  - "still on" is not the same as "no end" (mutation: `end.isna()`);
  - the revision check compares the features, not only `under`;
  - a clear region has no level (on the real pull).
- **Small finding.** The CSV round trip keeps the features exact: the revision check also passes with exact equality. `np.isclose` stays as a margin.
- **Unchanged.** `check` rewrote the same data report byte for byte, and `evaluate` still refuses to overwrite.

### Code review of step 4 (2026-10-12)

A spec review found two P2 bugs and one P3. Each was reproduced on a synthetic worked example before the plan, then fixed test-first; each new test failed before its fix.

- **Wrong #15: `score` crashed when every logged region was under alert.**
  - **Before.** Only clear rows are scored. A log whose rows were all under alert left nothing, and `pd.concat` of nothing raised `ValueError`: the trap of Wrong #8 again. Such a moment is real: on 2026-08-04 at 20:30 Kyiv every oblast was under alert.
  - **After.** `score` returns an empty table with the log's columns and types plus the score columns. The CLI says there is nothing to score, in words that hold both when no window has closed and when no region was clear.
- **Wrong #16: the revision check compared different rows.**
  - **Before.** When a later revision puts a region under alert at T, its recomputed forecast is NaN, because the model forecasts clear regions only. `.mean()` skipped that row while `n` counted it, and the logged Brier still covered every row. In the example (Lviv's all-clear withdrawn, T = 12:00), n = 24 but the recomputed Brier covered 23 rows; on those 23 rows the logged Brier is 0.0433, not 0.0415.
  - **After.** The per-horizon table moved from `main.py` to `live.summary`, where it is tested.
    - The main score still covers every logged clear row: it scores what was published. Dropping rows because of later revisions would condition it on the future.
    - The revision check shows its coverage, `still_clear` (the rows still clear at T in the current records), and compares `model_logged` with `model_recomputed` on exactly those rows. This replaces `model_on_revised_features`.
- **Wrong #17: a red record of zero or negative length turned the level red.**
  - **Before.** The level had its own rule for "a record covering the minute before T". It did not drop the empty intervals that `episodes()` drops, so yellow since 11:00 plus a red record 11:59:30–11:59:30 showed 🔴.
  - **After.** Red is read from the red records through the same `AlertGrid` as `under`. An empty record covers nothing, and red implies under by construction. The step-4 mutation "levels from all records" no longer applies: `AlertGrid` itself keeps only what is known at T.
  - **Measured.**
    - The saved data hold 2 oblast or raion records with end ≤ start, none of them red.
    - The new rule gives the same level as the old one at all 4,165 ten-minute moments × 24 regions from the splice to the map cutoff: 19,383 red region-moments, 0 differences, no holdout moment.
    - A fresh forecast at the logged T, 2026-10-11 12:46, reproduces the log: 5 red, 8 yellow, the same numbers. The log stays as committed.
- **Tests.** 100 pass: 97 before, plus three. The test helpers now build a tz-aware `end` even when every alert is still on, and the test log carries `made_at`, as `predict` writes it. Mutations, all caught:
  - the logged Brier taken over all n rows (0.0415 ≠ 0.0433);
  - `still_clear` counting all n rows;
  - an untyped empty score (its `ts` loses the datetime type).
- **Unchanged.** `predict` reports the moment as already logged. `score` has nothing to score, because the saved data end at T, so the holdout stays unscored.

## 2026-10-12: step 5 (history analytics)

### Decision 7: what the history analytics count

- **The user.** The minimal scope: weekly load, the reform windows and the red share. No hour-of-day profile.
- **Check before planning (descriptive only, nothing modelled, nothing after MAP_CUTOFF):**
  - National share of time under alert: 0.24 in 2025-10, 0.32 in 2026-08, 0.41 in 2026-09 and 10. Starts per region-day: 2.0 → 3.5 → 4.9–5.5.
  - Red share of alert minutes, SPLICE → MAP_CUTOFF: 0.46 overall, falling from 0.66 on 09-12 to 0.22–0.31 on 10-08 → 10-10.
- **Decisions.**
  1. **One data function, `data.daily`.** Per (Kyiv day, region): the minutes of the day in the window, minutes under alert (the union of oblast and raion records), episode starts (restarts count), and red minutes by the same union rule as the live level. Red is NaN before SPLICE: the map has no levels. Weeks, months and reform windows are groupbys of this table.
  2. **Reform windows:** 28 days on each side of 2026-09-07 00:00 Kyiv, so both sides have the same length.
  3. **Markers, not causes.** The report marks 2025-12-15 (raion-level alerting) and 2026-09-07 (levels). The rise began in late August (feasibility.md), so the before/after table describes, it does not attribute.
  4. **Red is an upper bound.** History keeps only each record's final level (yellow → red is an in-place update), so a record that turned red counts as red for its whole length.
  5. **Holdout.** The analytics stop at MAP_CUTOFF, as `check`'s per-oblast table does.
- **Plan:** [research/step-5-plan.md](research/step-5-plan.md).

### Step 5 result (2026-10-12 ~13:50 Kyiv)

- **Code.**
  - `data.daily`: per (Kyiv day, region), the day's minutes in the window, alert minutes, episode starts and red minutes. `data.REFORM` = 2026-09-07 00:00 Kyiv.
  - `main.py history`: offline, about 1 s. It writes `results/history_report.md` from 2025-10-04 (the first full Kyiv day) to the map cutoff. A rerun gives the same bytes.
- **One change to the plan.** The per-region table shows the share difference (after − before), not the ratio. On near-zero western bases the ratio gave `inf` for Zakarpattia (0.000 → 0.002) and 42× for Lviv (0.000 → 0.014).
- **What the history shows (measured, nothing after the map cutoff; descriptive only):**
  - **Load.** Share of time under alert, averaged over 24 regions: 0.291 over the year; by month 0.242 (2025-10) → 0.323 (2026-08) → 0.408 / 0.412 (2026-09 / 10). Starts per region-day: 1.99 → 3.51 → 4.93 / 5.54.
  - **The jump came before the level reform.** In the week of 08-24 the share went 0.321 → 0.365 and starts 3.23 → 4.34, two weeks before 09-07. This confirms feasibility.md's "late August".
  - **28 days around the reform:** share 0.340 → 0.407, starts per region-day 3.80 → 5.04.
    - Front-line regions are near saturation and flat: Dnipropetrovska, Donetska, Zaporizka and Kharkivska stay at 0.90–0.97.
    - The rise is in the centre and the west: Kyivska 0.351 → 0.663, Zhytomyrska 0.068 → 0.309, Kirovohradska 0.233 → 0.446, Kyiv City 0.200 → 0.337. Starts per day where they were near zero: Volynska 0.36 → 1.75, Rivnenska 0.75 → 2.96.
  - **Raion-level alerting (week of 2025-12-15):** share 0.198, the lowest week of the year, then 0.267 the week after. No lasting break is visible in the weekly series.
  - **Levels, 2026-09-12 → map cutoff:** red share 0.457 of alert time (an upper bound, final level only).
    - Front line mostly red: Dnipropetrovska 0.98, Donetska 0.91, Kharkivska 0.79, Zaporizka 0.76, Sumska 0.66.
    - Elsewhere mostly yellow: 0.02–0.22. Zakarpattia reads 1.00, but on 1 alert hour.
    - The national weekly red share falls 0.63 → 0.52 → 0.46 → 0.45 → 0.34. Not checked: whether this is a change in the attacks or labelling practice settling after the reform.
- **Wrong #18 (mine, in a mutation run): a crash counted as a caught mutation.**
  - **Before.** The test "an alert still on is censored at `hi`" failed in its own helper: with every `end` missing, `astype` cannot make a naive column tz-aware. My chained command ran two mutations anyway, and both "failed", so they proved nothing. The first try of the restart mutation also failed on a numpy dtype error, not on the assertion.
  - **After.** The helper builds `end` with `pd.to_datetime(utc=True)`, the step-4 fix. Both mutations were rerun on the green state, and both now fail on the assertion.
  - **Rule.** A mutation counts as caught only when the failure is the test's assertion.
- **Tests.** 108 pass: 100 before, 7 test-first in `tests/test_daily.py`, and one acceptance test on the real data. The real-data test checks starts against `episodes`, alert minutes since the splice against `compare`, `red ≤ alert`, `alert ≤ minutes`, and red NaN exactly before 09-12. Mutations, all caught on the assertion:
  - records counted instead of episodes (the overlap test, and the real-data test);
  - restarts merged within 2 min;
  - an alert still on dropped;
  - only regions with records kept.
- **Unchanged.** `check` rewrote the same data report byte for byte. `predict` reports the moment as already logged. The monthly shares recomputed from `daily` equal the planning numbers.
