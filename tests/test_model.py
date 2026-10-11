import numpy as np
import pandas as pd
import pytest

from alerts.model import Boosting, Platt


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
