# Benchmark report

Historical benchmark, seen by the feasibility probe. This is not the untouched holdout.

Generated offline by `python main.py evaluate benchmark` at commit `30cb39a1c08edd62ecc7f67a7d1c49b47fe1d12a`.
Window ends at 2026-10-10 19:03:00+00:00; horizons 1/3/6 h; all 24 regions (23 oblasts and Kyiv City).
Brier is mean squared probability error (lower is better). Skill = 1 - Brier / reference Brier.
95% intervals: 1,000 whole Kyiv-day bootstrap resamples, seed 0. Rows are weighted equally; days preserve their row counts.
clim28 and climall are recounted daily; recent7 follows the last seven days; persist repeats the previous horizon.
Model settings are fixed. Each block model fits completed past labels; Platt calibration uses only the previous 14 days of OOF forecasts.
The n < 100 flag was set before scoring; n >= 100 alone does not establish regional skill.
History contains final API revisions: event-time truncation cannot establish that every record was published at T.

## Registered rule

Choose the candidate with the highest mean calibrated skill vs daily clim28 over the three horizons, CHOOSE blocks 3-6.
Benchmark passes only when BOTH clim28 and recent7 lower CI bounds exceed zero on at least two horizons. No switching after benchmark.

## Horizon 1 h

n = 18538; base rate = 0.2439; 2026-09-12 21:00:00+00:00 through 2026-10-10 18:00:00+00:00; 4 scored blocks.
| forecast | brier | raw_brier | skill_clim28 | ci_clim28 | skill_recent7 | ci_recent7 |
|---|---|---|---|---|---|---|
| logistic | 0.1246 | 0.1265 | 0.0753 | [+0.0535, +0.0995] | 0.0547 | [+0.0353, +0.0743] |
| clim28 | 0.1348 | nan | nan | nan | nan | nan |
| climall | 0.1695 | nan | nan | nan | nan | nan |
| recent7 | 0.1318 | nan | nan | nan | nan | nan |
| persist | 0.2433 | nan | nan | nan | nan | nan |

### Brier per block

| block | n | logistic | clim28 | recent7 |
|---|---|---|---|---|
| 2026-09-12 21:00:00+00:00 | 5065 | 0.1245 | 0.1323 | 0.1296 |
| 2026-09-19 21:30:00+00:00 | 4310 | 0.1168 | 0.1306 | 0.1206 |
| 2026-09-26 21:00:00+00:00 | 4731 | 0.1189 | 0.1270 | 0.1275 |
| 2026-10-03 20:30:00+00:00 | 4432 | 0.1384 | 0.1500 | 0.1498 |

### Per region: logistic

| obl | region | n | base_rate | brier | skill_clim28 | skill_recent7 | quality |
|---|---|---|---|---|---|---|---|
| 3 | Хмельницька область | 1163 | 0.1376 | 0.1048 | 0.1280 | 0.1184 | n >= 100; pooled CI only |
| 4 | Вінницька область | 1060 | 0.2066 | 0.1532 | 0.0844 | 0.0729 | n >= 100; pooled CI only |
| 5 | Рівненська область | 1154 | 0.1724 | 0.1265 | 0.1309 | 0.1007 | n >= 100; pooled CI only |
| 8 | Волинська область | 1267 | 0.0837 | 0.0707 | 0.1028 | 0.0805 | n >= 100; pooled CI only |
| 9 | Дніпропетровська область | 62 | 0.8548 | 0.1160 | 0.1641 | 0.0985 | quality not verified |
| 10 | Житомирська область | 864 | 0.3773 | 0.2203 | 0.1082 | 0.0769 | n >= 100; pooled CI only |
| 11 | Закарпатська область | 1337 | 0.0045 | 0.0045 | 0.0055 | -0.0060 | n >= 100; pooled CI only |
| 12 | Запорізька область | 124 | 0.8306 | 0.1397 | 0.0378 | 0.0829 | n >= 100; pooled CI only |
| 13 | Івано-Франківська область | 1322 | 0.0197 | 0.0189 | 0.0430 | 0.0266 | n >= 100; pooled CI only |
| 14 | Київська область | 389 | 0.7121 | 0.2489 | 0.0443 | -0.2058 | n >= 100; pooled CI only |
| 15 | Кіровоградська область | 696 | 0.4368 | 0.2293 | 0.0912 | 0.0865 | n >= 100; pooled CI only |
| 17 | Миколаївська область | 676 | 0.5873 | 0.2254 | 0.0608 | 0.0567 | n >= 100; pooled CI only |
| 18 | Одеська область | 787 | 0.5451 | 0.2459 | 0.0294 | 0.0247 | n >= 100; pooled CI only |
| 19 | Полтавська область | 581 | 0.5215 | 0.2388 | 0.0482 | 0.0523 | n >= 100; pooled CI only |
| 20 | Сумська область | 228 | 0.7675 | 0.1766 | -0.0507 | 0.0587 | n >= 100; pooled CI only |
| 21 | Тернопільська область | 1273 | 0.0542 | 0.0457 | 0.1226 | 0.0924 | n >= 100; pooled CI only |
| 22 | Харківська область | 117 | 0.9231 | 0.0754 | 0.0353 | -0.0320 | n >= 100; pooled CI only |
| 23 | Херсонська область | 985 | 0.3462 | 0.2396 | -0.0416 | -0.0631 | n >= 100; pooled CI only |
| 24 | Черкаська область | 717 | 0.4338 | 0.2180 | 0.1196 | 0.1120 | n >= 100; pooled CI only |
| 25 | Чернігівська область | 211 | 0.7488 | 0.1632 | 0.2034 | 0.1676 | n >= 100; pooled CI only |
| 26 | Чернівецька область | 1287 | 0.0420 | 0.0385 | 0.0636 | 0.0494 | n >= 100; pooled CI only |
| 27 | Львівська область | 1317 | 0.0228 | 0.0218 | 0.0403 | 0.0281 | n >= 100; pooled CI only |
| 28 | Донецька область | 37 | 0.9459 | 0.0941 | -0.2525 | -0.8533 | quality not verified |
| 31 | м. Київ | 884 | 0.3767 | 0.2121 | 0.1071 | 0.0905 | n >= 100; pooled CI only |

### Reliability: logistic (bins [0,.1), ... [.9,1])

| bin | n | forecast | observed |
|---|---|---|---|
| 0 | 8159 | 0.0346 | 0.0302 |
| 1 | 2243 | 0.1442 | 0.1409 |
| 2 | 1598 | 0.2487 | 0.2603 |
| 3 | 1566 | 0.3503 | 0.3940 |
| 4 | 1545 | 0.4505 | 0.4621 |
| 5 | 1324 | 0.5459 | 0.5514 |
| 6 | 933 | 0.6479 | 0.6163 |
| 7 | 628 | 0.7469 | 0.7213 |
| 8 | 379 | 0.8456 | 0.8179 |
| 9 | 163 | 0.9263 | 0.8896 |

## Horizon 3 h

n = 18492; base rate = 0.4217; 2026-09-12 21:00:00+00:00 through 2026-10-10 16:00:00+00:00; 4 scored blocks.
| forecast | brier | raw_brier | skill_clim28 | ci_clim28 | skill_recent7 | ci_recent7 |
|---|---|---|---|---|---|---|
| logistic | 0.1333 | 0.1363 | 0.0789 | [+0.0399, +0.1233] | 0.0476 | [+0.0087, +0.0821] |
| clim28 | 0.1448 | nan | nan | nan | nan | nan |
| climall | 0.2120 | nan | nan | nan | nan | nan |
| recent7 | 0.1400 | nan | nan | nan | nan | nan |
| persist | 0.2735 | nan | nan | nan | nan | nan |

### Brier per block

| block | n | logistic | clim28 | recent7 |
|---|---|---|---|---|
| 2026-09-12 21:00:00+00:00 | 5065 | 0.1559 | 0.1619 | 0.1545 |
| 2026-09-19 21:30:00+00:00 | 4310 | 0.1036 | 0.1164 | 0.1071 |
| 2026-09-26 21:00:00+00:00 | 4731 | 0.1246 | 0.1336 | 0.1371 |
| 2026-10-03 20:30:00+00:00 | 4386 | 0.1460 | 0.1648 | 0.1587 |

### Per region: logistic

| obl | region | n | base_rate | brier | skill_clim28 | skill_recent7 | quality |
|---|---|---|---|---|---|---|---|
| 3 | Хмельницька область | 1160 | 0.3216 | 0.2028 | 0.0866 | 0.0912 | n >= 100; pooled CI only |
| 4 | Вінницька область | 1057 | 0.4503 | 0.2419 | 0.0588 | 0.0563 | n >= 100; pooled CI only |
| 5 | Рівненська область | 1153 | 0.3859 | 0.2162 | 0.1285 | 0.0608 | n >= 100; pooled CI only |
| 8 | Волинська область | 1264 | 0.2049 | 0.1498 | 0.1226 | 0.0828 | n >= 100; pooled CI only |
| 9 | Дніпропетровська область | 61 | 1.0000 | 0.0003 | nan | -12.8865 | quality not verified |
| 10 | Житомирська область | 864 | 0.7269 | 0.2045 | 0.1789 | 0.0200 | n >= 100; pooled CI only |
| 11 | Закарпатська область | 1333 | 0.0135 | 0.0142 | -0.0275 | -0.0389 | n >= 100; pooled CI only |
| 12 | Запорізька область | 122 | 0.9754 | 0.0250 | 0.0077 | -0.0156 | n >= 100; pooled CI only |
| 13 | Івано-Франківська область | 1318 | 0.0501 | 0.0473 | 0.0362 | 0.0203 | n >= 100; pooled CI only |
| 14 | Київська область | 389 | 0.9512 | 0.0885 | 0.0866 | -0.8634 | n >= 100; pooled CI only |
| 15 | Кіровоградська область | 694 | 0.7190 | 0.1909 | 0.0535 | 0.1080 | n >= 100; pooled CI only |
| 17 | Миколаївська область | 675 | 0.8859 | 0.0995 | -0.0001 | 0.0091 | n >= 100; pooled CI only |
| 18 | Одеська область | 786 | 0.8690 | 0.1100 | 0.0710 | 0.0636 | n >= 100; pooled CI only |
| 19 | Полтавська область | 578 | 0.8270 | 0.1422 | 0.0039 | 0.0129 | n >= 100; pooled CI only |
| 20 | Сумська область | 228 | 0.9693 | 0.0301 | 0.0319 | 0.0060 | n >= 100; pooled CI only |
| 21 | Тернопільська область | 1270 | 0.1260 | 0.0964 | 0.1423 | 0.0954 | n >= 100; pooled CI only |
| 22 | Харківська область | 117 | 1.0000 | 0.0006 | nan | -4326.9717 | n >= 100; pooled CI only |
| 23 | Херсонська область | 981 | 0.6585 | 0.2494 | -0.0828 | -0.0713 | n >= 100; pooled CI only |
| 24 | Черкаська область | 715 | 0.7329 | 0.1818 | 0.0930 | 0.0609 | n >= 100; pooled CI only |
| 25 | Чернігівська область | 211 | 0.9479 | 0.0502 | 0.1056 | 0.0488 | n >= 100; pooled CI only |
| 26 | Чернівецька область | 1283 | 0.1068 | 0.0915 | 0.0782 | 0.0687 | n >= 100; pooled CI only |
| 27 | Львівська область | 1314 | 0.0594 | 0.0553 | 0.0367 | 0.0263 | n >= 100; pooled CI only |
| 28 | Донецька область | 37 | 1.0000 | 0.0022 | 0.7881 | -2108.8611 | quality not verified |
| 31 | м. Київ | 882 | 0.6871 | 0.1901 | 0.1170 | 0.1217 | n >= 100; pooled CI only |

### Reliability: logistic (bins [0,.1), ... [.9,1])

| bin | n | forecast | observed |
|---|---|---|---|
| 0 | 4861 | 0.0468 | 0.0483 |
| 1 | 2247 | 0.1466 | 0.1326 |
| 2 | 1528 | 0.2475 | 0.2415 |
| 3 | 1108 | 0.3495 | 0.3403 |
| 4 | 958 | 0.4502 | 0.4478 |
| 5 | 956 | 0.5503 | 0.5805 |
| 6 | 1144 | 0.6512 | 0.6740 |
| 7 | 1623 | 0.7522 | 0.7498 |
| 8 | 2184 | 0.8512 | 0.8288 |
| 9 | 1883 | 0.9467 | 0.9230 |

## Horizon 6 h

n = 18419; base rate = 0.5361; 2026-09-12 21:00:00+00:00 through 2026-10-10 13:00:00+00:00; 4 scored blocks.
| forecast | brier | raw_brier | skill_clim28 | ci_clim28 | skill_recent7 | ci_recent7 |
|---|---|---|---|---|---|---|
| logistic | 0.1235 | 0.1276 | 0.0667 | [+0.0201, +0.1156] | 0.0280 | [-0.0272, +0.0783] |
| clim28 | 0.1323 | nan | nan | nan | nan | nan |
| climall | 0.2093 | nan | nan | nan | nan | nan |
| recent7 | 0.1271 | nan | nan | nan | nan | nan |
| persist | 0.2491 | nan | nan | nan | nan | nan |

### Brier per block

| block | n | logistic | clim28 | recent7 |
|---|---|---|---|---|
| 2026-09-12 21:00:00+00:00 | 5065 | 0.1544 | 0.1633 | 0.1495 |
| 2026-09-19 21:30:00+00:00 | 4310 | 0.1027 | 0.1070 | 0.1037 |
| 2026-09-26 21:00:00+00:00 | 4731 | 0.1070 | 0.1141 | 0.1157 |
| 2026-10-03 20:30:00+00:00 | 4313 | 0.1260 | 0.1412 | 0.1365 |

### Per region: logistic

| obl | region | n | base_rate | brier | skill_clim28 | skill_recent7 | quality |
|---|---|---|---|---|---|---|---|
| 3 | Хмельницька область | 1157 | 0.5108 | 0.2501 | 0.0418 | 0.0549 | n >= 100; pooled CI only |
| 4 | Вінницька область | 1055 | 0.6673 | 0.2312 | 0.0408 | 0.0295 | n >= 100; pooled CI only |
| 5 | Рівненська область | 1149 | 0.5727 | 0.2432 | 0.0937 | -0.0046 | n >= 100; pooled CI only |
| 8 | Волинська область | 1258 | 0.3347 | 0.2231 | 0.0596 | 0.0214 | n >= 100; pooled CI only |
| 9 | Дніпропетровська область | 59 | 1.0000 | 0.0000 | nan | -4132.1713 | quality not verified |
| 10 | Житомирська область | 864 | 0.8993 | 0.1053 | 0.2798 | -0.0854 | n >= 100; pooled CI only |
| 11 | Закарпатська область | 1327 | 0.0271 | 0.0298 | -0.0725 | -0.0806 | n >= 100; pooled CI only |
| 12 | Запорізька область | 122 | 1.0000 | 0.0000 | nan | -4328073.5491 | n >= 100; pooled CI only |
| 13 | Івано-Франківська область | 1312 | 0.0907 | 0.0832 | 0.0310 | 0.0229 | n >= 100; pooled CI only |
| 14 | Київська область | 389 | 1.0000 | 0.0120 | 0.5901 | -35.2537 | n >= 100; pooled CI only |
| 15 | Кіровоградська область | 691 | 0.8654 | 0.1164 | -0.0398 | 0.0730 | n >= 100; pooled CI only |
| 17 | Миколаївська область | 672 | 0.9881 | 0.0136 | -0.0785 | -0.1725 | n >= 100; pooled CI only |
| 18 | Одеська область | 780 | 0.9808 | 0.0197 | 0.0362 | -0.0212 | n >= 100; pooled CI only |
| 19 | Полтавська область | 577 | 0.9463 | 0.0517 | 0.0321 | 0.0020 | n >= 100; pooled CI only |
| 20 | Сумська область | 225 | 1.0000 | 0.0000 | nan | -401.7741 | n >= 100; pooled CI only |
| 21 | Тернопільська область | 1264 | 0.2009 | 0.1489 | 0.0940 | 0.0712 | n >= 100; pooled CI only |
| 22 | Харківська область | 115 | 1.0000 | 0.0000 | nan | -95312571.4250 | n >= 100; pooled CI only |
| 23 | Херсонська область | 976 | 0.8627 | 0.1248 | -0.0249 | 0.0030 | n >= 100; pooled CI only |
| 24 | Черкаська область | 713 | 0.8892 | 0.0959 | 0.1044 | 0.0326 | n >= 100; pooled CI only |
| 25 | Чернігівська область | 211 | 0.9953 | 0.0053 | 0.2173 | -0.1165 | n >= 100; pooled CI only |
| 26 | Чернівецька область | 1277 | 0.1848 | 0.1479 | 0.0846 | 0.0773 | n >= 100; pooled CI only |
| 27 | Львівська область | 1308 | 0.1009 | 0.0937 | 0.0050 | 0.0042 | n >= 100; pooled CI only |
| 28 | Донецька область | 36 | 1.0000 | 0.0005 | 0.2980 | -50231024.1378 | quality not verified |
| 31 | м. Київ | 882 | 0.8401 | 0.1260 | 0.0778 | 0.0858 | n >= 100; pooled CI only |

### Reliability: logistic (bins [0,.1), ... [.9,1])

| bin | n | forecast | observed |
|---|---|---|---|
| 0 | 2731 | 0.0555 | 0.0564 |
| 1 | 2406 | 0.1462 | 0.1488 |
| 2 | 1430 | 0.2477 | 0.2308 |
| 3 | 1179 | 0.3491 | 0.3554 |
| 4 | 994 | 0.4474 | 0.4366 |
| 5 | 916 | 0.5475 | 0.5306 |
| 6 | 916 | 0.6510 | 0.6234 |
| 7 | 1017 | 0.7535 | 0.7571 |
| 8 | 1705 | 0.8560 | 0.8716 |
| 9 | 5125 | 0.9600 | 0.9495 |

## Benchmark verdict

Per horizon: {1: True, 3: True, 6: False}. Strict bar: **PASS**.
Saved model: `models/logistic.joblib`; SHA-256 `ffbce213e5e203c6246c2c2e8f4bfb4461349a5837545e487467973b18219243`.
Models fit labels completed by 2026-10-10 19:03:00+00:00; final Platt uses preceding 14 days of OOF forecasts.
This artifact is frozen for step 7. No holdout outcomes were scored in step 3.

Forecast rows: `results/benchmark_forecasts.csv.gz`; SHA-256 `19db7e3d0d064c47c50c1ff81d3edfcff411fd3b58a421e76b3b1bc4ceffd155`.
The file includes unscored CHOOSE warm-up rows; for benchmark metrics filter ts >= benchmark start and scored = True.
