import numpy as np
import pandas as pd
import pytest

from alerts.features import Features, ForecastTable
from alerts.model import Boosting, Forecaster, ForwardRun, Logistic, Platt
from alerts.splits import Split


def test_platt_maps_each_forecast_to_its_observed_rate():
    # a model said 0.2 where 10 of 100 rows had a start, and 0.6 where 50 of 100 had one
    p = np.r_[np.full(100, 0.2), np.full(100, 0.6)]
    y = np.r_[np.ones(10), np.zeros(90), np.ones(50), np.zeros(50)]
    assert Platt().fit(p, y).predict(np.array([0.2, 0.6])) == pytest.approx([0.1, 0.5], abs=1e-3)


def test_recency_weights_halve_every_half_life():
    s = pd.Timestamp("2026-09-13", tz="UTC")
    ts = pd.Series([s, s - pd.Timedelta("60D"), s - pd.Timedelta("120D")])
    assert Boosting(half_life=60).weights(ts, s).tolist() == [1, 0.5, 0.25]
    assert Boosting().weights(ts, s) is None  # every row counts the same


DAY = lambda d, hhmm="00:00": pd.Timestamp(f"2026-09-0{d + 1} {hhmm}", tz="UTC")
# one oblast at 00:00, 06:00, 12:00, 18:00 and 23:30 of four days; y1 = a start in the next hour
LABELS = {0: [0, 0, 0, 0, 1], 1: [1, 1, 1, 1, 0], 2: [0, 0, 0, 0, 0], 3: [0, 0, 0, 0, 0]}
ROWS = pd.DataFrame([dict(obl=8, ts=DAY(d, t), y1=y) for d, ys in LABELS.items()
                     for t, y in zip(["00:00", "06:00", "12:00", "18:00", "23:30"], ys)])


class Constant:
    """A stub candidate that always says 0.5, so a calibrator returns the share of starts in its window."""
    name = "const"

    def fit(self, rows, hours, asof):
        return self

    def predict(self, rows):
        return np.full(len(rows), 0.5)


def test_each_block_is_calibrated_on_the_window_before_it():
    run = ForwardRun([Constant()], split=Split(DAY(0), DAY(3), DAY(3), DAY(4)), window=pd.Timedelta("2D"))
    out = run.run(ROWS, 1, [(DAY(0), DAY(3), 3), (DAY(3), DAY(4), 1)])  # three daily blocks, then one more range
    blocks = out.groupby("block").agg(scored=("scored", "first"), p=("const", "first"))
    assert blocks.index.tolist() == [DAY(0), DAY(1), DAY(2), DAY(3)]
    assert blocks.scored.tolist() == [False, False, True, True]  # a 2-day window needs 2 days of earlier forecasts
    assert blocks.p.iloc[:2].isna().all()
    assert blocks.p.iloc[2] == pytest.approx(5 / 9, abs=1e-3)  # days 0-1, but not 23:30 of day 1: its hour ends after s
    assert blocks.p.iloc[3] == pytest.approx(4 / 9, abs=1e-3)  # the first range's days 1-2; day 0 is out of the window


def world(seed=0, n=120):
    """Random 20-minute raion alerts in Volyn, Rivne and Lviv from 28 September to 4 October."""
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2026-09-28", tz="UTC") + pd.to_timedelta(rng.uniform(0, 6 * 86400, n), "s")
    return pd.DataFrame({"oblast_id": rng.choice([8, 5, 27], n), "level": "raion", "start": start,
                         "end": start + pd.Timedelta("20min")})


def test_a_saved_forecaster_forecasts_the_same_after_loading(tmp_path):
    first, asof = pd.Timestamp("2026-09-28", tz="UTC"), pd.Timestamp("2026-10-03", tz="UTC")
    rows = ForecastTable(world(), first, pd.Timestamp("2026-10-04", tz="UTC")).rows
    run = ForwardRun([Logistic(), Boosting()], split=Split(first, asof, asof, asof), window=pd.Timedelta("1D"))
    raws = {h: run.run(rows, h, [(pd.Timestamp("2026-09-30", tz="UTC"), asof, 3)]) for h in (1, 3)}
    later = rows[rows.ts >= asof]
    for name, forecaster in run.final(rows, raws, asof).items():
        forecaster.save(tmp_path / f"{name}.joblib")
        loaded = Forecaster.load(tmp_path / f"{name}.joblib")
        assert loaded.predict(later).equals(forecaster.predict(later))
        assert list(loaded.predict(later).columns) == ["p1", "p3"]
        assert (loaded.meta["train_start"], loaded.meta["asof"]) == (first, asof)


def test_final_forecaster_calibrates_only_on_completed_oof_labels():
    asof = DAY(3)
    run = ForwardRun([Constant()], split=Split(DAY(0), asof, asof, DAY(4)), window=pd.Timedelta('2D'))
    raw = run.run(ROWS, 1, [(DAY(0), DAY(4), 4)])
    final = run.final(ROWS, {1: raw}, asof)['const']
    # Known rows: 5 + 5 + 4. Calibration days 1-2: 4 positives among 9 completed rows.
    assert final.meta['counts'][1] == {'fit': 14, 'calibration': 9}
    assert final.predict(ROWS[ROWS.ts >= asof]).p1.tolist() == pytest.approx([4 / 9] * 5, abs=1e-3)


def test_progress_logs_each_scored_block_after_its_calibration(capsys):
    run = ForwardRun([Constant()], split=Split(DAY(0), DAY(3), DAY(3), DAY(4)), window=pd.Timedelta("2D"))
    run.run(ROWS, 1, [(DAY(0), DAY(3), 3), (DAY(3), DAY(4), 1)], progress=True)
    scored = [line for line in capsys.readouterr().out.splitlines() if "brier=" in line]
    # day 2: four held rows (23:30 is purged: its hour ends in the next block), no start, all at 5/9 -> Brier 25/81;
    # one class, so no AP or AUC
    assert scored == ["H=1 block=2026-09-03 00:00:00+00:00 const: n=4 base=0.000 mean_p=0.556 brier=0.3086 ap=nan auc=nan",
                      "H=1 block=2026-09-04 00:00:00+00:00 const: n=4 base=0.000 mean_p=0.444 brier=0.1975 ap=nan auc=nan"]


# one region at the same moment of the week: every feature equal, so a model can only learn the share of starts
S = pd.Timestamp("2026-09-30 12:00", tz="UTC")
SAME = {**{f: 1 for f in Features.NAMES}, "obl": 8, "hour": 12.0, "dow": 2}


def test_logistic_weights_recent_rows_more():
    # 10 rows with a start now, 10 without one 70 days (ten weeks) before: with a 70-day half-life the old rows weigh
    # 1/2 each, so the forecast is 10 / (10 + 5) = 2/3; unweighted it is 1/2
    rows = pd.DataFrame({**SAME, "ts": [S] * 10 + [S - pd.Timedelta("70D")] * 10, "y1": [1] * 10 + [0] * 10})
    assert Logistic(half_life=70).fit(rows, 1, S).predict(rows.head(1)) == pytest.approx([2 / 3], abs=1e-3)
    assert Logistic().fit(rows, 1, S).predict(rows.head(1)) == pytest.approx([1 / 2], abs=1e-3)


def test_logistic_can_take_a_reference_forecast_as_an_input():
    # every feature is the same; only the 7-day rate differs, and a start follows the high rate only
    rows = pd.DataFrame({**SAME, "ts": S, "recent7_1": [0.1] * 10 + [0.9] * 10, "y1": [0] * 10 + [1] * 10})
    p = Logistic(refs=["recent7"]).fit(rows, 1, S).predict(rows.iloc[[0, -1]])
    assert p[0] < .2 and p[1] > .8


def test_recalibrating_a_run_with_another_window_equals_running_with_it():
    split, ranges = Split(DAY(0), DAY(3), DAY(3), DAY(4)), [(DAY(0), DAY(3), 3), (DAY(3), DAY(4), 1)]
    three_days = ForwardRun([Constant()], split=split, window=pd.Timedelta("3D")).run(ROWS, 1, ranges)
    two_days = ForwardRun([Constant()], split=split, window=pd.Timedelta("2D"))
    assert two_days.calibrate(three_days, 1).equals(two_days.run(ROWS, 1, ranges))
