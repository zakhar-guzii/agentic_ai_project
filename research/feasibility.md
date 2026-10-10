# Feasibility probe: what can be built in ~2 days, and how good can it be on the latest period?

Measured on 2026-10-10, about 17:00–19:30 UTC. Alert data runs to **2026-10-10 19:03 UTC**. Every number below comes from my own runs. Things I did not check are listed in §7. Scripts and raw downloads are in the session scratchpad, under `scratchpad/feasibility/` (`scripts/`, `dl_*/`, `work/*.log`).

## TL;DR

- **Data: use the official map's ranged endpoint. It needs no key and is fresh to the minute.** `map.ukrainealarm.com/api/v2/data/mapGetRangedAlerts` returns raion-level history for about the last year, from 2025-10-03 to now. Fetching all oblasts took 351 requests in about 12 minutes, with no errors.
  - It is the same data as the frozen Vadimkin official file. Over 329 days of overlap, the minute-level Jaccard is **0.994**, and 99.1% of Vadimkin's raion rows have a map row within 60 s (median end difference 0.5 s).
  - It also matches alerts.in.ua (the JustJimer archive) after the reform: **Jaccard 0.998**. The map includes both yellow and red alerts, but does not label which is which.
- **Do not substitute the volunteer (eTryvoga) file.** It captures only 30–42% of official alert-minutes (Jaccard 0.25–0.33). Since the 2026-09-07 reform it is worse: 30% coverage and daily correlation 0.50.
- **Target (a), "a new alert starts within H", is the only target with a clear gain.** It covers oblasts not under alert, on the latest 27 days (2026-09-13 → 10-10).
  - LightGBM with Platt scaling has Brier skill vs a recent climatology of **+0.12 / +0.15 / +0.18** at H = 1 / 3 / 6 h. All 95% CIs exclude 0. AUC is 0.85 / 0.87 / 0.89.
  - Climatology alone (oblast × hour of day, last 28 days) already reaches **AUC 0.82 / 0.87 / 0.90**. A high AUC is cheap; skill against a recent climatology is the honest metric.
  - **The gain depends on the regime.** On an earlier, calmer window (2026-07-15 → 08-13) the skill was +0.03 / +0.02 / −0.00. The model wins mainly because it adapts faster than climatology when alert activity shifts.
- **Target (b), "any alert tonight", and target (c), "daily alert-minutes", do not reliably beat climatology.** Night skill is +0.09 (CI −0.03…+0.20) and is −0.21 in July. Daily MAE is 138 vs 146 min (skill +0.05, CI −0.04…+0.14).
- **Text from Telegram, scraped without login: feasible, but almost no lift.**
  - A per-oblast count of @kpszsu threat posts in the last 3–6 h lowers the Brier score of (a) by about **1–2.5%** relative (CIs mostly exclude 0).
  - For (b) the effect is inconsistent.
  - The monitor channel (@radar_raketaa) and national post counts add nothing, and stacking all four text features made things *worse* in one split.
- **Regime shift inside the evaluation window.** In the 21 modelled oblasts, the share of time under alert rose from about 0.20 (Jun to mid-Aug) to 0.30–0.39 (Sep–Oct), and starts per oblast-day rose from about 3 to 5–6. The rise began in late August, before the yellow/red reform. Climatology computed over the full training period loses 20–40% Brier against a 28-day climatology.

## 1. Data assembly recipe (no API keys)

| Period | Source | How |
|---|---|---|
| 2022-03-15 → 2025-10-03 (optional long history) | Vadimkin `official_data_uk.csv` | Download from GitHub. `drop_duplicates()` removes 113,845 of 299,275 rows. Keep levels oblast + raion and drop hromada. |
| **2025-10-03 → now** | **map ranged endpoint** | `GET https://map.ukrainealarm.com/` and read the token from `id="api-token" value="…"`. Then `api/v2/data/mapGetRangedAlerts?startDate=YYYYMMDD&endDate=YYYYMMDD&regionId=<state id>&apiToken=…`, with one request per oblast per 31 days and a 1 s pause. The answer is a JSON string that contains a JSON list. `isContinue=true` means the alert is still ongoing, so treat its end as unknown and censor it at the snapshot time. |
| Levels (yellow/red), 2026-09-06 → now | JustJimer `archive/alerts_in_ua.csv` | This is only needed if levels become features. Use `air_raid` rows only. Before 2026-09-07, `red` is just the default value. |

Turning these into a series:

- Build one series per oblast (24 = 23 oblasts + Kyiv city). The value is "some part of the oblast is under alert", computed as the union of raion- and oblast-level intervals. An episode start is a transition from clear to alert.
- **Drop hromada units from the map answer.** The state query also returns 8 hromada units with standing alerts, for example Lypetska, open since 2026-03-10. Left in, they keep Kharkivska and Dnipropetrovska permanently "under alert": 39 vs 1,159 episodes from March to August.
- Exclude Luhansk and Crimea, which are under permanent alert. I also excluded Dnipropetrovska, Kharkivska and Donetska, which were under alert for 80% or more of the training period, decided on training data only.
- Use the region IDs from `siren.pp.ua/api/v3/regions`. Unit names match exactly across Vadimkin, the map and JustJimer.

### Seam checks (minute-level union per oblast)

| A vs B | Window | Minutes B/A | Jaccard | Episode starts A / B | Starts matched ±2 min | Daily corr / MAE |
|---|---|---|---|---|---|---|
| Vadimkin vs map | 2025-10-04 → 2026-08-29 (329 d) | 0.997 | **0.994** | 20,859 / 20,879 | 99.7% / 99.6% | 0.996 / 2.2 min |
| Vadimkin vs map | monthly, Oct 2025 → Aug 2026 | 0.97–1.01 | 0.968–1.000 | equal ±2% | ≥ 98% | 0.97–1.00 |
| Vadimkin vs map | @air_alert_ua outage, 08-29 05:00 → 09-02 14:00 | 1.19 | **0.57** | **0** / 500 | – | 0.80 / 283 min |
| Vadimkin vs map | 09-02 14:00 → 09-07 05:00 (up to the freeze) | 0.998 | 0.982 | 450 / 454 | 99.8% / 98.7% | 0.999 / 4.2 min |
| map vs JustJimer (red + yellow) | 2026-09-06 12:00 → 10-10 09:00 | 1.001 | **0.998** | 4,178 / 4,174 | 99.8% / 99.8% | 1.000 / 0.7 min |
| map vs JustJimer, red only | same | 0.47 | 0.47 | – | 19% | – |
| Vadimkin vs JustJimer | the only direct overlap, 17 h | 1.07 | 0.93 | 48 / 52 | 100% / 92% | – |
| map vs volunteer | quarterly, 2025-10 → 2026-09 | 0.36–0.42 | 0.27–0.33 | volunteer has 1.5–1.8× more | 34–45% | 0.48–0.66 |
| map vs volunteer | 2026-09-07 → 10-10 | 0.31 | 0.25 | 4,100 / 4,930 | 21% | 0.50 / 452 min |

Conclusions:

- **During the outage, Vadimkin has no new starts, and alerts that were still open keep running with inflated durations.** The map fills the gap correctly.
- The JustJimer archive effectively starts on 2026-09-06, because of the API's rolling `month_ago` window.
- **The seam does not matter for modelling.** Splicing Vadimkin (up to 2026-08-29) onto the map changes every test metric by 0.003 or less in skill.

## 2. Setup

- **Grid and features.** Predictions are made every 30 min. Features use only minutes before T:
  - own recency: minutes since the oblast was last under alert, minutes since its last start, starts in the last 3 h / 24 h, alert-minutes in the last 24 h / 7 d;
  - neighbours: share of neighbouring oblasts under alert, their starts in the last 1 h / 3 h, minutes since a neighbour last started;
  - national: number of oblasts under alert now and 1 h ago, national starts in the last 1 h / 3 h;
  - calendar and identity: Kyiv hour, day of week, oblast.
- **Labels.** A start in [T, T+H).
- **Splits (purged, chronological).**
  - train: 2025-11-15 → 2026-08-29, minus H;
  - dev: 08-29 → 09-13, used for Platt scaling and text stacking;
  - test: 2026-09-13 → 2026-10-10 13:00 UTC, scored once;
  - two earlier folds, with the same layout shifted back by 30 and 60 days.
- **Models.** LightGBM: 300 trees, 31 leaves, `min_child_samples` 200. It takes about 10 s per full run on a laptop.
- **Target (b).** Issued at 21:00 Kyiv; positive if any alert-minute falls between 23:00 and 07:00. Climatology is the oblast's rate over the last 28 nights, with Laplace smoothing. Persistence is last night's outcome.
- **Target (c).** Issued at 00:00 Kyiv. The model is a LightGBM with L1 loss on lags 1–7, 7- and 28-day means, and the neighbour and national values for the previous day. Climatology is the trailing 28-day mean.
- **CIs.** Day-block bootstrap, 1,000–2,000 resamples.

## 3. Results on the latest period (test 2026-09-13 → 10-10, 21 oblasts)

Skill = 1 − Brier / Brier(clim 28 d), or 1 − MAE / MAE(clim 28 d) for (c). The 95% CI comes from the day-block bootstrap.

| Target | n | Base rate | Persistence | Clim. 28 d (AUC) | Clim. full train | LightGBM | LightGBM + Platt | AUC (GBM) |
|---|---|---|---|---|---|---|---|---|
| (a) start ≤ 1 h | 18,214 | 0.234 | Brier 0.237, skill −0.64 | 0.144 (0.82) | −0.20 | 0.129, +0.10 [0.08, 0.13] | **0.127, +0.12 [0.09, 0.15]** | 0.85 |
| (a) start ≤ 3 h | 18,214 | 0.414 | 0.270, −0.64 | 0.165 (0.87) | −0.35 | 0.145, +0.12 [0.07, 0.17] | **0.141, +0.15 [0.10, 0.20]** | 0.87 |
| (a) start ≤ 6 h | 18,214 | 0.531 | 0.249, −0.56 | 0.160 (0.90) | −0.40 | 0.137, +0.14 [0.08, 0.20] | **0.131, +0.18 [0.12, 0.25]** | 0.89 |
| (b) alert tonight | 567 | 0.714 | 0.175, −0.89 | 0.092 (0.94) | – | 0.084, +0.09 [−0.03, 0.20] | 0.085, +0.08 [−0.10, 0.22] | 0.94 |
| (c) daily alert-minutes | 567 | mean 492 min | MAE 159, −0.09 | MAE 146 | – | **MAE 138, +0.05 [−0.04, 0.14]** | – | – |

Earlier folds, LightGBM + Platt skill vs 28-day climatology:

| Test window | (a) 1 h | (a) 3 h | (a) 6 h | (b) | (c) |
|---|---|---|---|---|---|
| 2026-08-14 → 09-12 (escalation + reform) | +0.08 [0.06, 0.09] | +0.10 [0.06, 0.14] | +0.09 [0.02, 0.15] | +0.05 [−0.05, 0.16] | +0.07 [−0.02, 0.17] |
| 2026-07-15 → 08-13 (stable) | +0.03 [0.01, 0.05] | +0.02 [−0.01, 0.05] | −0.00 [−0.05, 0.04] | **−0.22** [−0.47, −0.05] | −0.04 [−0.13, 0.04] |

How to read these:

- **(a) is learnable; most of the structure is oblast × hour.** The model's extra value grows when activity shifts, and its top features by gain are oblast, alert-minutes over 7 d and 24 d, neighbour activity, and hour.
- **(b) and (c) are about at climatology level.** Their test sets of 27 days × 21 oblasts are too small to separate models.
- **Binary persistence is a weak baseline in every case.**

## 4. Text feature (Telegram, `t.me/s/` web preview, no login)

**Collection.**

- @kpszsu: 516 pages, 10,318 posts from 2026-08-27 to 10-10. It took about 17 min at about 2 s per page, with no 429s. The channel posts about 229 times a day, which means about 20 pages per day of history.
- @radar_raketaa: 75 pages, 1,498 posts, about 33 a day.
- @war_monitor was nearly silent on 10-09/10 ("технічні роботи", "technical works") and was not used.
- Post timestamps (UTC, original posting time) are present on every post. 84% and 81% of posts respectively name an oblast or a big city, matched with a stem regex.
- **Leakage caveat:** the preview shows only the latest edit, and the edit time is not visible. 2% of @kpszsu posts and 99% of @radar_raketaa posts are marked edited.

**Experiment.**

- **Features:** threat-post counts in (T − N, T], with N = 3 h for (a) at H = 3 and N = 6 h for (a) at H = 6 and for (b). There are four of them: per channel, a national count and a per-oblast count.
- **Method:** a logistic stack on top of the out-of-sample GBM (or climatology) prediction, fitted on a dev window and scored on test. I compared it with the same stack without text. ΔBrier < 0 means the text helps.

| Target | Split (dev / test) | All 4 text features on top of the GBM | Per-oblast @kpszsu count only |
|---|---|---|---|
| (a) 3 h | 08-29..09-12 / 09-13..10-10 | +0.0036 [+0.0004, +0.0069] (worse) | **−0.0025 [−0.0036, −0.0016]** (−1.8%) |
| (a) 3 h | 09-07..09-20 / 09-21..10-10 (post-reform) | −0.0029 [−0.0049, −0.0012] | **−0.0034 [−0.0053, −0.0019]** (−2.5%) |
| (a) 6 h | first split | +0.0029 [+0.0002, +0.0057] (worse) | −0.0017 [−0.0042, +0.0005] |
| (a) 6 h | post-reform split | −0.0025 [−0.0051, −0.0001] | **−0.0029 [−0.0051, −0.0010]** (−2.4%) |
| (b) tonight | first split | +0.0093 [+0.0008, +0.0186] (worse) | −0.0008 [−0.0014, −0.0002] |
| (b) tonight | post-reform split | +0.0091 [−0.0018, +0.0208] | +0.0018 [+0.0004, +0.0031] (worse) |

**Verdict.**

- **The per-oblast Air Force mention count carries real signal on its own.** Its univariate test AUC is 0.68 for (a) at 3 h, 0.74 at 6 h and 0.84 for (b).
- **It is almost entirely redundant with alert history.** It adds about 2% Brier at most for (a), and nothing reliable for (b).
- **National post counts and the monitor channel add nothing.**
- A text-heavy project would be repeating the known finding that text barely helps once neighbour features are present (lbgos). It is worth one honest ablation table, not the core of the project.

## 5. Practical blockers

- **API tokens.**
  - alerts.in.ua (levels and threats live, history for about 1 month) and api.ukrainealarm.com both need form-based keys with manual approval. That is **unlikely to arrive before the 2026-10-12 deadline**, and none of this probe needed them.
  - Telethon needs a my.telegram.org app (phone number). It is not needed: the web preview worked.
- **The map endpoint is undocumented.** It uses an anonymous page token, keeps about 1 year (the oldest record was 2025-10-03), carries no levels, and its terms of service are unclear. Cache the raw JSON once and cite it.
- **Rate limits.**
  - map: 351 requests at about 1 per second, no errors;
  - `t.me/s`: about 2 s per page, no throttling seen;
  - JustJimer and Vadimkin: plain GitHub raw files.
- **Time cost.** Data pull about 15 min (map) + about 17 min (@kpszsu, 6 weeks). Full pipeline run about 10 s. All the code for this probe is about 600 lines.
- **Data quirks to handle:**
  - hromada standing alerts;
  - Vadimkin duplicates and its 08-29 → 09-02 outage;
  - ongoing alerts (`isContinue`);
  - DST (Kyiv);
  - the rising alert level from late August, so calibrate on recent data.

## 6. Ranked project directions (for the deadline of 2026-10-12 23:59 Kyiv)

1. **Calibrated per-oblast "new alert within 1/3/6 h" forecaster on fresh map data, with honest evaluation.**
   - Expected quality: Brier skill +0.10…+0.18 vs a 28-day climatology on the latest month, AUC 0.85–0.89, and about 0 in stable periods.
   - Effort: about 1 day, since this probe is the skeleton.
   - Differentiators: a purged split, a rolling-origin table (as in §3), a reliability diagram, and an explicit statement that climatology already reaches AUC 0.82–0.90.
2. **Item 1 plus a "regime-shift / data-trap" story.**
   - Content: the seam table, the Vadimkin outage and freeze, hromada standing alerts, volunteer under-coverage, the yellow/red reform, and the late-August escalation that breaks long-window climatology.
   - Effort: +0.5 day.
   - This targets KSE's "handling errors / verify facts" criterion directly, and few of the June repos can show it.
3. **Item 1 plus a text ablation using @kpszsu per-oblast mentions.**
   - Expected: +1…2.5% Brier at 3–6 h, nothing for tonight.
   - Effort: +0.5 day (scraper and regex exist). Worth it as a rigorous negative or small-positive result, with the caveat about edits.
4. **Live usable artifact:** a CLI or Streamlit page that fetches the map and prints the next-6 h probabilities per oblast, and logs predictions so they can be scored later.
   - Effort: +0.5 day on top of item 1. It answers "practical outcome".
5. **Tonight or daily-minutes forecasting as the main product.**
   - Expected: no reliable gain over climatology (skill −0.22…+0.09 across folds).
   - Only worth doing as a baseline-honesty section; not recommended as the core.

## 7. Not verified / limitations

- **Single regime, short test.** There is one main test window (27 days) plus two earlier folds. There was no hyperparameter search and only one feature set, so the model is not tuned.
- **Map endpoint.** I did not check whether the map revises records after the fact; consistency with Vadimkin suggests it does not. I did not check its terms of use or its exact retention.
- **Oblast definition.** Kharkiv and Zaporizhzhia city queries, and all hromada-level alerts, were left out of the union. Including them changes the oblast definition, and I did not evaluate that.
- **Levels and threat types.** I did not test yellow/red levels from JustJimer as features. The data exist only from 2026-09-06.
- **Text features.**
  - The oblast regex for text is heuristic and was not hand-validated.
  - Edit times of Telegram posts are unknown, so a small leakage risk remains, mostly for @radar_raketaa.
  - I did not test whether text helps for frontline oblasts, which were excluded here.
- **Other repos' numbers** (for example lbgos AUC 0.88–0.92) were not reproduced. Their framing is similar, and our climatology alone reaches comparable AUC.
