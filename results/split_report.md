# What is wrong with the split, and what is already chronological

**Resolution (2026-10-11):** fixed as [PROCESS_LOG, Decision 4](../PROCESS_LOG.md) describes. `Split` and its purge are kept; forecast rows are sorted by time; sequential forecast checks are in `Split.forward`; AV holds out time blocks; all 24 oblasts are evaluated, each with its own counts.

Date: 2026-10-11. This review covers split membership, fold construction, geographic selection, label windows, row order, date choices and evaluation disclosure. Exact pre-cutoff checks are in [split_audit.json](split_audit.json); AV interventions are in [leakage_report.md](leakage_report.md).

## Direct answer

**The primary forecast train/val/test split is chronological and does not randomize membership. The randomization error is in the auxiliary AV folds.** Other concrete problems are that the forecast table is not globally time-sorted, the reported evaluation covers only 21 of the 24 forecast regions, and the historical period named `test` has already informed the research. The short validation period and its dual role in selection/calibration are additional evaluation limitations.

The main split is not made by oblast, by the target, by a percentage of rows, or by stratification. [`Split.rows`](../alerts/splits.py) uses only forecast timestamp `ts` and forecast horizon `H`:

```text
part_start <= T AND T + H <= part_end
```

All oblasts use the same boundaries. For H = 1/3/6 hours, the current real-data check finds **zero timestamps shared between parts and zero selected label windows crossing a boundary**. The existing synthetic split tests also pass: `2 passed`.

## Actual boundaries and their reasons

All calendar dates below are in Europe/Kyiv; the cutoff is also shown in UTC.

| Part | Forecast-time period, before its horizon purge | Reason in the repository |
|---|---|---|
| Train | 2025-11-15 00:00 → 2026-08-29 00:00 | Start after raion-level coverage reached all 23 included oblasts; inherit the probe's train/dev boundary. |
| Val | 2026-08-29 00:00 → 2026-09-13 00:00 | The probe defines dev as exactly 15 days before its hard-coded test start. Current code retains that window for step-3 choices and calibration. |
| Historical test | 2026-09-13 00:00 → 2026-10-10 22:03 | Inherit the probe's latest evaluation window and stop at the snapshot cutoff, 2026-10-10 19:03 UTC. |

The November start has a data reason: the latest first observed raion alert among the 23 oblasts in the map snapshot is Ternopilska, **2025-11-06 09:07:38 UTC**. The nine-calendar-day buffer is also sufficient for the 7-day trailing features. These are first observations in the snapshot, not a proof of an administrative rollout time. Kyiv City is a separate 24th series and does not require raion records of its own.

The August/September boundaries are inherited experimental choices. `research/probe/model.py` sets `TEST_START = 2026-09-13` and `DEV_START = TEST_START - 15 days`; `alerts/splits.py` copies the resulting dates. There is no code deriving those dates from geographic balancing or evidence that 15 validation days are optimal. In the old alternative-source probe there was also a Vadimkin/map splice on 2026-08-29, but the **current** map/API splice is 2026-09-12 00:00 Kyiv. Source selection and forecast split assignment are different operations.

## Confirmed problems

### 1. AV folds mix time and related oblast rows

[`AdversarialValidation.run`](../alerts/checks.py) first concatenates earlier and later periods, labels them 0/1, then applies `StratifiedKFold(..., shuffle=True)`. Stratification preserves the earlier/later class proportion, not temporal order or oblast grouping. Thus fit can contain later observations than a held observation, another oblast at the same timestamp, and the same oblast at a neighbouring timestamp.

In the actual folds, 99.993% of held rows share a timestamp with some fitting row; about 93.5–93.7% have a fitted same-oblast neighbour within one 30-minute step. National features are identical across oblasts at T, and trailing load features heavily overlap over time. This makes near-perfect AV substantially easier than discriminating independent unseen time blocks.

This random AV does **not** change the primary forecast train/val/test membership. Its defect is interpreting the auxiliary out-of-fold AUC as an independent-period or forward-generalization result. The blocked experiments in the previous audit are sensitivity checks; some fits include dates later than the held block, so **they are not a corrected forward forecast split either**.

Simply changing `shuffle=True` to `False` does not solve this: a k-fold scheme can still fit on later blocks and does not become forward chaining. Conversely, replacing AV with ordinary forward `TimeSeriesSplit` over the concatenated periods is not a drop-in fix: early fitting prefixes contain only the earlier-period class, so a two-class AV classifier cannot be fitted. AV needs its own clearly described blocked diagnostic protocol; forecast performance needs chronological forward evaluation.

### 2. The table is ordered by oblast before time

[`Features.at`](../alerts/features.py) creates all times for one oblast, then all times for the next (`np.repeat(oblasts, len(times))`, `np.tile(times, n_oblasts)`). `ForecastTable` keeps that order. The real-data check confirms that each selected train/val/test table has `ts.is_monotonic_increasing == False`.

This does not invalidate the existing timestamp-filtered `Split.rows`, nor fitting a tree model on the selected train rows. However, any future index-based chronological CV or percentage-of-rows split on this table would divide oblast-major rows rather than a global timeline. Before such CV, sort by `(ts, obl)` and split unique timestamps or complete day blocks, keeping all rows at T together. Disabling row shuffling alone cannot establish time order.

### 3. The historical `test` is already seen

The feasibility research scored 2026-09-13 → 2026-10-10 for multiple targets, models and text variants. Its findings helped choose the current task and omit text. `PROCESS_LOG.md` already discloses this period as seen. The split is therefore a valid chronological **historical evaluation window**, but it is not an untouched final test of the resulting project decisions.

No date change can make those observed outcomes unseen again. Reserve subsequent data/live logged forecasts for final verification, freeze decisions beforehand, and describe the old period honestly. This audit does not read or score post-cutoff event outcomes. The duration and data sufficiency of the future holdout remain to be checked at the final-run step; a short holdout cannot support a broad accuracy claim merely because it is untouched.

### 4. Reported geographic coverage differs from the full forecast table

The main table includes **24 series: 23 oblasts and Kyiv City**. The feasibility model, its acceptance comparison and the AV reproduction exclude three oblasts selected on **train only** by `share_under_alert >= 0.8`:

| Excluded oblast | ID | Current train time under alert | Clear forecast rows, train / val / historical test, H = 6 h |
|---|---:|---:|---:|
| Dnipropetrovska | 9 | 89.29% | 1,435 / 21 / 59 |
| Kharkivska | 22 | 81.92% | 2,443 / 30 / 115 |
| Donetska | 28 | 88.47% | 1,555 / 29 / 36 |

The current train data reproduce the same excluded IDs. This is **dataset selection, not geographic splitting**, and it does not use val/test to choose the exclusions. Its reason is that the task is conditional on the oblast being clear, so these almost continuously active series contribute very few later evaluation rows. The 80% cutoff is a heuristic; it does not prove that forecasts are impossible for them.

The problem is scope: results on 21 regions cannot establish forecast quality for all 24. The evaluation protocol must either include the three with explicit per-region support/uncertainty, or explicitly scope the fitted forecaster and its quality claim to the supported regions. Currently `Split.rows` and `ForecastTable` do not themselves enforce the 21-region mask; it is hard-coded in the probe reproduction and audit. The step-3 implementation must make the forecast/evaluation population consistent.

National and neighbour features still use past observations from all 24 series, including the three excluded from scored rows. That is legitimate contextual input available before T, not future leakage. Keeping the same known oblast in train and later val/test is also appropriate for predicting its future; a held-out-oblast experiment would answer a different question about forecasting unseen regions.

## Other factors and their status

| Factor | What the check establishes | Consequence |
|---|---|---|
| Label horizons | Rows are purged until `T + H <= boundary`, for H = 1/3/6 h. | Existing membership rule is correct, including equality because the target window is `[T, T + H)`. |
| Trailing 7-day history crossing into a later part | Val/test features can read earlier observed history, always before their own T. | This is valid for forward forecasting. A 7-day gap between forecast parts is not automatically required; do not confuse the AV independence experiment with label purging. |
| Effective validation size | Val spans 15 calendar days; 10,459 scored rows for 21 regions share events, overlapping target windows and national waves. | Row count overstates independent support. Uncertainty should respect time blocks; one short window cannot test robustness across regimes. |
| Selection and calibration | Project plan assigns both to the same 15-day val; the probe fits Platt on dev and scores later test. | Calibration on earlier dev followed by later testing is valid. If step 3 selects models using loss on those same calibration-fit rows, that loss is in-sample for the calibrator. Use chronological internal selection/calibration separation or forward out-of-sample predictions; do not report calibration-fit loss as an independent validation score. No such step-3 implementation exists yet. |
| Regime change | Train/val/test starts per oblast-day are 2.53 / 4.53 / 5.58; alert fractions are 0.194 / 0.301 / 0.343. | This is a real difficulty a latest-period chronological split should expose, not something to remove by random stratification. Whether recent weights help is a val experiment. |
| September level reform and source splice | Val includes the level reform and its last day overlaps the map/API splice; historical test is after both. Map-only AV is virtually unchanged. | The dates do not isolate these effects. They warrant separate descriptive regime/source checks, but the splice is not necessary for AV ≈ 1. Levels are not forecast features. |
| Historical revisions and API delays | The normalized history keeps final versions; truncation uses event times. | Chronological row assignment alone cannot guarantee input availability at T. This remains a data-provenance limitation, not a demonstrated split-membership error. |

## Evaluation contract required next

For the forecast, use sorted unique timestamps and shared time boundaries for every included oblast. Every fit/calibration stage may use only rows with labels mature before its cutoff. Model selection should use earlier forward validation windows; final calibration must precede final testing. Decide and disclose the geographic population before evaluating it. The seen September/October window remains a historical benchmark, while genuinely later outcomes remain the final check.

The corrections needed are to the **AV fold protocol and its interpretation, future time-order assumptions, geographic evaluation scope, and test disclosure**. Replacing the existing timestamp membership filter with a geographic or random split would make forecast evaluation less faithful to the task.
