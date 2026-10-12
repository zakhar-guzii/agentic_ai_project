# Prior solutions survey: every public KSE Stage 2 air-raid repo

_Survey date: 2026-10-10/11. Companion files:_
- [prior-solutions-cards.md](https://github.com/zakhar-guzii/agentic_ai_project/blob/fbc16df/research/prior-solutions-cards.md): per-repo review cards for 115 repos (working notes).
- [prior-solutions-scores.csv](prior-solutions-scores.csv): automatic features and heuristic score for all 190 repos.
- [existing-solutions.md](https://github.com/zakhar-guzii/agentic_ai_project/blob/fbc16df/research/existing-solutions.md): first-pass survey, including academic work.
- [data-sources.md](data-sources.md): data access, freshness and leakage traps.
- [brief.md](brief.md): our task text.

## TL;DR

1. **Coverage.**
   - GitHub search gave 936 hits. 190 were relevant: 159 created in June 2026, 11 in July, 20 in October.
   - Of these, 168 are on-topic, and 115 were reviewed by reading their code. Three review subagents worked from local clones and executed nothing.
   - Spot checks: the files and numbers quoted below were re-checked against the clones. One agent misstated the sign of robotheist's text gain; it is corrected here.
2. **Repo quality barely predicts passing.**
   - The only confirmed passer is [tbaraniuk/air_alert_analysis](https://github.com/tbaraniuk/air_alert_analysis), a Dash dashboard with a live alerts.in.ua ingester. Its demo data is a Kaggle CSV that ends **2022-10-15**. It has **no forecast**, **no evaluation** and **4 commits**.
   - It ranks **81st of 190** on our automatic score. That fits KSE's own statement: _"Your AI interaction log is our primary signal."_
   - The repo has to work and be honest. The log is what gets graded.
3. **The bar has risen since June.**
   - The October wave (our cohort, created 2026-10-09/10) already includes several strong repos: [maranferij-lang](https://github.com/maranferij-lang/Ukraine-air-alerts), [Ddrakkx](https://github.com/Ddrakkx/alerts-forecast), [lbgos](https://github.com/lbgos/AirAlerts), [robotheist](https://github.com/robotheist/Air-alerts-forecast), [Dopplerr24](https://github.com/Dopplerr24/air-raid-alert-analysis) and [olehm208](https://github.com/olehm208/air_alert_ai_analysis).
   - What they have in common:
     - onset targets ("a new alert starts within H");
     - truncation leakage tests;
     - test windows on the latest weeks;
     - recent-rate and climatology baselines;
     - in two cases, Telegram text with honest null results.
   - "Prophet on daily counts + Streamlit" no longer stands out.
4. **The most common fatal mistake** (dozens of repos): filtering the official file to `level=='oblast'`.
   - After about November 2025 only Kyiv City keeps oblast-level rows, so 2026 vanishes.
   - Several candidates then **accepted the AI's claim that "the official feed died after Oct 2025"** and cut their data. It is the raion-level reform; the raion rows are right there.
   - This is precisely the "challenge model hallucinations" moment KSE looks for.
5. **Gaps nobody filled.** These are our openings; details in §5.
   - **Bridging the official file's 2026-09-07 freeze** with post-freeze data.
   - **Yellow/red alert levels**, in force since 2026-09-07.
   - **Point-in-time data availability**, including Telegram edit masking.
   - **Leak-safe exogenous data:** archived weather *forecasts*, Air Force reports at their publication time, martial-law holidays.
   - **Monotone multi-horizon probabilities.**
   - **Raion-level forecasts.**
   - **Regime-aware evaluation.**

## 1. Method

- **Enumeration.** GitHub REST search, run on 2026-10-10.
  - Query terms: "air raid", "air alert(s)", "air raid alerts", "air-raid", "alarm(s) ukraine", "тривог(и)", "sirens ukraine", "kse", "alerts ukraine time series", plus `in:readme` searches for "air raid", "повітряні тривоги", "ukrainian-air-raid-sirens-dataset" and "alerts.in.ua".
  - Date windows: `created:2026-06-15..2026-07-15` and `created:>2026-10-01`.
  - Hits were kept if the README or description matched an alert term AND a Ukraine term AND an analysis or forecast term. Scripts are in the scratchpad: `enum.py`, `filter.py`.
- **Cloning.** Shallow clones with blobs over 3 MB skipped. Commit counts and messages came from treeless history clones.
- **Automatic features** (`features.py`, `score.py`):
  - code structure: Python files, lines of code, tests, lockfiles;
  - modelling and evaluation: models, baselines, metrics, split type, calibration, leakage mentions;
  - data handling: timezone handling, raion/hromada handling, data sources;
  - product and documentation: dashboard/API, AI-usage section, limitations section, latest date in the README.
- **Qualitative review.** Three parallel subagents covered 39 + 38 + 38 repos. Each repo got a card covering framing, data, target, methods, evaluation, a leakage check of the code, text use, product, engineering, documentation and process, ideas to borrow and red flags. Each repo was rated 1–5 on "likely passed" (LP) and on technical quality (T). The cards are in [prior-solutions-cards.md](https://github.com/zakhar-guzii/agentic_ai_project/blob/fbc16df/research/prior-solutions-cards.md).
- **Limits of this method.**
  - The AI logs and reflections, KSE's main signal, are not public.
  - Ground truth is a single passer.
  - LP ratings are therefore judgements about *visible* process evidence, not predictions with known accuracy.
  - Commit dates are not reliable lateness signals. The June deadline was 21 June 23:59, quoted in [Hroback's log](https://github.com/Hroback/KSE), yet 16 repos have their first commit on 23–30 June, probably published after submission.

## 2. Scoring rubric

### 2.1 Automatic score (0–100+, all 190 repos)

| Block | Weight | Signals |
|---|---|---|
| Reproducibility | 15 | lockfile/requirements; tests; at least 3 Python files |
| Data rigour | 20 | raion/hromada handling; Kyiv timezone; data after June 2026; discusses leakage |
| Evaluation rigour | 25 | walk-forward or backtest; baselines; proper metrics (Brier/AUC/MAE/log loss); calibration; no shuffled `train_test_split` |
| Product | 15 | Streamlit/Dash/FastAPI/Flask; Docker |
| Documentation | 15 | README length; limitations; AI-usage section |
| Ambition | 10 | exogenous data (Telegram, ISW, GDELT, weather, news); gradient boosting; calibration |
| Iteration bonus | 5 | commit count (capped at 15) |

**Validation against ground truth: it fails.** The confirmed passer scores 54.4, ranking 81 of 190. Use this score as a coarse filter for technical depth, not as a pass predictor.

### 2.2 What passing probably depends on

This rubric is inferred from KSE's text and the passer, and is not validated.

| Signal | Why we think it matters | Visible proxies in a repo |
|---|---|---|
| **Iteration with the AI and correcting it** | stated as the primary signal | decision/process logs with "wrong #n" entries; before/after numbers; pivots documented ([AndriyTkh](https://github.com/AndriyTkh/kse-summer-sch) `claude/pr-writedown/`, [maranferij](https://github.com/maranferij-lang/Ukraine-air-alerts) `PROCESS_LOG.md`, [spryima](https://github.com/spryima/kse-air-raid-predictability) `AI_DECISIONS.md`, [nitatsuu](https://github.com/nitatsuu/Kizashi) "Key decisions") |
| **Challenging hallucinations** | stated | catching the "feed died" myth; checking an API's claims against raw samples ([recruitabx](https://github.com/recruitabx/airraid-propagation-analysis) `AI_LOG.md`: "don't invent schemas, show raw samples first") |
| **A working, usable artifact** | stated ("final, working Python code"); the passer is a working app | runs from the README; no missing modules; no placeholders |
| **Honesty** | the passer's README has a "Known limitation" section | limitations; negative results reported; test-set disclosure ([kervad28](https://github.com/kervad28-debug/air-raid-alert-next-day-prediction)) |
| **Brief compliance** (new for October) | the October brief adds "latest data", "latest period" and "no leakage" explicitly | test window ends near submission; leakage tests; publication-time alignment |

## 3. The strongest solutions and what to borrow

Ratings are LP / T. "Oct" means our cohort. File paths are relative to each repo's root.

### Tier S

- **[maranferij-lang/Ukraine-air-alerts](https://github.com/maranferij-lang/Ukraine-air-alerts)** (Oct, 5/5). Best data forensics.
  - **Findings about the data:**
    - the 38% duplicates come from upstream re-running in append mode;
    - an outage mask for 2026-08-29 → 09-02;
    - it notices the 2026-09-07 freeze;
    - it rejects the volunteer feed with evidence: Cohen's κ against official falls from 0.98 to 0.42, and a substring parser bug mislabels Lviv and Volyn;
    - it finds 253 unflagged +1 h end times.
  - **Targets:** an oblast counts as under alert when at least half its raions are (`src/panel.py`). Exact "active" vs "new start" targets via `searchsorted` (`src/targets.py`).
  - **Leakage check:** `scripts/check_no_peeking.py` rebuilds every feature from data truncated at t and asserts equality, with negative controls.
  - **Result:** within-oblast AUC **0.688 / 0.645 / 0.639** at H = 1 / 3 / 6 h on the last 24 usable days, against "train frequency" at 0.495 / 0.581 / 0.612. A plain logistic regression matches the Brier but not the ranking. Verified in the README.
  - **Process:** `CLAUDE.md` holds the rules for the agent; `PROCESS_LOG.md` records rounds with "Wrong #n" findings.
- **[Ddrakkx/alerts-forecast](https://github.com/Ddrakkx/alerts-forecast)** (Oct, 5/5). Best evaluation protocol.
  - **Test design:** onset at 15 min–6 h for 4 oblasts. Test block = **last 8 weeks (2026-08-14 .. 2026-10-09)**, verified. Validation is the previous 8 weeks, purged by H.
  - **Strict reference:** reports both the no-hindsight best baseline and the best baseline chosen on test.
  - **Leakage tests:** `src/alerts_forecast/leakage.py` + `tests/test_leakage.py`, a truncation test with adversarial moments and a planted-leak positive control.
  - **Baselines:** `baselines.py` has the `recent_level` rate baseline (3/7/14/30 days, refit daily).
  - **Uncertainty:** paired ISO-week block bootstrap.
  - **Process:** `docs/decisions.md` records retractions, external-review fixes, and a **pre-registered** holdout on the next data snapshot (git tag `holdout-freeze`).
  - **Live record:** `demo/live_forecast.py` keeps a live, pre-registered forecast log; `demo/emap_logger.py` starts *logging* yellow/red levels.
  - **Result:** honestly reported as mostly negative (Poltava).
- **[lbgos/AirAlerts](https://github.com/lbgos/AirAlerts)** (Oct, 5/5). Best deployable nowcaster.
  - **Data:** scrapes Telegram itself, up to 2026-10-09. Works on a 5-minute grid, for siren starts and all-clears from 15 min to 6 h.
  - **Split:** purged train / calibrate / test; a separate dev window; the final 14-day test run once. Brier skill vs climatology, e.g. 1 h: 0.118 vs 0.164, AUC 0.88.
  - **Calibration:** a cautious calibrator capped by a Wilson bound.
  - **Text:** radar posts labelled once by an LLM, then distilled into a small local classifier.
  - **Live scoring:** a live prediction log, scored afterwards.
  - **Ablation:** radar text adds nothing once neighbour sirens are features.
  - Paths: `src/ua_alert_forecast/{model,dataset,alerts,radar,live}.py`, `reports/experiments*.md`.
- **[spryima/kse-air-raid-predictability](https://github.com/spryima/kse-air-raid-predictability)** (Jun, 5/5). Gold standard for decision logging.
  - **Decision log:** `AI_DECISIONS.md`, each entry going proposal → risk → validation → result → adjustment.
  - **Reproducibility:** SHA-256 pinned inputs.
  - **Targets:** union onsets.
  - **Evaluation:** 12 rolling monthly folds with a 6-hour purge.
  - **Diagnostic:** `src/between_within_diagnostic.py` shows most "skill" is just region and month prevalence, a must-have sanity check.
- **[Trigger111/ukraine-air-raid-alerts-tsa](https://github.com/Trigger111/ukraine-air-raid-alerts-tsa)** (Jun, 5/4). Model process.
  - **Data:** deduplication (~42%), data pinned by commit and SHA-256 (`data/meta.json`), and "oblast union time" as a metric that survives the raion reform (`src/aggregate.py`).
  - **Verdict:** a skill bar agreed in advance (`src/model.py::_verdict`), with an honest "doesn't beat baselines".
  - **Reflection:** `reflection.md`, about 100 words, exemplary.
- **[AndriyTkh/kse-summer-sch](https://github.com/AndriyTkh/kse-summer-sch)** (Jun, 5/4). Most legible AI process.
  - **Session export:** `scripts/export_sessions.py` → `_sessions/INDEX.md`, sessions ranked by how much the human typed.
  - **Documented pivot:** a "hollow headline" catch drove the switch from "is there an alert" to onset.
  - **Caveat:** its Kaggle missile features are keyed on event time, not publication time, so they leak; some configuration was tuned on test.
- **[tbaraniuk/air_alert_analysis](https://github.com/tbaraniuk/air_alert_analysis)** (Jun, confirmed passer, T 2).
  - **What it has:** a clean ingester (pydantic, tenacity, DuckDB upsert), correct UTC→Kyiv SQL and an honest "Known limitation" note.
  - **What it lacks:** forecasting and evaluation.

### Tier A

| Repo | Cohort | LP/T | Why it matters | Borrow |
|---|---|---|---|---|
| [robotheist/Air-alerts-forecast](https://github.com/robotheist/Air-alerts-forecast) | Oct | 4/5 | **Best text experiment.** @kpszsu posts via `t.me/s` mapped to regions with a gazetteer (with Ukrainian case forms). 32% of onsets have a channel mention in the prior 30 min, vs 18% of random moments. Validation Brier improved 2.4% at h = 1, but on the test month the gain fell to **0.4% and is not significant**. "Lead time is minutes, not hours." Scores quiet origins separately. | `src/airalerts/text_features.py`, `tests/test_leakage.py::test_text_features_do_not_see_the_future`, `scripts/05_text_lead_time.py`, `scripts/06_significance.py`, `docs/experiment_log.md` |
| [Dopplerr24/air-raid-alert-analysis](https://github.com/Dopplerr24/air-raid-alert-analysis) | Oct | 4/5 | Panel leakage guards that abort training on failure. Walk-forward 2025-06 → 2026-09 with a 24 h embargo. Per-region persistence and hour-of-week climatology. Diagnoses per-region miscalibration caused by the raion switch. | `proj/features.py` (`_past`, `check_causality`, `check_region_isolation`), `proj/model.py` |
| [olehm208/air_alert_ai_analysis](https://github.com/olehm208/air_alert_ai_analysis) | Oct | 4/4 | Labels are used only after their window has passed. Models selected per fold on validation only. Perturbation tests: a future event must not change features at t. | `forecasting.py`, `test_v3_backtesting.py`, `ai_usage.md` |
| [chud00s/tryvoha-radar-tsa](https://github.com/chud00s/tryvoha-radar-tsa) | Jun | 4/4 | Calibrated 6-hour per-oblast risk with neighbour features and isotonic calibration. README: AUC 0.878 / Brier 0.141 vs climatology 0.827 / 0.174, test 2025-08 → 2026-06. Detects mass-attack and surprise days. **But it uses the volunteer feed without saying so.** | `src/features.py`, `src/forecast.py`, `src/analysis.py`, `app/dashboard.py` |
| [mseheda/airraid-ts](https://github.com/mseheda/airraid-ts) | Jun | 4/4 | An acceptance gate frozen before modelling and built so it can't be gamed: beat the best baseline by at least 5% in at least 8 of 12 folds. CRPS against dispersion-matched baselines. Red-team subagents. Honest null. | `src/contract.py`, `src/prob_eval.py`, `.claude/agents/red-team.md`, `ai-log/render.py` |
| [umunevich/air-raid-alerts-analysis](https://github.com/umunevich/air-raid-alerts-analysis) | Jun | 4/4 | Exposure target for 1–24 h, conditional persistence, isotonic calibration on validation. Found non-monotone horizons: P(N+1) < P(N) in 606 of 672 rows. Cursor log exported to markdown. | `transform/panel.py`, `models/baselines.py`, `models/calibration.py`, `scripts/export_chat_history.py` |
| [iuad0qll/KSE_analytics](https://github.com/iuad0qll/KSE_analytics) | Jun | 4/4 | Naive summing overstates time under alert **2.1×, and 4.1× in 2026**. Hawkes process with a goodness-of-fit test. DST audit checks. Model reflection. | `minutes_overlap_compare.py`, `hawkes_analysis.py`, `audit_checks.py`, `reflection.txt` |
| [tymof1j/ai-stage2](https://github.com/tymof1j/ai-stage2) | Jun | 4/4 | Forecasts the raion-era **share of raions under alert**. Ridge reaches skill 0.245 vs persistence at h = 1 (MAE 0.0439 vs 0.0581) on the last 30 days, verified in `site-data/forecast.json`. Counterfactual "exposure saved by raion-level alerts". Quarto site. | `src/intervals.py`, `src/analysis.py`, `src/forecast.py` |
| [recruitabx/airraid-propagation-analysis](https://github.com/recruitabx/airraid-propagation-analysis) | Jun | 4/4 | Lead-lag between oblasts against a circular-shift null, with wave control; re-validated on the alerts.in.ua API; Telegram bot. | `analyze.py`, `validate.py`, `AI_LOG.md` |
| [nitatsuu/Kizashi](https://github.com/nitatsuu/Kizashi) | Jun | 4/3 | Every caught error logged with before/after numbers. A persistence off-by-one had inflated the margin from +0.03 to +0.11. Ships the raw session JSONL. **Its test is in 2025, not the latest period.** | README "Key decisions", `log/session.jsonl` |
| [goodfrog33/air-raid-forecasting-ukraine](https://github.com/goodfrog33/air-raid-forecasting-ukraine) | Jun | 4/4 | Interval-merge cleaner with an audit trail; live Streamlit Cloud app and FastAPI. **But its targets are persistence-dominated, it selects models on the backtest folds, and its holiday features are empty.** | `data/clean.py`, `evaluation/backtest.py`, `REFLECTION.txt` |
| [HoiSerhii](https://github.com/HoiSerhii/air-alerts-analysis), [Freit007](https://github.com/Freit007/air-alert-analytics), [Semfayni](https://github.com/Semfayni/Air-Raid-Analysis) | Jun | 4/3 | **Passer-shaped:** modest descriptive apps with correct dedup and episode merging. HoiSerhii includes a verbatim AI log. Semfayni has a live alerts.in.ua map. | `src/timeutils.py` (DST-safe), `live_api.py`, `scripts/cross_check.py` |
| [slobodskyi/tsa-air-raid](https://github.com/slobodskyi/tsa-air-raid) | Jun | 3/4 | Best rollup to oblast level (2-minute tolerance union). Count view and burden view (drop vs clip at 24 h). Bootstrap CI on the gain. Metrics split before and after the reform. | `src/aggregate.py`, `src/data_loader.py`, `src/forecast.py` |
| [petroltradesupply-dotcom](https://github.com/petroltradesupply-dotcom/time-series-air-raid-alerts-ua) | Jun | 3/3 | **The only one to splice** Vadimkin history with a fresh alerts.in.ua month and check the seam on the overlap. | `src/build_spliced.py`, `src/compare_sources.py` |

**Not KSE submissions, but worth borrowing from:**
- [rayhankhilji/terrestrial](https://github.com/rayhankhilji/terrestrial): issue-time features; exogenous data lagged by its *publication delay*; a conditional-persistence baseline; a model card with a "beats baselines" flag. It does leak observed weather.
- [Nazar32/forecast-driven-route-selection](https://github.com/Nazar32/forecast-driven-route-selection), IEEE Access code: a **rolling 42-day Markov-chain baseline beat their ML**. Also pre-registration rounds and daily per-unit logit recalibration.
- [bratxja-cmd/hromady-alarms](https://github.com/bratxja-cmd/hromady-alarms): a daily GitHub-Actions collector that accumulates alerts.in.ua history beyond its 1-month window.

## 4. Common mistakes, by frequency

1. **The `level=='oblast'` trap.**
   - Every oblast except Kyiv City disappears after about November 2025.
   - Our verification on the official CSV: the last oblast-level rows fall between 2025-08-20 and 2025-11-04, depending on the oblast.
   - Affected repos include Yaroo-a (Oct), koalla05 (Oct), Heir-of-God, uiuxdesigner18, Python-UA, borovkov-d, zadorozhna-dariia, PrepAIre-edu and others.
2. **Accepting "the official feed died after Oct 2025".** dukarev "proved" it with confirmation-biased checks, and borovkov-d, zadorozhna, Vlad1343, monsterkokoko and mykoladomanskyi truncated their data because of it. This is an unchallenged hallucination, precisely the failure KSE probes.
3. **No deduplication.** Every record before 2026-01-25 appears exactly twice, which doubles counts and fakes a 2026 "drop".
4. **Summing overlapping raion/hromada rows instead of taking the union.** This inflates alert time 2.1–4.1×. One repo read it as a "3× escalation" (sergkern1).
5. **Persistence-dominated targets** ("alert active within window"). They produce high AUCs that are mostly persistence: goodfrog33 0.915 vs 0.78, tanchikr12 0.90, MaksimPrykhodko's "100% precision", which is a target leak via `hours_since_last_alert = 999`. The fix is onset-from-quiet targets or scoring quiet origins separately.
6. **Selection on the test window** (models, configurations, thresholds, early stopping): goodfrog33, asobkiv, egorcusai, mashta-lilia, oleksandrsafandula, MaksimPrykhodko.
7. **Not evaluating on the latest period**, through deliberate cutoffs (nitatsuu, denkor, MishaDvali, andrii-kondratok and others) or whole-history CV.
8. **Exogenous data joined on event time instead of availability time.**
   - Kaggle missile rows (AndriyTkh). These are published around 09:20 Kyiv the next morning.
   - Observed weather for the target day (terrestrial, mokliak, timkaster).
   - Same-day news (mokliak).
   - Google Trends normalised over the whole window (sasha2lapina).
9. **Timezone slips:** fixed UTC+2 or UTC+3 instead of `Europe/Kyiv`, and UTC days used as calendar days. Seen in Mafusail2020, HATSKER-228, Nzrch, sergkern1 and others.
10. **The volunteer feed treated as ground truth.** It covers about 35–60% of official alert time, and its parser has bugs. Only maranferij measured this.
11. **Missing, weak or buggy baselines**, such as Prophet with no naive comparison or a persistence off-by-one.
12. **Hygiene:**
    - synthetic or mock data (Solomiia27, iamanavor-droid, colobocman);
    - a hallucinated API (sergii-brt);
    - missing modules (Hroback);
    - AI template text left in the README;
    - `C:/Users/...` paths;
    - committed `__pycache__` and `.idea`.
13. **Over-engineering in place of analysis:** K8s/Redis on 55 rows; FastAPI around empty modules; a GNN with no baselines.
14. **Silent empty holiday features.** `holidays.country_holidays('UA')` returns no holidays under martial law unless you pass `categories=('public','workday')`.

## 5. Gaps nobody filled (our openings)

| # | Gap | Why it matters for our brief | Feasible in about 1.5 days? |
|---|---|---|---|
| 1 | **Bridging the 2026-09-07 official freeze.** Sources: alerts.in.ua `month_ago`, the JustJimer archive, map.ukrainealarm ranged history, Kyiv Digital, with seam validation. | "Most recent data" and "latest period" are explicit in the October brief. Every October repo either stops at the freeze or falls back to the incomplete volunteer feed. | Yes. Seam-check recipe exists in petroltradesupply; sources in data-sources.md. |
| 2 | **Yellow/red levels and threat types**, since 2026-09-07 (Resolution 1092). | A brand-new regime that nobody analysed. Ddrakkx only *logs* levels; lbgos parses them only to define starts. | Descriptive analysis: yes. As a target or feature: limited, with about 5 weeks of data. |
| 3 | **Point-in-time availability of the history.** A Vadimkin row appears only after the alert ends plus a daily batch run, a lag of up to about 29 h. Telegram posts are edited after the fact. | The literal no-leakage rule: "nothing … may come from after the time at which the forecast is made". | Yes: simulate an availability lag and mask edits (`edit_date`). |
| 4 | **Leak-safe exogenous data:** Open-Meteo Previous Runs (archived forecasts); Air Force summaries at their publication time; martial-law holidays. | The optional text/media part done *correctly*. Everyone who used weather used observed values. | Partly. Weather and holidays are cheap; publication-time text is moderate. |
| 5 | **A regime-aware evaluation:** pre- and post-raion reform, and pre- and post-level reform, evaluated separately. | Explains drift, the failure KSE expects candidates to diagnose. | Yes. |
| 6 | **Strong simple baselines:** a rolling Markov chain / semi-Markov on-off model and a `recent_level` rate. | ML often fails to beat these (Nazar32, Ddrakkx). Beating them, or showing honestly that you can't, is credible. | Yes. |
| 7 | **Monotone multi-horizon probabilities** (cumulative-hazard formulation). | umunevich found P(N+1) < P(N) in 606 of 672 rows. | Yes. |
| 8 | **Raion-level forecasting.** | The reform made raions the operational unit. | Risky in the time we have. |
| 9 | **Decision-oriented evaluation:** warning lead time, recall at a fixed false-alarm rate, a backtested decision policy. | "Real-world defense problem" framing. | Partly. |
| 10 | **A standing-alert registry:** frontline hromadas under alert for months. | Breaks unions and onset targets in frontline oblasts. | Yes, as a cleaning step. |
| 11 | **Coverage comparison of sources** (official vs volunteer vs alerts.in.ua) on the same window, before choosing labels. | Choosing labels on evidence, not by default. | Yes. |

## 6. Implications: what is likely to pass, and what would add real value

_Our read, now checked against our own measurements in [feasibility.md](feasibility.md):_
- **Data:** the official map's ranged-history endpoint gives keyless raion-level history from 2025-10-03 to now. It matches Vadimkin with Jaccard 0.994 and JustJimer with 0.998, so the freeze can be bridged.
- **Start forecast works:** "a new alert starts within 1/3/6 h", tested on 2026-09-13 → 10-10, beats a 28-day oblast×hour baseline by +0.12 / +0.15 / +0.18 Brier skill, with all confidence intervals excluding zero.
- **The other targets don't:** "any alert tonight" and daily alert-minutes are not reliably better than the baseline.
- **Text adds little:** @kpszsu threat-post features improve the start forecast by only 1.8–2.5%.

1. **Process first.** KSE grades the log.
   - Make the iteration visible: a `PROCESS_LOG.md` or decision log (proposal → risk → check → result → adjustment) with explicit "Wrong #n" entries and before/after numbers. Pre-register the evaluation (a frozen skill bar or holdout).
   - In the log, ask for raw samples before trusting a schema, and challenge claims like "the feed died".
   - This conversation is part of the log, and so is the research trail in `research/`.
2. **Meet the October brief literally.**
   - Data that runs past 2026-09-07, stitched with a validated seam.
   - A final test on the last weeks before submission, run once.
   - A truncation leakage test.
   - Text, if used, aligned on publication time with edits masked.
3. **Pick a framing where honest results are possible.**
   - Short-horizon onset (1–6 h) from a quiet state per oblast has real but modest signal. Prior work reports AUC from about 0.64 within-oblast to about 0.88 across oblasts, depending on the metric.
   - Daily or next-day targets mostly lose to persistence.
   - A clearly reported null is acceptable; several strong repos did exactly that.
4. **Differentiate on the gaps**, not on dashboard polish.
   - Bridging the freeze (gap 1) plus a regime-aware evaluation including the new levels (gaps 2 and 5) is a combination nobody has.
   - Text is optional and probably low-gain at short horizons (lbgos, robotheist). If we test it, do it cleanly and report the null.
5. **Keep the artifact small and working.** The passer was modest. A runnable `main.py` with clear output and a lean README beats an MLOps facade.
