# Prior work: analysing and forecasting Ukrainian air-raid alerts

_Survey date: 2026-10-10. Scope: public code, notebooks, papers and write-ups that analyse or forecast air-raid alerts in Ukraine. How to get the data (APIs, datasets, Telegram, ISW, weather) is covered in [data-sources.md](data-sources.md)._

All metrics below are **as reported by each project's authors**. They were not reproduced here, with one exception: one notebook was inspected (§3.6). The projects use different targets, horizons and test windows, so the numbers are **not directly comparable** across rows.

## TL;DR

- **This exact task has already been solved in public about 100 times.** It was the Stage 2 take-home of the [KSE Agentic AI Summer School](https://university.kse.ua/en/agentic-ai-summer-school-2026) selection in June 2026. GitHub search finds 116 repos matching "air raid" created 15 Jun–10 Jul 2026, against 26 in the equally long window 15 Sep–10 Oct 2026. 103 repos cite the Vadimkin dataset in their README. A new wave started on 2026-10-09 (see the appendix). The typical submission is EDA, then Prophet/ARIMA/GBM, then a Streamlit/Dash dashboard on [Vadimkin/ukrainian-air-raid-sirens-dataset](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset).
- **Freshness trap (per [data-sources.md](data-sources.md)):** the Vadimkin `official_data` file is **frozen at 2026-09-07**, because its upstream channel @air_alert_ua stopped posting. 38 % of its rows are exact duplicates. Every June project ran before this happened. For the "latest period" you need the alerts.in.ua or ukrainealarm API, or the volunteer file, which is oblast-level only and incomplete.
- **The biggest data trap:** from 2025-12-15 (when nationwide raion-level alerting was announced; confirmed in data-sources.md), the official data records alerts at raion/hromada level. If you keep only `oblast` rows, 2026 looks quiet. One project read that as a "feed collapse" and cut its data at 2025-10-31 ([Vlad1343](https://github.com/Vlad1343/ukraine-air-alerts-timeseries)). Others merge sub-oblast intervals back into oblast-level intervals ([goodfrog33](https://github.com/goodfrog33/air-raid-forecasting-ukraine), [MishaDvali](https://github.com/MishaDvali/Air_raid_alert_analysis_and_prediction), [Trigger111](https://github.com/Trigger111/ukraine-air-raid-alerts-tsa)). See §5.
- **Short horizons work.** The target is "a new alert starts in this oblast within H". The best-documented results:
  - [lbgos/AirAlerts](https://github.com/lbgos/AirAlerts): AUC 0.88–0.92, with Brier 0.112–0.127 against a climatology baseline of 0.200–0.207 at 3–6 h. Tested on the last 14 days up to 2026-10-10.
  - [rayhankhilji/terrestrial](https://github.com/rayhankhilji/terrestrial): AUC 0.86 at 6 h, with Brier 0.150 against 0.185 for persistence. Tested on 2026.
  - [MishaDvali](https://github.com/MishaDvali/Air_raid_alert_analysis_and_prediction): AUC 0.813 and PR-AUC 0.423 at 3 h.
- **Long horizons are hard.** For next-day prediction in a single oblast, logistic regression scored a test AUC of 0.498 and lost to persistence ([kervad28-debug](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction)). Daily counts barely beat seasonal-naive ([h00yaday](https://github.com/h00yaday/kse-air-raid-forecasting)) or don't beat a flat line at all ([Vlad1343](https://github.com/Vlad1343/ukraine-air-alerts-timeseries)).
- **Text signals so far add little at short horizons.**
  - Radar/monitor Telegram channels do carry signal. On top of neighbour-oblast alerts, though, they add nothing: skill went from 0.278 to 0.273–0.277 ([lbgos](https://github.com/lbgos/AirAlerts)).
  - GDELT and Telegram variants gave "small" lift ([goodfrog33](https://github.com/goodfrog33/air-raid-forecasting-ukraine)).
  - ISW and GUR text is used with a "D+1 shift" ([AEGIS](https://github.com/abrukhanska/alarm_prediction)).
  - No project found here shows a clear text lift under a leakage-safe evaluation on the latest period. That is an open gap, and probably more promising at night-ahead or 24 h horizons than at ≤1 h.
- **Anti-patterns seen in public repos:**
  - The target is "alert is active" rather than "alert starts", and the decision threshold is tuned on the test set. One repo claims precision 1.00 this way (§3.6).
  - A single 80/20 split with no baselines.
  - Count-based claims that span the late-2025 granularity shift.

## 1. Context: the KSE selection task

- One June-2026 README quotes the brief as: _"You have two days to complete a mini pet-project in Python solving a real-world defense problem: Time Series Analysis of air raid alerts in Ukraine."_ ([MishaDvali](https://github.com/MishaDvali/Air_raid_alert_analysis_and_prediction)).
- Other READMEs say the work was done "for Stage 2 of the KSE AI Agentic Summer School selection" ([kervad28-debug](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction), [HATSKER-228](https://github.com/HATSKER-228/time-series-analysis-of-air-raid-alerts-in-Ukraine), [Vlad1343](https://github.com/Vlad1343/ukraine-air-alerts-timeseries)).
- The full June brief is not public, so we can't tell whether it already contained the clauses in our brief: "most recent data", "evaluate on the latest period", "no leakage", and optional text/media.
- The [programme page](https://university.kse.ua/en/agentic-ai-summer-school-2026) lists these selection criteria:
  - **thinking as a process:** do you iterate on AI answers, or accept the first one?
  - **handling errors:** do you spot model weaknesses, verify facts, and adjust?
  - **practical outcome:** is the artifact actually usable?
  - **autonomy:** can you drive the AI workflow to completion?
- The same page describes Stage 2 as a 90-minute online exercise. That does not match the two-day take-home that the June repos describe, so the format may differ between rounds.
- One June README notes that _"the complete AI conversation log is submitted separately through the Stage 2 submission form"_ ([kervad28-debug](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction)).

### 1.1 Confirmed to have passed Stage 2 (June 2026)

The user found these in KSE's Instagram posts about who advanced. Add more here as they turn up.

- **[tbaraniuk/air_alert_analysis](https://github.com/tbaraniuk/air_alert_analysis)**, created 2026-06-20, last pushed 2026-06-21. It is **not a forecasting project**. It is a clean, usable Dash dashboard:
  - **Views:** a monthly choropleth with a slider; a live "currently active" panel down to raion/hromada level; oblast rankings both by alert count *and* by cumulative time under alert; daily series with filters; a 7-day escalation/de-escalation readout; duration histograms by alert type.
  - **Engineering:** a live ingestion pipeline (`alerts.in.ua` API with httpx, pydantic and tenacity) storing into DuckDB. It has a `backfill` mode for roughly the last month and a `live` polling mode. Data from different sources is tagged with separate id ranges.
  - **Historical data:** the Kaggle dataset [cashncarry/airraid-sirens-in-ukraine](https://www.kaggle.com/datasets/cashncarry/airraid-sirens-in-ukraine) (`full_data.csv`, oblast/raion/hromada levels, UTC). Oblast names are canonicalised between the English transliteration and the Ukrainian names.
  - **Honest "Known limitation" section:** hromada names collide across oblasts, which inflates per-oblast totals. It recommends deduplicating on `(started_at, finished_at, location_title)`.
  - **Takeaway:** passing did **not** require a sophisticated model. A working, usable artifact and a clean, honest README were enough. This matches KSE's criteria of practical outcome and handling errors. The AI conversation log and the interview probably carry much of the weight.

## 2. Forecasting results at a glance

| Project | Target (per oblast unless noted) | Horizon | Test period | Model | Reported result vs baseline |
|---|---|---|---|---|---|
| [lbgos/AirAlerts](https://github.com/lbgos/AirAlerts) | new siren start, only for oblasts not under alert; separate all-clear model | 15 min–6 h | last 14 days, ending 2026-10-10 16:20 UTC | LightGBM per horizon, recency-weighted, Platt scaling plus a conservative cap | 1 h: Brier 0.118 vs climatology 0.164, AUC 0.88 · 3 h: 0.127 vs 0.207, AUC 0.90 · 6 h: 0.112 vs 0.200, AUC 0.92 |
| [rayhankhilji/terrestrial](https://github.com/rayhankhilji/terrestrial) | new alert | 6 h | calendar 2026 (trained 2022–2025, calibrated on late 2025) | sklearn gradient boosting with isotonic calibration | AUC 0.86, Brier 0.150 vs persistence 0.185 and climatology 0.199 |
| [MishaDvali](https://github.com/MishaDvali/Air_raid_alert_analysis_and_prediction) | new alert start, on a 30-min grid | 3 h | oblast-era data only, up to 2025-10-31 | HistGradientBoosting | AUC 0.813, PR-AUC 0.423, F1 0.419. Its own v1 baseline (hourly grid, 1 h horizon, LR): AUC 0.763, PR-AUC 0.140 |
| [goodfrog33](https://github.com/goodfrog33/air-raid-forecasting-ukraine) | any alert in [t, t+H−1], **including ongoing ones** (an easier target) | 6 h | expanding-window backtest, 30-day folds | XGBoost | AUC 0.915, log loss 0.364 vs persistence AUC 0.782, log loss 0.505 ([report](https://github.com/goodfrog33/air-raid-forecasting-ukraine/blob/HEAD/reports/final_report.md)) |
| [goodfrog33](https://github.com/goodfrog33/air-raid-forecasting-ukraine) | national hourly alert count | 1 h | same backtest (`--fast` profile, 2 folds) | CatBoost | MAE 1.663 vs naive 2.274 and moving average 1.737 |
| [kervad28-debug](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction) | ≥1 alert start tomorrow (Khmelnytska only) | next day | 2025-10-30 → 2026-06-23 | logistic regression | AUC 0.498; F1 0.282 vs persistence 0.383, so **persistence wins** |
| [h00yaday](https://github.com/h00yaday/kse-air-raid-forecasting) | daily alert count (Kyiv City) | days | time-based backtest | SARIMAX with weekly seasonality | MAE 1.506 vs seasonal naive 1.643 |
| [Vlad1343](https://github.com/Vlad1343/ukraine-air-alerts-timeseries) | daily national count | days | last 60 days up to 2025-10-31 | simple baselines | best RMSE 10.08, about equal to the test std; conclusion: "cannot beat a flat line" |
| [Pavlyshenko & Pavlyshenko 2024](https://arxiv.org/abs/2411.14625) | alert within the next 5 min, for 4 oblasts | 5 / 15 min | 2024-07-01 → 2024-11-06 | random forest, 500 trees | metrics appear only in figures; ongoing alerts are labelled 1 |
| [Youngerfornday/tykho-chy-ni](https://github.com/Youngerfornday/tykho-chy-ni) | any alert tonight, 23:00–07:00 Kyiv time | tonight | rolling 60-night backtest, republished on every build | analog nights plus shrinkage | Brier vs base rate and a reliability diagram on the [live page](https://youngerfornday.github.io/tykho-chy-ni/) |
| [MaksimPrykhodko](https://github.com/MaksimPrykhodko/Ukraine-air-raid-prediction) | alert **active** in the next hour (Kyiv City) | 1 h | last 20 % of hours | XGBoost with Optuna | claims F1 0.87 and precision 1.00. **Not credible**, see §3.6 |

## 3. Notable projects

### 3.1 Strongest references

- **[lbgos/AirAlerts](https://github.com/lbgos/AirAlerts)** (created 2026-10-10). Calibrated per-oblast forecasts of siren **starts** for oblasts not under alert, and of **all-clears** for oblasts that are, at 15 min, 30 min, 1 h, 3 h and 6 h.
  - **Data:** public Telegram channels scraped with Telethon, covering 2025-12-01 → 2026-10-09. `@UkraineAlarmSignal` supplies labels plus threat notes. Radar channels `@kpszsu` and `@deraketaua` were turned into structured events by a TF-IDF + logistic regression classifier trained on 3,000 posts labelled once by an LLM.
  - **Older data was deliberately dropped:** "tactics changed".
  - **Grid and features:** a 5-minute grid. Features use only events before T: time of day, the oblast's own history, neighbour and second-ring oblasts (including minutes since the latest neighbour siren), national counts, and "last-minutes" features.
  - **Split:** train | calibrate | test, purged so that no label window crosses a boundary. Model selection used a separate 14-day dev window, and the final test ran once.
  - **Feature ablation:** skill = 1 − Brier/Brier_climatology, mean over 30 min–6 h:

    | Features | Skill |
    |---|---|
    | time + oblast | 0.162 |
    | + own history | 0.217 |
    | + threat notes | 0.239 |
    | + neighbours | 0.275 |
    | + national counts | 0.276 |
    | + wave timing | 0.278 |
    | + radar channels | 0.273–0.277 |

  - **Radar channels added nothing on top:** "a neighbor siren preceded 94% of siren episodes, radar posts 53%, and radar was the only early warning in 0.6%".
  - **Calibration:** Platt scaling on the last 7 days beat isotonic and longer windows. Without calibration, ECE doubles.
  - It also logs live predictions and scores them afterwards (`forecast score-live`).
- **[rayhankhilji/terrestrial](https://github.com/rayhankhilji/terrestrial)** (EDTH London 2026 hackathon). A live map that fuses more than 25 open streams: Air Force and `war_monitor` Telegram, the official alert map, DeepStateMap, ADS-B, GDELT and others.
  - **"Danger forecast":** the chance of a new alert per region within 6 h. It trains on every alert since 2022 plus reported attacks, weather and moon phase.
  - **Validation:** "Trained on 2022–2025, calibrated on late 2025, and tested only on 2026: never random splits". Each model has a model card that compares it against persistence and climatology.
  - **History sources:** the Vadimkin dataset and VIINA 2.0.
- **[MishaDvali/Air_raid_alert_analysis_and_prediction](https://github.com/MishaDvali/Air_raid_alert_analysis_and_prediction)** (June 2026).
  - **Iterations:** went from v1 (hourly grid, 1 h horizon, LR) to v6 (30-min grid, 3 h horizon, HistGBM, day-of-year sin/cos). The biggest gains came from **target framing and time resolution**.
  - **Geography didn't help:** neighbouring raions "mostly noise" at 1–3 h horizons.
  - **Two data views:** a clean benchmark up to 2025-10-31, and an "operational latest" view up to 2026-06-24. The latter projects raion/hromada alerts back to oblast level: 273,274 raw rows become 140,199 after deduplication.
  - **Descriptive stats:** median alert 40.4 min, p90 182 min, lag-7 daily autocorrelation 0.284.
- **[goodfrog33/air-raid-forecasting-ukraine](https://github.com/goodfrog33/air-raid-forecasting-ukraine)** (June 2026). The most engineered submission ([live demo](https://air-raid-forecasting-ukraine.streamlit.app/)).
  - **Scope:** 12+ models compared by expanding-window backtest, on four targets: count, probability, duration and severity.
  - **Stack:** SHAP, FastAPI, Streamlit with a choropleth, pytest and Docker.
  - **Leakage rule:** features at hour t use data up to t−1 only.
  - **Data:** oblast-level consolidation, because "District-level alerts only appear from late 2025". Luhansk and Crimea are excluded as permanent alerts. Every download is logged with its SHA-256.
  - **Optional "event-signal" variants:** GDELT war-news intensity, and the Telegram channels `war_monitor` and `radar_raketaa`, scraped from the public web preview without a login. Reported lift is "small".
  - **Ceiling:** the national "any alert somewhere" rate is about 93 %, which is degenerate, so binary targets are evaluated per region.
- **[Youngerfornday/tykho-chy-ni](https://github.com/Youngerfornday/tykho-chy-ni)**. "Тихо чи ні?" ("Quiet or not?") is a live per-region forecast of whether there will be an alert tonight.
  - **Method:** analog nights, weighted by the similarity of the national alert count, by recency (half-life 14 days) and by the region's current state, then shrunk toward the base rate. Intervals come from a bootstrap.
  - **Backtest:** each build publishes a rolling 60-night Brier score and a reliability diagram.
  - **Data:** official Vadimkin data is treated as authoritative. Volunteer data fills only the last days, and only for regions where the two sources agree on at least 70 % of the past 60 nights. Live state comes from `ubilling.net.ua/aerialalerts`.

### 3.2 Honest negative and baseline-first results

- **[kervad28-debug](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction)**. Next-day alert in Khmelnytska oblast, using a volunteer-data snapshot of 2026-06-25 with its SHA-256 recorded.
  - **Split:** train ≤ 2025-03-06, validation to 2025-10-29, test 2025-10-30 → 2026-06-23.
  - **Drift:** the positive rate fell from 56.0 % in train to 41.4 % in validation.
  - **Result:** persistence beat logistic regression.
  - It also discloses an accidental look at the test set, a good example of transparent reporting.
- **[Trigger111/ukraine-air-raid-alerts-tsa](https://github.com/Trigger111/ukraine-air-raid-alerts-tsa)**. Kyiv City `has_alert_next_day`.
  - **Data:** 271,160 events (2022-03-15 → 2026-06-20) become 157,315 canonical events after deduplication. The README documents the "Dec-2025 oblast→raion granularity shift" and notes that Kyiv City is single-level, so it is unaffected.
  - **Baselines:** persistence, 7-day rolling mean and seasonal naive.
  - **Metrics:** F1, ROC-AUC, and Brier with the base rate.
  - **Leakage controls:** past-only features are built *after* the split, and `finished_at` is never used as a feature.
- **[Vlad1343/ukraine-air-alerts-timeseries](https://github.com/Vlad1343/ukraine-air-alerts-timeseries)**. Found that the official data stores almost every oblast-level alert twice: 130,049 rows, of which 65,128 are unique. It also saw a "coverage collapse" after October 2025 (most likely the raion-level shift, see §5) and stopped at 2025-10-31. Conclusion: daily counts can't beat a flat line.
- **[h00yaday/kse-air-raid-forecasting](https://github.com/h00yaday/kse-air-raid-forecasting)**. Daily counts per oblast: SARIMAX against seasonal naive, served through FastAPI.

### 3.3 EDA, dashboards and other framings (mostly the June 2026 cohort)

- [Heir-of-God/AlerticUA](https://github.com/Heir-of-God/AlerticUA): Dash dashboard with 5 tabs, and Prophet for daily counts and mean duration.
- [KrafterDen/Alerts-Analysis](https://github.com/KrafterDen/Alerts-Analysis): merges the Vadimkin history with a recent **alerts.in.ua API delta** (needs a token), about 158k events through 2026-06-21. It adds a calendar of Ukrainian and Russian symbolic dates with event-window "uplift". Baselines: rolling 7-day, same weekday, event-adjusted. 60-day forecasts.
- [HATSKER-228](https://github.com/HATSKER-228/time-series-analysis-of-air-raid-alerts-in-Ukraine): compares the volunteer (eTryvoga) and official sources side by side.
- [recruitabx/airraid-propagation-analysis](https://github.com/recruitabx/airraid-propagation-analysis): lead-lag analysis between oblasts over 101,266 alert onsets (2022-02-25 → 2026-06-20).
  - **Method:** directional asymmetry P(A→B) − P(B→A), with a control for nationwide waves.
  - **Finding:** most raw "A leads B" links are wave artifacts. Some genuine local propagation remains, e.g. Khmelnytska → Chernivtsi (z = 6.0).
  - It deliberately does not forecast, and serves the results through a Telegram bot.
- [karavaievg/KSE-AI-Agentic-Summer-School-](https://github.com/karavaievg/KSE-AI-Agentic-Summer-School-): "Air Alert Downtime Index" for manufacturers. It measures historical working hours lost to alerts per oblast. A different, business-impact framing with no forecasting.
- [rudakovevgenij/ukraine-air-raid-analysis](https://github.com/rudakovevgenij/ukraine-air-raid-analysis): merges overlapping sub-oblast alerts, drops alerts over 24 h, converts UTC to Kyiv time. Finds the peak start hour is 21:00.
- [osynichenko/The-Alarm-Clock-Nobody-Chose](https://github.com/osynichenko/The-Alarm-Clock-Nobody-Chose): data-viz story (R + Tableau) covering more than 107k alerts from Feb 2022 to Aug 2026.
  - **Donetsk:** 428 cumulative days under alert. The longest single alert lasted 87 h 45 min (Donetsk, 20–24 Feb 2026).
  - **Night share:** about a third of alerts start between 22:00 and 06:00.
  - **"July 2026 was the loudest month of the entire war":** count-based claims made after late 2025 depend on how raion-level rows are counted, so treat this one with caution.
- [shymanskyimarian-ux/air-raid-prediction](https://github.com/shymanskyimarian-ux/air-raid-prediction): ARIMA one week ahead, plus a heuristic "weapon type" guessed from geography and duration. The heuristic is not supported by the data.

### 3.4 Multi-source "SaaS" forecasters (ISW, weather, Telegram)

A recurring project template from 2023 to 2026, apparently from university courses: predict alarms for every region 12 or 24 h ahead from **ISW reports (TF-IDF), weather and alarm history**, serve it as a web app, and refresh hourly.

- [abrukhanska/alarm_prediction](https://github.com/abrukhanska/alarm_prediction) ("AEGIS", 2026).
  - **Inputs:** ISW TF-IDF (500 features) with a **D+1 shift**, GUR reports with a D+1 shift and rolling "tactical indices", 6–8 Telegram channels via Telethon, and the Visual Crossing weather API. The 24 h forecast uses forecast weather.
  - **Evaluation:** TimeSeriesSplit CV with a 30-day hold-out, and weekly retraining behind an F1 gate.
  - **Not verified:** whether training used *observed* weather. If it did, there is skew between training and serving.
- [GeoChernykh/AlarmForecast](https://github.com/GeoChernykh/AlarmForecast) (2026): 24 h ahead from alarms, weather forecasts, Telegram and ISW, with spatial neighbour features. Backend plus a Next.js front end.
- [texasiaa/alarm-prediction-model](https://github.com/texasiaa/alarm-prediction-model) and [issaravas/alarm-prediction-model](https://github.com/issaravas/alarm-prediction-model) (2024, same template): 12 h ahead from ISW (NLP), weather and alarms. Models: GradientBoosting, RF, DecisionTree, LinReg, LogReg.
- [Anivone/alarm-prediction](https://github.com/Anivone/alarm-prediction) (2023): Open-Meteo, the ukrainealarm API and ISW, hourly 12 h predictions, split into microservices over RabbitMQ.
- [kovalsviat/ukraine-air-raid-forecast](https://github.com/kovalsviat/ukraine-air-raid-forecast): hourly 12 h predictions from 334 days of multi-source data including ISW. RF and LR with TimeSeriesSplit, Flask on AWS EC2.
- [mak74ik/ukraine-alert-forecast](https://github.com/mak74ik/ukraine-alert-forecast) (2026-10): live raion-level radar and a 24 h danger forecast, with threat levels by weapon type (Shahed, missile/ballistic, KAB). Ukrainian UI.

### 3.5 Other

- [curiousartem/predict-alerts](https://github.com/curiousartem/predict-alerts) (2023): XGBoost on calendar features to predict alert counts.
- [xxanin/alert_prediction](https://github.com/xxanin/alert_prediction) (2023): a bot that predicts Kyiv alerts from statistics.
- [jerzy99jerzy/air-alert-early-warning](https://github.com/jerzy99jerzy/air-alert-early-warning): cross-border early warning for Poland, built on Ukrainian feeds.
  - **Gate:** a rule must reach recall ≥ 0.90 and a lift ≥ 1.5 *at the lower bound* of its precision interval.
  - **Source outage:** its public Telegram source "went silent mid-attack" on 2026-08-29, so it switched to polling `api.ukrainealarm.com`. This matters for data freshness; see data-sources.md.

### 3.6 Anti-pattern case study: an implausible "100 % precision"

[MaksimPrykhodko/Ukraine-air-raid-prediction](https://github.com/MaksimPrykhodko/Ukraine-air-raid-prediction) claims that Kyiv City next-hour alerts can be predicted with F1 0.87, precision 1.00 and recall 0.77. The [notebook](https://github.com/MaksimPrykhodko/Ukraine-air-raid-prediction/blob/HEAD/notebooks/Time_series_analys_of_alerts.ipynb) shows why:

1. **The target includes ongoing alerts.** The target is `has_alert`, meaning an alert is *active* in hour t, while the features include `alert_1h_ago`. A long alert is therefore "predicted" by persistence.
2. **The threshold was tuned on the test set.** It comes from `precision_recall_curve(y_test, …)`, and the best-F1 threshold is picked there (cells 15–28).
3. **One 80/20 chronological split**, with `eval_set=[(X_test, y_test)]` passed to `fit`.

Lesson: predict **starts**, choose thresholds on a validation window, and always report persistence and climatology baselines.

## 4. Academic and journalistic work

- **Pavlyshenko D., Pavlyshenko B. "Predictive Analytics of Air Alerts in the Russian-Ukrainian War", [arXiv:2411.14625](https://arxiv.org/abs/2411.14625) (Nov 2024).** This is the only peer-style paper found on forecasting alerts.
  - **Data:** Vadimkin data on a 1-minute grid, 2022-03-25 → 2024-11-06, with one binary feature per oblast.
  - **Target:** an alert within the next 5 min (15 min in the appendix).
  - **Features:** other oblasts' states and lags, cumulative alert duration, hour/day-of-week/month, and days since the start.
  - **Model and split:** a random forest per oblast (Lviv, Vinnytsia, Kyiv oblast, Kharkiv), trained before 2024-07-01.
  - **Main finding:** "the alert status in a particular region is highly dependable on the features of its adjacent regions".
  - **Caveats:** no numeric metrics in the text; ongoing alerts are labelled positive (an easier target); no code repository.
- **No Hawkes, point-process or survival-analysis work** on Ukrainian alerts turned up in searches. That is a possible angle, since alerts come in self-exciting "waves", but none was found.
- **Data journalism:** Texty.org.ua keeps a [tag on air-raid alerts](https://texty.org.ua/tag/povitrjani-tryvohy/) with analyses such as alerts eating Kyiv's working day and drone/missile charts. Media stats commonly cite air-alarms.in.ua (see data-sources.md).
- **Ukrainian academic papers found** (low relevance): statistical analysis of alerts in order to plan teaching at the National Defence University ([NUOU](https://znp-vo.nuou.org.ua/article/download/363678/350511/848660)), and regional "security index" forecasting ([NUPP](https://reposit.nupp.edu.ua/item/15988)). Neither forecasts alerts themselves.

## 5. Data pitfalls that earlier projects ran into

These are leads; data-sources.md verifies them against the data itself.

| Pitfall | Evidence | What prior projects did |
|---|---|---|
| From about Nov–Dec 2025, official alerts are recorded at raion/hromada level. Oblast-only filtering makes 2026 look near-zero. | [goodfrog33](https://github.com/goodfrog33/air-raid-forecasting-ukraine): "District-level alerts only appear from late 2025". [Trigger111](https://github.com/Trigger111/ukraine-air-raid-alerts-tsa): "Dec-2025 oblast→raion granularity shift". [Vlad1343](https://github.com/Vlad1343/ukraine-air-alerts-timeseries): ~23 alerts/day in Oct 2025, then "near zero through 2026". | Union of sub-oblast intervals per oblast (an oblast counts as under alert while any part of it is), then deduplicate. Or cut the benchmark at 2025-10-31, which conflicts with our "latest period" requirement. |
| Exact duplicate rows in official data | 130,049 oblast rows but only 65,128 unique ([Vlad1343](https://github.com/Vlad1343/ukraine-air-alerts-timeseries)); 271,160 events → 157,315 canonical events ([Trigger111](https://github.com/Trigger111/ukraine-air-raid-alerts-tsa)) | Deduplicate on (oblast, start, end) |
| Timestamps are in UTC | several projects | Convert to `Europe/Kyiv`, with DST handled, before any hour-of-day or calendar-day logic |
| `naive=True` rows in the volunteer data (end time estimated as start + 30 min) | 5,023 rows (~4.9 %) in a 2026-06-25 snapshot ([kervad28-debug](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction)) | Keep for start-based targets; drop for duration analysis |
| Permanent or very long alerts in occupied and frontline oblasts | Luhansk and Crimea excluded ([goodfrog33](https://github.com/goodfrog33/air-raid-forecasting-ukraine)); longest single alert ~88 h, Donetsk, Feb 2026 | Exclude, or model separately |
| The live CSV changes over time | — | Freeze a snapshot and record its SHA-256 ([kervad28-debug](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction)); keep a download manifest ([goodfrog33](https://github.com/goodfrog33/air-raid-forecasting-ukraine)) |
| Lost all-clear messages in Telegram-derived data | 26 alerts in 60 days never got an all-clear ([lbgos](https://github.com/lbgos/AirAlerts)) | Expire an alert after 24 h |
| Source outage: a public alert channel went silent on 2026-08-29 | [jerzy99jerzy](https://github.com/jerzy99jerzy/air-alert-early-warning) | Switched to the ukrainealarm API; check whether the dataset has a gap (data-sources.md) |
| Regime and base-rate drift | positive rate fell from 56 % to 41 % ([kervad28-debug](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction)); "tactics changed" ([lbgos](https://github.com/lbgos/AirAlerts)) | Recency weighting (60-day half-life), recent-only training, calibration on the last 7 days |

## 6. What this implies for our project (our read)

1. **Target.** Per oblast: "a new alert starts within H", for oblasts not currently under alert. This target has proven signal and honest baselines. Optionally add a night-ahead target, where text features have time to matter. Avoid "alert is active" targets.
2. **Baselines.** Use persistence, climatology (oblast × hour of day, recency-weighted) and seasonal naive. Report skill as 1 − Brier/Brier_baseline, plus AUC and PR-AUC.
3. **Evaluation.** Use chronological, purged splits, with a dev window for model selection. Run the final test **once**, on the latest 14–30 days before the data cutoff, which is what our brief asks for. Report calibration with a reliability diagram and ECE.
4. **Features with proven value.** Own recency, neighbour-oblast recency (minutes since the last neighbour siren), the national active count, and time of day. Use only events strictly before T.
5. **Training window.** Compare full history with recent-only or recency-weighted training. Both lbgos and the base-rate drift suggest recent data matters more.
6. **Data handling.** Merge raion/hromada rows into oblast intervals, deduplicate, convert UTC to Kyiv time, and snapshot with a hash. Without this, "latest period" evaluation on Vadimkin data is broken.
7. **Text and media are the open gap.** Nobody has shown lift under a leakage-safe evaluation on the latest period.
   - **Best candidates:** Air Force (`@kpszsu`) launch reports and monitor channels, aligned by **message timestamp**, for 6–24 h and night-ahead horizons. ISW only with alignment to its publication time.
   - **What to expect:** lbgos shows little gain at ≤6 h once neighbour alerts are in. A clean negative result, honestly reported, is still a valid finding.
8. **Differentiation.** Reviewers have already seen about 100 EDA+Prophet dashboards. The current brief stresses fresh data, leakage and evaluation on the latest period, and KSE's criteria stress process, error handling and a usable artifact. Rigour and honesty on those points will matter more than dashboard polish.

## 7. Method and caveats

- **Search:** GitHub REST search on 2026-10-10 (unauthenticated). Queries: "air raid ukraine", "air alert ukraine", "air alarm ukraine", "alarm prediction ukraine", "air raid prediction", "alarms forecast ukraine", "тривога", `"ukrainian-air-raid-sirens-dataset" in:readme`, "agentic summer school", "alarm isw weather", "air raid sirens ukraine", "air alerts ukraine analysis", plus `created:` date windows. Web search covered arXiv, Ukrainian academic repositories, Texty.org.ua and the KSE pages.
- **Reading:** READMEs were read via raw.githubusercontent.com. Code was inspected only for MaksimPrykhodko (§3.6) and the goodfrog33 report.
- **Not covered:** Kaggle notebooks were not surveyed in depth. Kaggle *datasets* are covered in data-sources.md.
- **Repos change:** numbers, dates and claims may have changed after 2026-10-10.

## Appendix

**June 2026 repos that name the KSE school in their name or description** (sample):
[lyriKgt/kse-air-raids-analysis](https://github.com/lyriKgt/kse-air-raids-analysis) ·
[alinasamoilenko292/KSE-AI-Agentic-Summer-School](https://github.com/alinasamoilenko292/KSE-AI-Agentic-Summer-School) ·
[tannyaQ/ukraine-air-alerts-tsa](https://github.com/tannyaQ/ukraine-air-alerts-tsa) ·
[Denys-Klekots/KSE_AI_Agentic_Summer_School_task](https://github.com/Denys-Klekots/KSE_AI_Agentic_Summer_School_task) ·
[kononskyinazar/KSE-AI-Agentic-Summer-School-Stage-2](https://github.com/kononskyinazar/KSE-AI-Agentic-Summer-School-Stage-2) ·
[DanyloBeha/KSE-agentic-school-application-2026](https://github.com/DanyloBeha/KSE-agentic-school-application-2026) ·
[zadorozhna-dariia/AI_Agentic_school_stage_2](https://github.com/zadorozhna-dariia/AI_Agentic_school_stage_2) ·
[gbatulin/kse_summer](https://github.com/gbatulin/kse_summer) ·
[Hroback/KSE](https://github.com/Hroback/KSE) ·
[oleksandrsafandulaKSE/AirAlerts-TimeSeries-Analysis-Ukraine](https://github.com/oleksandrsafandulaKSE/AirAlerts-TimeSeries-Analysis-Ukraine)

**Alert-analysis repos created 2026-10-09/10, possibly a new selection round:**
[lbgos/AirAlerts](https://github.com/lbgos/AirAlerts) ·
[3olena3/air-raid-alerts-forecast](https://github.com/3olena3/air-raid-alerts-forecast) ·
[Kamenqq/air-raid-alerts-forecast](https://github.com/Kamenqq/air-raid-alerts-forecast) ·
[Dopplerr24/air-raid-alert-analysis](https://github.com/Dopplerr24/air-raid-alert-analysis) ·
[LasonD/air-raids-analyzer](https://github.com/LasonD/air-raids-analyzer) ·
[Yaroo-a/ukrainian-air-raid-sirens-analysis](https://github.com/Yaroo-a/ukrainian-air-raid-sirens-analysis) ·
[mariia008/air-alert-analysis](https://github.com/mariia008/air-alert-analysis) ·
[maranferij-lang/Ukraine-air-alerts](https://github.com/maranferij-lang/Ukraine-air-alerts)
