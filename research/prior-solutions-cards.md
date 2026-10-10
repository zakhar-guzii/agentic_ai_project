# Prior solutions: per-repo review cards

_Raw review cards for 115 on-topic repos, written by three review subagents on 2026-10-10 from local clones. Nothing was executed. The synthesis and verified numbers are in [prior-solutions-survey.md](prior-solutions-survey.md); treat these cards as working notes. Ratings: likely-passed (LP/P) and technical quality (T), each 1–5._

---

## Batch 1 review: KSE Stage 2 air-raid TSA repos (39 repos)

Reviewed from the local clones only. File paths below are relative to each clone root
(`scratchpad/clones/<owner>_<repo>/`). Nothing was executed. "Likely" means likely passed
against KSE's criteria, given that the AI log is mostly unseen and the one confirmed passer
(tbaraniuk) is a modest live-data Dash dashboard with no forecasting. "Tech" is technical quality.
Both are scored 1–5.

## Ratings at a glance

| # | Repo | Cohort | Likely | Tech | One-liner |
|---|---|---|---|---|---|
| 1 | chud00s/tryvoha-radar-tsa | Jun | 4 | 4 | Calibrated per-oblast 6-h risk model with neighbour features, beats baselines on the latest 10 months; polished UI |
| 2 | anechytailenko/AirRaidAlerts | Jun | 3 | 3 | Leak-aware GNN pipeline with an embargo and ASOF OSINT, but AUC 0.61 and no baselines |
| 3 | rayhankhilji/terrestrial | Oct | 3 | 4 | Not a KSE repo (EDTH hackathon platform); its alert-forecast module is excellent |
| 4 | Trigger111/ukraine-air-raid-alerts-tsa | Jun | 5 | 4 | Model process: dedup, union time, pinned data, baseline-first, honest negative result |
| 5 | chernysholeksandr/air-raid-timeseries | Jun | 3 | 2 | Good reasoning in its AI log, but the repo is broken (scrambled files, forecast code missing) |
| 6 | gklymenko/ukraine-air-raid-alerts-time-series | Jun | 3 | 3 | Solid probabilistic baseline harness; uses the oblast-only filter |
| 7 | ArseniiKlimenko/air-raid-alerts-time-series | Jun | 3 | 3 | Daily GitHub Actions dashboard; SARIMAX MASE 1.75 reported honestly; counts mix levels |
| 8 | maranferij-lang/Ukraine-air-alerts | Oct | 5 | 5 | Best in batch: data forensics, exact targets, a no-peeking check, latest window, three baselines |
| 9 | AZAR1VAN/kse-project-v1 | Jun | 3 | 2 | Good process story (dropped the LLM layer); its Prophet forecast is never evaluated |
| 10 | DanyloBeha/KSE-agentic-school-application-2026 | Jun | 3 | 2 | Union-based alert-hours; SARIMA vs ETS with no naive baseline |
| 11 | YuraHusynskyii/AirRaidAnalysis | Jun | 2 | 2 | K8s/Redis MLOps theatre; every metric is computed on a 55-row sample |
| 12 | yevayarova/air-alerts-ukraine_yarova_ai | Jun | 3 | 3 | Clean descriptive burden indices; no forecast |
| 13 | LysanetsAndriy/air-alert-analysis | Jun | 3 | 3 | Reconstructs "synthetic oblast" alerts from raions; baselines only |
| 14 | tShyshatskyi/Alert-prediction | Jun | 3 | 3 | Kyiv vs Nikopol; 5×30-day backtest; leftover AI scaffolding |
| 15 | Python-UA/Ukraine-alerts-v3-learning | Jun | 2 | 2 | Kitchen sink; hindsight event regressors; double-counted sources |
| 16 | HoiSerhii/air-alerts-analysis | Jun | 4 | 3 | One sharp question (night share), correct data handling, verbatim AI log |
| 17 | mseheda/airraid-ts | Jun | 4 | 4 | Frozen non-gameable gate, CRPS, leakage tripwire, red-team subagents; honest null |
| 18 | guilbk/air-raid-raion-forecast | Jun | 3 | 3 | Raion-level 60-min start target with a purge gap; no reported numbers |
| 19 | mylovanov-alt/ukraine-airraid-analysis | Jun (06-29) | 3 | 4 | Independent Telegram re-collection audit and synthetic-truth tests; no dedup |
| 20 | 3Metrovuy/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine | Jun | 3 | 2 | Modest correct Streamlit EDA |
| 21 | simonenkoanastasiia-eng/air-raid-analysis | Jun | 3 | 3 | Hourly per-oblast HGB, AUC 0.74; fixed a nowcast bug |
| 22 | h00yaday/kse-air-raid-forecasting | Jun | 2 | 2 | FastAPI/Docker shell with empty modules and template leftovers |
| 23 | kokojas/ukraine-air-alert-time-series | Jun | 3 | 2 | Burden/fatigue metrics; fixed-weight baseline only |
| 24 | KharinTymofii/air-alert-analysis | Jun | 3 | 3 | Burden observatory with school-exposure denominators (EDBO); descriptive |
| 25 | recruitabx/airraid-propagation-analysis | Jun | 4 | 4 | Lead-lag with a circular-shift null and wave control, re-validated on the official API; live bot |
| 26 | sasha2lapina-spec/ukraine-air-raid-analysis-oleksandra-lapina | Jun | 2 | 2 | XGBoost plus Trends/Telegram/weather; leaky features; `__pycache__` committed |
| 27 | nataliiakubik/air-raid-alerts-time-series | Jun | 2 | 2 | Descriptive; deliberately stops at 2025-07-31 |
| 28 | mykoladomanskyi25-dotcom/Air-raid-alerts | Jun | 2 | 1 | Oblast filter; calls the raion shift a "collection failure"; tests on Jul–Aug 2025 |
| 29 | Ianitskyi/ukraine-air-alerts-analysis | Jun | 3 | 2 | Deployed Streamlit atlas; descriptive; a UTC/Kyiv hour bug |
| 30 | MishaDvali/Air_raid_alert_analysis_and_prediction | Jun | 3 | 3 | Six documented model versions; tests on Sep–Oct 2025, not the latest data |
| 31 | tui2019/Air-Raid-Analysis | Jun | 3 | 2 | CLI report and dashboard with Gemini summary; 41 commits |
| 32 | antonprasol-cmyk/ukraine-air-alert-forecasting | Jun | 2 | 3 | Survival and Hawkes models on 2025 only; oblast filter |
| 33 | artiekra/air-alert-analysis | Jun | 2 | 2 | Single-file Streamlit, STL; descriptive |
| 34 | uiuxdesigner18/ukraine-air-raid-analysis | Jun | 2 | 1 | Oblast filter, then ARIMA on the collapsed tail; no evaluation |
| 35 | itpsychologist/Analysis-of-air-raid-alerts | Jun | 3 | 2 | Closest analogue to the passer: live alerts.in.ua Streamlit; unevaluated Holt-Winters |
| 36 | dvasylchuk/kse_ai_agent_school | Jun | 2 | 2 | Kyiv City burstiness; cuts data at 2025-11-29 when it did not need to |
| 37 | shynkaruk00-collab/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine | Jun | 3 | 3 | Granularity-invariant "oblasts under alert/day"; ARIMA loses to the mean |
| 38 | lewym90/egida | Oct | 1 | – | Off-topic |
| 39 | mariia008/air-alert-analysis | Oct | 1 | 1 | Empty placeholder |

---

## Per-repo cards

### 1. chud00s/tryvoha-radar-tsa — likely 4 · tech 4
June cohort; 19 commits within about 9.5 h on 2026-06-25; heuristic score 101.8.
- **Framing:** a per-oblast forecast of alert risk over the next 6 h, plus pattern analytics and an OSINT layer that an LLM extracts from Telegram. The UI is a Ukrainian-language Streamlit app with three modes: consumer, analyst and "threats now".
- **Data:**
  - Vadimkin `volunteer_en`, chosen deliberately because it stays oblast-level for the whole period. The comment in `src/config.py` notes that the official feed moved to raion level in December 2025.
  - So the raion shift is sidestepped, and dedup is unnecessary because the volunteer file has no duplicates.
  - UTC is kept internally; calendar features use Europe/Kyiv.
  - Latest data: 2026-06-23 18:00 UTC.
  - **Not disclosed:** the volunteer feed covers only about 35–60% of official alert time and degrades after mid-2025.
- **Target/horizon:** y = 1 if any alert is active in (t, t+6h], on an hourly grid of 25 regions.
- **Methods:**
  - HistGradientBoosting with region as a categorical feature, plus isotonic calibration fitted on a separate validation slice.
  - Features: Kyiv-local calendar, lags of 1–48 h, rolling sums of active hours and starts, hours since the last alert, and neighbour-oblast activity from a geo adjacency table.
  - Baselines: climatology (region × hour, from train) and binary persistence.
- **Evaluation:**
  - Chronological 65/15/20 split; the test window is 2025-08-12 → 2026-06-23, i.e. the latest period.
  - Model: ROC-AUC **0.878**, PR-AUC 0.879, Brier **0.141**.
  - Climatology: 0.827 / 0.823 / 0.174. Persistence: 0.666 / 0.653 / 0.339.
  - Test positive rate 0.51; the reliability curve is saved in `data/processed/model_metrics.json`.
- **Leakage:**
  - Features are shifted correctly.
  - Minor: `active_now` and same-hour neighbour state cover the whole hour bucket starting at `ts`. That is fine only if the forecast is issued at the end of the hour, which is never stated.
  - No purge gap between validation and test (6 h of target overlap); only a single split.
- **Text/media:** `src/ai_extractor.py` uses Claude haiku with tool use to turn Telegram posts into typed geo-events, with a regex fallback. These events are displayed only and never feed the model, so there is no leakage.
- **Product:**
  - Streamlit (`app/dashboard.py`, 60 KB) with three modes, a folium threat map and a data-freshness indicator.
  - Optional live alerts.in.ua (`src/live.py`).
  - Committed parquet caches, so it runs offline and without any keys; `Makefile` targets.
- **Engineering:** clean `src/` package, 3 pytest files for transform, extractor and live, pinned upper bounds on dependencies.
- **Docs/iteration:**
  - Honest limitations section.
  - The AI log is deliberately kept out of the public repo (`.gitignore: docs/AI_LOG.*`).
  - Commit messages show an audit pass ("Audit fixes: correctness, robustness…", "Analyst clarity: honest labels").
- **Borrow:**
  - Neighbour features (`src/features.py`).
  - Isotonic calibration on a held-out slice plus a reliability curve (`src/forecast.py`).
  - `mass_attack_episodes` (≥18/24 oblasts), `surprise_days` (robust z-score against a 28-day baseline) and `propagation_lead_lag` (`src/analysis.py`).
  - The consumer/analyst UI split.
- **Red flags:** the volunteer undercount is not disclosed; persistence is a weak binary baseline; scope creep into an OSINT map on day 2.
- **Why:** correct, latest-window, calibrated and baseline-beating, with a usable product. The process can't be checked because the log is withheld.

### 2. anechytailenko/AirRaidAlerts — likely 3 · tech 3
June cohort; 11 commits.
- **Framing:** probability of an alert at each horizon k = 1…6 h per oblast, using a spatio-temporal GNN (A3T-GCN), plus an LLM "Narrative Analyst" chat and MCP OSINT agents.
- **Data:**
  - `volunteer_en` loaded into Postgres with pydantic validation, a dead-letter table and idempotent upserts.
  - Open-Meteo ERA5 archive weather.
  - 1,021 Telegram OSINT flags (MiG-31K airborne, Tu-95 takeoff, mass attack) in `data/osint/osint_flags.csv`.
  - Latest data about 2026-06-24. The raion shift doesn't apply (volunteer feed).
  - Calendar features are computed in **UTC**, so they drift with DST.
- **Target:** alert active at t+k, for k = 1…6.
- **Methods:** A3T-GCN with a 12-h window and adjacency edges, weighted BCE, and per-horizon F-beta thresholds calibrated on validation. **No baselines.**
- **Evaluation:**
  - Train ≤ 2025-06-30, validation 2025-07 → 2025-12, test from 2026-01-01.
  - An **embargo of window + horizon** hours separates the splits; the scaler is fitted on train only.
  - README results: mean ROC-AUC **0.608**, PR-AUC 0.336, F1-macro 0.472. ROC-AUC falls from 0.708 at k1 to 0.575 at k6. Per-oblast table included.
- **Leakage:**
  - Handled with care: the OSINT flags are joined with a DuckDB ASOF join (event_ts ≤ t), a 6-h TTL and staleness columns.
  - ERA5 weather at t is not available in real time (about 5 days' latency), a train/serve mismatch.
- **Text/media:** OSINT flags are model features. The LLM analyst runs a sandboxed tool router.
- **Product:** Dash chat UI, FastAPI, two MCP servers, docker-compose and W&B tracking.
- **Engineering:**
  - Heavy: Postgres schema, DuckDB export, 3 test files, 8 plan docs in `plans/` and research docs.
  - 24 MB of parquet exports committed.
- **Docs:**
  - The README has metrics and plots but **no interpretation of the weak AUC** and no limitations.
  - `session_log.txt` is an empty `script` capture.
- **Borrow:**
  - `src/ml/dataset.py`: embargo between splits and a train-only scaler.
  - `src/airraid/export_dataset.py`: ASOF join with TTL and staleness for flags derived from text.
  - Per-oblast × horizon metric tables.
- **Red flags:** no baselines (persistence would probably beat ROC-AUC 0.708 at k=1); over-engineered for two days.

### 3. rayhankhilji/terrestrial — likely 3 (not a KSE submission) · tech 4
October cohort (10-02 → 10-04); 27 commits.
- **Off-scope:** this is an EDTH London 2026 hackathon "live war picture" built on 25+ streams (ADS-B, AIS, satellites, DeepState). It includes one carefully built alert-forecast module, reviewed below.
- **Data:**
  - `volunteer_en`, loaded by `history/sirens.py` with strict checks on column and region mappings.
  - VIINA 2.0 events, the Open-Meteo daily archive and moon phase.
  - Latest data about 2026-10-03.
- **Target:** one row per region × 6-h UTC block, issued at the end of the block. Two targets: `y_active`, and `y_new` (a new alert starts in the next block).
- **Methods:**
  - HGB plus isotonic calibration.
  - Features: alert minutes over the last 1/4/28/120 blocks, starts, active at issue time, hours since the last alert, neighbour and national aggregates, weather, VIINA air-attack counts **lagged 5 days for the publication delay**, and moon phase.
  - Baselines: climatology (region × block of day) and **conditional persistence**, i.e. the training-period rate given whether there was an alert in the last block.
- **Evaluation:**
  - Train < 2025-07-01, calibration 2025-07 → 2025-12, test ≥ 2026-01-01 (the latest period).
  - ROC-AUC **0.86** and Brier **0.150**, against persistence 0.185 (19% better) and climatology 0.199 (25% better).
  - The model card JSON records whether the model beats the baselines (BSS), per-region AUC and permutation importance.
- **Leakage:**
  - The train/serve parity rule (CLAUDE.md §16.4) is followed and the VIINA lag is handled.
  - **Observed** weather for the target day is used in training and test; the card admits "observed in training; forecast in live use".
- **Text/media:** parses the Air Force and monitoring Telegram channels plus news; an LLM writes SITREPs that must cite facts. None of this feeds the model except VIINA.
- **Product:** React, MapLibre and deck.gl globe; FastAPI WebSocket hub; Vercel replay; models published to Hugging Face; 128 tests.
- **Borrow:**
  - `predict/strike/features.py`: issue-time block design and lagged exogenous data.
  - `predict/strike/train.py`: conditional-persistence baseline, `beats` flag and model-card pattern.
- **Red flags:** not the assignment; huge scope; weather leakage.

### 4. Trigger111/ukraine-air-raid-alerts-tsa — likely 5 · tech 4
June cohort; 10 phase-named commits in one day: Phase 0 → 6B, then reflection.
- **Framing:** EDA plus a baseline-first next-day forecast of "any alert tomorrow" for Kyiv City, explicitly framed as not attack prediction.
- **Data:**
  - `official_en`, pinned to upstream commit `dac507f`, with SHA-256 and row count in `data/meta.json`.
  - 271,160 rows, of which **113,845 are exact duplicates (42%)**; dropping them leaves 157,315.
  - Overlaps within a unit are merged; 686 alerts longer than 24 h are flagged rather than dropped.
  - UTC → Europe/Kyiv with DST-correct splitting across local days.
  - The raion shift is handled two ways: (a) the model unit is Kyiv City, which has no raions; (b) national EDA uses **oblast union time** and region-alert-days, both granularity-invariant.
  - Latest data: 2026-06-20.
- **Target:** `has_alert_next_day` for Kyiv City (plus optional minutes).
- **Methods:**
  - Baselines: majority, base rate, persistence, rolling 7 and 30 days, day-of-week climatology.
  - Models: logistic regression (scaled plus one-hot) and HGB with default settings as a sanity check.
- **Evaluation:**
  - Chronological 80/20 split; the test window is 2025-08-12 → 2026-06-17 (latest), base rate 0.739.
  - Best ROC-AUC 0.548 (rolling 7 days); base-rate Brier **0.195**.
  - LogReg 0.505 / 0.203; HGB **0.438** / 0.248.
  - A **pre-agreed rule** (beat the recency AUC *and* the base-rate Brier) makes both models fail, and this is reported as an honest negative result.
- **Leakage:** features are built after the split from data ≤ t; no tuning on test. Permutation importance on test is used only as a diagnostic.
- **Text/media:** none.
- **Product:** exploratory Streamlit app (no model inside).
- **Engineering:** `src/` modules with one config as the single source of truth; reproducible pinned fetch; no tests.
- **Docs:** excellent README (data-quality section, methodology notes, limitations). `reflection.md` is about 100 words and on point.
- **Borrow:**
  - `src/data_loader.py` with `data/meta.json`: pinned commit plus SHA.
  - `src/aggregate.py`: union time and region-alert-days.
  - The skill-bar rule in `src/model.py` (`_verdict`).
  - Reflection format.
- **Red flags:** a weak target (daily, 74% base rate) leaves little to learn; single split.
- **Why:** this matches KSE's stated criteria almost point by point.

### 5. chernysholeksandr/air-raid-timeseries — likely 3 · tech 2
June cohort; 3 commits.
- **Scope:** northern approach to Kyiv (Kyiv city and oblast, Chernihiv, Sumy, Zhytomyr): burden, border → capital propagation, structural breaks and a 1-h forecast for Kyiv.
- **Data:** official feed; raion alerts are collapsed to oblast on an hourly grid; Kyiv timezone; latest 2026-06-26. **No dedup**, so counts such as "50,280 alerts" are inflated.
- **Claimed results:**
  - A time-shift density null for lead-lag: +9 pp at 30 min, with a head start of about 34 min.
  - Nested walk-forward logistic models over the last 6 months: rhythm AUC 0.57 → plus persistence 0.77 → plus border 0.77.
- **Broken repo:**
  - Filenames were scrambled on upload: `__init__.py`, `breaks.py` and `download_data.py` are PNGs, `clean.py` is JSON, and `forecast.py` is empty.
  - **The Layer-3 forecast code isn't present**, so its results can't be verified.
  - Unsourced "events": "Feb 2026 northern drone-guidance mesh taken down" and "Jun 2026 Belarus relay corridor switched off".
- **Plus:** `AI_LOG.md` shows real self-correction (caught a base-rate confound, insisted on a persistence control, kept a negative result).

### 6. gklymenko/ukraine-air-raid-alerts-time-series — likely 3 · tech 3
June cohort; 8 commits.
- **Data and target:**
  - Daily alert minutes per oblast; latest data 2026-06-21.
  - Official feed **filtered to `level=='oblast'`**, deduplicated on (region, start, end) (it notes about 2× duplicates). Volunteer data is used only as a cross-check.
  - The focus unit is Kyiv City, so the main result survives. For the other oblasts, though, the filter empties 2026, which contradicts the README's claim that the series "survives the transition intact".
- **Methods and evaluation:**
  - Naive, SeasonalNaive and MA7, each with an empirical 80% prediction interval.
  - Expanding walk-forward, h = 1 day, over the last third of the series (about 520 days).
  - MA7: MAE 96.3, MASE 1.03; naive: 110.2; interval coverage 72% against a nominal 80%.
- **Engineering:** a `Forecaster` interface, a `verify.py` quality report, 62 tests, a synthetic fixture and a CLAUDE.md spec.
- **Flags:**
  - Hour-of-day is in UTC; the README admits it.
  - Negative lower bounds on the intervals; also admitted.
  - The winner is chosen on the same backtest it is scored on.
- **Borrow:** the interval and pinball/MASE harness in `src/airraid_tsa/evaluate.py`.

### 7. ArseniiKlimenko/air-raid-alerts-time-series — likely 3 · tech 3
June cohort; 3 commits.
- **Data:** national daily counts from the official feed, deduplicated. **All levels are counted**, so counts jump after the shift. Uses Kyiv-day splitting, Pydantic validation per row, and is refreshed daily (latest 2026-06-24).
- **Model:** SARIMAX(1,1,1)(1,0,1,7) with a rolling-origin backtest at a 30-day horizon. **MASE 1.75**, i.e. worse than seasonal-naive, and the README says so.
- **Product:**
  - A Plotly dashboard on GitHub Pages, rebuilt daily by GitHub Actions, with an optional LLM briefing.
  - Commit: "Harden AI analyst prompt against training-cutoff hallucinations".
  - CI runs ruff and 50 pytest tests.
- **Flags:** mixed-level counts; the "rebuilt from reality every morning" dashboard has been stale since the official feed froze on 2026-09-07.
- **Borrow:** `.github/workflows/daily_agent.yml`.

### 8. maranferij-lang/Ukraine-air-alerts — likely 5 · tech 5
October cohort (2026-10-10); 7 commits, one per "round" (Rounds 1–4) plus CLAUDE.md edits and a merged PR.
- **Framing:** "At hour t, using only what is known at t: will there be an alert in oblast X in the next H hours (H = 1, 3, 6)?" One model covers all oblasts.
- **Data:** official feed, pulled 2026-10-10 08:27 UTC from upstream commit `7ccd436` and recorded in `data/raw/PULL_INFO.md`.
  - **Data forensics (PROCESS_LOG Round 1):**
    - Read the upstream processor code before the data.
    - The 38% duplicates are traced to **upstream re-running its processor in append mode**: rows 113,911–227,831 are a second pass over the history.
    - Found 66 mislabelled Zviahelskyi rows (`hromada == raion`) and relabelled them.
    - Found **253 unflagged imputed +1 h ends**.
    - **Inspected upstream's state pickles with `pickletools`, without unpickling them**, to see which alerts were still open, i.e. right-censored.
    - Detected the **2026-08-29 → 09-02 official outage** and masked it as `OFFICIAL_OUTAGES` in `src/load.py`.
    - Noticed the official feed has been **frozen since 2026-09-07** and trimmed the final partial day plus one day as a margin (`data_end`).
  - **The volunteer feed was rejected with evidence:**
    - Hourly Cohen's κ against official falls from 0.98 (2022Q3) to 0.42 (2026Q3).
    - Found an upstream **parser bug**: "Подільський" is mapped to Lviv, and "Прилуцький" contains "Луцьк" (Volyn).
  - **Raion shift:** official rows are mapped to raions, and an oblast counts as under alert when **≥ half of its raions** are (fixed 2020 raion lists). Hromada-only rows are dropped. Restarts within 5 min are joined into one episode, but "active at t" uses the un-joined episodes, since nobody at t knows whether a restart will follow. All times are UTC; the calendar features use Kyiv time.
- **Target:** `src/targets.py` computes targets exactly from episode intervals using `searchsorted`:
  - (a) an alert is active at any point in (t, t+H];
  - (b) a **new episode starts** in (t, t+H].
  - The repo models (b) and reports (a) as "1 if active now, else model(b)", documenting the 3 rows where this identity breaks.
- **Methods:**
  - One LightGBM per H, with oblast as a categorical feature.
  - Features: own state (active at t, time since start, time since end); shares of the last 6 h / 24 h / 7 d spent under alert; starts in the last 24 h / 7 d; neighbours over the last completed hour (hand-written land-border table); Kyiv hour and weekday; `freq4w`, a rolling version of the frequency table.
  - Comparison fits: a hand-written IRLS logistic regression (`src/logit.py`) and LightGBM trained from 2026-01-01 only.
  - Three baselines: persistence, same hour yesterday, and train frequency (oblast × Kyiv hour × weekday).
- **Evaluation:**
  - The test window is the **last 30 full days of official data, 2026-08-07 → 09-05**. Masking the outage leaves 24 usable days.
  - Thresholds are tuned on the **last train week** only; the 0/1 baselines get no threshold search.
  - The main metric is **within-oblast ROC-AUC**, alongside Brier, precision and recall.
  - Results for target (b), shown as within-oblast AUC / Brier:

    | H | LightGBM | Train frequency | Same hour yesterday | Persistence |
    |---|---|---|---|---|
    | 1 | 0.688 / 0.087 | 0.495 / 0.101 | 0.525 / 0.181 | 0.438 / 0.288 |
    | 3 | 0.645 / 0.145 | 0.581 / 0.177 | — | — |
    | 6 | 0.639 / 0.140 | 0.612 / 0.178 | — | — |

    The logistic regression gets near-equal Brier but an AUC of about 0.5, so LightGBM "earns its keep on ranking".
  - "H = 6 not established": the result flips with two extra days. Per-period tables are in `results/test_table_by_period.md`.
  - Calibration is in `results/calibration.md`, including an analysis of the lowest bin (western oblasts over-predicted).
- **Leakage:** `scripts/check_no_peeking.py` rebuilds every baseline input and **every model feature** from data truncated at t, for 40 test origins, and requires exact equality. It includes **two negative controls**, a future target and a deliberately leaky feature, which prove the check fires.
- **Text/media:** none.
- **Product:** none; scripts only. This is the main gap.
- **Engineering:** small `src/` modules, one script per step, data snapshot committed with checksums. No pytest; the checks are executable scripts instead.
- **Docs/iteration:**
  - `CLAUDE.md` holds the user's rules for the agent, e.g. "if something i ask for looks wrong, say so before doing it", "a number without baselines does not go in the README".
  - `PROCESS_LOG.md` (48 KB) records each round's decisions, the "Wrong #n" findings, and "a bug I introduced this round and fixed before the results".
- **Borrow:** almost everything. `src/load.py`, `src/panel.py`, `src/targets.py`, `scripts/check_no_peeking.py`, `src/baselines.py`, `src/metrics.py` (within-oblast AUC, Brier decomposition), plus the CLAUDE.md rules and PROCESS_LOG format.
- **Red flags:**
  - The test window is short (24 days).
  - It didn't stitch in alerts.in.ua or the JustJimer archive to cover 2026-09/10 or the new red/yellow levels.
  - No UI.

### 9. AZAR1VAN/kse-project-v1 — likely 3 · tech 2
June cohort; 11 commits in under an hour (R1–R7).
- **What it is:** a Streamlit multipage app built on volunteer data: overview, STL trend with ruptures, anomaly detection (MAD z-score plus IsolationForest), a Prophet forecast and KMeans region clusters, with deterministic text insights.
- **Evaluation gap:** the "backtest MAE" is computed for **seasonal-naive** on the last 14 days, not for the Prophet model shown. Prophet is fitted on all the data, so it is never evaluated.
- **Process is strong:**
  - `conv.md` contains the prompts verbatim; also `log.md`, a `Plan_Folder` roadmap with tasks and plans, and `reflex.md`.
  - The candidate removed an LLM orchestrator/judge layer after the judge flagged valid numbers as hallucinations.
  - UI verified with Playwright screenshots.
- **Borrow:** the reflection story; `scripts/playwright_screenshots.js`.

### 10. DanyloBeha/KSE-agentic-school-application-2026 — likely 3 · tech 2
June cohort; 26 conventional commits.
- **Data:** daily alert-hours per oblast from a **union of all levels**, which handles both the shift and the duplicates; the national series is the sum. Days are in UTC.
- **Analysis:** ADF, decomposition and ACF.
- **Models:** SARIMA vs Holt-Winters on a 30-day holdout, with **no naive baseline** and no numbers in the README. Also a damped-ETS forecast to the end of 2026 with no justification.
- **AI log:** `conversation.md` (103 KB) shows the AI catching the oblast-filter bug ("alert-hours collapse to ~0 after Dec 2025").
- **Product:** Streamlit with commentary.

### 11. YuraHusynskyii/AirRaidAnalysis — likely 2 · tech 2
June cohort; 9 commits.
- **What it is:** MLOps scaffolding — FastAPI with auth, Redis rate limiting, Prometheus and OTel, K8s manifests, drift detection, a model registry and 89 tests.
- **Fatal problem:** every metric comes from `data/samples/sample_alerts.csv`, a **55-row sample** dated June 2024 (seasonal-naive MAE = 0.000). There is no real-data analysis.
- **Docs:** a long reflection that claims rigour, with links to a Gemini share and a Cursor log.

### 12. yevayarova/air-alerts-ukraine_yarova_ai — likely 3 · tech 3
June cohort; 9 commits.
- **What it is:** descriptive civilian-burden analytics (Alert Burden Index, sleep and work/study disruption indices, inequality, change points) in a Streamlit app ready for a Hugging Face Space. Pipeline in polars.
- **Data handling:**
  - Official rows deduplicated (`unique`); volunteer rows used only **before** the official feed starts (a stitching rule).
  - Overlapping episodes merged; raw record counts kept separate from merged-episode counts; Kyiv-local hours.
- **No forecast**, by explicit choice.
- **Engineering:** 7 test files and validation reports.
- **Borrow:** the "Metric Semantics" section in the README; the stitching rule in `src/air_alerts/cleaning.py`.

### 13. LysanetsAndriy/air-alert-analysis — likely 3 · tech 3
June cohort; 4 commits.
- **Data:** official feed, deduplicated. "Synthetic oblast alerts" are reconstructed from raion alerts that fire together: ≥80% of raions starting within 10 min, and at least 2 raions (`air_alert_analysis/synthetic.py`). The 80% threshold probably undercounts after the shift.
- **Product:** Streamlit with EDA, anomalies and tendencies.
- **Forecast:**
  - Walk-forward **baselines only**, on national daily counts and hours.
  - Test window 2025-08-16 → 2026-06-24 (latest).
  - MA-30: MAE 11.84; naive: 15.5. ARIMA is disabled.
- **Docs:** no AI log.

### 14. tShyshatskyi/Alert-prediction — likely 3 · tech 3
June cohort; 16 commits.
- **Scope:** Kyiv City vs **Nikopol hromada**, plus an interactive map comparing all oblasts.
- **Data:**
  - "Alert in the oblast" means the union of its communities.
  - The Nikopol filter was fixed to include oblast-wide alerts, after an artefact of the granularity change made its trend look like it was rising.
  - UTC → Kyiv.
- **Models:**
  - Baselines: ConstantRate, RecentRate (14 d), climatology (hour × weekday) and persistence (24 h earlier).
  - HGB hourly classifier using 1-step lags (a nowcast-style regime, which the README admits).
  - SARIMA/Holt-Winters on daily data.
- **Evaluation:** 5 expanding folds × 30 days at the end of the series, with `max(train) < min(test)` asserted. Kyiv: ML AUC about 0.64 vs climatology 0.58.
- **Hygiene problems:**
  - `reflection.txt` still contains "[~190 words — trim to ~100 for submission…]".
  - The README contains a `<your-username>` placeholder.
  - `models/forecast.py.bak` is committed.

### 15. Python-UA/Ukraine-alerts-v3-learning — likely 2 · tech 2
June cohort; 3 commits.
- **What it is:** a 13-stage "pre-registered" pipeline (SARIMA/SARIMAX, LightGBM, Prophet, stacking, conformal prediction, SHAP, Chronos) on national daily counts.
- **Data problems:** the official feed is filtered to **oblast level** and **concatenated with volunteer data**, then deduplicated on (oblast, started_at). The two feeds' timestamps differ, so the dedup misses and events are double-counted.
- **Leakage:**
  - A hand-picked, hindsight "ISW events" list, including outcome-defined events such as "Largest single-day missile strike", used as ±3-day exogenous flags.
  - Stacking weights fitted on validation; static distances to the front line.
- **Results:**
  - SARIMA test MAE 17.9 vs naive 28.8.
  - LightGBM 36.8 and the ensemble 38.6 are **worse than naive**.
  - "Ensemble + conformal" equals SARIMA, with coverage 1.0 and interval width 155, which is degenerate.

### 16. HoiSerhii/air-alerts-analysis — likely 4 · tech 3
June cohort; 4 commits.
- **Question:** did alerts become nocturnal? It answers this one question well.
- **Data:** official feed with exact full-row dedup; an oblast union of all sub-oblast alerts; DST-safe interval explosion into Kyiv-local hours (`src/timeutils.py`); stuck sirens excluded.
- **Result:** the night share (22:00–05:59) is about **0.11–0.13 above the 0.333 uniform baseline** in 2023–25.
- **Engineering:** `sanity_check.py` acceptance gate, `spec.md` contract, Streamlit app.
- **No forecast**, by design.
- **AI log:** `docs/AI_LOG.md` (125 KB, verbatim) shows the user **challenging the dedup semantics** and the AI proving them.
- **Why:** comparable to the known passer — modest, correct and honest.

### 17. mseheda/airraid-ts — likely 4 · tech 4
June cohort; 7 commits named STEP 1 / STEP 2.
- **Framing:** daily counts of alert **onsets** for Kyivska oblast, with Kyiv City as a null control; horizon 14 days.
- **Data:** `volunteer_en` only (never spliced with official); finished_at is not used; day bins are in UTC, with a documented sensitivity check (13.7% of onsets fall on a different Kyiv-local day). The official regime break is noted but irrelevant here.
- **Methods:**
  - DIRECT per-lead Poisson/Negative-Binomial GLM.
  - A **suite of 7 baselines**: EWMA α = 0.1 frozen, trailing mean, train mean/median, naive, seasonal-naive, constant zero.
- **Evaluation:**
  - Expanding rolling origin, 12 folds, covering the last ~24 weeks of 2026.
  - `src/contract.py` holds an acceptance contract **frozen before modelling**. The original MASE < 1 gate was shown to be gameable (an all-zero forecast passes on hourly data), so it was replaced with: beat the strongest baseline by ≥5% in ≥8/12 folds.
  - Result: **FAIL.** GLM MAE 2.161 vs EWMA 2.158.
  - Probabilistic results in `src/prob_eval.py`: CRPS 1.591 vs a dispersion-matched EWMA-NB baseline at 1.549, within noise (sign test p = 1.0).
- **Leakage:** a runtime **tripwire** asserts that no feature reads a y-index at or after the origin (`src/model.py`); it was validated by injecting a real leak. The red team also found and fixed a look-ahead in the seasonal-naive baseline.
- **Process:**
  - Three red-team subagent passes (`.claude/agents/red-team.md`).
  - A LangGraph generate → execute → evaluate → correct loop with human-in-the-loop interrupts (`src/airraid_loop.py`).
  - Raw transcripts published after a gitleaks scan (`ai-log/`).
- **Red flags:**
  - Leftover scripts (`src/_critic_checks*.py`); over-engineered for the task.
  - The volunteer feed's onset fragmentation after 2025 (see #8) could distort 2026 counts.
  - Daily onset counts are of limited practical value.

### 18. guilbk/air-raid-raion-forecast — likely 3 · tech 3
June cohort; 12 commits.
- **Target:** a new alert starts **in a raion within 60 minutes**, on a 15-minute grid.
- **Data:**
  - Official (uk) feed from 2025-01-01.
  - Oblast-wide alerts are **inherited by all raions**; hromada alerts are mapped to a raion proxy (`src/prepare_alerts.py`).
  - No dedup.
- **Evaluation:** train < 2025-11-01, validation Nov–Dec 2025, test 2026, with a 120-min purge at the boundaries (`src/apply_purge_gap.py`). CatBoost plus a logistic search on validation; reports PR-AUC, Brier and precision@top-10%.
- **Gaps:**
  - **No results in the README.** The metric CSVs aren't committed; only 25 MB of `.cbm` models are.
  - `live_alerts_client.py` is empty.
  - `.idea/` is committed; no AI log.
- **Borrow:** downscaling to raions, the right unit after 2025.

### 19. mylovanov-alt/ukraine-airraid-analysis — likely 3 · tech 4
June cohort, created 06-29 (after the 20–26 June cluster); 2 commits.
- **Scope:** a "danger & hazard" study with pure-numpy GLMs (`src/lib_stats.py`) and large HTML reports.
- **Data:**
  - Official feed, 274,972 rows, **not deduplicated**.
  - Oblast-hours come from a union on a 10-min occupancy grid, so duplicates don't matter for hours, but `n_starts` is doubled before 2026.
  - **Independently re-collected @air_alert_ua with Telethon** for 2026-04-30 → 06-28 and matched it against the dataset: r = 0.9996, 98.7% of events within 60 s (`VERDICT.md`, `src/manual_check.py`).
- **Models:**
  - A self-exciting log-linear OLS for national oblast-hours at 1 and 7 days ahead, expanding window over the last 200 days, against naive, seasonal-naive and MA7 (claims +10–37%).
  - Per-oblast logistic model for a "heavy day tomorrow" (>3 h): pooled AUC 0.92; rear oblasts reported separately at 0.61.
- **Leakage:** today's front-line distance is applied to the whole history.
- **Borrow:** `synthetic_tests/caseA–C` inject ground truth to test the pipeline; the fidelity-audit idea.
- **Red flags:** no dedup. `data/processed/forecast_summary.json` (14-day horizon, probably from the older `src/forecast.py`) says the best model is seasonal-naive and lists no model row, so the evidence is inconsistent across scripts.

### 20. 3Metrovuy/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine — likely 3 · tech 2
- **What it is:** a Streamlit EDA: oblast → raion sunburst, weekday × hour heatmap in Kyiv local time with DST, and a raion coverage metric.
- **Data:** official feed deduplicated (271,894 → 158,041 rows) with an interval union.
- **Gaps:** 1 test; no forecast. The README lists `ai_log.md`, `reflection.txt` and `CLAUDE.md`, but they are **missing** from the repo.

### 21. simonenkoanastasiia-eng/air-raid-analysis — likely 3 · tech 3
- **Model:** hourly per-oblast HGB predicting `active(t+H)` from causal lags and neighbour features. Calendar is in UTC; no dedup (harmless for the active flags).
- **Evaluation:** `TimeSeriesSplit` with 5 folds over the full history (not only the latest). H = 1: mean AUC **0.744**; beats binary persistence in 24/24 oblasts. AUC decays with the horizon (0.73 at 1 h → 0.58 at 12 h for Kharkiv).
- **Reflection:** honestly fixes an earlier nowcast (AUC 0.88).
- **Hygiene:** single commit.

### 22. h00yaday/kse-air-raid-forecasting — likely 2 · tech 2
- **Model:** SARIMAX on daily counts for Kyiv City from volunteer data: MAE 1.506 vs seasonal-naive 1.643. Served by FastAPI + Docker.
- **Hygiene:**
  - The README still has a template line: "(Pull these directly from your 02_modeling_experiments.ipynb output…)", and the notebooks are missing.
  - Many 0-byte modules (`features/calendar_features.py`, `visualization/plots.py`, `tests/test_models.py`).
  - 78 MB of `.pkl` committed.

### 23. kokojas/ukraine-air-alert-time-series — likely 3 · tech 2
- **What it is:** burden and fatigue metrics from volunteer data, with intervals unioned and split into Kyiv-local days.
- **Forecast:** a fixed-weight blend (0.45·7d + 0.35·30d + 0.20·weekday), backtested per oblast with MAE but **not compared to anything**.
- **Product:** static GitHub Pages dashboard and a DOCX report.
- **Hygiene:** the README's method section says it uses the official CSV, but the code uses volunteer data.

### 24. KharinTymofii/air-alert-analysis — likely 3 · tech 3
- **What it is:** a burden observatory with work, school and night windows, broad synchronised-event detection (≥85% of regions for ≥5 min), and **school-institution exposure from EDBO counts**.
- **Data:** the main pipeline is the official feed filtered to **oblast level**. It does recognise the 2026 drop-off and adds an any-raion reconstruction plus a combined series for the national trend.
- **Engineering:** 9 test files; static HTML dashboard; descriptive only.

### 25. recruitabx/airraid-propagation-analysis — likely 4 · tech 4
June cohort; 4 commits.
- **Question:** when an alert starts in oblast A, does B tend to follow, and how soon? No forecasting, by deliberate choice.
- **Data:** `volunteer_en` pinned to `dac507f`; 101,266 onsets, 2022-02-25 → 2026-06-20.
- **Method:**
  - Directional asymmetry D = P(A→B) − P(B→A) for windows of 5, 15 and 30 min.
  - A **circular-shift null** with 200 replicates; links are ranked by **effect size, not z**.
  - **Wave control:** the analysis is re-run on isolated onsets (≤4 oblasts co-active), each with its own null.
  - Of 120 significant links, 45 survive; about 63% of apparent propagation is "the wave reaching the west last".
- **Validation:** re-run on the official **alerts.in.ua** last month, with raion/hromada rolled up to oblast episodes merged at 30 min. 6/16 headline links reproduce, 8 are inconclusive (too sparse) and 2 do not reproduce.
- **Product:** a live Telegram bot that serves frozen artefacts only, deployed with systemd.
- **AI log:** `AI_LOG.md` shows the user steering ("Do NOT invent field names…", "show me a raw sample before you write the adapter").
- **Borrow:** `analyze.py` (null and wave control), `validate.py`.
- **Caveat:** the "western co-triggering" links (e.g. Volyn → Zakarpattia, about 0.4 min) may be **artefacts of the volunteer parser bug** found in #8.

### 26. sasha2lapina-spec/ukraine-air-raid-analysis-oleksandra-lapina — likely 2 · tech 2
- **What it is:** XGBoost and SARIMAX on daily counts from volunteer data, with Google Trends, a Telegram scrape of the last 5 pages, the Open-Meteo archive, moon phase and "geopolitical birthdays" as features.
- **Results:** Kyiv MAE 2.81 vs seasonal-naive 3.43; nationwide 16.95 vs 21.57; evaluated with `TimeSeriesSplit`.
- **Leakage:** Trends values are normalised over the whole query window (look-ahead); the Telegram feature exists only for recent dates.
- **Hygiene:** `__pycache__` committed; `file:///C:/…` links in the report; single commit.

### 27. nataliiakubik/air-raid-alerts-time-series — likely 2 · tech 2
- **What it is:** descriptive weekly frequency and duration from oblast-level official rows, deduplicated, in a Colab notebook with an AI log.
- **Problem:** deliberately **cut at 2025-07-31** to avoid the raion shift, which violates "use the most recent data".

### 28. mykoladomanskyi25-dotcom/Air-raid-alerts — likely 2 · tech 1
- **What it is:** notebooks that filter to oblast level and call the post-Nov-2025 collapse a "**data-collection failure**".
- **Evaluation:** test set Jul–Aug 2025; MA7 MAE 14.28; baselines only.

### 29. Ianitskyi/ukraine-air-alerts-analysis — likely 3 · tech 2
- **What it is:** a deployed Streamlit atlas with folium maps. All levels are merged into oblast episodes, so duplicates are absorbed. Descriptive only.
- **Bugs:** durations are rounded up to whole hours. The Kyiv-time strings are re-parsed with `utc=True`, so `hour` is actually UTC.
- **Hygiene:** many one-off scripts; 54 MB of CSV committed.

### 30. MishaDvali/Air_raid_alert_analysis_and_prediction — likely 3 · tech 3
- **Target:** a new alert starts within 3 h, on a 30-min grid.
- **Evolution:** documented in `docs/VERSION_2..6.md` and `docs/improvements/1–10`. V1 logistic regression had ROC-AUC 0.763 and PR-AUC 0.140; V6 HGB reaches **0.813 and 0.423**.
- **Evaluation:**
  - The test window is **2025-09-01 → 10-31**: a "clean" oblast-only benchmark, not the latest period. The threshold is tuned on validation.
  - An "operational latest" model, projecting every level to oblast, is trained up to 2026-06-24 but **never evaluated**.
  - Many versions are compared on the same test window, which amounts to selecting on test.
- **Hygiene:** local `C:/Users/…` links; 3 bulk commits.

### 31. tui2019/Air-Raid-Analysis — likely 3 · tech 2
- **What it is:** a CLI report generator plus an HTML dashboard. Intervals are unioned per region over a rolling window of N days; an optional Gemini summary.
- **Evidence of iteration:** 41 commits in one day, including fixes to the counts.
- **No forecast.**

### 32. antonprasol-cmyk/ukraine-air-alert-forecasting — likely 2 · tech 3
- **Data:** 2025 only. The CSV is over 3 MB and wasn't cloned; the files sit nested under `repo/`. The national "next alert" episodes use only oblast-level rows.
- **Models:**
  - Log-normal survival model for gaps between alerts.
  - Oblast and raion spatial **Hawkes** processes with numba and analytic gradients, with a walk-forward log-likelihood test.
  - Corridor analysis.
- **Misdiagnosis:** the quantiles from the last 20% of 2025 are miscalibrated (the 50% quantile captures only 31% of gaps). The repo blames non-stationarity, but the oblast → raion shift explains it.
- **Hygiene:** single commit.

### 33. artiekra/air-alert-analysis — likely 2 · tech 2
Single-file Streamlit app with an STL decomposition, Kyiv timezone and an oblast/all-levels toggle, plus Docker. No dedup and no forecast.

### 34. uiuxdesigner18/ukraine-air-raid-analysis — likely 2 · tech 1
Filters to `level=='oblast'` ("sub-oblast granularity discarded"), then fits ARIMA(2,1,2) on a series that collapses after Dec 2025, with no evaluation. Single commit.

### 35. itpsychologist/Analysis-of-air-raid-alerts — likely 3 · tech 2
- **Closest analogue to the confirmed passer:** live alerts.in.ua ingestion (active alerts plus 30-day `month_ago` history) in a Streamlit Cloud app, with KPIs, a diurnal heatmap and a vulnerability ranking.
- **Forecast:** Holt-Winters / Ridge over 7 days, fitted on only 30 days and **never backtested**.

### 36. dvasylchuk/kse_ai_agent_school — likely 2 · tech 2
- **What it is:** Kyiv City clustering and burstiness. Official data deduplicated (3,590 → 1,795 rows).
- **Problem:** cut at 2025-11-29 "to avoid the raion shift", although Kyiv City is unaffected by it, so 7 months of the newest data are thrown away. Descriptive only.

### 37. shynkaruk00-collab/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine — likely 3 · tech 3
- **Metric:** a granularity-invariant metric, the **number of distinct oblasts under alert per day**, with all levels attributed to their parent oblast. No dedup, so the regional bar counts are doubled.
- **Model:** ARIMA chosen by AIC on train; holdout is the last 30 days (the latest data).
- **Result:** ARIMA MAE 3.32 vs **the historical mean 3.28**, i.e. it doesn't beat the mean, and the README says so.

### 38. lewym90/egida — off-topic
A Polish civil-safety PWA in JavaScript (Polish RSO alerts, shelters, NEPTUN feed). Not Ukrainian alert time-series analysis and not Python.

### 39. mariia008/air-alert-analysis — likely 1 · tech 1
An empty placeholder: a README and `.gitignore` only, created 2026-10-10.

---

## Top picks in this batch

Clone root: `scratchpad/clones/<owner>_<repo>/`.

1. **maranferij-lang/Ukraine-air-alerts — the template to copy.**
   - `src/load.py`: dedup, the `hromada==raion` relabel, the `OFFICIAL_OUTAGES` mask, and `data_end`, which trims the final partial day plus one day for right-censoring.
   - `src/panel.py`: maps alerts to raions, applies the ≥½-raions rule for "oblast under alert", and joins restarts within 5 min while reading the state at t from un-joined episodes.
   - `src/targets.py`: exact targets using `searchsorted`, separating (a) "active" from (b) "new start".
   - `scripts/check_no_peeking.py`: rebuilds features from data truncated at t and checks equality, with negative controls. **The single most valuable artefact in the batch.**
   - `src/baselines.py` (persistence, same hour yesterday, train frequency) and `src/metrics.py` (within-oblast AUC, Brier decomposition).
   - `CLAUDE.md` (user rules for the agent) and `PROCESS_LOG.md` (rounds with "Wrong #n" findings), which suit the "AI log is the primary signal" criterion.
   - Data forensics to reuse: the volunteer parser bugs (Lviv/Volyn substring matches), κ drift, the outage window, 253 unflagged +1 h ends, and the explanation of the duplicates as an append-mode re-run.
2. **Trigger111/ukraine-air-raid-alerts-tsa.**
   - `src/data_loader.py` with `data/meta.json`: fetch pinned to a commit and checked by SHA-256.
   - `src/clean.py`: dedup, overlap merge and an `is_long_alert` flag.
   - `src/aggregate.py`: DST-correct Kyiv-day splitting, **oblast union time** and region-alert-days as granularity-invariant metrics.
   - `src/model.py` (`_verdict`): a pre-agreed skill bar (beat the recency AUC *and* the base-rate Brier).
   - `reflection.md`: a model ~100-word reflection.
3. **chud00s/tryvoha-radar-tsa.**
   - `src/features.py`: neighbour-oblast features from a geo adjacency table, hours since the last alert, Kyiv-local calendar.
   - `src/forecast.py`: HGB with isotonic calibration on a separate slice, climatology and persistence baselines, and a saved reliability curve.
   - `src/analysis.py`: `mass_attack_episodes`, `surprise_days` (robust z) and `propagation_lead_lag`.
   - `app/dashboard.py`: consumer vs analyst modes and a data-freshness badge.
4. **mseheda/airraid-ts.**
   - `src/contract.py`: an acceptance gate frozen before modelling and designed so it can't be gamed (beat the strongest of the baselines by ≥5% in ≥8/12 folds).
   - `src/prob_eval.py`: CRPS, coverage and **dispersion-matched** baselines.
   - `src/model.py`: the leakage tripwire asserts.
   - `.claude/agents/red-team.md` and `ai-log/render.py`: red-team subagents and a renderer for publishing raw transcripts.
5. **recruitabx/airraid-propagation-analysis.**
   - `analyze.py`: circular-shift null, links ranked by effect size, and a **wave control** using the co-active count.
   - `validate.py`: replays the findings on the official alerts.in.ua API, rolling raions up to oblast episodes.
   - `bot.py`: a product that serves frozen artefacts only.
   - The `AI_LOG.md` prompting style ("don't invent schemas, show raw samples first").
6. **rayhankhilji/terrestrial (forecast module only).**
   - `predict/strike/features.py`: features computed at issue time on 6-h blocks; separate `y_active` and `y_new` targets; exogenous data lagged to its publication delay (VIINA +5 d).
   - `predict/strike/train.py`: **conditional persistence** baseline, Brier skill score, a "beats baselines" flag, a model card JSON, per-region AUC and permutation importance.
   - `CLAUDE.md` §16.4: the train/serve parity rule.
7. **mylovanov-alt/ukraine-airraid-analysis.**
   - `src/collect_airalert.py`, `src/analyze.py`, `src/manual_check.py` and `VERDICT.md`: an independent re-collection from Telegram to audit dataset fidelity.
   - `synthetic_tests/caseA–C/gen.py`: synthetic data with injected ground truth to check that the pipeline recovers known effects.
8. **anechytailenko/AirRaidAlerts (leakage plumbing only).**
   - `src/ml/dataset.py`: an embargo of window + horizon between splits and a train-only scaler.
   - `src/airraid/export_dataset.py`: a DuckDB ASOF join for text-derived flags, with TTL and staleness features.
   - `src/ml/losses.py`: per-horizon thresholds calibrated on validation.

**Also worth a look:**
- guilbk: raion downscaling (`src/prepare_alerts.py`) and a purge gap (`src/apply_purge_gap.py`).
- HoiSerhii: DST-safe hour explosion (`src/timeutils.py`) and an acceptance gate (`sanity_check.py`).
- yevayarova: separates raw record counts from merged episodes, and stitches volunteer → official.
- shynkaruk00: the "distinct oblasts under alert per day" metric.
- tShyshatskyi: a hromada-level target (Nikopol).

## Common mistakes seen

1. **Oblast-only filtering of the official feed.** It empties 2026 or makes it misleading:
   - uiuxdesigner18, mykoladomanskyi (who calls it a "collection failure"), Python-UA, gklymenko for the non-Kyiv oblasts, KharinTymofii's main pipeline, antonprasol's national episodes, and artiekra's default view.
   - Variant: **cutting the data before the shift**, which throws away the latest period — nataliiakubik (2025-07-31), dvasylchuk (2025-11-29, needlessly for Kyiv City), MishaDvali's benchmark (≤ 2025-10-31) and mykoladomanskyi (≤ 2025-08-31).
2. **No dedup.** Hours computed by union are unaffected, but counts and starts double for 2022 → 2026-01, which fakes a "drop" in 2026: chernysholeksandr, mylovanov-alt (`n_starts`), shynkaruk00 (regional counts), guilbk, simonenko and artiekra.
3. **Summing rows across levels.** Counts jump about 4× after the raion switch (ArseniiKlimenko's national counts, MishaDvali's operational model).
4. **Trusting the volunteer feed as ground truth.** It covers about 35–60% of official time, and in 2025–26 it degrades through keyword-parser mislabels and fragmentation. Used without caveat by chud00s, anechytailenko, terrestrial, mseheda, recruitabx, AZAR1VAN, kokojas, h00yaday and sasha2lapina. Only maranferij measured the problem.
5. **Missing, wrong or weak baselines.** anechytailenko has none. AZAR1VAN reports the MAE of a baseline, not of its model. DanyloBeha compares SARIMA only with ETS. simonenko uses only binary persistence. The strongest baselines appear in Trigger111 (base rate), maranferij (frequency table), mseheda (EWMA and train mean), terrestrial (conditional persistence) and shynkaruk00 (historical mean); chud00s and tShyshatskyi used a decent climatology baseline.
6. **Forecasts never evaluated:** AZAR1VAN (Prophet), itpsychologist (Holt-Winters on 30 days), uiuxdesigner18 (ARIMA), DanyloBeha (damped ETS to the end of 2026), and MishaDvali's "operational" model.
7. **Leakage patterns:**
   - Observed weather for the target day (terrestrial).
   - Google Trends normalised over the whole window (sasha2lapina).
   - Hindsight event lists, including events defined by the outcome (Python-UA's "ISW ±3d").
   - Today's front-line distance applied to all history (mylovanov-alt, Python-UA).
   - Model or version selection on the test window (MishaDvali; gklymenko, mildly).
   - Hour-bucket "active now" without a stated issue time (chud00s, anechytailenko).
8. **Calendar in UTC instead of Kyiv:** anechytailenko, simonenko, DanyloBeha (UTC days), gklymenko (acknowledged), mseheda (acknowledged, frozen), and Ianitskyi (accidentally re-converted to UTC).
9. **Over-engineering in place of analysis:** YuraHusynskyii (K8s/Redis on 55 rows), Python-UA (13 stages), anechytailenko (Postgres + GNN + MCP), h00yaday (an API around empty modules).
10. **Leftovers and hygiene:**
    - AI template text left in: h00yaday's README and tShyshatskyi's reflection.
    - Placeholders and local paths: `<your-username>`, `C:/Users/…`, `file:///` links.
    - Junk committed: `.bak`, `__pycache__`, `.idea`, large binaries.
    - Broken uploads: chernysholeksandr's scrambled files; 3Metrovuy's promised logs are missing.
11. **Misreading the structural break** as a real de-escalation or a data failure: mykoladomanskyi, and antonprasol's late-2025 "non-stationarity".
12. **Missing the official-feed freeze (2026-09-07):** ArseniiKlimenko's daily rebuild has been stale since then. In the October cohort only maranferij noticed.

## Gaps nobody in this batch addressed

1. **Post-freeze and post-reform data.** Nobody brought in alerts.in.ua history, the JustJimer archive or ukrainealarm to extend past 2026-09-07. Nobody modelled the new **red/yellow levels** or threat types (drone vs missile). Even the October repos stop at the frozen official file.
2. **Real-time availability.** Vadimkin rows appear only after an alert ends and after the next daily run, a lag of up to about 29 h. No one priced this into a deployable "forecast at t". Live feeds appear only for display (chud00s, itpsychologist, terrestrial).
3. **Synthetic or imputed end times.** Only maranferij flagged the unflagged +1 h official ends. Nobody else masked them, or the volunteer `naive` +30 min ends, in duration-based features or targets.
4. **Leak-safe exogenous data.** No one used archived weather *forecasts* (the Open-Meteo Previous Runs API), the Air Force @kpszsu morning summary with its publication timestamp, ISW with D+1 publication timing, or martial-law holidays (`holidays` with the `workday` category). The only text features came from anechytailenko's ASOF-joined OSINT flags.
5. **Region identity by ID rather than name.** Nobody joined on region UIDs to handle raion renames (Novomoskovskyi → Samarivskyi, Chervonohradskyi → Sheptytskyi). guilbk and antonprasol work at raion level but key on names.
6. **Cross-source reconciliation.** Only maranferij (κ) and recruitabx (alerts.in.ua replay) compared feeds. Nobody used the Kyiv Digital official dataset, which has levels and causes since 2026-09, as an independent check.
7. **Decision-relevant evaluation.** No one measured warning lead time, cost-weighted errors, or alert-start recall at a fixed false-alarm rate per region. Within-oblast AUC (maranferij) was the only metric that stops easy cross-region discrimination from inflating the score. terrestrial's per-region AUC and mylovanov's rear-only AUC come close.
8. **Regime-aware evaluation.** Only maranferij compared full-history training with post-2026 training. Nobody evaluated pre- and post-shift test windows separately, or the effect of the September 2026 levels reform.
9. **Censoring at forecast time.** Except for maranferij's truncation check, nobody treated ongoing alerts at t as censored. Features such as "duration so far" or "hours since end" were built from completed intervals.

---

## Batch 2 review: KSE Agentic AI School Stage 2 (air-raid alert time series)

There are 38 repos in this batch. Everything was reviewed from the local clones under `scratchpad/clones/<owner>_<repo>/`, and no repo code was executed. In the file references below, `owner/repo:path` is relative to the repo root.

**Rating scales**

- **Likely passed (P)**, judged against KSE's criteria: process and iteration, a functional result, latest-period and leakage-free evaluation. The AI log itself is unseen.
  - 1 = very unlikely, 2 = unlikely, 3 = coin flip, 4 = likely, 5 = very likely.
  - Calibration point: the confirmed passer (tbaraniuk) is a modest Dash dashboard with live alerts.in.ua data and no forecasting. A repo does **not** need forecasting to pass.
- **Technical quality (T)**:
  - 1 = not real data, doesn't run, or claims not backed by code.
  - 2 = runs, but a core data or evaluation flaw invalidates the results.
  - 3 = sound but basic, or good with one notable flaw.
  - 4 = solid: leakage-aware, evaluated on the latest period, with baselines.
  - 5 = exemplary: multiple safeguards, honest negative results, reproducible.

## Summary table (sorted by P, then T)

| Repo | Cohort | Framing (short) | P | T |
|---|---|---|---|---|
| Ddrakkx/alerts-forecast | Oct | Onset forecast, 4 oblasts, 15 min–6 h; strict references; pre-registered holdout | 5 | 5 |
| AndriyTkh/kse-summer-sch | Jun | Per-oblast LightGBM 30 min–6 h → onset pivot; React map; exported AI sessions | 5 | 4 |
| robotheist/Air-alerts-forecast | Oct | 24 regions, 1–24 h, LightGBM + @kpszsu Telegram text features | 4 | 5 |
| Dopplerr24/air-raid-alert-analysis | Oct | National panel, onset next 1 h, LightGBM; causality and region-isolation tests | 4 | 5 |
| tymof1j/ai-stage2 | Jun | Raion-load forecast + "localisation effect" counterfactual; Quarto site | 4 | 4 |
| goodfrog33/air-raid-forecasting-ukraine | Jun | Multi-target platform; Streamlit Cloud + FastAPI; GDELT/Telegram variants | 4 | 4 |
| Freit007/air-alert-analytics | Jun | Descriptive Streamlit; correct episode unification; wave replay | 4 | 3 |
| Semfayni/Air-Raid-Analysis | Jun | Descriptive Streamlit + live alerts.in.ua map + anomaly lab (passer-shaped) | 4 | 3 |
| AnnaKiulafli/anna_kiulafli_kse_stage2_2026 | Jun | 2026 raion-level daily series; baseline-only walk-forward | 4 | 3 |
| tannyaQ/ukraine-air-alerts-tsa | Jun | National daily counts; Holt vs baselines; weekly walk-forward | 4 | 3 |
| egorcusai/air-raid-alert-forecast | Jun | "Where are alerts predictable?"; 3 h classifier per region; AI-log reading guide | 4 | 3 |
| Petit925/kse-air-raids-forecast | Jun | Prophet vs seasonal naive + work-shift scheduler | 3 | 3 |
| kervad28-debug/air-raid-alert-next-day-prediction | Jun | Next-day occurrence, Khmelnytska; honest negative result | 3 | 3 |
| gbatulin/kse_summer | Jun | 5/15/30-min onset, LightGBM; "as-of" experiments (not latest) | 3 | 3 |
| asobkiv/air-raid-analytics | Jun | SARIMA/Prophet + spread probability; metric-driven variant loop | 3 | 3 |
| timkaster/AirAlerts | Jun | Own parser of @air_alert_ua export; weather; daily alert hours | 3 | 3 |
| alinasamoilenko292/KSE-AI-Agentic-Summer-School | Jun | National breadth series, hypothesis tests, Prophet, clustering | 3 | 3 |
| karavaievg/KSE-AI-Agentic-Summer-School- | Jun | "Downtime index" business dashboard (no forecast) | 3 | 3 |
| ZahBoy/ukrainian-air-alarm-data | Jun | Descriptive case studies; LLM threat-type labels from Telegram | 3 | 3 |
| mashta-lilia/S.T.A.L.K.E.R.… | Jun | 3 macro-zones, 7-day SARIMA/Prophet, embargoed CV | 3 | 2 |
| Shenshyn/Air-Alerts | Jun | Survival model of alert duration (KM/Cox/XGB) | 3 | 2 |
| Yaroo-a/ukrainian-air-raid-sirens-analysis | Oct | Calm-hour onset, LightGBM; rigorous scaffolding on an oblast-filtered target | 3 | 2 |
| nazariidatsenko25-png/ukraine-air-raid-analysis | Jun | Next.js + FastAPI; HMM, cascade, Prophet; no evaluation | 3 | 2 |
| tanchikr12/air-alert-analytics | Jun | Streamlit 30-day "forecast" using HistGBM | 3 | 2 |
| Heir-of-God/AlerticUA | Jun | Dash dashboard + Prophet (oblast-filtered) | 3 | 2 |
| Nzrch/ukraine-air-raid-analysis | Jun | Flask dashboard, Isolation Forest, Telegram collector | 3 | 2 |
| Lahodzinskyi/air-rapid | Jun | Local web app: stats, weather, inter-oblast correlation | 3 | 2 |
| sergkern1-netizen/air-raid-alerts-analysis | Jun | Prophet/ETS/LSTM on summed minutes; raion artifact read as escalation | 2 | 2 |
| mokliak/ksestagetwomokliak | Jun | RF/LR daily panel + Gemini-scored news; invalid CV | 2 | 2 |
| YaroslavKheilyk/Time-Series-Analysis-… | Jun | Baselines-only MVP; log is about GitHub account migration | 2 | 2 |
| monsterkokoko/ukraine-air-alerts-timeseries | Jun | Oblast-filtered; truncated at 2025-09 | 2 | 2 |
| Vlad1343/ukraine-air-alerts-timeseries | Jun | Oblast-filtered; truncated at 2025-10 | 2 | 2 |
| abricos69/TimeSeriesAnalysisUkraine | Jun | SARIMA vs naive ("Stage 1") | 2 | 2 |
| CPTshkarpetka/ukraine-alerts | Jun | Hour-of-day probability map (oblast-filtered) | 2 | 2 |
| iamanavor-droid/AirRaid | Jun | Synthetic data only | 1 | 2 |
| Solomiia27/AirAlertsAnalyzer | Jun | Mock data | 1 | 1 |
| 3olena3/air-raid-alerts-forecast | Oct | CatBoost Gradio app; placeholder URL, unsupported metrics | 1 | 1 |
| Nazar32/forecast-driven-route-selection | Oct | **Not a KSE submission** (IEEE Access paper code); highly relevant | n/a | 5 |

---

## Tier A: strong repos (full cards)

### Ddrakkx/alerts-forecast (Oct 2026; 36 commits, 2026-10-09 → 10-10)

- **Framing:** Probabilistic forecast of alert **onsets** per oblast.
  - Target: P(a new alert starts in (t, t+H]), evaluated only from quiet moments, on a 15-minute UTC grid.
  - Main case is Poltava; Kyiv oblast, Kharkiv and Lviv are comparisons.
  - Horizons are 1, 3 (main) and 6 h, plus 15 and 30 min.
- **Data:**
  - **Primary:** the Vadimkin **volunteer** file, pinned to commit `2f11554` (2026-10-09; last timestamp 2026-10-09 05:12 UTC).
  - **Official file as robustness check:** deduplicated, with raions merged into oblast episodes. The author found the 2026-09-07 freeze, the 08-29..09-02 hole, and that Kharkiv is "always on" after merging.
  - **Lviv data warning:** 91% of Lviv volunteer starts fall inside no official episode.
  - **Timezone:** UTC everywhere; Kyiv local time only for calendar features.
  - **`naive` ends:** flagged, and a sensitivity run excludes them.
  - **Yellow/red levels:** recognised (decision 12) and collected going forward by a live eMap logger.
- **Target/horizon:** onset label; the main sample is moments with no active alert. "Active" uses only "not finished yet", never the value of `finished_at`.
- **Methods:**
  - **Baselines:**
    - "alert ended within the last H" (adapted persistence)
    - hour of week, smoothed hour of week
    - constant rate
    - `recent_level`: 3/7/14/30-day rate, refit daily
  - **Models:** logistic regression on own / +neighbours / +country feature sets, with or without Platt scaling, and gradient boosting.
  - **Selection:** a small grid per family; the configuration is chosen by validation Brier.
- **Evaluation:**
  - **Test:** the last 8 weeks (2026-08-14..10-09, about 4.5k moments per oblast and horizon). **Validation:** the 8 weeks before, purged by H. Refit weekly in walk-forward.
  - **Intervals:** 95% paired bootstrap over ISO-week blocks.
  - **Two references:** "no-hindsight" (best baseline family on validation) and "strict" (best baseline *configuration on the test block itself*, chosen per metric).
  - **Results:**
    - **Poltava:** no gain against the strict reference at any horizon. At H=1, boosting PR-AUC is 0.351 vs 0.359 for the 3-day recent level; at H=3, logistic is 0.689 vs 0.734.
    - **Kyiv oblast:** significant gains at 15 min–1 h, driven by neighbour features. At 1 h these replicate on an earlier period (PR-AUC +0.057).
    - **Kharkiv:** significant gains at 15–30 min, also from neighbour features.
    - **Lviv:** nothing robust.
- **Leakage:**
  - **Truncation test** (`src/alerts_forecast/leakage.py`, `tests/test_leakage.py`): cut the data at t (drop later alerts, hide later ends) and require identical features. It runs at adversarial moments and on real data, and it catches a planted leaky feature.
  - **Purges:** train→val and val→test.
  - **Label-flip test:** checks that test labels cannot affect predictions.
  - **Self-declared residual leaks:** invented neighbour ends and late dataset additions. Every test-informed decision is listed (Lviv choice, short horizons, extra baselines).
- **Text/media:** none; proposed only with "published before the forecast moment".
- **Product:**
  - `demo/index.html`: a self-contained explainer of what is known at t versus the hidden window.
  - `demo/emap_logger.py`: a live logger.
  - `demo/live_forecast.py`: **pre-registered live forecasts** at each Poltava all-clear, written to a JSONL record with outcomes.
- **Engineering:**
  - Clean `src/alerts_forecast/` package and 6 test files.
  - Pinned snapshot with size checks, fixed seeds.
  - Per-oblast runner and generated `results/summary.md`.
- **Documentation:** the best in the batch.
  - `docs/decisions.md` has 13 numbered decisions with retractions.
  - An external review by a second agent is re-verified and fixed in decision 10.
  - **Pre-registration** of an untouched holdout on a new snapshot (git tag `holdout-freeze`, `scripts/run_holdout.py`).
  - README section: "How the conclusion changed".
  - AI-usage section.
- **Standout ideas:**
  - Strict vs no-hindsight references.
  - `recent_level` baseline refit daily.
  - Pre-registered holdout on the next data snapshot.
  - Truncation test.
  - A live forecast record as an out-of-sample check.
  - Cross-checking volunteer against official per oblast.
- **Red flags:**
  - The test block was looked at many times (admitted).
  - Models are refit weekly while the baseline is refit daily; this asymmetry weakens the negative Poltava claim.
  - The volunteer series undercounts official alert time; this is not quantified globally.
  - Neighbour lists come from memory.
- **P 5 / T 5.** The batch's best demonstration of challenging and retracting AI-produced claims, with exemplary evaluation hygiene.

### AndriyTkh/kse-summer-sch (Jun 2026; 31 commits, 06-20 → 06-21)

- **Framing:** short-horizon (30m/1h/3h/6h) per-oblast alert probability, later pivoted to **onset**, plus duration (survival) and quantile intervals. All of it shows in a React + MapLibre dashboard.
- **Data:**
  - **Alerts:** Vadimkin official, **rolled up to oblast regardless of level** (with an explicit docstring explaining why an oblast filter would empty 2026). Exact duplicates are dropped; data is in UTC.
  - **Kaggle piterfm missile waves:** converted from Kyiv time to UTC.
  - **UCDP GED:** used as an annual prior, from prior years only.
  - **Grid:** clamped to 2023-07 or later; crimea, sevastopol and luhanska are excluded.
  - **Freshness:** `scripts/update_data.py` and `scripts/data_freshness.py`.
- **Target/horizon:**
  - **"Whether" model:** an alert active in (t, t+H] on an hourly grid. On this grid **30m ≡ 1h**, and the metrics are identical.
  - **Onset model:** a new alert starts in (t, t+H], evaluated from a quiet state.
- **Methods:**
  - **Main models:** 4 direct LightGBM models, recency-weighted, with `scale_pos_weight` and isotonic calibration on a 4-week calibration fold.
  - **Baseline:** a Prophet daily model ("Model A").
  - **Onset model:** LightGBM plus revived threat features.
  - **Other models:** KM + Cox PH for duration; quantile LightGBM for q10/q50/q90 intervals; PSI drift detection with walk-forward retraining.
- **Evaluation:**
  - **Split:** train_fit < calibration (4 weeks) < test (**last 8 weeks**, to 2026-06-21), with a 6 h purge. Walk-forward uses 4 folds.
  - **"Whether" model:** PR-AUC 0.89–0.91 against base rates of 0.36–0.53; the Prophet baseline gets 0.87–0.91.
  - **Onset model:** PR-AUC rises with horizon while the lift over the base rate falls.

    | Horizon | PR-AUC | Base rate |
    |---|---|---|
    | 1 h | 0.257 | 0.078 |
    | 3 h | 0.486 | 0.186 |
    | 6 h | 0.614 | 0.289 |

  - **Quantile intervals:** they under-cover, 0.64 against a nominal 0.80 (admitted).
- **Leakage:**
  - **Correct for alert history:** features are shifted ≥1, and a purge is applied.
  - **Problem 1, Kaggle timing:** wave features are keyed on the **event-window start** (`time_start`; date-only rows parse to 00:00 Kyiv) and shifted only 1 h. The night's total `launched` count becomes visible at the start of the attack, long before publication (around 09:20 Kyiv). The onset model uses these features, so its numbers are optimistic. The "tempo" feature uses the previous UTC day, which is also partly pre-publication.
  - **Problem 2, test-set tuning:** the GRID_START clamp, threat pruning and dropping walk-forward were all decided on the single 8-week test block (they admit the clamp "rests on a single 8-week holdout").
  - **Problem 3, operational eval:** `src/operational_eval.py` masks only the last N hours of the test window, so it cannot detect the systematic per-row lag and reports a 0% gap.
- **Text/media:** none (OSINT launch counts only).
- **Product:**
  - `viz/` React + MapLibre app: choropleth, live alert overlay, horizon toggle, metrics panel.
  - `run.py` runs install → compute → serve in one go.
  - The precomputed `viz/public/*.json` is committed.
- **Engineering:**
  - 16 test files (86 tests).
  - `src/config.py` is the single source of truth.
  - Clean modules.
- **Documentation:** the strongest *process* evidence among the June repos.
  - `_sessions/` holds every Claude Code transcript.
  - `_sessions/INDEX.md` ranks them by **human-typed characters**, and `_sessions/important/` collects the curated picks. Both are produced by `scripts/export_sessions.py`.
  - `claude/PLAN.md`, `claude/STRUCTURE.md` and `claude/pr-writedown/*.md` contain explicit "GOOD/BAD decisions" lists. They include catching the "hollow headline" (persistence-driven PR-AUC), which led to the onset pivot.
- **Standout ideas:**
  - The session exporter ranked by human input.
  - Phase write-downs.
  - The persistence critique and onset reframe.
  - Per-oblast lift vs base rate.
  - The "data vintage" idea for operational evaluation.
- **Red flags:**
  - The Kaggle availability-time leak.
  - Test-set-driven configuration.
  - No persistence baseline (Prophet is a weak comparator).
  - 30m and 1h are duplicates.
  - Frontline oblasts are "on" most of the time after the roll-up (acknowledged).
- **P 5 / T 4.** It visibly shows human steering and self-correction, which is exactly KSE's stated signal. The technical work is strong but has one real leak.

### robotheist/Air-alerts-forecast (Oct 2026; 4 commits on 2026-10-10)

- **Framing:** at the end of each hour, the probability that an alert is active in each of 24 regions at h = 1, 3, 6, 12 and 24 h. It also asks whether the Air Force Telegram channel adds signal.
- **Data:**
  - **Alerts:**
    - Volunteer (eTryvoga) file up to 2026-10-10 morning. It was chosen because the official file froze on 2026-09-07 and has the raion break.
    - Luhansk is excluded; alerts over 24 h are capped; naive alerts are set to 30 min.
    - Alerts are rasterised to a minute-level on/off matrix, and a 1 h margin is dropped at the right edge because alerts are published after they end.
  - **Telegram:** 41,241 posts from **@kpszsu** (2025-10-01→2026-10-10), scraped from the `t.me/s` web preview.
    - Collection fell back to a browser-console scraper when t.me was unreachable.
    - Post-ID gap checks caught 4 of 7 lost parts.
  - **Gazetteer:** KATOTTG (via 0G3RA/ua-geo-set).
- **Target/horizon:** alert *state* in the target hour; the "quiet origins" subset is also reported.
- **Methods:**
  - **Baselines:** persistence, same hour yesterday, and **climatology** (28-day rate at that hour of day).
  - **v1:** logistic regression.
  - **v2:** one global LightGBM across regions and horizons, with neighbour-adjacency and national-wave features.
  - **v3:** v2 plus text features — region mentions in the last 30/60/180 min, minutes since mention, neighbour mentions, and national threat-type counts.
- **Evaluation:**
  - **Split:** train, then validation (08-15..09-12), then **test = the latest 28 days (2026-09-12→10-10)**, used once, with weekly walk-forward refit.
  - **Brier at h=1:** 0.131 for v2, against 0.184 for climatology and 0.210 for persistence. At h ≥ 3 the models get 0.177–0.180 against 0.183–0.185.
  - **Quiet origins:** +9% over climatology at h=1, and only 2–3% at longer horizons.
  - **Text features:** −2.4% Brier on validation at h=1, but only −0.4% on test.
    - Day-block bootstrap: at 1 h the CI includes 0; at 3 h P(no gain) = 0.03.
    - The comparison is fair: v2 is retrained on the same text-covered window.
  - **ROC:** 0.86 at h=1; the model is calibrated.
- **Leakage:**
  - `tests/test_leakage.py` runs truncation tests for both the alert features **and the text features**: a post at or after T must not change any feature.
  - Training rows also need their *target hour* to end before the cutoff.
  - A pandas µs/ns bug (which zeroed all text features) was caught by a lead-time sanity check, and the test was hardened.
  - Telegram edits remain a possible leak, which they acknowledge: the web preview shows the final text.
- **Text/media:** the best text use in the batch.
  - `src/airalerts/text_features.py` combines a gazetteer, Ukrainian case forms, threat types and the `to_ns()` fix.
  - `scripts/05_text_lead_time.py` measures lead time: 32% of onsets have a mention in the preceding 30 min, against 18% of random moments.
- **Product:** a CLI only. `scripts/04_forecast_now.py` produces a forecast from the latest hour, and `reports/forecast_latest.csv` is committed.
- **Engineering:** `src` package, numbered scripts, one test file, figures; reproducible download.
- **Documentation:** `docs/experiment_log.md` records:
  - logistic regression losing to climatology beyond 1 h,
  - "regime" features overfitting,
  - lost scraper parts,
  - the unit bug.

  `docs/reflection.md` and an honest limitations section complete it.
- **Standout ideas:**
  - Quiet-origin scoring.
  - The climatology baseline.
  - Lead-time analysis.
  - Gazetteer-based region extraction.
  - The bootstrap significance test (`scripts/06_significance.py`).
- **Red flags:**
  - The state target makes h=1 skill mostly persistence (they say so).
  - Text covers only one year.
  - Telegram edits.
  - Only 4 commits, so the git history shows little process.
- **P 4 / T 5.**

### Dopplerr24/air-raid-alert-analysis (Oct 2026; 2 upload commits)

- **Framing:** P(a new alert starts within the next hour) for every region and hour. Built as a single-region MVP (Kyiv City) first, then a 24-region national panel.
- **Data:**
  - **Source:** the official file.
  - **Cleaning:**
    - About 114k exact duplicates are dropped.
    - Raion and hromada rows are rolled up, and intervals are merged per oblast ("any alert anywhere in the oblast").
    - Luhansk is excluded.
    - The grid stops at the last complete hour, and the latest event is 2026-09-07 (the freeze is acknowledged).
  - **Volunteer file deliberately rejected:** it disagrees on about 1/5 of Kyiv starts, and its naive ends are fabricated.
- **Target/horizon:** onset in [t, t+1 h); `--horizon` is configurable.
- **Methods:**
  - **Baselines:** global base rate, region base rate, raw and per-region-fitted persistence, hour-of-week climatology.
  - **Models:** LightGBM on own history only; global LightGBM with national features; optional `--adjacency` neighbour features.
- **Evaluation:**
  - **Protocol:** walk-forward, 5 × 90-day folds covering **2025-06-14→2026-09-07** (latest), with a 24 h embargo and one shared time cut.
  - **Metrics:** PR-AUC pooled and macro (per-region timing skill), and Brier skill against the region base rate.

    | Model | Pooled PR-AUC | Macro PR-AUC | Brier skill |
    |---|---|---|---|
    | Global LightGBM | 0.324 | 0.248 | 0.116 |
    | Fitted persistence | 0.282 | 0.148 | 0.041 |
    | Global + adjacency | 0.337 | 0.263 | 0.126 |

  - The global model beats the region base rate on Brier in 104 of 120 region-folds.
- **Leakage:**
  - `proj/features.py:_past()` shifts and raises an error on lag < 1 or on stacked (multi-index) input.
  - `check_causality` (noise after a cut) and `check_region_isolation` (rewrite one region and check the others are unchanged) run before any training, and abort it on failure.
  - Both checks were validated against planted bugs.
  - **Positive control:** feeding the current hour sends PR-AUC to 0.99.
  - Hyperparameters are fixed, not tuned.
- **Text/media:** none.
- **Product:** a CLI (`proj/main.py`), results CSVs and 3 EDA figures.
- **Engineering:**
  - Clean modules: everything fitted lives in `proj/model.py`.
  - `__pycache__` is committed, and the README references a missing `eda_visuals.py`.
  - Tests are embedded in the run rather than in a test suite.
- **Documentation:**
  - An excellent README with a **per-region calibration diagnosis**: western regions are over-forecast 2–3×, frontline regions are under-forecast by 20–40%. It is attributed to the raion switch.
  - It also covers degenerate onset in near-permanent regions (Dnipropetrovska is under alert >99% of the time).
  - **Missing:** no AI-usage section and no reflection in the repo, and only 2 upload commits.
- **Standout ideas:**
  - The region-isolation test (panel-bleed bug).
  - The fitted persistence baseline.
  - Pooled vs macro PR-AUC.
  - The calibration-by-region analysis.
- **Red flags:**
  - Miscalibration is documented but not fixed.
  - No confidence intervals.
  - The process is invisible in git.
- **P 4 / T 5.**

### tymof1j/ai-stage2 (Jun 2026; 11 commits on 06-25)

- **Framing:** a three-page "Air Alert Atlas":
  1. a daily oblast/raion archive map;
  2. a **"localisation effect"** counterfactual: the raion-hours of alert avoided by raion-level warnings versus an oblast-wide policy;
  3. a 1–6 h forecast of national alert-system load (the share of 120 raions under alert).
- **Data:**
  - **Source:** Vadimkin official, up to 2026-06-24 00:55 UTC.
  - **Processing:** interval unions per raion and per oblast (`src/intervals.py`, `src/analysis.py`), joined to OCHA COD-AB boundaries.
  - **Scope:** the forecast is restricted to the raion era (since 2025-12-01), and Crimea, Sevastopol and Luhansk are excluded from the denominator.
  - **Notes:** `air_alerts_data_research.md` records row counts and alerts.in.ua API limits.
- **Target/horizon:** the hourly share of raions under alert, h = 1..6.
- **Methods:** a dependency-free direct standardized ridge on autoregressive and calendar features. Baselines are persistence and seasonal.
- **Evaluation:**
  - **Split:** validation from 2026-04-24 (ridge alpha chosen there); **test 2026-05-24→06-23** (720 h).
  - **Results:** at h=1, MAE 0.0439 against 0.0581 for persistence (24% skill); at h=2, 0.060 against 0.073 (18%).
- **Leakage:** clean; the alpha is selected on validation.
- **Text/media:** none.
- **Product:** a Quarto site deployed to GitHub Pages (`.github/workflows/publish.yml`) with interactive maps and a calendar.
- **Engineering:** regression tests for the interval algebra, a Makefile, checksums and reproducible metadata.
- **Documentation:** a clear README covering deftech value and a methodology page. There is no AI section in the repo.
- **Standout ideas:**
  - Using a raion-level target after the switch.
  - The counterfactual "alert exposure saved" metric, a policy-evaluation angle unique in the batch (`src/analysis.py:counterfactual_savings`).
- **Red flags:**
  - Only a national aggregate is forecast.
  - A single 30-day test.
  - A static snapshot.
- **P 4 / T 4.**

### goodfrog33/air-raid-forecasting-ukraine (Jun 2026; 12 commits, 06-21 20:45 → 06-22 00:08)

- **Framing:** a "production-style platform" with four targets:
  - A: national hourly alert count
  - B: per-region P(any alert within 1/6/24 h)
  - C: duration
  - D: severity
- **Data:**
  - **Sources:** Vadimkin official + volunteer, with a SHA-256 download manifest. Data runs up to 2026-06-19 23:47 UTC.
  - **Cleaning** (`data/clean.py`, with a `CleaningReport` audit trail): raion and hromada rows are **merged into oblast intervals**; exact duplicates are removed; Luhansk and Crimea are excluded.
  - **Timezone:** UTC, with Kyiv time for calendar features.
- **Methods:**
  - **Baselines:** naive, seasonal naive, moving average, persistence, prior rate.
  - **Models:** ETS/SARIMA, Prophet, LSTM, RF, XGBoost, LightGBM and CatBoost.
  - **Production:** a global region model.
  - **Variants:** GDELT and Telegram (war_monitor, radar_raketaa).
- **Evaluation:**
  - **Protocol:** expanding-window rolling origin, 3 × 30-day folds placed **flush against the end of the data**.
  - **National count:** MAE 1.66 for CatBoost, 1.74 for the moving average, 2.27 for naive.
  - **Per-region P(any alert ≤ 6 h):** XGBoost ROC 0.915 (LogLoss 0.364), against 0.782 for persistence.
  - **News lift:** about −2% (reported honestly and kept optional).
- **Leakage:**
  - Features use only data up to t−1.
  - **Label bleed:** `gap_hours: 0` with 6–24 h forward targets leaks labels at fold boundaries.
  - **Selection on the test folds:** best-model auto-selection and a LightGBM search run on the same backtest folds.
  - **Target choice:** the target is *state* (`any_alert`), which persistence dominates.
  - **Empty holiday feature:** `holidays.country_holidays('UA')` without the martial-law categories, so the feature is likely all zeros.
- **Text/media:** GDELT timelinevol and Telegram post counts, both lagged one day, so safe. Coverage is shallow.
- **Product:**
  - A live Streamlit Community Cloud app with a choropleth and region/model/factor selectors.
  - FastAPI with `/predict` and `/predict_batch`.
  - Docker and a devcontainer.
- **Engineering:** src-layout package, typed YAML config, 6 test files and a Makefile. The 6 notebooks are about 1.5 KB stubs, and a 39 MB model bundle is committed.
- **Documentation:** a detailed README, `reports/final_report.md` and `REFLECTION.txt` (concrete failures: Python 3.14 wheels, a map winding-order bug, GDELT rate limits). There is no AI log in the repo.
- **Standout ideas:**
  - The interval-merge cleaner with an audit trail.
  - Placing backtest folds at the end of the data.
  - A one-click Streamlit Cloud deploy recipe.
- **Red flags:**
  - A model zoo (12+ models) with automatic selection on the evaluation folds.
  - The state target.
  - Stub notebooks.
  - An API "confidence" field with unclear meaning.
- **P 4 / T 4.**

### Nazar32/forecast-driven-route-selection (Oct 2026; 2 commits): **not a KSE submission**

This is the code for an IEEE Access paper (Melnyk & Pysarchuk) that turns hourly alert-probability forecasts into road-route choices. It is off-task for KSE but highly relevant and borrowable.

- **Forecast:** per-lead gradient-boosting models for 0–18 h, anchored to each unit's recent alert level and blended 50/50 with a **rolling 42-day Markov chain**. On their 2024 control, that chain *beat* the original ML.
- **Recalibration:** per-unit daily logit-offset recalibration, using only matured targets.
- **Data and truth:** raion-level truth for Mar–Sep 2026, from the official file deduplicated (113,845 rows removed).
- **Protocol:**
  - Pre-registered rounds in `results/p3v6/raion_exp/PREREG.md`.
  - Paired 3-day moving-block bootstrap.
  - A look-ahead "leaky" ablation (`results/p3v5/direct_probs_leaky.parquet`).
  - The final confirmation run only once.
- **P n/a / T 5.**

---

## Tier B: middle repos (medium cards)

### Freit007/air-alert-analytics (Jun; 2 commits)

- **Framing:** a descriptive Streamlit app covering frequency, Kaplan-Meier durations, heatmaps, co-occurrence and correlation, a choropleth with drill-down, and an **attack-wave replay**: a two-pointer sliding window finds bursts in which N or more oblasts alert, rendered as an animated map.
- **Data:** official file, done right.
  - All levels are unified into oblast episodes with interval merging.
  - Exact duplicates are dropped.
  - DST-aware timezone conversion; censoring flags; permanent regions excluded.
  - `scripts/cross_check.py` compares official against volunteer (ρ ≈ 0.92–0.96).
- **No forecast and no evaluation.**
- **Engineering:** 4 test files, including `tests/test_adversarial_data.py`.
- **Red flags:**
  - It calls alerts.in.ua the "Ukrainian government alert API… official state system"; it is a volunteer project.
  - The README quotes ρ inconsistently (0.92 vs 0.96).
  - Only 2 commits.
- **P 4 / T 3.** Shaped like the passer, with very solid data hygiene.

### Semfayni/Air-Raid-Analysis (Jun; 15 commits over about 4.5 h)

- **Framing:** a Streamlit dashboard with four parts:
  - historical overview and regional explorer;
  - a **live map from the alerts.in.ua token API** (`src/air_alerts/live_api.py`, mocked in tests);
  - an anomaly lab (transparent rolling score);
  - holiday proximity.
- **Data:** dedup plus oblast interval unions (`src/air_alerts/metrics.py`), Kyiv-date splitting, and unfinished alerts excluded.
- **Engineering:** 11 test files.
- **Documentation:** the reflection lists concrete bugs fixed (Streamlit route clash, `groupby.apply` dropping `region`).
- **Red flags:**
  - No forecasting.
  - `holidays.country_holidays('UA')` is called without martial-law categories; a manual important-dates list partly compensates.
- **P 4 / T 3.** The closest match in this batch to the confirmed passer.

### AnnaKiulafli/anna_kiulafli_kse_stage2_2026 (Jun; 27 commits, Codex PRs)

- **Framing:** deliberately stays inside the raion era: a national daily count of raion-level records, 2026-01-01→06-23.
- **Data:**
  - Exact dedup; UTC→Kyiv with complete-day logic (the partial day is excluded).
  - Intervals are split at midnight and overlaps merged per raion-day for minutes.
  - Non-raion rows are audited separately.
- **Methods:** baselines only (persistence, seasonal_7, trailing_mean_7).
- **Evaluation:** walk-forward over the last 35 days. trailing_mean_7 gets MAE 76.9, against 96.6 for persistence and 112.8 for seasonal_7.
- **Engineering:** 35 tests and a PR-review workflow.
- **Documentation:** `docs/SOURCE_AUDIT.md`, `docs/AI_ASSISTANCE_SUMMARY.md` and `REFLECTION.md`.
- **Red flags:**
  - The target counts fragmented raion records (one wave produces many records).
  - No model beyond baselines, and no product.
- **P 4 / T 3.**

### tannyaQ/ukraine-air-alerts-tsa (Jun; 2 commits)

- **Framing:** national daily alert counts from the volunteer file (Kyiv days), with STL decomposition and forecasting.
- **Evaluation:** walk-forward over **12 weekly folds** (h=7) covering the last 84 days to 2026-06-19, training from 2025-07-01. Mean MAE across folds: Holt 21.84, Holt-Winters 22.39, naive with drift 28.22, seasonal naive 31.69. A per-fold table is included.
- **Documentation:** a 105 KB AI log is in the repo (`AI_LOG_ukraine_air_alerts.md`), plus `reports/INSIGHTS.md`.
- **Red flags:**
  - The "4.4× rise / regime change July 2025" in volunteer counts may partly come from the keyword parser fragmenting raion messages: volunteer median duration falls over the same period. It was not checked against merged official episodes.
  - No product.
- **P 4 / T 3.**

### egorcusai/air-raid-alert-forecast (Jun; 10 commits in about 1 h)

- **Framing:** "Where are alerts predictable?" A per-region classifier for "a new alert begins within 3 h".
- **Data:** volunteer file.
- **Methods:** logistic regression and random forest, with and without neighbour features.
- **Evaluation:** a chronological 68/12/20 split, with the threshold tuned on validation (the fix for a test-set tuning leak they caught). Test ROC is 0.55–0.66 per region: Lviv and Zhytomyr are the most predictable, Kyiv City is near random.
- **Leakage:** `src/leakage_audit.py` checks byte-identical feature reconstruction after truncation, recomputes the target independently, and checks max |corr|.
- **Product:** a static `web/index.html` dashboard and an LLM interpretation layer (with fallback).
- **Documentation:** `submission/AI_LOG_HEADER.md` is a *reading guide* that points the reviewer to five iteration moments.
- **Red flags:**
  - No persistence or climatology baseline.
  - "Best-of (LR, RF)" is reported on test.
  - ECE ≈ 0.25 (admitted).
- **P 4 / T 3.**

### Petit925/kse-air-raids-forecast (Jun; 6 commits)

- **Framing:** daily alert counts (volunteer, Kyiv days) for Kyiv City and Dnipropetrovska.
- **Methods:** seasonal-naive(7) against Prophet.
- **Evaluation:** a 14-day holdout ending 2026-06-21. MAE is 1.20 against 1.71 for Kyiv, and 2.94 against 3.64 for Dnipro (SMAPE also reported).
- **Product:** a decision layer, `src/scheduler.py`, picks the 9-hour work block that minimises expected alerts under a curfew. It ships as Streamlit plus a zero-install `report.html`.
- **AI log:** 275 KB, but only 11 user prompts, mostly feature requests; little challenge of the model.
- **Red flags:**
  - A single 14-day window.
  - The hourly profile used by the scheduler is computed from the full history.
  - Prophet parameters are not justified.
- **P 3 / T 3.**

### kervad28-debug/air-raid-alert-next-day-prediction (Jun; 13 commits, notebook)

- **Framing:** next-day occurrence for Khmelnytska oblast.
- **Data:** a volunteer snapshot with SHA-256 in the README.
- **Methods:** a frozen 12-feature logistic regression against persistence.
- **Evaluation:** the test (2025-10-30→2026-06-23) was evaluated once. LR ROC is 0.498; F1 is 0.28 against 0.38 for persistence. It is reported as negative.
- **Documentation:** it **discloses an accidental peek at the test class balance**.
- **Red flags:**
  - The committed snapshot is 2 bytes (empty).
  - Notebook only.
  - The region was chosen with full-period class balance.
- **P 3 / T 3.**

### gbatulin/kse_summer (Jun; 15 commits)

- **Framing:** 5/15/30-min onset prediction for 6 chosen oblasts (2 high, 2 mid and 2 low activity).
- **Methods:**
  - LightGBM on a 5-minute grid, with oblast state = any level.
  - "As-of" experiments (2023-03, 2024-01, 2025-07), each with a strict data-end cutoff, embargo and `no_future_audit.json`.
  - Threshold and calibration set on dev only; PSI checks.
- **Evaluation:** test (as-of 2025-07) PR-AUC is 0.032, 0.076 and 0.132 against base rates of 0.007, 0.022 and 0.042 (ROC 0.74–0.77).
- **Documentation:** a human-written README with candid critique ("I don't understand these metrics", a QC flaw on implicit negatives), and GPT-5.5 / Codex logs in `prediction/ai_logs/`.
- **Red flags:**
  - **The latest test is July 2025 even though data runs to June 2026.**
  - The design was delegated to AI.
  - `.pyc` files are committed.
- **P 3 / T 3.**

### asobkiv/air-raid-analytics (Jun; 10 commits)

- **Framing:** national daily counts and a "spread index", with an adjacency-based spread probability.
- **Methods:** SARIMA(1,1,1)(1,1,1,7) and Prophet; spread probability scored by Brier; PELT changepoints; KM survival.
- **Evaluation:** rolling origin with about 15 origins and a 30-day horizon, scored by MASE.
- **Data:** official file at a pinned commit, with level roll-up and interval merge.
- **Process:** a variant loop (`src/air_raid/optimize.py` + `variants.yaml` + leaderboard) overturned their own changepoint idea.
- **Engineering:** 9 test files.
- **Red flags:**
  - The "champion" is picked on the "frozen test origins", which is selection on test.
  - No results are committed.
  - Gaussian models on counts.
- **P 3 / T 3.**

### timkaster/AirAlerts (Jun; 15 commits)

- **Framing:** daily alert hours per location, built on the author's own parser of the official @air_alert_ua channel.
- **Data:** a Telegram Desktop export of the channel (`scripts/build_alert_dataset.py`): 314k location events become 157k paired intervals, with 580 unmatched.
- **Enrichment:** Open-Meteo weather, Nominatim geocoding and a Tkinter app.
- **Methods:** a linear model of same-day alert hours for the top 40 locations.
- **Evaluation:** test 2025-12-23→2026-06-20, MAE 3.10 h/day. Permutation importance shows the 7-day mean dominates weather.
- **Documentation:** `RESEARCH_LOG.md` has a per-entry AI-assistance note.
- **Red flags:**
  - Same-day *observed* weather is used as a feature.
  - The only baseline is "simple average".
  - The data archive is hosted off GitHub.
- **P 3 / T 3.**

### alinasamoilenko292/KSE-AI-Agentic-Summer-School (Jun; 1 commit)

- **Framing:** the national breadth series (oblasts under alert per day).
- **Data:** correct day-splitting and per-oblast-day interval merging.
- **Methods:**
  - Hypothesis tests with effect sizes.
  - A weekly-only Prophet. Its CV runs over the whole history (initial 365 d, period 90 d, horizon 30 d): MAE 4.45 against 4.89 for naive, with 91% coverage.
  - k-means clusters.
- **Documentation:** `LIMITATIONS.md` and `docs/problem_framing.md`.
- **Red flags:**
  - CV is not focused on the latest period, and the configuration was chosen on the same CV.
  - The weekday×hour heatmap is in UTC.
  - A single commit.
- **P 3 / T 3.**

### karavaievg/KSE-AI-Agentic-Summer-School- (Jun; 3 commits, last on 07-07)

- **Framing:** a "downtime index" Streamlit dashboard. Merged oblast intervals (all levels rolled up, overlaps merged, rows over 24 h dropped) are overlaid on a user-defined work schedule to give lost hours, person-hours, cost and availability.
- **No forecast.**
- **Red flags:**
  - No AI log.
  - `.pyc` files committed.
  - The last commit is after the deadline.
- **P 3 / T 3.**

### ZahBoy/ukrainian-air-alarm-data (Jun; 2 commits)

- **Framing:** descriptive "case studies" from Sep 2023 to Jun 2026:
  - MSTL decomposition and a GARCH "uncertainty index";
  - a Markov transition matrix;
  - holiday effects;
  - Shahed wave propagation (median about 3 h to Kyiv);
  - manual CUSUM/Welch changepoints.
- **Data:** threat-type labels come from Telegram dumps (monitor, regional ОВА/OVA (regional military administrations), Suspilne), classified per alert by DeepSeek (`scripts/final_deepseek_parsing.py`, up to 8 messages per alert).
- **Documentation:** the reflection shows physical sanity checks (missile vs drone propagation).
- **Red flags:**
  - No forecast evaluation.
  - The holiday claims (+5.7% / −12–16%) have no significance tests.
  - The LLM labels are not validated.
  - Over 70 MB of raw dumps are committed.
- **P 3 / T 3.**

### mashta-lilia/S.T.A.L.K.E.R.--- (Jun; 2 commits)

- **Framing:** 7-day daily counts for 3 macro-zones.
- **Methods:** SARIMA, Prophet and naive moving average, compared with walk-forward CV (100-day train, 7-day horizon, 4 folds, 1-day embargo). A low-information router uses Syntetos–Boylan.
- **Evaluation:** CV MAE (from the log) is 16.96, 4.96 and 2.73 across the three zones.
- **Documentation:** Claude and Gemini logs are in the repo; the limitations are honest (hromada count inflation, an ACF test on the full series).
- **Red flags:**
  - No dedup and no interval merge.
  - The pipeline can silently fall back to **synthetic** data.
  - Selection MAE equals reported MAE.
- **P 3 / T 2.**

### Shenshyn/Air-Alerts (Jun; 6 commits)

- **Framing:** survival analysis of alert duration.
- **Methods:** KM, Cox PH and XGBoost `survival:cox`, with a sweep-line concurrency feature.
- **Data:** dedup reports 41.7% duplicates.
- **Evaluation:** C-index 0.640 (XGBoost) and 0.637 (Cox) against 0.552 for KM; MAE about 84 min.
- **Documentation:** the full chat history and audit reports are included.
- **Red flags:**
  - It **filters to `level=='oblast'`**.
  - A "stratified chronological split" per region gives each region a different test window: not the latest period, and with cross-region temporal leakage.
- **P 3 / T 2.**

### Yaroo-a/ukrainian-air-raid-sirens-analysis (Oct; 8 commits)

- **Framing:** onset within the next hour, forecast from calm hours only.
- **Methods and process:**
  - LR and LightGBM, each with and without spatial lags.
  - Clustering fitted on train only; F2 thresholds chosen on validation; bootstrap CIs.
  - `tests/test_leakage_invariance.py`.
  - An adaptive 14-day baseline.
  - A commit titled "address all 8 review points".
- **Evaluation:** test Jun 2025→Sep 2026. LightGBM with spatial features gets PR-AUC 0.238 against 0.221 for the adaptive baseline, but the baseline wins on Brier (0.0189 vs 0.0203).
- **Critical flaw:** `src/data/cleaner.py` keeps only `level=='oblast'` and never deduplicates. The whole test period sits in the raion era, so the target is built on collapsing oblast rows, and the EDA counts (for example "92–94 alerts/day") include duplicates.
- **P 3 / T 2.**

### nazariidatsenko25-png/ukraine-air-raid-analysis (Jun; 23 commits)

- **Framing:** a Next.js, FastAPI and Docker dashboard with EDA, a cascade P(B | A within N h), GaussianHMM regimes and a 14-day Prophet forecast.
- **Data:** volunteer file (a deliberate choice); naive ends are imputed with a per-region log-normal model.
- **AI log:** `CONVERSATION.md` (1.1 MB).
- **Red flags:**
  - **No backtest or metrics at all.**
  - The "Hawkes" in the README is empirical conditional frequencies (the code itself calls it a "simplified" Hawkes).
  - The commits are dominated by UI polish.
- **P 3 / T 2.**

### tanchikr12/air-alert-analytics (Jun; 8 commits)

- **Framing:** a Streamlit app with three modes: a 30-day "forecast", a historical fact-check and the busiest days.
- **Methods:** HistGBM on an oblast×hour state grid, with ROC ≈ 0.90 on the last 20%.
- **Product:** a Loom video.
- **Red flags:**
  - At forecast time, the `recent_*` features are replaced by monthly averages, so the reported ROC does not describe the deployed forecast.
  - A `year` feature.
  - No baseline.
  - `.pyc` files committed.
- **P 3 / T 2.**

### Heir-of-God/AlerticUA (Jun; 17 commits)

- **Framing:** a 5-tab Dash dashboard with a Prophet 14-day forecast and a date-picker cutoff for visual comparison; no metrics.
- **Red flags:** `filter_oblast_level` empties the raion era, and there is no dedup.
- **P 3 / T 2.** Passer-like in shape, but its data is broken.

### Nzrch/ukraine-air-raid-analysis (Jun; 4 commits)

- **Framing:** a Flask dashboard with an Isolation Forest anomaly view and a 14-day trend forecast (unevaluated).
- **Data:** optional Telethon @kpszsu and Wikipedia collectors. The raion era is handled by clustering starts within 10 minutes.
- **Red flags:**
  - A **fixed UTC+3 offset** (wrong in winter).
  - Dedup by rounding.
  - A sample-data generator.
- **P 3 / T 2.**

### Lahodzinskyi/air-rapid (Jun; 1 commit)

- **Framing:** a local web app (Python server plus JavaScript):
  - official/volunteer switch and raion filters;
  - a national interval merge for durations;
  - weather, moon phases and lagged inter-oblast correlations;
  - oblast→raion transition tables.
- **Engineering:** 4 test files.
- **Red flags:**
  - No exact-duplicate removal, so counts are doubled for the duplicated rows.
  - A single commit.
- **P 3 / T 2.**

---

## Tier C: weak repos (terse)

- **sergkern1-netizen/air-raid-alerts-analysis** (70 commits):
  - **Method:** Prophet, ETS and LSTM on national daily *summed alert minutes*. The Vadimkin and Kaggle-dimakyn files are concatenated, with dedup only on `timestamp`. A 70/30 split gives a 469-day multi-step test with MAPE 75–91%.
  - **Red flags:** it reads the raion fragmentation as "3× escalation". It claims "Production Ready". The README links the wrong Vadimkin repo (power outages), and the AI log mixes in an unrelated project.
  - **P 2 / T 2.**
- **mokliak/ksestagetwomokliak** (10 commits):
  - **Method:** RF and LR on a daily oblast panel built from the official file (2025 onward, no dedup, all levels counted). Features include observed archive weather and **same-day** NewsAPI headlines scored by Gemini.
  - **Invalid CV:** `TimeSeriesSplit` runs over rows sorted by oblast, not time, and the top-12 RF features are selected on all data.
  - **Product:** a dashboard plus a video.
  - **P 2 / T 2.**
- **YaroslavKheilyk/Time-Series-Analysis-of-Air-Raid-Alerts-in-Ukraine** (4 commits): baselines only (seasonal naive at lag 24, hour-of-week risk), with a chronological split and no committed results. The "chat logs" cover a GitHub account migration, not the project. **P 2 / T 2.**
- **monsterkokoko/ukraine-air-alerts-timeseries** (1 commit): oblast filter, dedup and Kyiv timezone. They saw the late-2025 collapse and **cut the data at 2025-09-01**, so the 30-day test ends in Aug 2025. 7-day MA RMSE is about 17, against 25 for naive. **P 2 / T 2.**
- **Vlad1343/ukraine-air-alerts-timeseries** (1 commit): the same pattern. Oblast filter and dedup; the raion switch is read as "data feed breaking" and the data truncated at 2025-10-31. Honestly concludes it can't beat a flat line. **P 2 / T 2.**
- **abricos69/TimeSeriesAnalysisUkraine** (1 commit): volunteer daily counts, STL, and SARIMA(2,1,2)(1,0,1,7) with MAE 18.9 against 18.6 for naive. The README says "Stage 1". **P 2 / T 2.**
- **CPTshkarpetka/ukraine-alerts** (1 commit): a Streamlit map of hour-of-day empirical probability. It filters to `level=='oblast'` with a default range of 2025-01-01→now, so 2026 is nearly empty. No forecast. **P 2 / T 2.**
- **iamanavor-droid/AirRaid** (2 commits): runs on **synthetic** alerts and ACLED data by default (stated openly). Persistence against RF/GBM on a planted signal; nothing about the real world. **P 1 / T 2.**
- **Solomiia27/AirAlertsAnalyzer** (1 commit): **mock data** "based on real patterns", with `get-pip.py` committed. **P 1 / T 1.**
- **3olena3/air-raid-alerts-forecast** (Oct; 4 commits):
  - **Method:** CatBoost daily count and duration in a Gradio app. `GITHUB_RAW_URL` is a placeholder (`username/repository`), so it does not run.
  - **Data:** no dedup, all levels counted, dates in UTC.
  - **Unsupported claims:** the README gives metric *ranges* that no code produces.
  - **P 1 / T 1.**

---

## Top picks in this batch (what to borrow)

1. **Ddrakkx/alerts-forecast**, for evaluation protocol and process artefacts.
   - `src/alerts_forecast/leakage.py` + `tests/test_leakage.py`: the truncation test (cut at t, hide later ends, require identical features). Includes adversarial moments and a planted-leak check.
   - `src/alerts_forecast/baselines.py`: the `recent_level` baseline (3/7/14/30-day rate, refit daily) and "alert ended within H" persistence. These are the baselines to beat.
   - `src/alerts_forecast/walkforward.py` + `experiment.py`: purged validation and test blocks, per-family grids, selection by validation Brier, and the **strict reference** (the best baseline config on test) beside the no-hindsight one.
   - `src/alerts_forecast/metrics.py`: paired ISO-week block bootstrap.
   - `docs/decisions.md`: a decision log with retractions, the external-review fixes, and **pre-registration** of a holdout on the next data snapshot (`scripts/run_holdout.py`, git tag `holdout-freeze`).
   - `demo/live_forecast.py` + `demo/live/forecasts.jsonl`: pre-registered live forecasts as a real out-of-sample record. `demo/emap_logger.py` collects yellow/red levels.
2. **robotheist/Air-alerts-forecast**, for text data and honest skill accounting.
   - `scripts/00_scrape_telegram.py` / `scripts/browser_scraper.js` / `scripts/00_merge_browser_parts.py`: @kpszsu collection from `t.me/s`, with post-ID gap checks.
   - `src/airalerts/text_features.py`: KATOTTG gazetteer region extraction with Ukrainian case forms, threat types, and the `to_ns()` timestamp-unit fix.
   - `tests/test_leakage.py::test_text_features_do_not_see_the_future`.
   - `scripts/05_text_lead_time.py`: does the channel speak before the siren?
   - `scripts/06_significance.py`: day-block bootstrap for v3 vs v2.
   - `reports/metrics/test_scores_quiet_origins.csv`: separate scoring for quiet origins.
   - The 28-day hour-of-day **climatology** baseline (`src/airalerts/models.py`).
   - `docs/experiment_log.md` as a model of a "what failed" log.
3. **Dopplerr24/air-raid-alert-analysis**, for panel leakage guards and baselines.
   - `proj/features.py:_past`: shift with guards that raise on lag < 1 or stacked input.
   - `proj/features.py:check_causality` and `check_region_isolation`, run before training.
   - `proj/model.py`: `walk_forward_splits` (shared cut, 24 h embargo, asserted gap) plus `PersistenceModel` (fitted per region) and `HourOfWeekClimatology`.
   - `proj/data_loader.py:merge_intervals`, `to_hourly` (grid stops at the last complete hour).
   - README "Limitations": the per-region calibration diagnosis tied to the raion switch, and degenerate onset in near-permanent regions.
4. **AndriyTkh/kse-summer-sch**, for making the AI process legible.
   - `scripts/export_sessions.py` → `_sessions/INDEX.md`: transcripts ranked by human-typed characters, with curated `_sessions/important/`.
   - `claude/pr-writedown/2026-06-21_phase4-recency-pruning-onset-pivot.md`: GOOD/BAD decisions and the "hollow headline" catch that drove the pivot from *whether* to *onset*.
   - `src/loaders.py:load_alerts`: the docstring explaining *why* to roll all levels up to oblast.
   - `src/model_onset.py`: the quiet-state onset target.
   - `src/drift.py` (PSI) and the idea behind `src/operational_eval.py` (backtest vs data vintage). Don't copy its Kaggle feature timing.
5. **tymof1j/ai-stage2**, for the raion-era target and a policy framing.
   - `src/intervals.py` + `tests/test_intervals.py`: interval union and hour allocation.
   - `src/analysis.py:build_raion_unions`, `counterfactual_savings`: the "alert exposure avoided by localisation" metric.
   - `src/forecast.py`: dependency-free direct ridge for raion-share load, with persistence/seasonal baselines and validation-selected alpha.
   - `.github/workflows/publish.yml` + `*.qmd`: a Quarto site on GitHub Pages.
6. **goodfrog33/air-raid-forecasting-ukraine**, for product and data cleaning.
   - `src/air_raid_forecasting/data/clean.py`: oblast interval consolidation with a `CleaningReport` audit.
   - `src/air_raid_forecasting/evaluation/backtest.py:make_folds`: the last fold sits flush against the end of the data.
   - `src/air_raid_forecasting/service/` (FastAPI) + `dashboard/streamlit_app.py`: a Streamlit Community Cloud deploy recipe.
   - `REFLECTION.txt`: a concrete ~100-word reflection.
7. **Semfayni/Air-Raid-Analysis + Freit007/air-alert-analytics**, as passer-shaped references.
   - Semfayni `src/air_alerts/live_api.py`: a token-safe alerts.in.ua live client, tested with mocks.
   - Semfayni `src/air_alerts/metrics.py`: dedup, merge and Kyiv-day split.
   - Freit007 `scripts/cross_check.py`: official vs volunteer.
   - Freit007 `src/analysis/correlation.py`: attack-wave detection with a two-pointer window.
   - Freit007 `tests/test_adversarial_data.py`.
8. **Nazar32/forecast-driven-route-selection** (not KSE, but the most transferable modelling idea).
   - A rolling 42-day **Markov-chain baseline**, which beat their ML on 2024.
   - Anchoring and blending ML with it.
   - Per-unit daily logit recalibration.
   - `results/p3v6/raion_exp/PREREG.md`: round-by-round pre-registration.
   - A "leaky" look-ahead ablation as a positive control.

Smaller items worth stealing:

- **egorcusai** `submission/AI_LOG_HEADER.md`: a reading guide that points reviewers to the iteration moments in the AI log.
- **Petit925** `src/scheduler.py`: turns a forecast into a decision (the work window under curfew).
- **kervad28** README "Test-set disclosure": a section for an accidental test peek.
- **ZahBoy** `scripts/final_deepseek_parsing.py`: LLM threat-type labels for alert episodes from monitoring channels.
- **timkaster** `scripts/build_alert_dataset.py`: rebuilds alerts directly from an @air_alert_ua export.
- **AnnaKiulafli**: the complete-day logic and the PR-based Codex review workflow.

## Common mistakes seen

1. **Filtering the official file to `level=='oblast'`.** This empties the post-Dec-2025 period.
   - Seen in Yaroo-a (the whole test set sits on it), Heir-of-God, CPTshkarpetka (default range 2025→now) and Shenshyn.
   - monsterkokoko and Vlad1343 noticed the collapse but *truncated the data* to Aug/Oct 2025, giving up the latest period. Vlad1343 called it "a data feed breaking".
2. **Counting raw rows instead of merged episodes.**
   - sergkern1 read the raion fragmentation as "3× escalation".
   - mokliak, mashta-lilia (acknowledged), 3olena3 and Lahodzinskyi count raw rows.
   - AnnaKiulafli's target counts fragmented raion records.
   - Nzrch approximates episodes with 10-minute start clustering.
3. **Not removing the ~38% exact duplicates.** Seen in mokliak, mashta-lilia, 3olena3, Yaroo-a, Heir-of-God and Lahodzinskyi; sergkern1 dedups only on `timestamp`. (Repos that build an "any alert active" state grid are immune.)
4. **High scores from a persistence-dominated "alert active in window" target.**
   - goodfrog33 (ROC 0.915 vs 0.78 for persistence) and tanchikr12 (ROC 0.90).
   - AndriyTkh's first model had the same problem; they recognised it and pivoted.
   - Good fixes: onset from a quiet state (Ddrakkx, Dopplerr24, Yaroo-a) or separate quiet-origin scoring (robotheist).
5. **Selection or tuning on the evaluation window.**
   - asobkiv: champion picked on "frozen test" origins.
   - goodfrog33: auto best-model and hyperparameter search on the backtest folds.
   - AndriyTkh: grid clamp and pruning chosen on the 8-week test.
   - egorcusai: best-of LR/RF on test.
   - mashta-lilia: selection MAE equals reported MAE.
   - mokliak: feature selection on all data.
   - alinasamoilenko: Prophet configuration chosen on the same CV.
6. **Invalid splits.**
   - mokliak: `TimeSeriesSplit` over rows sorted by oblast.
   - Shenshyn: per-region 80/20, so test windows differ by region.
   - sergkern1: one origin with a 469-day multi-step forecast.
   - goodfrog33: `gap_hours: 0` with 6–24 h targets.
7. **Exogenous data aligned on event time, not availability time.**
   - AndriyTkh: Kaggle missile waves at the window start and at 00:00 for date-only rows, against publication around 09:20 Kyiv.
   - mokliak: observed archive weather plus same-day NewsAPI + Gemini.
   - timkaster: same-day observed weather for a same-day target.
8. **Synthetic or mock data.**
   - Solomiia27 and iamanavor-droid use it outright.
   - mashta-lilia has a silent synthetic fallback.
   - Nzrch ships a sample-data generator.
9. **Timezone slips.**
   - Nzrch: a fixed UTC+3 offset (wrong in winter).
   - sergkern1: timezone stripped, so days are UTC days.
   - 3olena3: UTC dates.
   - alinasamoilenko: weekday×hour heatmap in UTC.
10. **Not evaluating on the latest period.**
    - gbatulin: latest test July 2025.
    - Shenshyn: per-region splits.
    - monsterkokoko and Vlad1343: truncated data.
    - alinasamoilenko: whole-history CV.
    - nazariidatsenko and Heir-of-God: no metrics at all.
11. **Empty holiday features.** `holidays.country_holidays('UA')` without `categories=('public','workday')` returns no holidays under martial law. Seen in goodfrog33 and Semfayni.
12. **Missing or weak baselines.**
    - sergkern1, mokliak, tanchikr12, egorcusai and 3olena3 have none.
    - timkaster's only baseline is "simple average".
    - AndriyTkh uses only Prophet.
13. **Overclaiming.**
    - sergkern1: "Production Ready".
    - 3olena3: README metrics that no code computes.
    - ZahBoy: "Holiday terror" percentages without tests.
    - Freit007: calls alerts.in.ua the "official state system".
    - goodfrog33: an unexplained API "confidence" field.

## Gaps nobody in this batch addressed

1. **Bridging the official file's 2026-09-07 freeze.**
   - The October repos either stop at the freeze (Dopplerr24, Yaroo-a) or switch to the volunteer file (Ddrakkx, robotheist).
   - Nobody stitched in the alerts.in.ua `month_ago` history, the JustJimer archive, the ukrainealarm / map ranged history, or Kyiv Digital as a cross-check.
2. **Yellow/red levels and threat types (from 2026-09-07).**
   - Only Ddrakkx starts *logging* levels for later use.
   - Nobody evaluated the post-reform regime separately or used alerts.in.ua `alert_level` or `threats[]`.
3. **Raion-level forecasting.**
   - Only tymof1j forecasts in the raion era, and only as a national load share.
   - Nobody forecasts per raion or hromada in the KSE set (Nazar32 does, but it is not a submission).
4. **Publication-time alignment of exogenous sources.**
   - Nobody used availability time: the Kaggle missile dataset around 09:20 Kyiv the next day, ISW on D+1, or Telegram `edit_date` filtering.
   - robotheist only notes the edit problem.
5. **Archived weather *forecasts*.** Everyone who used weather used observed or archive values; nobody used the Open-Meteo Previous Runs API.
6. **Real-time data vintage.**
   - Vadimkin rows appear only after an alert ends plus a daily batch.
   - Only Ddrakkx (a snapshot comparison is planned) and AndriyTkh (the idea only) consider it.
   - Nobody backtests against historical git snapshots of the dataset.
7. **Official-file artefacts.**
   - Nobody flagged the synthetic +1 h closes (about 360 rows).
   - Nobody flagged the months-long standing frontline hromada alerts. AnnaKiulafli saw identical totals across Donetsk raions without explaining them; Dopplerr24 only notes degenerate onset at oblast level.
8. **Per-region recalibration under drift.** Dopplerr24 diagnoses it, but nobody in the KSE set recalibrates by region or regime. Nazar32's daily logit offset is the template.
9. **Strong simple time-series baselines.** Nobody in the KSE set compares against a **rolling Markov chain** or a semi-Markov on/off model. Ddrakkx's `recent_level` is the closest.
10. **Decision-oriented evaluation.** Petit925 (shift scheduler), karavaievg (downtime cost) and tymof1j (exposure saved) frame decisions, but none *backtests* forecast-driven decisions against a baseline policy.
11. **Martial-law holiday calendar.** No repo uses the `workday` category, so every holiday feature is silently near-empty.

---

## Batch 3 review: 38 repos

Scope: every repo in `batch3.txt`, reviewed from the local clones. No repo code was executed. Ratings run 1–5:
- **LP** = "likely passed" against KSE's criteria. The AI log is unseen, and the known passer is modest.
- **Tech** = technical quality.

## Calibration notes

- **The known passer (tbaraniuk) is in this batch.**
  - Its submitted demo data is the stale Kaggle `cashncarry` CSV, which ends **2022-10-15**. I checked `data/full_data.csv`.
  - It has no forecasting and no evaluation.
  - What it does have: a clean, rate-limit-aware alerts.in.ua ingester (pydantic, tenacity, DuckDB upsert), correct UTC→Kyiv SQL and an honest "known limitation" note.
  - So the repo alone clearly did not decide the outcome. LP below weights visible process evidence heavily: logs, reflections, caught errors, experiment logs.
- **Facts I verified on the local official CSV** (`dl_vadimkin/official_data_en.csv`), useful for judging everyone:
  - **Duplicates:** 113,740 unique rows appear exactly twice, all with `started_at` before 2026-01-25 13:12 UTC. After that date rows appear once (105 exceptions). So "every record before 2026-01-25 is doubled" is accurate. orestes-d diagnosed it exactly.
  - **Oblast-level rows:** the last oblast-level row per oblast, excluding Kyiv City, falls between 2025-08-20 (Khmelnytska) and 2025-11-04. After that, `level=='oblast'` rows are effectively only **Kyiv City**. The `level=='oblast'` filter therefore deletes every oblast except Kyiv for 2026.
  - **koalla05's split:** its README count of 65,172 oblast-level episodes reproduces exactly. Its 80/20 split therefore starts **2025-01-13**, and 2026 contributes only 445 episodes, all Kyiv City.
- **Deadline caveat.** Hroback's AI log quotes the deadline as "June 21, 2026, 23:59 EEST". Of the June-cohort repos, 16 have their first commit on June 23–30, among them slobodskyi, iuad0qll, nitatsuu, colobocman and spok.
  - Either deadlines varied, or these repos were published after submission.
  - I did not penalise this, but commit dates can't be used as a lateness signal without the real deadline.

## Summary table (sorted by LP, then Tech)

| # | Repo | Cohort | LP | Tech | One-line verdict |
|---|---|---|:-:|:-:|---|
| 1 | lbgos/AirAlerts | Oct | 5 | 5 | Live Telegram nowcaster on a 5-min grid; purged splits, separate dev and final windows, ablations, conservative calibration, live scoring |
| 2 | spryima/kse-air-raid-predictability | Jun | 5 | 5 | Auditable research baseline: pinned data, union onsets, 12 purged monthly folds, between-vs-within diagnostic, exemplary decision log |
| 3 | tbaraniuk/air_alert_analysis | Jun | 5 (confirmed) | 2 | The known passer: Dash, DuckDB and live alerts.in.ua ingester; 2022 Kaggle demo data; no forecasting |
| 4 | olehm208/air_alert_ai_analysis | Oct | 4 | 4 | Leakage-aware walk-forward (label maturation, validation-only selection) plus perturbation leakage tests; thin README |
| 5 | umunevich/air-raid-alerts-analysis | Jun | 4 | 4 | Requirements-first package; 1–24h exposure target, persistence baseline, validation calibration; public Cursor log |
| 6 | iuad0qll/KSE_analytics | Jun | 4 | 4 | Union-based minutes-under-alert, overcount quantified, leak-free Holt-Winters, Hawkes with goodness-of-fit; one commit |
| 7 | nitatsuu/Kizashi | Jun | 4 | 3 | Kharkiv next-hour LightGBM; caught an off-by-one in its persistence baseline; test set is Jan–Jul 2025, not the latest period |
| 8 | slobodskyi/tsa-air-raid | Jun | 3 | 4 | Best union/cleaning method in batch, honest forecasting with bootstrap CI; single commit, no process trace |
| 9 | petroltradesupply-dotcom/time-series-air-raid-alerts-ua | Jun | 3 | 3 | Vadimkin history spliced with alerts.in.ua month and cross-checked; measured the granularity jump; 14-day holdout |
| 10 | alitskevych/air-raid-ts | Jun | 3 | 3 | Volunteer daily counts; SARIMA vs seasonal-naive over 6 walk-forward folds in the latest 6 months |
| 11 | aleksey1chern/spok | Jun | 3 | 3 | Kyiv "smart all-clear" product with a re-strike survival backtest (in-sample); strong reflection |
| 12 | denkor1015-debug/Air-alerts-analysis | Jun | 3 | 3 | Correct raion-shift diagnosis but cut at 2025-07-31; 31-fold walk-forward over six models |
| 13 | HadyBytes/Air-raid-alerts-in-Ukraine-Analysis | Jun | 3 | 3 | Descriptive HTML report with a raion-quorum rollup and independent per-minute re-derivation; no forecasting |
| 14 | andrii-kondratok/ukrainian-air-raid-analysis | Jun | 3 | 3 | Precursors of mass attacks against external ground truth (piterfm); AUC 0.63 from random CV; cut at Nov 2025 |
| 15 | dukarev/ukraine-air-alerts-analysis | Jun | 3 | 3 | TDD and mutation testing on an anomaly detector; accepted a hallucinated "official feed died" diagnosis |
| 16 | orestes-d/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine | Jun | 3 | 3 | Single-file union dashboard; exact duplicate-structure diagnosis; descriptive only |
| 17 | KrafterDen/Alerts-Analysis | Jun | 3 | 2 | Big Streamlit app with symbolic-date windows; no union; 60-day baselines; no reported metrics |
| 18 | borovkov-d/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine | Jun | 3 | 2 | Honest backtest refutes a single-split win; but oblast filter plus "collection stopped" misdiagnosis |
| 19 | kowalsking/time-series-analysis | Jun | 3 | 2 | 2022 Kaggle plus API-month dashboard, deployed; good reflection; weak data and evaluation |
| 20 | mariiaikonnikova6-rgb/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine | Jun | 2 | 3 | Kyiv daily duration: ARIMA, SARIMA and Ridge vs seasonal-naive; cut at 2025-11-30; LFS-pointer data |
| 21 | koalla05/air-alerts | Oct | 2 | 2 | Nice survival framing, but the oblast filter leaves 2026 almost empty; no reported metrics |
| 22 | colobocman/airalert-planner | Jun | 2 | 2 | Excellent agentic process (reviewer agents, PR reviews) but **synthetic data only** |
| 23 | Mafusail2020/air-alerts-analysis | Jun | 2 | 2 | Union-merged dashboard with live status; the predictor has zero evaluation; heatmap uses fixed UTC+2 |
| 24 | zadorozhna-dariia/AI_Agentic_school_stage_2 | Jun | 2 | 2 | Honest "forecasting fails" verdict, but misdiagnosed feed collapse and cut at 2025-10-31 |
| 25 | arborfam/ukraine-air-raid-analysis-for-KSE | Jun | 2 | 2 | Descriptive plus Prophet (r≈0.1); raion cutover undercounts the transition; README/repo mismatch |
| 26 | volodymyrfrydel-bit/ukraine-air-raid-timeseries | Jun | 2 | 2 | Deployed Streamlit; Prophet with no naive baseline; UTC hours |
| 27 | yaroslavopanasenko25-eng/Yaroslav_AI_Agentic | Jun | 2 | 2 | Full-stack app with LLM (Grok) "forecasting" and RAG; no evaluation |
| 28 | HATSKER-228/time-series-analysis-of-air-raid-alerts-in-Ukraine | Jun | 2 | 2 | EDA plus source comparison; fixed UTC+2 "as the user requested" |
| 29 | whylineee/ukraine-air-raid-alerts-analysis | Jun | 2 | 2 | Clean EDA package (volunteer data, STL); no forecasting or evaluation |
| 30 | MrmaderatorYT/air-raid-alerts-analysis | Jun | 2 | 2 | Eight-city EDA plus ARIMA/HW/Prophet with negative R²; README text not checked against the code |
| 31 | PrepAIre-edu/-TSAofAirRaidAlerts | Jun | 2 | 2 | Monolithic script; oblast filter; data truncated to fit GitHub |
| 32 | Hroback/KSE | Jun | 2 | 1 | `src/` package missing, so `main.py` cannot run; claims unverifiable |
| 33 | oleksandrsafandulaKSE/AirAlerts-TimeSeries-Analysis-Ukraine | Jun | 1 | 2 | LightGBM with early stopping on the test fold; README is a single link |
| 34 | bratxja-cmd/hromady-alarms | Jun | 1 | 2 | Not a TSA submission; useful daily GitHub-Actions alerts.in.ua collector |
| 35 | MaksimPrykhodko/Ukraine-air-raid-prediction | Jun | 1 | 1 | "100% precision" comes from a target leak in `hours_since_last_alert` |
| 36 | sergii-brt/KSE_alert_analysis | Jun | 1 | 1 | Unverified "sirens.in.ua" API with swallowed errors; descriptive only |
| 37 | SPAZZ2411609/shadowbroker-main | Jul | 1 | n/a | **Off-topic**: re-upload of the open-source ShadowBroker OSINT platform |
| 38 | Syed-Muhammad-Tayyab/ConflictLens | Oct | 1 | n/a | **Off-topic**: Next.js/TypeScript OSINT dashboard (Iran/Israel default) |

---

## Strong repos (full cards)

### lbgos/AirAlerts (Oct cohort): LP 5 · Tech 5
- **Framing:** a per-oblast nowcaster with two targets:
  - for oblasts not under alert, P(a siren **starts** within 15m, 30m, 1h, 3h or 6h);
  - for oblasts under alert, P(the **all-clear** comes) within the same horizons.

  The stated goal is calibration ("70% should come true 70% of the time").
- **Data:**
  - **Sources:** own Telethon scrape of `@UkraineAlarmSignal` (eTryvoga), used as both label and feature source, plus the radar channels `@kpszsu` and `@deraketaua`. `@raketa_trevoga` is recorded live but had too little history to use.
  - **Window:** 2025-12-01 → **2026-10-09/10**, so it is fully post-raion-shift by design ("tactics changed").
  - **Raion handling:** an oblast counts as under alert from its first siren until the all-clear for every place in it. A 24h expiry covers lost all-clear posts.
  - **Parser:** the custom parser maps place tags to oblasts. It already parses 🔴/🟡 levels and treats "Відбій червоної… жовта ще триває" ("red all-clear, yellow still on") as a downgrade, not a new start (`alerts.py`).
  - **Freeze and duplicates:** not applicable, since it bypasses the frozen Vadimkin file. UTC throughout.
- **Target/horizon:** binary labels on (T, T+h], h ∈ {15m, 30m, 1h, 3h, 6h}, on a 5-minute grid. Live mode forecasts every 30 s.
- **Methods:**
  - LightGBM per horizon, with recency weighting (60-day half-life);
  - logistic regression and ensembles as alternatives;
  - calibration compared across none, isotonic, Platt and a "conservative" Platt capped at a 99% Wilson bound per bin;
  - baselines: climatology (oblast × hour-of-day rate fit on train) and base rate.
- **Evaluation:**
  - **Split:** train | calibrate (7 days) | test, purged so no label window crosses a boundary (`Split.periods` in `model.py`).
  - **Selection:** model choice used a separate 14-day dev window. The **final test (last 14 days, ending 2026-10-10 16:20 UTC)** was run once per chosen model, so it is the latest period.
  - **Siren-start Brier (model vs climatology):** 15m 0.058 vs 0.069; 1h 0.118 vs 0.164; 6h 0.112 vs 0.200. AUC 0.88–0.92, ECE 0.018–0.037.
  - **All-clear Brier:** 1h 0.172 vs 0.190, AUC 0.81.
  - **Over-confidence check:** "confident-wrong vs promised" is reported for every horizon.
- **Leakage:**
  - Every feature uses events with `ts < T` via `searchsorted(side="left")` (`dataset.py`).
  - Calibration is on its own window, and the dev/final windows are separate.
  - **Residual risk:** eTryvoga posts are often edited. `scrape.py` stores `edit_date`, but features don't mask posts edited after T. Minor.
- **Text/media:**
  - Radar-channel posts were labelled once by an LLM (Haiku agents, prompts in `prompts/`, labels in `labels/`).
  - Those labels were distilled into a **local TF-IDF + logistic classifier** (`radar.py`), so no LLM runs at forecast time.
  - Tested in three rounds and **honestly dropped**: radar beats threat notes alone (0.249 vs 0.239 skill) but adds nothing over neighbour sirens. A neighbour siren preceded 94% of episodes, radar 53%.
  - Lead-time study in `reports/raketa_trevoga.md`.
- **Product:**
  - `forecast live` polls the channel every 30 s and serves a bilingual one-page map: red shading for start probability, blue for all-clear, Kyiv inset, dark/light theme, greyed occupied areas.
  - Every poll's forecasts go to `data/live/predictions.jsonl`, and `forecast score-live` scores them prospectively.
- **Engineering:** package `src/ua_alert_forecast`, a `forecast` CLI (login, scrape, train, fit-live, live, score-live), `uv.lock`, 3 test files, reports per experiment round.
- **Docs/iteration:**
  - 13 commits in one day with meaningful messages, for example "Fix alert duration, punish overconfidence, improve 15-minute forecasts".
  - `reports/experiments*.md` and `metrics*.md` log every round. README results tables include "what helped" and "previous models on the same window".
  - No AI-usage section, but the experiment trail is the strongest iteration evidence in the batch.
- **Borrow:**
  - the purged three-way split with label-window containment;
  - a dev window separate from a single-use final window;
  - feature-group ablation tables;
  - conservative Wilson-capped calibration plus the "points"/"penalty" metrics that punish confident misses;
  - LLM-label-then-distil for text;
  - the prospective prediction log with a scorer;
  - the all-clear model as a second target.
- **Red flags:**
  - Labels come from a volunteer channel, not the official feed; coverage against official alerts is not validated.
  - The final test is a single 14-day window.
  - The post-reform yellow/red levels are parsed but not modelled or evaluated separately.
- **Ratings:** LP 5: latest data, explicit leakage design and visible iterative correction. Tech 5: the most rigorous and most operational repo in the batch.

### spryima/kse-air-raid-predictability: LP 5 · Tech 5
- **Framing:** how predictable are oblast-level alert onsets, and how robust are simple models to the 2025 oblast→raion reporting shift? Explicitly not claiming anything about enemy behaviour.
- **Data:**
  - Frozen Vadimkin official snapshot pinned by upstream commit and **SHA-256** in `config.yaml`, committed (28 MB).
  - Exact dedup (271,894 → 158,049 rows).
  - **Union of oblast + raion intervals** per oblast, with half-open `[start, end)` intervals. Hromada rows are excluded from the primary construction, which sidesteps standing frontline hromada alerts.
  - Reporting periods labelled pre-transition, transition and post-rollout. UTC.
- **Target/horizon:**
  - **Target:** at least one union onset (a clear→active transition) in (t, t+6h], on an hourly panel.
  - **Population:** oblast-hours that are clear at t. Using this population was tested, with all timestamps kept as a sensitivity check.
  - **Censoring:** the final 6 hours are right-censored.
- **Methods:**
  - Smoothed **seasonal frequency hierarchy**, fit on training only (oblast×weekday×hour → oblast×hour → oblast → global, minimum 30 observations, α = 20).
  - Against it, an L2 SGD logistic regression with calendar plus own-oblast history: time since onset, onset counts and active minutes over 24h and 7d.
- **Evaluation:**
  - **12 rolling monthly test folds, Jun 2025 – May 2026** (the latest year), each with the preceding 12 months for training and a **6-hour purge**, enforced by an assertion (`select_train_test` in `src/evaluate.py`).
  - **Pooled results:** logistic PR-AUC 0.778 / ROC 0.842 / Brier 0.145 / ECE 0.012, vs baseline 0.753 / 0.831 / 0.152 / 0.017. The model won 12 of 12 months on PR-AUC and 19 of 24 oblasts.
  - **Between-vs-within diagnostic:** most discrimination is oblast-month stratification. Within-cell ROC is about 0.59–0.60, but still beats a 200-permutation reference.
  - All out-of-sample predictions, splits, calibration bins and verification logs are saved.
- **Leakage:**
  - Careful partial-interval handling at t (`cumulative_active_ns_at` in `src/targets.py`), features built from `searchsorted(side="right")` on starts ≤ t, the purge, and training-only hierarchies. I found nothing.
- **Text/media:** none.
- **Product:** none; this is a reproducible research CLI (`python -m src.evaluate`).
- **Engineering:** `src/` modules, 3 test files, `pytest.ini`, pinned requirements, `outputs/verification/` (pip freeze, timings, logs). The clean run takes about 29 s.
- **Docs/iteration:**
  - `AI_DECISIONS.md` logs each change as proposal → risk → validation → result → adjustment. Entries include runtime failures, the switch to SGD, the switch from expanding to rolling 12-month windows, and a serialisation timeout.
  - Also `DATA_AUDIT.md`, `DATA_CONTRACT.md`, `REFLECTION.md`, `FINAL_MANIFEST.md`.
  - Single commit, but the strongest written process record in the batch.
- **Borrow:**
  - `AI_DECISIONS.md` format;
  - SHA-pinned input;
  - clear-state population with a sensitivity check;
  - purged rolling monthly folds;
  - `src/between_within_diagnostic.py` (it shows how much "skill" is just regional prevalence);
  - saved out-of-sample predictions.
- **Red flags:**
  - No product.
  - The model comparison changes both model family and features at once (they say so).
  - Data ends around June 2026, which was the latest available then.
- **Ratings:** LP 5: textbook process and honesty, matching KSE's rubric. Tech 5: the most defensible evaluation design in the batch.

### olehm208/air_alert_ai_analysis (Oct cohort): LP 4 · Tech 4
- **Framing:** a retrospective dashboard plus "experimental alert-start forecasting". It says repeatedly that it is not an operational service.
- **Data:**
  - Both Vadimkin CSVs committed: official 31 MB and volunteer 9 MB, which the author regenerated via Telethon according to `ai_usage.md`.
  - Separate source modes. `drop_duplicates()` with the comment "district observations are NOT duplicates".
  - Official rows are attributed to their oblast, and **starts at any level count**; there is no interval union. Because the target is binary and the lookback is 240 days, the window is mostly post-shift for the official source.
  - **The official freeze at 2026-09-07 is not mentioned.** Volunteer data runs to 2026-10-10.
  - UTC features with Kyiv calendar features.
- **Target/horizon:** P(≥1 recorded start in the region in [t, t+h)), h ∈ {1, 3, 6, 12} hours, per region and source.
- **Methods:**
  - Logistic regression vs HistGradientBoosting, chosen **per fold on a 14-day validation set** by Brier, then refit on train+validation.
  - Four baselines: past overall rate, smoothed hour-of-day rate, and trailing 7-day and 30-day matured-label frequencies.
- **Evaluation:**
  - 4 disjoint 28-day walk-forward folds; the latest fold ends at the last record, so it is the latest period.
  - Non-overlapping test windows (every h-th row). Brier, AP, ROC-AUC and reliability plots.
  - `ai_usage.md` reports honestly that the trailing-30-day baseline **beat ML** for Kyiv City at 6h on volunteer data. No numeric results table in the README.
- **Leakage:** the best explicit treatment in the batch.
  - A label at s is used only once s+h ≤ t, both in training and in the online baselines (`temporal_splits`, `rolling_prior_probabilities` in `forecasting.py`).
  - **Perturbation tests** in `test_v3_backtesting.py`: adding a future start leaves features and baselines at t unchanged, and an earlier fold is immune to later data changes.
  - The missing publication time is acknowledged as an open limitation.
- **Text/media:** none at runtime.
- **Product:**
  - Streamlit with Analytics and Predictions tabs, a source switch and filters.
  - `standing_alerts.json` annotations (Luhansk, Crimea, Sevastopol) are kept out of the labels.
  - Native light/dark themes.
- **Engineering:** flat modules, 6 test files (34 tests), CHANGELOG (v6, v7). Large CSVs are committed.
- **Docs/iteration:**
  - `ai_usage.md` has a human-vs-AI responsibility table and milestones with corrections, for example "the first benchmark was too weak, so positive results were treated skeptically" and a RecursionError fix.
  - 14 commits in about 3.5 hours.
- **Borrow:** maturation-aware splits and baselines; perturbation leakage tests; validation-only selection per fold; the responsibility table in `ai_usage.md`.
- **Red flags:**
  - The README is thin on method and results.
  - No union for official raion rows.
  - Freeze and outage not noted.
  - The year-cycle features are pointless with a 240-day lookback.
- **Ratings:** LP 4: clear iteration and scepticism toward its own early wins. Tech 4: rigorous evaluation hygiene with a modest model.

### umunevich/air-raid-alerts-analysis: LP 4 · Tech 4
- **Framing:** "Will my region be under an air-raid alert at any point in the next N hours?" N = 1…24, with a forecast origin every hour.
- **Data:**
  - Vadimkin official, downloaded with a git-SHA manifest (`ingest/fetch_vadimkin.py`). Latest origin 2026-06-21 01:00 UTC.
  - All rows of an oblast are merged into **union intervals** (`transform/intervals.py`). That merge also absorbs the duplicates; there is no explicit dedup.
  - Each row is tagged with a granularity era (`docs/DATA.md`).
  - Stored in UTC, with Kyiv-time calendar features.
  - Only `kyiv_city` was trained, although the registry lists 7 regions with per-region training windows.
- **Target/horizon:** **exposure**: y_N = 1 if the region is under alert at t or an alert starts in (t, t+N] (`transform/panel.py`).
- **Methods:**
  - One logistic regression per horizon (class_weight balanced), with **isotonic calibration on the 8-week validation set** (`models/calibration.py`).
  - Baselines: marginal rate, hour-of-week seasonal rate, and **persistence as a conditional rate given active-now** (`models/baselines.py`). All are fit on train.
- **Evaluation:**
  - Time split: test = last 4 weeks before the cutoff (the latest period), validation = the 8 weeks before that.
  - Metrics: Brier, log loss, PR-AUC.
  - **Post-calibration results, which appear only in the chat log:** h1 Brier 0.063 vs persistence 0.064; h6 0.202 vs 0.206; h12 0.236 vs 0.242; **h24 0.236 vs 0.198 (loses)**.
- **Leakage:**
  - Features are strictly past (`hours_since_last_event` uses side="right"; lag sums use `shift(1)`).
  - **No purge gap** between train/val/test, so 24h labels overlap the boundary.
  - The last 24h of test labels are right-censored at the cutoff. Both are minor.
- **Text/media:** none.
- **Product:** CLI `air-alerts fetch | process | train | predict`, with per-region manifests and artefacts.
- **Engineering:** proper package, pyproject, ruff, YAML configs, 21 test modules (102 tests per the log), schema constants. Heavy for a 2-day project, but clean.
- **Docs/iteration:**
  - `docs/REQUIREMENTS.md` and `docs/DATA.md`, the latter with per-region training windows and an era table.
  - The **exported Cursor chat is in the repo** (`docs/chat-history/*.md`, the raw `cursor-chat-export.jsonl`, and the exporter `scripts/export_chat_history.py`).
  - In the log, the user asks "is there any crucial mistake?". The AI flags non-calibration, persistence dominance and non-monotone horizons. The user then orders the persistence comparison and the calibration.
- **Borrow:** the exposure target definition; conditional persistence as the baseline to beat; validation-only calibration; the DATA.md era/registry design; the chat-export script for submitting the AI log.
- **Red flags:**
  - The README has no results and no limitations.
  - The model barely ties persistence and loses at long horizons.
  - Non-monotone P(N), with P(N+1) < P(N) in 606 of 672 test rows, is noted but not fixed.
  - Single region.
- **Ratings:** LP 4: visible, user-driven iteration in the log. Tech 4: sound, leakage-aware pipeline with honest but modest skill.

### iuad0qll/KSE_analytics: LP 4 · Tech 4
- **Framing:** decision-useful signals: time under alert, escalation, forecastability and wave clustering.
- **Data:**
  - Vadimkin official, 2022-03-15 → 2026-06-24.
  - Explicit dedup: 273,274 → 159,429 rows (42%).
  - DST-aware Kyiv time; 24h cap rather than deletion; Luhansk excluded.
  - **Oblast union over all levels**, which keeps the series comparable across the shift.
- **Target/horizon:** national mean minutes per day under alert per region; one day ahead.
- **Methods:**
  - Holt-Winters (additive trend and weekly seasonality) vs seasonal-naive (lag 7).
  - Hawkes process (own MLE plus time-rescaling goodness-of-fit) per region.
  - Lead-lag propagation analysis.
- **Evaluation:**
  - Test = last 60 days (the latest), with **rolling one-step refits**.
  - Holt-Winters beats lag-7 by 31% MAE and 28% RMSE, MASE 0.86.
  - Hawkes branching ratio 0.18–0.69. Goodness-of-fit is rejected for busy regions, and the README says so.
- **Leakage:** none found; each prediction uses data up to t−1. The last day may be partial (not dropped). Minor.
- **Text/media:** none.
- **Product:** static `index.html` dashboard (`build_dashboard.py`). Optional `fetch_alerts.py` for alerts.in.ua.
- **Engineering:** flat scripts; `audit_checks.py` verifies DST days are 23h/25h, that splits don't overlap, and the grouping. No tests.
- **Docs/iteration:**
  - README with findings and limitations.
  - `reflection.txt` (~100 words): started from 2022-only data and naive sums; fixed duplicates, union and the Hawkes collapse on simultaneous events.
  - The earlier 2022-only exploration is kept "to document iteration".
  - Single commit.
- **Borrow:**
  - `minutes_overlap_compare.py` (naive summed durations overstate time under alert 2.1× overall and 4.1× in 2026, above 24h/day);
  - `hawkes_analysis.py` with goodness-of-fit;
  - the rolling one-step refit pattern;
  - `audit_checks.py`.
- **Red flags:**
  - The only baseline is lag-7; a lag-1 persistence or moving average was not compared.
  - National aggregate only for the forecast.
  - Single commit.
- **Ratings:** LP 4: honest reflection and correct data handling. Tech 4: strong analysis and a simple but leak-free forecast.

### nitatsuu/Kizashi: LP 4 · Tech 3
- **Framing:** a binary hourly forecast of whether Kharkiv oblast will be under alert in the next hour.
- **Data:**
  - Vadimkin official; `level=='oblast'` only, **deliberately capped at about August 2025** (the reform point).
  - They tested an all-level union and rejected it because the alert rate goes to about 1.0. That confound is really standing hromada alerts. They found two corrupt records spanning June 2024 → January 2026 and removed them.
  - Kyiv time via named zone; resampled in UTC to avoid DST duplicates.
- **Target/horizon:** alert state at T+1 from information at T.
- **Methods:** majority and persistence baselines; LightGBM with and without `days_since_start`.
- **Evaluation:**
  - Temporal split with test **Jan–Jul 2025**, which is **not the latest period**.
  - PR-AUC: persistence 0.808, LightGBM 0.840 without the drift feature (chosen) and 0.882 with it, which they explain as trend extrapolation.
- **Leakage:** documented anchoring: lags through T−1, rolling through T, the calendar of T+1. They found and fixed an **off-by-one in the persistence baseline** that had inflated the model's margin from +0.03 to +0.11.
- **Text/media:** none.
- **Product:** none; scripts only.
- **Engineering:** 6 small scripts; models are committed as `.pkl`.
- **Docs/iteration:**
  - README "Key decisions" lists each decision with errors caught: the persistence off-by-one, gain-based vs split-based feature importance, the series boundary, holidays dropped because of shifting Ukrainian holiday dates.
  - The full Claude Code `session.jsonl` and a readable markdown version are included.
- **Borrow:** documenting caught errors with before/after numbers; the "decision-time anchoring" paragraph; reporting the drift feature separately.
- **Red flags:** violates "evaluate on latest period"; single region; oblast-only.
- **Ratings:** LP 4: the iteration evidence is strong. Tech 3: correct but stops at August 2025.

### slobodskyi/tsa-air-raid: LP 3 · Tech 4
- **Framing:** honest, rhythm-focused analysis plus probabilistic forecasting. Spikes are "under-predicted by design".
- **Data:**
  - Vadimkin official, downloaded at runtime and cached, with a stale-data banner.
  - **Oblast-equivalent interval union** with a 2-minute tolerance; it reproduces air-alarms.in.ua's yearly totals within a few percent.
  - Two cleaning views: **drop alerts over 24h for counts, clip them to 24h for burden**.
  - Under-1-minute blips dropped.
  - ISO 3166-2 crosswalk; adjacency derived from polygon touches.
  - Kyiv-local bucketing; the transition band is marked on charts.
  - Dedup happens implicitly through the union.
- **Target/horizon:**
  - (a) the national hourly episode count;
  - (b) per-oblast onset in the next hour, given the oblast is calm now.
- **Methods:**
  - (a) HistGradientBoosting on the **deviation of √count from a train-only climatology**, with 5/95% quantile bands; seasonal-naive and lag-24 persistence baselines.
  - (b) HistGradientBoosting classifier with neighbour-oblast activity features.
- **Evaluation:**
  - Time-ordered 80/20 split, so the test is the latest roughly 20%.
  - (a) MAE/RMSE with a **paired bootstrap CI on the MAE difference** and pre/post-break metrics. The model edges seasonal-naive on MAE and loses on RMSE, reported plainly.
  - (b) AUC about 0.82, Brier, log loss, calibration curve.
- **Leakage:**
  - Climatology fit on train only; lags use `shift`; neighbour features use the current-hour bucket, so the origin is the end of the hour.
  - The early-stopping validation fold is random (documented).
  - The onset AUC is compared with "persistence ≈ 0.5", which is a weak strawman, instead of a seasonal-rate baseline.
- **Text/media:** none.
- **Product:** 8-tab Streamlit app including an animated MapLibre choropleth, MSTL/STL, MAD anomalies and quiet-period analysis.
- **Engineering:** clean `src/` split; `tests/test_core.py` covers union edge cases, minute conservation across days, clipping and reproducibility. One commit.
- **Docs/iteration:** an excellent README with methodology, caveats and "can / cannot predict". There is **no AI log, reflection or iteration trail** in the repo.
- **Borrow:**
  - `src/aggregate.py` (`oblast_equivalent_intervals`);
  - the drop-vs-clip views in `src/data_loader.py`;
  - the paired bootstrap and pre/post-break evaluation in `src/forecast.py`;
  - `data/crosswalk.csv` and `data/adjacency.json`.
- **Red flags:** process is invisible (a single commit); the onset baseline is weak.
- **Ratings:** LP 3: excellent output, but nothing shows the process. Tech 4.

---

## Middle tier (compact cards)

### tbaraniuk/air_alert_analysis (known passer): LP 5 (confirmed) · Tech 2
- **Framing:** a Dash dashboard: monthly choropleth, live "currently active" panel, totals, escalation trend, durations.
- **Data:** live alerts.in.ua (backfill via `month_ago`) plus the Kaggle `cashncarry` CSV for the demo. That CSV **ends 2022-10-15**. No dedup, only a note. SQL converts UTC to Kyiv correctly.
- **Model and evaluation:** none; no forecasting.
- **Product and engineering:**
  - `src/ingest.py` validates with pydantic, retries with tenacity, upserts into DuckDB, and paces requests to the 2/min history limit.
  - uv lock; separate id ranges per source.
- **Docs:** setup, a source table and a "known limitation" on hromada name collisions.
- **Borrow:** the ingester pattern.
- **Ratings:** LP is ground truth. Tech 2: stale data, no analysis depth. The pass was decided by the log and process, not this repo.

### petroltradesupply-dotcom/time-series-air-raid-alerts-ua: LP 3 · Tech 3
- **Data:**
  - Vadimkin history **spliced** with the last month from the alerts.in.ua API (`src/build_spliced.py`), cross-checked over the last week (correlation 1.000, mean difference 0.49 h per oblast; `src/compare_sources.py`).
  - Hours per day under alert from the oblast union, clipped to 24h and split at Kyiv midnight, with a DST-safe +25h trick (`src/preprocess.py`).
  - **Measures the residual granularity jump** in `src/eda.py` (Kharkiv +138%, Kyiv +60%, Lviv −3%) instead of assuming it away.
- **Model:** SARIMA(1,0,1)(1,0,0,7) on a 365-day window vs seasonal-naive, for all 25 oblasts.
- **Evaluation:** last 14 days (the latest). SARIMA beats the baseline in 17 of 25 oblasts; mean MAE 1.38 vs 1.83 h/day. The README says it makes "no strong claim".
- **Second layer:** a descriptive one-month hromada-level snapshot.
- **Iteration:** commits include "Fix DST infinite loop"; the reflection explains the shift from counts to union hours.
- **Red flags:** a single 14-day holdout; no tests.
- **Ratings:** LP 3: good reflection. Tech 3: sound data handling, thin evaluation.

### alitskevych/air-raid-ts: LP 3 · Tech 3
- **Data:** volunteer (eTryvoga) data to 2026-06-25; naive-flagged rows are excluded from durations only; the trailing partial day is dropped.
- **Model:** national daily counts, SARIMA(1,1,1)(1,1,1)₇ vs seasonal-naive.
- **Evaluation:** 6-fold walk-forward over **Dec 2025 – Jun 2026** (the latest). MASE 0.91±0.12 vs 1.11±0.14; SARIMA wins 5 of 6 folds.
- **Docs:** honest limitations; CLAUDE.md "non-negotiables".
- **Red flags:**
  - Volunteer counts are treated as complete; parser fragmentation inflates counts after the shift.
  - National aggregate only. 2 commits.
- **Ratings:** LP 3. Tech 3.

### aleksey1chern/spok: LP 3 · Tech 3
- **Framing:** a Kyiv-only FastAPI web app ("Спокійна Ніч", "Calm Night") centred on a "smart all-clear": after the all-clear, a traffic light for re-strike risk. Also an official readiness level from alerts.in.ua UID 31.
- **TSA:**
  - `tools/tsa_report.py`: diurnal profile, re-strike survival curve, and a short-alert proxy.
  - `tools/backtest_allclear.py`: threshold backtest on 2,090 episodes. The 120-minute combat floor ≈ p80 of night re-strikes (124 minutes).
- **Leakage:** the backtest is in-sample, with no time split or latest-period evaluation.
- **Reflection:** the AI over-claimed a "heavy night" forecast from N≈44, and its threat-ellipse tilt was an artefact. A multi-agent review flagged it and it was rejected. A fail-open "calm" error path was also fixed.
- **AI log:** deliberately excluded from the repo.
- **Engineering:** 8 test files.
- **Ratings:** LP 3: good self-correction story. Tech 3: thoughtful product, weak out-of-sample evaluation.

### denkor1015-debug/Air-alerts-analysis: LP 3 · Tech 3
- **Data:** correctly diagnoses the oblast→raion shift (a `regime_transition.png` chart), but restricts everything to oblast level **2022-03-15 → 2025-07-31**. Dedup handled.
- **Evaluation:** walk-forward of 31 windows × 28 days. ETS MAE 15.9 vs naive 21.6; SARIMA, ETS and log-SARIMA are tied; Prophet and GBM are worse.
- **Insight:** a single holdout made naive look competitive, and walk-forward refuted it.
- **Next steps:** names the union fix as the upgrade but does not do it.
- **Ratings:** LP 3: honest, but violates the latest-period requirement. Tech 3. One commit.

### HadyBytes/Air-raid-alerts-in-Ukraine-Analysis: LP 3 · Tech 3
- **What it is:** a descriptive self-contained HTML report (Plotly embedded) from one script.
- **Rollup method:** an oblast counts as under alert if oblast-level rows are present nearby, otherwise if **at least 50% of its active raions** are under alert. "Active" uses a ±30-day adaptive denominator, with at least 2 raions required. This is a more conservative alternative to any-raion union.
- **Verification:** **every figure re-derived independently** with a per-minute grid.
- **Time zone:** Kyiv local time with interval splitting at UTC hours.
- **AI log:** `conversation_log.md` included. The user questions provenance and asks for a mapping check.
- **Gaps:** no forecasting; no explicit dedup (the interval algebra absorbs it).
- **Ratings:** LP 3. Tech 3.

### andrii-kondratok/ukrainian-air-raid-analysis: LP 3 · Tech 3
- **Analysis:** notebook sections covering seasonality, trends (concurrency share), and **precursors of mass attacks defined from external ground truth** (piterfm), using a rolling 75th-percentile threshold over 180 days.
- **Precursor result:** about 30% more alert-hours in the 24–72h before an attack, p≈4e−6.
- **Classifier:** AUC about 0.63 from a **random stratified split and CV**, not temporal.
- **Data window:** cut at the end of November 2025, with the raion shift cited correctly.
- **Output:** a GitHub Pages report.
- **Iteration:** commits show it (threshold refactor; Section D replaced by C.5).
- **Ratings:** LP 3. Tech 3: a clever framing that avoids circularity, but weak validation and not the latest period.

### dukarev/ukraine-air-alerts-analysis: LP 3 · Tech 3
- **What it does:**
  - Per-oblast anomaly score against the oblast's own 30-day norm (median and MAD, shifted by one day), with a fatigue composite.
  - A→B alert chains with MiG-31K-style nationwide filtering.
  - 77 TDD tests plus **mutation testing**: 82.8% on `elevated.py`.
- **Data:**
  - `RECON-FINDINGS.md` "proves" with "3 oracles" that the official feed died after October 2025. **That is the raion shift, misread.** It was filtered to `level=='oblast'`, and raion rows were never checked.
  - They then switched to the volunteer dataset, which is a valid fallback.
- **Validation:** recall 67–83% on 6 historical attack dates with a ±1-day window, against a 32% daily base rate. A 3-day window gives about 69% by chance, so the recall is roughly chance level.
- **Not latest period:** no forecasting.
- **Ratings:** LP 3: heavy process (plan, PRs, review fixes), but it accepted a hallucinated diagnosis. Tech 3.

### orestes-d/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine: LP 3 · Tech 3
- **What it is:** a single-file bilingual Streamlit app.
- **Method:** oblast union over all units; share of time under alert and alert-hours.
- **Duplicates:** it correctly explains that everything before 2026-01-25 appears exactly twice (verified above).
- **Cleaning:** sets aside about 12 unterminated multi-week records; excludes Crimea and Luhansk.
- **Gaps:** descriptive only; one "Add files via upload" commit.
- **Ratings:** LP 3. Tech 3.

### KrafterDen/Alerts-Analysis: LP 3 · Tech 2
- **Data:** Vadimkin plus an alerts.in.ua delta, merged into event level (158k rows) through 2026-06-21. Exact and cross-source dedup.
- **No interval union:** daily counts and summed minutes across raion and hromada rows inflate after the shift. Daily bucketing is in UTC.
- **Models:**
  - next-day risk and 60-day count/minutes "forecasts" from baselines (rolling-7d, same-weekday, event-adjusted);
  - an optional LSTM, admitted unfinished.
  - Backtest code exists; **no metrics are reported** and the outputs are gitignored.
- **Product:**
  - a 73 KB Streamlit app with a clickable oblast map, a **Ukrainian/Russian symbolic-date timeline**, and "View into the future" mode;
  - also a Dash app.
  - The README claims a "no-token" run from prepared data, but the processed files are not in the repo.
- **Iteration:** 21 commits, staged; the README honestly lists "planned but not completed".
- **Ratings:** LP 3. Tech 2.

### borovkov-d/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine: LP 3 · Tech 2
- **Data:**
  - `level=='oblast'`, with the series cut at 2025-10-31 because of a "collection stop". That is the raion shift, misdiagnosed, and it is repeated in the limitations.
  - A synthetic fallback if the download fails.
- **Model:** national daily count, SARIMA vs naive and MA-7.
- **Evaluation:**
  - Single split: SARIMA MAE 6.84 vs naive 8.20.
  - **5-fold backtest refutes it:** SARIMA 13.88±6.30 vs MA-7 14.01±8.89.
- **Docs:** good "key decisions" reflection; a live alerts.in.ua check up to the auth boundary only.
- **Ratings:** LP 3: the honest refutation is a good process signal. Tech 2: wrong data diagnosis, not the latest period.

### kowalsking/time-series-analysis: LP 3 · Tech 2
- **Data:** Kaggle `dimakyn` (Feb–Apr 2022, 45 days) plus an alerts.in.ua month (rate-limit-aware client with disk cache and 429 handling). A synthetic fallback.
- **Model:** Holt-Winters vs seasonal-naive on the last test days; short horizon only.
- **Product:** Streamlit, **deployed**.
- **Docs:** good reflection (perpetual occupied-region alerts clipped; plotly hiding tick labels). The Claude Code chat export is committed.
- **Hygiene:** about 164 MB of 2022 → 2025-06 raw JSON is committed but unused (the loader reads only `*.csv`).
- **Ratings:** LP 3: similar profile to the passer. Tech 2: weak data window and evaluation.

### mariiaikonnikova6-rgb/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine: LP 2 · Tech 3
- **Target:** Kyiv City daily alert minutes; oblast-level rows, which is fine for Kyiv.
- **Data window:** analysis cut at **2025-11-30**, not the latest.
- **Models:** seasonal-naive, Ridge (TimeSeriesSplit), ARIMA and SARIMA with training-only order selection.
- **Evaluation:** test 2025-06-04 → 11-30. SARIMA MAE 101 vs seasonal-naive 134; Ridge has the best RMSE (151). Rolling-origin folds.
- **Reproducibility:** the data CSVs are **Git LFS pointers** (133 B), so a clone can't reproduce; `__pycache__` and `.idea` are committed.
- **Ratings:** LP 2. Tech 3.

### koalla05/air-alerts (Oct cohort): LP 2 · Tech 2
- **Framing (good):** survival-style:
  - Task A: remaining alert duration given elapsed time;
  - Task B: time to the next alert given quiet time.
  - Methods: empirical conditional-quantile and **Kaplan-Meier conditional survival** baselines vs LightGBM quantile and probability models.
- **Data trap:** filtered to `level=='oblast'`. The 80/20 split starts **2025-01-13**, and 2026 is near-empty (445 Kyiv City episodes; verified above). So "held-out recent months" is really 2025.
- **Other issues:**
  - The official freeze is not mentioned.
  - Hour features are in UTC.
  - Dedup on (region, start).
  - No metrics reported anywhere (empty notebook outputs, sample output only).
  - `docs/ai_usage.md` is empty. 4 commits.
- **Borrow:** the conditional survival framing for all-clear prediction (`src/alertpred/models/baseline.py`).
- **Ratings:** LP 2. Tech 2.

### colobocman/airalert-planner: LP 2 · Tech 2
- **Framing:** a planning-risk CLI and Telegram bot: hierarchical shrinkage of region×weekday×hour alert rates.
- **Evaluation:** TimeSeriesSplit on distinct hours, with a **Brier skill score vs hour-of-day climatology** (0.117 vs 0.135).
- **Data: all on SYNTHETIC data** (`data/sample_alerts.csv`), with no real source at all. That fails the core requirement.
- **Process (excellent):**
  - `.claude/agents/time-series-reviewer.md` and `/harsh-review` command;
  - PR-based review merges ("Address review: honest climatology framing, non-tautological skill test");
  - AI logs (Hermes, Claude Code).
- **Ratings:** LP 2: the process is great, the data is fake. Tech 2.

### Mafusail2020/air-alerts-analysis: LP 2 · Tech 2
- **What it is:** a Streamlit choropleth dashboard.
- **Data:** Vadimkin plus live alerts.in.ua status; per-oblast sweep-line union (`ingest.py`).
- **Predictor:** `src/analytics/predictor.py` trains logistic regression per oblast on **all data with no split or metric**.
- **Time zone bug:** the heatmap uses a **fixed UTC+2** (DST ignored) and takes the weekday from the UTC date.
- **AI logs:** compressed and raw Claude/Gemini logs show the user pushing back ("Cannot accept the known gap. Implement temporal deduplication"), but mostly on UI tweaks.
- **Ratings:** LP 2. Tech 2.

### zadorozhna-dariia/AI_Agentic_school_stage_2: LP 2 · Tech 2
- **Data:**
  - oblast-only;
  - "feed collapses after Oct 2025, only Kyiv reports — collection failure", which is a misdiagnosis;
  - cut at 2025-10-31.
- **Analysis:** STL anomalies and holiday windows.
- **Models:**
  - daily negative-binomial GLM does not beat naive;
  - hourly logistic AUC 0.57, reported honestly.
- **Reproducibility:** `make_pdf.py` is referenced but missing.
- **Ratings:** LP 2. Tech 2.

### arborfam/ukraine-air-raid-analysis-for-KSE: LP 2 · Tech 2
- **Rollup:** oblast rows before the switch, and raion union after each oblast's last oblast-level row. Those dates are 2025-08-20 → 11-04 (verified), so the Aug–Nov 2025 transition is undercounted.
- **Model:** Prophet for 4 regions, trained to 2026-01-31 and tested to 2026-06-23 (the latest); correlation 0.07–0.10, with no naive baseline.
- **Luhansk:** treated as one continuous alert.
- **Docs mismatch:** the README describes `notebooks/`, but the repo has `src/*.py`. 2 commits.
- **Ratings:** LP 2. Tech 2.

### volodymyrfrydel-bit/ukraine-air-raid-timeseries: LP 2 · Tech 2
- **What it is:** volunteer data, a deployed Streamlit app with Chart.js visuals, and Prophet per region.
- **Evaluation:** a 14-day holdout with MAPE, and **no naive baseline**.
- **Time zone:** hour charts and the "night" flag are in **UTC** (acknowledged).
- **Iteration:** 12 commits incl. "Fix: forecast horizon slider was a no-op (caught in review)".
- **Ratings:** LP 2. Tech 2.

### yaroslavopanasenko25-eng/Yaroslav_AI_Agentic: LP 2 · Tech 2
- **What it is:** "GuardianEye", a FastAPI (plus legacy React/Vite) app.
- **Data:** an alerts.in.ua poller and store; 30-day statistics.
- **Model:** Grok LLM chat, RAG and "forecasting" with **no evaluation**.
- **Hygiene:** `.vite` dependency bundles are committed; Supabase/DigitalOcean deploy files.
- **Commits:** messages like "Fix_FIn" and "finish".
- **Ratings:** LP 2. Tech 2.

---

## Weak and off-topic (terse)

- **HATSKER-228/time-series-analysis-of-air-raid-alerts-in-Ukraine** (LP 2 · Tech 2):
  - EDA plus a volunteer-vs-official comparison, and it correctly spots the raion shift.
  - Local time is a **fixed UTC+2 "as the user requested"**. No modelling; one commit.
- **whylineee/ukraine-air-raid-alerts-analysis** (LP 2 · Tech 2): a tidy package, notebook and CLI EDA on volunteer data with STL. No forecasting or evaluation; one commit.
- **MrmaderatorYT/air-raid-alerts-analysis** (LP 2 · Tech 2):
  - Eight "cities" (really oblasts); ARIMA, Holt-Winters and Prophet on a 30-day holdout with negative R²; no naive baseline.
  - README findings discuss Donetsk, which is not in its own city list, so the AI-written text was not checked.
- **PrepAIre-edu/-TSAofAirRaidAlerts** (LP 2 · Tech 2):
  - A 70 KB monolithic `main.py`; `level=='oblast'` (it admits 2026 is "not quite correct").
  - **Data truncated to 2026-04-25 to fit GitHub**. Random forest for duration plus Prophet.
  - 27 web-UI commits.
- **Hroback/KSE** (LP 2 · Tech 1):
  - The README describes a `src/` package, but **`src/` is not in the repo**, so `main.py` fails on import.
  - Claims SARIMA MASE 0.58, which can't be checked. A 90 KB AI log and a reflection are present.
- **oleksandrsafandulaKSE/AirAlerts-TimeSeries-Analysis-Ukraine** (LP 1 · Tech 2):
  - LightGBM onset model with TimeSeriesSplit, but **early stopping uses the test fold** (`eval_set=[(X_test, y_test)]`).
  - The README is just a Streamlit link; `.idea` files and a 52 MB `training_matrix.csv` are committed.
- **bratxja-cmd/hromady-alarms** (LP 1 · Tech 2):
  - Not a TSA submission: a 20-region alerts.in.ua dashboard.
  - It **accumulates history daily via GitHub Actions** into SQLite, with dedup on alert id (`.github/workflows/update.yml`, `collect_hromady.py`). Real data June → 2026-10-10; 139 bot commits. That collector is worth borrowing.
- **MaksimPrykhodko/Ukraine-air-raid-prediction** (LP 1 · Tech 1):
  - Kyiv next-hour XGBoost claiming **100% precision, F1 0.87**.
  - Cause: in the notebook, `hours_since_last_alert` is set to **999 for every non-alert hour** and computed only for alert hours. That is a direct target leak, and SHAP ranks it the top feature.
  - Their "leak check" only tested for zeros. Optuna is on a time-series CV, but that is irrelevant given the leak.
- **sergii-brt/KSE_alert_analysis** (LP 1 · Tech 1):
  - Descriptive Streamlit app on a "sirens.in.ua API" (`/api/v3/alerts`) with a lat/lon schema that matches no documented API. The real keyless proxy is siren.pp.ua.
  - Every request error is silently swallowed, and there is no sample or cache showing real data. Likely a hallucinated source.
- **SPAZZ2411609/shadowbroker-main**: **off-topic**. A single-commit re-upload of the open-source ShadowBroker OSINT platform (210k LOC).
- **Syed-Muhammad-Tayyab/ConflictLens**: **off-topic**. A Next.js/TypeScript OSINT dashboard, Iran/Israel by default; not Python and not TSA.

---

## Top picks in this batch

1. **lbgos/AirAlerts**: the closest thing in the batch to a deployable, honestly evaluated system.
   - Borrow:
     - `src/ua_alert_forecast/model.py`: the `Split.periods` purge (a row belongs to a period only if its whole label window fits inside), the `Conservative` Wilson-capped calibrator, and the `points`/`penalty` scores.
     - `src/ua_alert_forecast/dataset.py`: strictly-before features via `searchsorted`; neighbour, second-ring and last-minutes features.
     - `src/ua_alert_forecast/alerts.py`: the yellow/red parser and the red→yellow downgrade rule.
     - `src/ua_alert_forecast/radar.py` with `prompts/` and `labels/`: LLM labels distilled into a local classifier.
     - `src/ua_alert_forecast/live.py` and `forecast score-live`: a prospective prediction log.
     - `reports/experiments*.md`: the per-round ablation log as an iteration artefact.
2. **spryima/kse-air-raid-predictability**: the gold standard for evaluation design and decision logging.
   - Borrow:
     - `AI_DECISIONS.md` (proposal → risk → validation → result → adjustment);
     - `config.yaml` SHA-256 input pinning;
     - `src/targets.py` (union onsets, clear-state population, partial-interval handling at t);
     - `src/evaluate.py::select_train_test` (rolling 12-month training, purge plus assertion);
     - `src/between_within_diagnostic.py` (separates oblast-month prevalence from real temporal skill);
     - `outputs/verification/`.
3. **olehm208/air_alert_ai_analysis**: the best leakage tests.
   - Borrow:
     - `forecasting.py::temporal_splits` and `rolling_prior_probabilities` (labels enter only after maturing);
     - per-fold validation-only model selection, then refit;
     - `test_v3_backtesting.py` perturbation tests (a future event must not change features at t);
     - the `ai_usage.md` human/AI responsibility table;
     - `standing_alerts.json`, which keeps manual context out of the labels.
4. **umunevich/air-raid-alerts-analysis**: the best problem definition and AI-log packaging.
   - Borrow:
     - the exposure target in `src/air_raid_alerts/transform/panel.py`;
     - conditional persistence in `models/baselines.py`;
     - validation-set isotonic calibration in `models/calibration.py`;
     - the `docs/DATA.md` granularity-era and per-region training-window tables;
     - `scripts/export_chat_history.py`, which turns Cursor JSONL into markdown for the AI-log submission.
5. **slobodskyi/tsa-air-raid**: the best data cleaning and rollup.
   - Borrow:
     - `src/aggregate.py::oblast_equivalent_intervals` (2-minute tolerance union);
     - `src/data_loader.py` `counts_view` vs `burden_view` (drop vs clip at 24h);
     - `src/forecast.py` (deviation-from-train-climatology target for trees, a paired bootstrap CI on the MAE gain, pre/post-break metrics, neighbour onset features);
     - `data/crosswalk.csv` and `data/adjacency.json`.
6. **iuad0qll/KSE_analytics**: the best analysis narrative.
   - Borrow:
     - `minutes_overlap_compare.py`, which quantifies naive-sum overcount (2.1×, 4.1× in 2026) as a "why union" argument;
     - `hawkes_analysis.py` (MLE plus time-rescaling goodness-of-fit);
     - `forecast_baseline_vs_model.py` (rolling one-step refit);
     - `audit_checks.py` (DST 23h/25h day checks);
     - `reflection.txt` as a model 100-word reflection.
7. **nitatsuu/Kizashi**: the best "caught errors" documentation.
   - Borrow the README "Key decisions" pattern: each fix with its before/after metric, for example the persistence off-by-one moving the margin from +0.11 to +0.03.
   - Also borrow shipping the raw `log/session.jsonl` alongside a readable version.
8. **petroltradesupply-dotcom/time-series-air-raid-alerts-ua**: the best source bridging.
   - Borrow:
     - `src/build_spliced.py` and `src/compare_sources.py` (splice history with a fresh API month and validate the seam on the overlap);
     - `src/eda.py` (measure the granularity jump per oblast);
     - the `src/preprocess.py` DST-safe day split.

**Honourable mentions:**
- `aleksey1chern/spok/tools/backtest_allclear.py`: re-strike survival after the all-clear as a recall-vs-vigilance-hours trade-off. A good product framing; it needs a temporal split.
- `bratxja-cmd/hromady-alarms/.github/workflows/update.yml`: a daily accumulator that beats alerts.in.ua's one-month window.
- `HadyBytes`: the raion-quorum rollup plus independent per-minute re-derivation.
- `orestes-d`: the duplicate-structure diagnosis.
- `koalla05/src/alertpred/models/baseline.py`: Kaplan-Meier conditional survival.
- `andrii-kondratok`: external ground truth to avoid circular "mass attack" labels.
- `colobocman/.claude/agents/time-series-reviewer.md` and `.claude/commands/harsh-review.md`: reviewer subagents that challenge the AI.
- `dukarev`: mutation testing.

---

## Common mistakes seen

1. **The `level=='oblast'` trap.**
   - It silently deletes every oblast except Kyiv City after about November 2025.
   - Seen in koalla05 (whose test is effectively 2025), borovkov-d, zadorozhna-dariia, PrepAIre-edu, HATSKER-228 (EDA) and dukarev (initially).
   - mariiaikonnikova is unaffected only because it models Kyiv City.
2. **Accepting the AI's diagnosis that "the official feed died / collection stopped after October 2025."** It is the raion shift.
   - dukarev "proved" it with three confirmation-biased "oracles".
   - borovkov-d and zadorozhna-dariia repeat it in their limitations.
   - Nobody in those three checked the raion rows. This is exactly the hallucination KSE asks candidates to challenge.
3. **Not evaluating on the latest period.** Deliberate cutoffs, even when well argued:
   - nitatsuu (test Jan–Jul 2025);
   - denkor (to 2025-07-31);
   - borovkov and zadorozhna (to 2025-10-31);
   - andrii-kondratok (Nov 2025);
   - mariiaikonnikova (2025-11-30).
4. **Summing counts or durations across overlapping raion/hromada rows without a union.**
   - KrafterDen does it, and olehm208's official mode partly does: it counts starts at any level.
   - iuad0qll shows this overstates time under alert 2.1× (4.1× in 2026).
5. **Leakage and evaluation hygiene:**
   - a target leak (MaksimPrykhodko's `hours_since_last_alert` = 999 on all negative hours, giving "100% precision");
   - early stopping on the test fold (oleksandrsafandula);
   - random stratified splits and CV on temporal data (andrii-kondratok);
   - in-sample "backtests" (spok);
   - models trained and served with no holdout at all (Mafusail2020, yaroslavopanasenko);
   - no purge between adjacent splits with multi-hour labels (umunevich).
6. **Time zone errors:**
   - fixed UTC+2 instead of `Europe/Kyiv` (Mafusail2020's heatmap, with the weekday taken from the UTC date; HATSKER-228, at the user's request);
   - UTC hours used as "time of day" (volodymyrfrydel-bit, koalla05's features).
7. **Weak or absent baselines:**
   - Prophet with no naive comparison (volodymyrfrydel, arborfam, MrmaderatorYT);
   - only lag-7 seasonal-naive for daily series (iuad0qll, mariiaikonnikova);
   - an onset AUC compared with "persistence ≈ 0.5" (slobodskyi);
   - no metrics reported at all (KrafterDen, koalla05, Mafusail2020).
8. **Single-holdout optimism.** Single splits gave rosy wins that walk-forward later refuted (borovkov-d, denkor). The good ones show the refutation; several others still report a single 14–30-day window (petroltradesupply, volodymyrfrydel, MrmaderatorYT).
9. **Data-source problems:**
   - synthetic data instead of real (colobocman, and the kowalsking and borovkov fallbacks);
   - a likely hallucinated API (sergii-brt);
   - stale Kaggle 2022 data (kowalsking, and also the passer);
   - volunteer (eTryvoga) counts treated as complete, with no note on partial coverage or fragmentation (alitskevych, volodymyrfrydel, whylineee, MaksimPrykhodko).
   - Among the October repos, nobody using the official CSV mentions its 2026-09-07 freeze.
10. **Reproducibility breakage:**
    - missing `src/` (Hroback);
    - Git LFS pointers instead of data (mariiaikonnikova);
    - a README promising prepared data that is gitignored (KrafterDen);
    - data truncated to fit GitHub (PrepAIre);
    - committed `.idea`, `__pycache__` and `.vite` artefacts and 50 MB matrices;
    - a README that doesn't match the repo layout (arborfam, MrmaderatorYT).
11. **Using an LLM as the forecaster** (Grok in yaroslavopanasenko), with no validation.

---

## Gaps nobody in this batch addressed

1. **Yellow/red alert levels after 2026-09-07** (Resolution 1092). No repo modelled them as a target or feature, or evaluated the post-reform regime separately. lbgos parses 🔴/🟡 but uses the level only to define starts.
2. **The official CSV freeze (2026-09-07) and its 2026-08-30 → 09-01 hole.** The October repos that read the official file (olehm208, koalla05) don't flag either one, so the gap reads as "no alerts". Nobody used Kyiv Digital, the JustJimer archive, map.ukrainealarm ranged history or siren.pp.ua to bridge it.
3. **Point-in-time availability of the history itself.** A Vadimkin row exists only after the alert ends and the next daily run. Nobody simulated that publication lag in backtests. olehm208 names it as an unsolved limitation; lbgos avoids it by scraping live.
4. **Telegram edit masking.** lbgos stores `edit_date` but never drops or masks posts edited after T. No one else uses timestamped text.
5. **Weather of any kind.** No repo used weather, let alone archived forecasts (Open-Meteo Previous Runs).
6. **Holidays under martial law.** Nobody used `holidays` with `categories=("public","workday")`. Calendars were hand-coded (KrafterDen, zadorozhna) or dropped as unreliable (nitatsuu).
7. **Exogenous strike data as features with proper availability times.** piterfm appears only as ground truth for labels (andrii-kondratok). Nobody used Air Force morning summaries or Kaggle missile rows shifted to their publication time as predictors.
8. **Monotone multi-horizon probabilities.** umunevich found P(N+1) < P(N) in 606 of 672 rows. Nobody enforced monotonicity or used a cumulative-hazard formulation. koalla05's survival framing is closest but is unevaluated.
9. **An explicit standing-alert registry.** Frontline hromada alerts lasting months were only capped (24h, 72h or 7 days) or dropped by level. Nobody identified standing units and removed them from the oblast union, which is what broke nitatsuu's union attempt.
10. **Comparing official, volunteer and alerts.in.ua coverage on the same window, before choosing a label source.** Only partial attempts exist: HATSKER-228 does volunteer vs official, petroltradesupply does alerts.in.ua vs Vadimkin over one week. Nobody quantified eTryvoga's alert-time coverage against the official feed, and lbgos and the volunteer-based repos depend on it.
