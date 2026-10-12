# v2 report

Decision 12, registered at `ad82822125b2c3eae07dfb713562606df3c468d3` before the search. Generated offline, once, by `python main.py retrain` at commit `c9cc1ba30043a3df4239c6ce3426c174ca5cadf9`.
- **Search:** CHOOSE only (to 2026-09-12 21:00:00+00:00). Configs tried in the seeded order within the box: CatBoost 9, LightGBM 30, logistic 64. Every config and its scores: `results/v2/search_<family>.csv`.
- **Winner** per family and horizon: the highest pooled F1 on CHOOSE blocks 3-6 at its max-F1 threshold; that threshold is then fixed. On CHOOSE the scores are in-sample.
- **Benchmark and holdout:** the winners run forward, each block fitted on the past only, with a Platt on the window before it. Neither period was used for tuning, but both were seen before (the benchmark by the probe and the weak-spot analysis, the holdout by step 7 and the weak-spot analysis), so they are not independent checks. The untouched check is the data after 2026-10-12 12:43:00+00:00, scored after the submission.
- Thresholds of v1, clim28 and recent7: max F1 on CHOOSE, as in `metrics_report.md`. f1_always is the F1 of always saying yes.

## Winners

| winner | f1 | threshold | window | precision | recall | config | params |
|---|---|---|---|---|---|---|---|
| v2 CatBoost, 1 h | 0.5928 | 0.2600 | 7 | 0.4723 | 0.7960 | 4 | {"refs": [], "half_life": null, "iterations": 300, "learning_rate": 0.03, "depth": 6, "l2_leaf_reg": 1} |
| v2 CatBoost, 3 h | 0.7644 | 0.3700 | 14 | 0.7252 | 0.8081 | 6 | {"refs": [], "half_life": 120, "iterations": 600, "learning_rate": 0.03, "depth": 6, "l2_leaf_reg": 1} |
| v2 CatBoost, 6 h | 0.8140 | 0.3300 | 14 | 0.7702 | 0.8632 | 6 | {"refs": [], "half_life": 120, "iterations": 600, "learning_rate": 0.03, "depth": 6, "l2_leaf_reg": 1} |
| v2 LightGBM, 1 h | 0.5976 | 0.2700 | 7 | 0.4823 | 0.7854 | 10 | {"refs": [], "half_life": 30, "n_estimators": 200, "learning_rate": 0.05, "num_leaves": 15, "min_child_samples": 200, "subsample": 0.7, "colsample_bytree": 0.6, "reg_lambda": 1} |
| v2 LightGBM, 3 h | 0.7653 | 0.3600 | 14 | 0.7189 | 0.8180 | 10 | {"refs": [], "half_life": 30, "n_estimators": 200, "learning_rate": 0.05, "num_leaves": 15, "min_child_samples": 200, "subsample": 0.7, "colsample_bytree": 0.6, "reg_lambda": 1} |
| v2 LightGBM, 6 h | 0.8154 | 0.3800 | 14 | 0.7899 | 0.8427 | 25 | {"refs": [], "half_life": 60, "n_estimators": 200, "learning_rate": 0.02, "num_leaves": 127, "min_child_samples": 50, "subsample": 0.7, "colsample_bytree": 0.6, "reg_lambda": 1} |
| v2 logistic, 1 h | 0.6038 | 0.2600 | 14 | 0.4911 | 0.7835 | 59 | {"refs": [], "half_life": null, "C": 0.1, "class_weight": null} |
| v2 logistic, 3 h | 0.7697 | 0.4100 | 14 | 0.7342 | 0.8087 | 58 | {"refs": [], "half_life": 60, "C": 0.01, "class_weight": null} |
| v2 logistic, 6 h | 0.8171 | 0.3100 | 14 | 0.7818 | 0.8556 | 13 | {"refs": [], "half_life": null, "C": 10, "class_weight": "balanced"} |

## Horizon 1 h

| period, forecast | threshold | precision | recall | f1 | f1_always | ap | auc | brier | n |
|---|---|---|---|---|---|---|---|---|---|
| choose, v1 logistic | 0.2600 | 0.4928 | 0.7787 | 0.6036 | 0.2969 | 0.5734 | 0.8832 | 0.0997 | 20607 |
| benchmark, v1 logistic | 0.2600 | 0.5213 | 0.8240 | 0.6386 | 0.3922 | 0.6480 | 0.8628 | 0.1246 | 18538 |
| holdout, v1 logistic | 0.2600 | 0.5245 | 0.8451 | 0.6472 | 0.5051 | 0.5901 | 0.7796 | 0.1794 | 1089 |
| choose, v2 logistic | 0.2600 | 0.4911 | 0.7835 | 0.6038 | 0.2969 | 0.5739 | 0.8832 | 0.0995 | 20607 |
| benchmark, v2 logistic | 0.2600 | 0.5219 | 0.8253 | 0.6394 | 0.3922 | 0.6483 | 0.8629 | 0.1245 | 18538 |
| holdout, v2 logistic | 0.2600 | 0.5253 | 0.8478 | 0.6486 | 0.5051 | 0.5898 | 0.7794 | 0.1794 | 1089 |
| choose, v2 LightGBM | 0.2700 | 0.4823 | 0.7854 | 0.5976 | 0.2969 | 0.5889 | 0.8854 | 0.0984 | 20607 |
| benchmark, v2 LightGBM | 0.2700 | 0.5283 | 0.7999 | 0.6363 | 0.3922 | 0.6480 | 0.8627 | 0.1248 | 18538 |
| holdout, v2 LightGBM | 0.2700 | 0.5039 | 0.8832 | 0.6417 | 0.5051 | 0.6478 | 0.7912 | 0.1748 | 1089 |
| choose, v2 CatBoost | 0.2600 | 0.4723 | 0.7960 | 0.5928 | 0.2969 | 0.5872 | 0.8841 | 0.0987 | 20607 |
| benchmark, v2 CatBoost | 0.2600 | 0.5149 | 0.8160 | 0.6314 | 0.3922 | 0.6459 | 0.8602 | 0.1255 | 18538 |
| holdout, v2 CatBoost | 0.2600 | 0.4954 | 0.8804 | 0.6341 | 0.5051 | 0.6476 | 0.7901 | 0.1755 | 1089 |
| choose, clim28 | 0.1900 | 0.4473 | 0.7275 | 0.5540 | 0.2969 | 0.5435 | 0.8582 | 0.1075 | 20607 |
| benchmark, clim28 | 0.1900 | 0.4965 | 0.8005 | 0.6129 | 0.3922 | 0.6127 | 0.8371 | 0.1348 | 18538 |
| holdout, clim28 | 0.1900 | 0.5281 | 0.7147 | 0.6074 | 0.5051 | 0.6114 | 0.7695 | 0.1931 | 1089 |
| choose, recent7 | 0.2200 | 0.4696 | 0.7640 | 0.5816 | 0.2969 | 0.5610 | 0.8648 | 0.1032 | 20607 |
| benchmark, recent7 | 0.2200 | 0.4963 | 0.8080 | 0.6149 | 0.3922 | 0.6211 | 0.8420 | 0.1318 | 18538 |
| holdout, recent7 | 0.2200 | 0.5072 | 0.8641 | 0.6392 | 0.5051 | 0.5997 | 0.7709 | 0.1811 | 1089 |

## Horizon 3 h

| period, forecast | threshold | precision | recall | f1 | f1_always | ap | auc | brier | n |
|---|---|---|---|---|---|---|---|---|---|
| choose, v1 logistic | 0.3800 | 0.7345 | 0.8030 | 0.7672 | 0.4858 | 0.8134 | 0.9107 | 0.1112 | 20566 |
| benchmark, v1 logistic | 0.3800 | 0.7377 | 0.8470 | 0.7886 | 0.5933 | 0.8415 | 0.8861 | 0.1333 | 18492 |
| holdout, v1 logistic | 0.3800 | 0.7952 | 0.8553 | 0.8242 | 0.7503 | 0.8698 | 0.8411 | 0.1585 | 1036 |
| choose, v2 logistic | 0.4100 | 0.7342 | 0.8087 | 0.7697 | 0.4858 | 0.8130 | 0.9102 | 0.1104 | 20566 |
| benchmark, v2 logistic | 0.4100 | 0.7402 | 0.8404 | 0.7871 | 0.5933 | 0.8416 | 0.8862 | 0.1337 | 18492 |
| holdout, v2 logistic | 0.4100 | 0.7962 | 0.8666 | 0.8299 | 0.7503 | 0.8629 | 0.8375 | 0.1574 | 1036 |
| choose, v2 LightGBM | 0.3600 | 0.7189 | 0.8180 | 0.7653 | 0.4858 | 0.8164 | 0.9096 | 0.1115 | 20566 |
| benchmark, v2 LightGBM | 0.3600 | 0.7332 | 0.8429 | 0.7843 | 0.5933 | 0.8424 | 0.8855 | 0.1341 | 18492 |
| holdout, v2 LightGBM | 0.3600 | 0.7677 | 0.8714 | 0.8163 | 0.7503 | 0.8595 | 0.8260 | 0.1622 | 1036 |
| choose, v2 CatBoost | 0.3700 | 0.7252 | 0.8081 | 0.7644 | 0.4858 | 0.8144 | 0.9075 | 0.1124 | 20566 |
| benchmark, v2 CatBoost | 0.3700 | 0.7429 | 0.8266 | 0.7825 | 0.5933 | 0.8417 | 0.8844 | 0.1349 | 18492 |
| holdout, v2 CatBoost | 0.3700 | 0.7696 | 0.8859 | 0.8236 | 0.7503 | 0.8267 | 0.8138 | 0.1658 | 1036 |
| choose, clim28 | 0.2300 | 0.6736 | 0.8304 | 0.7438 | 0.4858 | 0.7881 | 0.8915 | 0.1269 | 20566 |
| benchmark, clim28 | 0.2300 | 0.7102 | 0.8577 | 0.7770 | 0.5933 | 0.8298 | 0.8734 | 0.1448 | 18492 |
| holdout, clim28 | 0.2300 | 0.8260 | 0.8167 | 0.8213 | 0.7503 | 0.8793 | 0.8456 | 0.1982 | 1036 |
| choose, recent7 | 0.4100 | 0.7325 | 0.7769 | 0.7540 | 0.4858 | 0.7969 | 0.8965 | 0.1179 | 20566 |
| benchmark, recent7 | 0.4100 | 0.7455 | 0.8037 | 0.7735 | 0.5933 | 0.8327 | 0.8763 | 0.1400 | 18492 |
| holdout, recent7 | 0.4100 | 0.8298 | 0.8232 | 0.8265 | 0.7503 | 0.8704 | 0.8455 | 0.1529 | 1036 |

## Horizon 6 h

| period, forecast | threshold | precision | recall | f1 | f1_always | ap | auc | brier | n |
|---|---|---|---|---|---|---|---|---|---|
| choose, v1 logistic | 0.3100 | 0.7790 | 0.8569 | 0.8161 | 0.5855 | 0.8935 | 0.9223 | 0.1098 | 20501 |
| benchmark, v1 logistic | 0.3100 | 0.7669 | 0.9104 | 0.8325 | 0.6980 | 0.9152 | 0.9031 | 0.1235 | 18419 |
| holdout, v1 logistic | 0.3100 | 0.8722 | 0.9118 | 0.8916 | 0.8592 | 0.9538 | 0.8899 | 0.1178 | 964 |
| choose, v2 logistic | 0.3100 | 0.7818 | 0.8556 | 0.8171 | 0.5855 | 0.8932 | 0.9218 | 0.1102 | 20501 |
| benchmark, v2 logistic | 0.3100 | 0.7680 | 0.9064 | 0.8315 | 0.6980 | 0.9144 | 0.9022 | 0.1240 | 18419 |
| holdout, v2 logistic | 0.3100 | 0.8763 | 0.9077 | 0.8917 | 0.8592 | 0.9527 | 0.8876 | 0.1216 | 964 |
| choose, v2 LightGBM | 0.3800 | 0.7899 | 0.8427 | 0.8154 | 0.5855 | 0.8816 | 0.9158 | 0.1112 | 20501 |
| benchmark, v2 LightGBM | 0.3800 | 0.7937 | 0.8782 | 0.8338 | 0.6980 | 0.9119 | 0.9006 | 0.1253 | 18419 |
| holdout, v2 LightGBM | 0.3800 | 0.8822 | 0.9077 | 0.8948 | 0.8592 | 0.9558 | 0.8949 | 0.1103 | 964 |
| choose, v2 CatBoost | 0.3300 | 0.7702 | 0.8632 | 0.8140 | 0.5855 | 0.8869 | 0.9148 | 0.1121 | 20501 |
| benchmark, v2 CatBoost | 0.3300 | 0.7694 | 0.8947 | 0.8273 | 0.6980 | 0.9103 | 0.8985 | 0.1269 | 18419 |
| holdout, v2 CatBoost | 0.3300 | 0.8510 | 0.9201 | 0.8842 | 0.8592 | 0.9445 | 0.8762 | 0.1178 | 964 |
| choose, clim28 | 0.2700 | 0.7706 | 0.8410 | 0.8043 | 0.5855 | 0.8744 | 0.9055 | 0.1254 | 20501 |
| benchmark, clim28 | 0.2700 | 0.7969 | 0.8784 | 0.8356 | 0.6980 | 0.9133 | 0.8979 | 0.1323 | 18419 |
| holdout, clim28 | 0.2700 | 0.9402 | 0.8017 | 0.8654 | 0.8592 | 0.9603 | 0.9017 | 0.1740 | 964 |
| choose, recent7 | 0.4500 | 0.8020 | 0.8144 | 0.8081 | 0.5855 | 0.8804 | 0.9091 | 0.1169 | 20501 |
| benchmark, recent7 | 0.4500 | 0.8067 | 0.8789 | 0.8412 | 0.6980 | 0.9132 | 0.8989 | 0.1271 | 18419 |
| holdout, recent7 | 0.4500 | 0.9347 | 0.8871 | 0.9102 | 0.8592 | 0.9611 | 0.9058 | 0.1017 | 964 |

## Saved models

- `models/v2/logistic.joblib` (logistic): SHA-256 `4599231d2b4f1e8054490c7a11f853d4c55746e924f4cd3415db927822430b4e`
- `models/v2/gbm.joblib` (LightGBM): SHA-256 `e16b183560c2c8ac35d6a6fbd157a07ab6dc39a0105ac1b453da7696c7a04672`
- `models/v2/catboost.joblib` (CatBoost): SHA-256 `7d5a66532e4954b43cbcd46c48af36e10b7b98ebe5598bb26c1443ee81d0444f`

Each is refitted on every label known at 2026-10-12 12:43:00+00:00, with a Platt on the window before it; the meta holds each horizon's config, window and threshold. Load only these trusted files (joblib uses pickle).

Forecast rows: `results/v2/forecasts.csv.gz`, SHA-256 `c0998b1bfa6b857f08beaa48a74f507131c67a065a429c2eb06d261a1f8cfcb6`.
