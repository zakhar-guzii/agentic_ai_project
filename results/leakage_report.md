# Leakage audit and the cause of the near-perfect adversarial AUC

**Resolution (2026-10-11):** AV now holds out time blocks with a 7-day gap ([PROCESS_LOG, Decision 4](../PROCESS_LOG.md)): train vs test, 24 oblasts, AUC 0.944. The endpoint numbers below remain sensitivity diagnostics, not a forecast estimate.

Date: 2026-10-11. Scope: the existing step-2 features, baselines, chronological split and AV diagnostic. No forecast model was fitted or selected in this audit.

The follow-up [split review](split_report.md) distinguishes the chronological forecast partitions from shuffled AV folds, verifies the geographic exclusions and identifies the limits of the period named `test`.

## Finding

**No event-time look-ahead was detected in the tested features and climatology, and forecast label windows do not cross split boundaries. The near-perfect AV is substantially inflated by random folds over dependent time-series rows, alongside a real increase in alert load.** This is a problem with interpreting the AV diagnostic as evidence of independent-period generalization; it is not evidence that future forecast targets entered the features.

There is a separate, unresolved availability-time risk: historical records are final versions, and the audit cannot reconstruct when each field first reached the live API. Passing event-time truncation does not rule this out.

## Reproduction

Run from the repository root, offline:

```sh
.venv/bin/pytest -q tests/test_leakage.py tests/test_splits.py tests/test_drift.py
.venv/bin/python results/audit_leakage.py
```

The tests returned **9 passed** (one joblib CPU-detection warning). The audit's exact metrics, feature gains, fold sizes and availability summary are saved in [leakage_audit.json](leakage_audit.json). The script asserts unique `(oblast, T)` rows, label maturity inside each split, and the absence of targets, timestamps and source/version fields from the feature list.

The AV reproduction uses the same 21 oblasts as the logged experiment (excluding 9, 22 and 28, as the probe decided on train), 30-minute forecast rows, a common 6-hour label purge and the existing fixed 300-tree settings. Only the thread count is limited to two. Train/val/test contain 232,474 / 10,459 / 18,209 rows. All analyzed event windows end at or before `MAP_CUTOFF = 2026-10-10 19:03 UTC`; the subsequent holdout is not scored. These are leakage diagnostics on the already-seen test period, not inputs to model selection.

## Why random AV approaches 1

The mechanism starts at [`AdversarialValidation.run`](../alerts/checks.py): `StratifiedKFold(5, shuffle=True, random_state=0)` splits individual rows. However, [`Features.at`](../alerts/features.py) produces many rows for each timestamp, with identical national features across oblasts, overlapping neighbour histories, and strongly overlapping rolling windows across successive moments.

In the actual random folds:

| Dependence between a held row and fitting rows | Train/val | Train/test |
|---|---:|---:|
| Some other row at exactly the same timestamp is fitted | 99.9934% | 99.9936% |
| The same oblast at T − 30 min or T + 30 min is fitted | 93.7394% | 93.5293% |

Successive 7-day windows overlap by 10,050 of 10,080 minutes (**99.70%**). Even successive 3-hour windows overlap by **83.33%**. The combination of oblast, recent local load and national wave therefore acts as a fingerprint of a small time interval. A random-fold AV model can recognize that interval from nearby fitted rows and recover its period label. The exact row is out of fold, but its temporal context largely remains in fit.

The interventions confirm that the issue is broader than either duplicate timestamps or the two 7-day features alone:

| Diagnostic | Train/val AUC | Train/test AUC |
|---|---:|---:|
| Original random rows, all features | 0.999400 | 0.999501 |
| All rows at a timestamp kept in the same random fold | 0.998031 | 0.998459 |
| Random rows, remove `starts_7d` and `alert_min_7d` | 0.992471 | 0.993831 |
| Random rows, only `obl`, `hour`, `dow` | 0.514655 | 0.541761 |
| Hold complete 3-day endpoint blocks, no gap | 0.849078 | 0.910544 |
| Same endpoint blocks, exclude fitting times within 7 days | 0.748524 | 0.892216 |

Grouping timestamps eliminates exact same-time sharing, but leaves neighbouring timestamps in fit. Removing the 7-day columns leaves the correlated 24-hour, neighbour and national features, notably `nat_starts_3h`. Neither intervention makes the rows independent. Calendar and oblast alone have much weaker discrimination; high gain for `obl` in the full model does not establish a geographic shift by itself, because it also supports interactions with each oblast's load fingerprint.

**Endpoint experiment limits.** Two separate fits hold the first and then the last 3 days of both compared periods, with all oblasts held together. With the 7-day gap, fitting times are outside `[block_start − 7 days, block_end + 7 days)` (the earlier equality is allowed), so the trailing feature windows do not overlap. The same held rows are used for the no-gap and gap comparisons. The pooled scores cover only 8,907 rows for train/val and 8,486 for train/test, not the full periods. Individual gap-fold AUCs are 0.890 / 0.615 for val and 0.937 / 0.935 for test; pooled AUC also reflects score-scale differences between fitted models. The gap reduces fitting data, especially in the short val period. Consequently, the decline is a sensitivity result consistent with strong temporal dependence, not an exact decomposition of the original AUC or a forecast-performance estimate. Both periods are represented in fit, including later dates: this is still an AV classification experiment, not forward forecast validation.

This interpretation agrees with the [scikit-learn cross-validation documentation](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-of-time-series-data): random folds over autocorrelated time-series observations give misleading estimates of generalization.

## Real drift remains

The event series and past-only features independently show rising load:

| Metric | Train | Val | Test |
|---|---:|---:|---:|
| Share of time under alert, 21 oblasts | 0.194 | 0.301 | 0.343 |
| Union episode starts per oblast-day | 2.53 | 4.53 | 5.58 |
| Mean `starts_7d` on clear forecast rows | 13.97 | 24.17 | 28.86 |
| Mean `alert_min_7d` on clear forecast rows | 1,185 | 1,798 | 2,071 |
| Mean `nat_starts_3h` on clear forecast rows | 7.82 | 12.83 | 15.69 |
| Base rate of a start within 6 h, purged clear rows | 0.329 | 0.465 | 0.531 |

Episode statistics use all times in each period, not only clear rows. Local feature means are conditional on clear forecast rows; national features still cover all 24 oblasts, as in production. Historical unweighted rates can therefore be too low for the later regime. **AV alone cannot prove that every model fitted on all history will lag or that recency weights improve it.** That model choice must be compared on chronological val against the daily 28-day climatology and `RecentLevel`, using forecast loss and calibration.

## Alternative causes checked

**Future feature values or forecast labels.** [`AlertGrid`](../alerts/features.py) shifts cumulative and last-event arrays so queries at T use minutes strictly before T. Forward windows are used only for `y1/y3/y6`, outside `Features.NAMES`. The existing truncation checks compare full history with history restricted to events before T and unfinished alerts censored at T; they pass on synthetic data and 30 real moments, including starts, all-clears, DST switches and the source splice. The deliberately planted T + 1 min feature leak is caught. This is evidence for the tested event-time behavior, not a proof over every possible input or publication delay.

**Labels crossing train/val/test.** [`Split.rows`](../alerts/splits.py) requires `T + H <= part_end`. The real-data and synthetic purge checks pass for 1/3/6 h. Earlier observations reused in a later period's trailing features are legitimate forecast-time history; this does not require a 7-day gap between actual forecast periods. The extra gap above is for diagnosing AV dependence.

**Source splice as the cause of AV ≈ 1.** Rebuilding the history entirely from the map before cutoff gives train/test random-fold AUC **0.999515**, compared with **0.999501** for the spliced history. Source identity and alert level are not features, and the earlier seam checks found union-state Jaccard about 0.9994. The source switch is not necessary to reproduce the near-perfect AUC, although small timestamp and coverage differences remain.

**Late history revisions.** [`load_api`](../alerts/data.py) keeps the newest saved version of each record and does not retain `updated_at` in the normalized table. [`TruncationCheck.known_at`](../alerts/checks.py) uses event start/end times, not first publication or record-version availability. Among **13,885 completed AIR oblast/raion records across all 24 oblasts before cutoff**, **183 (1.32%)** have `updated_at` more than 60 seconds after `finished_at`. Median update-minus-finish is 3.046 s; the 99th percentile is 77.973 s. An update could also concern another field, so these counts do not prove that an all-clear was unavailable until the update. They identify a risk the existing tests cannot settle. Historical snapshots alone cannot establish the first availability of an end; timestamped live snapshots/version history are needed to validate it. Final alert levels are excluded from the forecast features, so level revisions do not directly enter the current AV.

## Corrected explanation

The reported AV AUCs describe how well random-fold classifiers recognize the recorded periods from correlated load fingerprints. Their near-perfect values combine real escalation with substantial temporal dependence across folds. They do not establish future-target leakage, nor do they measure how an alert forecaster generalizes to a new regime. Event-time leakage checks and horizon purges pass on the tested cases; availability-time leakage from retrospectively revised history remains unverified. The appropriate next model evaluation is chronological, with matured training labels and calibration data, and weighting decisions made on val rather than on AV or test.
