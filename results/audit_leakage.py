"""Reproduce the step-2 AV diagnosis offline; never read the post-cutoff holdout.

Run: .venv/bin/python results/audit_leakage.py
This is a diagnostic, not a forecast model or a model-selection experiment.
"""
import gzip
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from alerts import data as D
from alerts.checks import AdversarialValidation
from alerts.features import Features, ForecastTable
from alerts.splits import DECISION


def forecast_rows(records):
    rows = ForecastTable(records[records.start < D.MAP_CUTOFF],
                         DECISION.bounds["train"][0], D.MAP_CUTOFF).rows
    # Same 21 oblasts as the logged step-2 experiment, chosen on train in the probe, in the oblast-major order the
    # logged AUCs were computed on: random folds and bagging depend on the row order.
    rows = rows[~rows.obl.isin([9, 22, 28])]
    return rows.sort_values(["obl", "ts"], ignore_index=True)


def random_av(a, b, names, group_timestamps=False):
    rows = pd.concat([a, b], ignore_index=True)
    labels = np.r_[np.zeros(len(a)), np.ones(len(b))]
    score = np.zeros(len(rows))
    gain = np.zeros(len(names))
    same_time, near_time = 0, 0
    folds = StratifiedKFold(5, shuffle=True, random_state=0).split(rows, labels)
    if group_timestamps:
        codes, times = pd.factorize(rows.ts, sort=True)
        groups = (np.random.default_rng(0).permutation(len(times)) % 5)[codes]
        folds = ((np.flatnonzero(groups != k), np.flatnonzero(groups == k)) for k in range(5))
    for fit, held in folds:
        model = LGBMClassifier(**AdversarialValidation.SETTINGS, n_jobs=2)
        model.fit(rows.iloc[fit][names], labels[fit])
        score[held] = model.predict_proba(rows.iloc[held][names])[:, 1]
        gain += model.booster_.feature_importance("gain")
        same_time += rows.iloc[held].ts.isin(rows.iloc[fit].ts).sum()
        keys = pd.MultiIndex.from_frame(rows.iloc[fit][["obl", "ts"]])
        neighbour = lambda delta: pd.MultiIndex.from_arrays(
            [rows.iloc[held].obl, rows.iloc[held].ts + pd.Timedelta(delta)])
        near_time += ((keys.get_indexer(neighbour("30min")) >= 0)
                      | (keys.get_indexer(neighbour("-30min")) >= 0)).sum()
    importance = pd.Series(gain / gain.sum(), index=names).sort_values(ascending=False)
    return dict(auc=float(roc_auc_score(labels, score)),
                importance=importance.to_dict(),
                held_same_timestamp_in_fit=float(same_time / len(rows)),
                held_same_oblast_neighbour_30min_in_fit=float(near_time / len(rows)))


def api_update_lag():
    """Late edits are a risk marker, not proof of when an end first became available."""
    records = []
    for manifest in sorted(D.API_DIR.glob("*/MANIFEST.json")):
        for file in json.loads(manifest.read_text())["files"]:
            body = json.loads(gzip.decompress((manifest.parent / file["file"]).read_bytes()))
            records.extend(dict(r, fetched=file["fetched_utc"]) for r in body["alerts"])
    rows = pd.DataFrame(records).sort_values("fetched").drop_duplicates("id", keep="last")
    for name in ("started_at", "finished_at", "updated_at"):
        rows[name] = pd.to_datetime(rows[name], utc=True, format="ISO8601")
    rows = rows[(rows.alert_type == "air_raid") & rows.location_type.isin(["oblast", "raion"])
                & (rows.started_at < D.MAP_CUTOFF) & (rows.finished_at <= D.MAP_CUTOFF)]
    lag = (rows.updated_at - rows.finished_at).dt.total_seconds()
    return dict(finished_core_records=len(rows), oblast_scope="all 24",
                updated_more_than_60s_after_end=int((lag > 60).sum()),
                lag_seconds_quantiles=lag.quantile([0.5, 0.9, 0.99, 1.0]).to_dict())


def endpoint_av(a, b, gap_days):
    """Hold first/last 3 days of BOTH classes, all oblasts together, twice.

    A 7-day gap excludes shared trailing feature windows. Ordinary TimeSeriesSplit
    on the concatenated periods cannot supply both AV classes in early fit folds.
    Scores cover only these endpoint blocks, NOT all rows or future forecasting.
    """
    labels, scores, folds = [], [], []
    for edge in ("first", "last"):
        fitting, holding = [], []
        for rows in (a, b):
            lo = rows.ts.min() if edge == "first" else rows.ts.max() + pd.Timedelta("30min") - pd.Timedelta("3D")
            hi = lo + pd.Timedelta("3D")
            held = (rows.ts >= lo) & (rows.ts < hi)
            gap = pd.Timedelta(days=gap_days)
            fit = (rows.ts <= lo - gap) | (rows.ts >= hi + gap)
            fit &= ~held
            assert fit.any() and held.any()
            if gap_days == 7:
                assert not ((rows.loc[fit, "ts"] > lo - gap)
                            & (rows.loc[fit, "ts"] < hi + gap)).any()
            fitting.append(rows[fit])
            holding.append(rows[held])
        x, z = pd.concat(fitting), pd.concat(holding)
        y = np.r_[np.zeros(len(fitting[0])), np.ones(len(fitting[1]))]
        target = np.r_[np.zeros(len(holding[0])), np.ones(len(holding[1]))]
        model = LGBMClassifier(**AdversarialValidation.SETTINGS, n_jobs=2)
        model.fit(x[Features.NAMES], y)
        pred = model.predict_proba(z[Features.NAMES])[:, 1]
        labels.extend(target)
        scores.extend(pred)
        folds.append(dict(edge=edge, fit_rows=[len(r) for r in fitting],
                          held_rows=[len(r) for r in holding], auc=float(roc_auc_score(target, pred))))
    return dict(auc=float(roc_auc_score(labels, scores)), folds=folds,
                scored_rows=len(scores), gap_days=gap_days)


def main():
    map_records = D.load_map()
    history = D.history(map_records, D.load_api())
    rows = forecast_rows(history)
    parts = {part: DECISION.rows(rows, part, 6).reset_index(drop=True) for part in DECISION.bounds}
    for h in (1, 3, 6):
        for part, (_, end) in DECISION.bounds.items():
            selected = DECISION.rows(rows, part, h)
            assert (selected.ts + pd.Timedelta(hours=h) <= end).all()
    assert not rows.duplicated(["obl", "ts"]).any()
    assert not set(Features.NAMES) & {"ts", "y1", "y3", "y6", "src", "alert_level", "end", "fetched"}
    result = dict(cutoff=str(D.MAP_CUTOFF), feature_names=Features.NAMES,
                  api_update_lag=api_update_lag(), parts={})
    for part, selected in parts.items():
        lo, hi = DECISION.bounds[part]
        ep = D.episodes(history[history.start < hi], hi)
        ep = ep[~ep.oblast_id.isin([9, 22, 28])]
        minutes = (ep.end - ep.start.clip(lower=lo)).dt.total_seconds().clip(lower=0).sum() / 60
        days = (hi - lo) / pd.Timedelta("1D")
        result["parts"][part] = dict(rows=len(selected),
            base_rate={f"y{h}": float(selected[f"y{h}"].mean()) for h in (1, 3, 6)},
            alert_fraction=float(minutes / (21 * days * 1440)),
            starts_per_oblast_day=float((ep.start >= lo).sum() / (21 * days)),
            feature_means=selected[Features.NAMES].mean().to_dict())
    output = ROOT / "results/leakage_audit.json"
    def save(name, value):
        result[name] = value
        output.write_text(json.dumps(result, indent=2) + "\n")
        print(name, json.dumps(value), flush=True)
    for other in ("val", "test"):
        a, b = parts["train"], parts[other]
        for name, names in (("all", Features.NAMES),
                            ("without_7d", [n for n in Features.NAMES if n not in ("starts_7d", "alert_min_7d")]),
                            ("calendar", ["obl", "hour", "dow"])):
            save(f"random_{other}_{name}", random_av(a, b, names))
        save(f"timestamp_grouped_{other}", random_av(a, b, Features.NAMES, group_timestamps=True))
        for gap in (0, 7):
            save(f"endpoint_{other}_gap{gap}", endpoint_av(a, b, gap))
    # Change only the history source: use the map throughout the pre-cutoff window.
    map_rows = forecast_rows(map_records)
    save("random_test_map_only", random_av(
        DECISION.rows(map_rows, "train", 6).reset_index(drop=True),
        DECISION.rows(map_rows, "test", 6).reset_index(drop=True), Features.NAMES))


if __name__ == "__main__":
    main()
