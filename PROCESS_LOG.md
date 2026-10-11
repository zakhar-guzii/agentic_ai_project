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
