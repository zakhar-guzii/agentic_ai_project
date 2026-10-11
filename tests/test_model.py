import numpy as np
import pandas as pd
import pytest

from alerts.model import Boosting, ForwardRun, Platt
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
