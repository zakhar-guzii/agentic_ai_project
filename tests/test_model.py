import numpy as np
import pandas as pd
import pytest

from alerts.features import ForecastTable
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
