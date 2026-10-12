# Holdout report

The untouched holdout: everything after the map cutoff, never used for a decision before this run.

Generated offline, once, by `python main.py holdout` at commit `4d116ee3cfd03df4fd8e1d3f3079252e9e6d889f`; pre-registered at `7ff31a24476be57ca7f81fe3bf1c7f52c32a7094` (PROCESS_LOG, Decision 10).
Window: T from the map cutoff 2026-10-10 19:03:00+00:00 to 2026-10-12 12:43:00+00:00, where the saved alerts.in.ua data end; for horizon H only rows with T + H inside it. Rows, references and scores as in the benchmark: 30-min moments, regions clear at T, all 24 regions, daily clim28 and recent7, Brier, 1,000 whole-Kyiv-day bootstrap resamples (seed 0).
Model: `models/logistic.joblib`, SHA-256 `ffbce213e5e203c6246c2c2e8f4bfb4461349a5837545e487467973b18219243`, as frozen in step 3: no refit, no recalibration.
With about three Kyiv days the day bootstrap has very few days to resample: its intervals are wide and the registered bar is expected to be inconclusive. It is reported as registered.
History holds final API revisions (see the revision check below), as in the benchmark.

## Pooled

| horizon | n | base_rate | model | clim28 | recent7 | skill_clim28 | skill_recent7 |
|---|---|---|---|---|---|---|---|
| 1 h | 1089 | 0.3379 | 0.1794 | 0.1931 | 0.1811 | +0.0707 [+0.0611, +0.2451] | +0.0093 [+0.0015, +0.0932] |
| 3 h | 1036 | 0.6004 | 0.1585 | 0.1982 | 0.1529 | +0.2003 [+0.1104, +0.5997] | -0.0364 [-0.1805, +0.3044] |
| 6 h | 964 | 0.7531 | 0.1178 | 0.1740 | 0.1017 | +0.3230 [+0.2856, +0.5061] | -0.1582 [-0.6373, +0.0690] |

Registered bar (both lower bounds > 0 on at least two horizons): per horizon {1: True, 3: False, 6: False}; **FAIL**.

## Horizon 1 h: per Kyiv day

| day | n | base_rate | model | skill_clim28 | skill_recent7 |
|---|---|---|---|---|---|
| 2026-10-10 | 40 | 0.3750 | 0.1434 | 0.2451 | 0.0932 |
| 2026-10-11 | 647 | 0.3338 | 0.1718 | 0.0611 | 0.0100 |
| 2026-10-12 | 402 | 0.3408 | 0.1953 | 0.0685 | 0.0015 |

### Per region (1 h)

| obl | region | n | base_rate | brier | skill_clim28 | skill_recent7 | quality |
|---|---|---|---|---|---|---|---|
| 3 | Хмельницька область | 60 | 0.3667 | 0.2225 | 0.2289 | 0.0957 | quality not verified |
| 4 | Вінницька область | 46 | 0.5217 | 0.2762 | 0.2529 | 0.0157 | quality not verified |
| 5 | Рівненська область | 64 | 0.3281 | 0.2051 | 0.1440 | 0.0776 | quality not verified |
| 8 | Волинська область | 74 | 0.1622 | 0.1349 | 0.0469 | 0.0242 | quality not verified |
| 10 | Житомирська область | 45 | 0.6000 | 0.2648 | 0.0933 | -0.0578 | quality not verified |
| 11 | Закарпатська область | 81 | 0.0000 | 0.0001 | -0.2862 | nan | quality not verified |
| 12 | Запорізька область | 3 | 1.0000 | 0.0150 | 0.6179 | -5.9202 | quality not verified |
| 13 | Івано-Франківська область | 78 | 0.0513 | 0.0510 | -0.0539 | -0.0437 | quality not verified |
| 14 | Київська область | 20 | 0.8500 | 0.2010 | -0.4624 | -0.4351 | quality not verified |
| 15 | Кіровоградська область | 34 | 0.6765 | 0.2422 | 0.2715 | -0.0596 | quality not verified |
| 17 | Миколаївська область | 44 | 0.5682 | 0.2247 | 0.0052 | 0.2354 | quality not verified |
| 18 | Одеська область | 65 | 0.3692 | 0.3463 | -0.3556 | -0.2937 | quality not verified |
| 19 | Полтавська область | 48 | 0.5208 | 0.2782 | -0.1803 | -0.1053 | quality not verified |
| 20 | Сумська область | 28 | 0.6429 | 0.2483 | -0.0690 | 0.1091 | quality not verified |
| 21 | Тернопільська область | 73 | 0.2877 | 0.2047 | 0.2209 | 0.0824 | quality not verified |
| 22 | Харківська область | 6 | 1.0000 | 0.0136 | 0.1929 | -101.9674 | quality not verified |
| 23 | Херсонська область | 55 | 0.4909 | 0.2598 | 0.0131 | 0.1329 | quality not verified |
| 24 | Черкаська область | 46 | 0.6957 | 0.2277 | 0.2841 | 0.0741 | quality not verified |
| 25 | Чернігівська область | 4 | 1.0000 | 0.1385 | -0.3225 | -48.1121 | quality not verified |
| 26 | Чернівецька область | 77 | 0.0909 | 0.0915 | -0.0525 | -0.0879 | quality not verified |
| 27 | Львівська область | 79 | 0.0759 | 0.0665 | 0.0617 | 0.0763 | quality not verified |
| 28 | Донецька область | 1 | 1.0000 | 0.0033 | -3.1135 | -19.9044 | quality not verified |
| 31 | м. Київ | 58 | 0.3276 | 0.2185 | 0.0656 | 0.0220 | quality not verified |

### Reliability (1 h; bins [0,.1), ... [.9,1])

| bin | n | forecast | observed |
|---|---|---|---|
| 0 | 279 | 0.0483 | 0.0609 |
| 1 | 156 | 0.1461 | 0.1474 |
| 2 | 107 | 0.2514 | 0.2991 |
| 3 | 109 | 0.3534 | 0.4128 |
| 4 | 134 | 0.4515 | 0.5373 |
| 5 | 118 | 0.5526 | 0.5847 |
| 6 | 79 | 0.6472 | 0.5823 |
| 7 | 74 | 0.7460 | 0.5541 |
| 8 | 22 | 0.8537 | 0.5455 |
| 9 | 11 | 0.9214 | 1.0000 |

## Horizon 3 h: per Kyiv day

| day | n | base_rate | model | skill_clim28 | skill_recent7 |
|---|---|---|---|---|---|
| 2026-10-10 | 40 | 0.7750 | 0.1248 | 0.5997 | 0.3044 |
| 2026-10-11 | 647 | 0.5471 | 0.1645 | 0.1104 | 0.0011 |
| 2026-10-12 | 349 | 0.6791 | 0.1512 | 0.2791 | -0.1805 |

### Per region (3 h)

| obl | region | n | base_rate | brier | skill_clim28 | skill_recent7 | quality |
|---|---|---|---|---|---|---|---|
| 3 | Хмельницька область | 57 | 0.7544 | 0.2387 | 0.3795 | -0.1216 | quality not verified |
| 4 | Вінницька область | 44 | 0.8409 | 0.1858 | 0.3874 | -0.2612 | quality not verified |
| 5 | Рівненська область | 60 | 0.7500 | 0.2318 | 0.2800 | -0.1710 | quality not verified |
| 8 | Волинська область | 70 | 0.4429 | 0.2742 | 0.0877 | -0.0455 | quality not verified |
| 10 | Житомирська область | 43 | 0.9535 | 0.0813 | 0.2884 | -0.5906 | quality not verified |
| 11 | Закарпатська область | 77 | 0.0000 | 0.0011 | -2.0408 | nan | quality not verified |
| 12 | Запорізька область | 3 | 1.0000 | 0.0002 | 0.3663 | -21434.4155 | quality not verified |
| 13 | Івано-Франківська область | 74 | 0.1622 | 0.1544 | -0.0560 | -0.1181 | quality not verified |
| 14 | Київська область | 18 | 1.0000 | 0.0322 | -3.3328 | -123.3208 | quality not verified |
| 15 | Кіровоградська область | 34 | 1.0000 | 0.0300 | 0.6558 | -6.8442 | quality not verified |
| 17 | Миколаївська область | 41 | 0.8049 | 0.1534 | -0.1765 | 0.1954 | quality not verified |
| 18 | Одеська область | 62 | 0.8065 | 0.1649 | -0.0744 | 0.0126 | quality not verified |
| 19 | Полтавська область | 48 | 0.8750 | 0.1143 | -0.1161 | -0.0411 | quality not verified |
| 20 | Сумська область | 28 | 0.9643 | 0.0346 | 0.0901 | 0.0292 | quality not verified |
| 21 | Тернопільська область | 69 | 0.6232 | 0.2978 | 0.3963 | -0.0230 | quality not verified |
| 22 | Харківська область | 6 | 1.0000 | 0.0001 | nan | -55087421.4082 | quality not verified |
| 23 | Херсонська область | 51 | 0.7843 | 0.1637 | 0.0856 | 0.2008 | quality not verified |
| 24 | Черкаська область | 44 | 0.9773 | 0.0460 | 0.5522 | -0.5460 | quality not verified |
| 25 | Чернігівська область | 4 | 1.0000 | 0.0101 | -0.5232 | -345633.8736 | quality not verified |
| 26 | Чернівецька область | 73 | 0.2329 | 0.2141 | -0.0770 | -0.1467 | quality not verified |
| 27 | Львівська область | 75 | 0.2267 | 0.1651 | 0.1600 | 0.1349 | quality not verified |
| 28 | Донецька область | 1 | 1.0000 | 0.0001 | nan | -17586226.5592 | quality not verified |
| 31 | м. Київ | 54 | 0.6481 | 0.1990 | 0.1732 | 0.1591 | quality not verified |

### Reliability (3 h; bins [0,.1), ... [.9,1])

| bin | n | forecast | observed |
|---|---|---|---|
| 0 | 92 | 0.0393 | 0.0435 |
| 1 | 129 | 0.1498 | 0.2326 |
| 2 | 92 | 0.2505 | 0.3587 |
| 3 | 66 | 0.3486 | 0.3939 |
| 4 | 64 | 0.4479 | 0.5938 |
| 5 | 70 | 0.5572 | 0.6714 |
| 6 | 81 | 0.6508 | 0.7037 |
| 7 | 129 | 0.7501 | 0.8450 |
| 8 | 182 | 0.8517 | 0.8571 |
| 9 | 131 | 0.9410 | 0.9313 |

## Horizon 6 h: per Kyiv day

| day | n | base_rate | model | skill_clim28 | skill_recent7 |
|---|---|---|---|---|---|
| 2026-10-10 | 40 | 0.7750 | 0.0890 | 0.5061 | 0.0690 |
| 2026-10-11 | 647 | 0.7465 | 0.1298 | 0.3234 | -0.0722 |
| 2026-10-12 | 277 | 0.7653 | 0.0939 | 0.2856 | -0.6373 |

### Per region (6 h)

| obl | region | n | base_rate | brier | skill_clim28 | skill_recent7 | quality |
|---|---|---|---|---|---|---|---|
| 3 | Хмельницька область | 52 | 1.0000 | 0.0573 | 0.7638 | -1.0134 | quality not verified |
| 4 | Вінницька область | 40 | 0.9750 | 0.0585 | 0.5590 | -1.1512 | quality not verified |
| 5 | Рівненська область | 55 | 0.9818 | 0.0670 | 0.6825 | -1.2906 | quality not verified |
| 8 | Волинська область | 65 | 0.5846 | 0.2902 | -0.0049 | -0.1421 | quality not verified |
| 10 | Житомирська область | 41 | 1.0000 | 0.0108 | 0.1839 | -38.0889 | quality not verified |
| 11 | Закарпатська область | 71 | 0.0000 | 0.0036 | -3.5246 | nan | quality not verified |
| 12 | Запорізька область | 3 | 1.0000 | 0.0000 | nan | -18241915151.7617 | quality not verified |
| 13 | Івано-Франківська область | 68 | 0.3529 | 0.2840 | 0.0249 | -0.1698 | quality not verified |
| 14 | Київська область | 18 | 1.0000 | 0.0039 | nan | -49477.4158 | quality not verified |
| 15 | Кіровоградська область | 33 | 1.0000 | 0.0027 | 0.8836 | -160.8896 | quality not verified |
| 17 | Миколаївська область | 36 | 0.9444 | 0.0542 | 0.0228 | 0.0246 | quality not verified |
| 18 | Одеська область | 56 | 0.9643 | 0.0361 | -0.0637 | -0.0262 | quality not verified |
| 19 | Полтавська область | 47 | 1.0000 | 0.0011 | 0.7910 | -10.3974 | quality not verified |
| 20 | Сумська область | 26 | 1.0000 | 0.0000 | nan | -174684.2656 | quality not verified |
| 21 | Тернопільська область | 63 | 0.9683 | 0.1898 | 0.6935 | -0.3177 | quality not verified |
| 22 | Харківська область | 6 | 1.0000 | 0.0000 | nan | -79412937701419712.0000 | quality not verified |
| 23 | Херсонська область | 48 | 0.9375 | 0.0617 | 0.0335 | 0.0836 | quality not verified |
| 24 | Черкаська область | 42 | 1.0000 | 0.0035 | 0.8197 | -21.0549 | quality not verified |
| 25 | Чернігівська область | 4 | 1.0000 | 0.0006 | -103.1282 | -382686293331.0566 | quality not verified |
| 26 | Чернівецька область | 67 | 0.4328 | 0.3221 | -0.0149 | -0.1840 | quality not verified |
| 27 | Львівська область | 69 | 0.4203 | 0.2667 | 0.2214 | 0.0791 | quality not verified |
| 28 | Донецька область | 1 | 1.0000 | 0.0000 | nan | -613079944656340224.0000 | quality not verified |
| 31 | м. Київ | 53 | 0.8679 | 0.1216 | -0.0162 | -0.0179 | quality not verified |

### Reliability (6 h; bins [0,.1), ... [.9,1])

| bin | n | forecast | observed |
|---|---|---|---|
| 0 | 68 | 0.0479 | 0.0000 |
| 1 | 50 | 0.1617 | 0.4800 |
| 2 | 80 | 0.2502 | 0.4375 |
| 3 | 55 | 0.3520 | 0.5818 |
| 4 | 60 | 0.4445 | 0.4333 |
| 5 | 43 | 0.5556 | 0.6047 |
| 6 | 48 | 0.6499 | 0.9167 |
| 7 | 80 | 0.7576 | 0.9625 |
| 8 | 108 | 0.8556 | 0.9259 |
| 9 | 372 | 0.9594 | 0.9731 |

## Live log

2 moment(s) logged: 2026-10-11 15:46 Kyiv (made 20.3 h after T), 2026-10-12 15:43 Kyiv (made 0.3 h after T). A window is scored once it closes inside the saved data.

| horizon | n | moments | base_rate | model | clim28 | recent7 | revised_rows | still_clear | model_logged | model_recomputed |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 h, replay | 11 | 1 | 0.1818 | 0.2436 | 0.2375 | 0.2014 | 0 | 11 | 0.2436 | 0.2436 |
| 3 h, replay | 11 | 1 | 0.7273 | 0.1837 | 0.2952 | 0.1843 | 0 | 11 | 0.1837 | 0.1837 |
| 6 h, replay | 11 | 1 | 0.9091 | 0.2057 | 0.3400 | 0.1914 | 0 | 11 | 0.2057 | 0.2057 |

`live` rows were made before their window closed; `replay` rows after it, from a saved pull, so they are not a test of forecasting. Revision check: on the `still_clear` rows (clear at T in the current records too), `model_logged` is the Brier score of the logged forecasts and `model_recomputed` that of the forecasts on the recomputed features.

## Late revisions

The same record id in the first pull (20261011T1247Z) and in the newest: a changed start, a changed end that was already set (an ongoing alert getting its end is not a revision), a changed level.

- compared: 16291
- start: 0
- end: 0
- alert_level: 0
- start, starting before the map cutoff: 0
- end, starting before the map cutoff: 0
- alert_level, starting before the map cutoff: 0
