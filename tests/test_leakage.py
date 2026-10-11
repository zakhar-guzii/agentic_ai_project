import numpy as np
import pandas as pd

from alerts.baselines import Climatology
from alerts.checks import TruncationCheck
from alerts.features import AlertGrid, Features, ForecastTable

T = lambda s: pd.Timestamp(s, tz="UTC")
ORIGIN, END = T("2026-09-20 00:00"), T("2026-10-04 00:00")


def synthetic_world(seed=0, n=150):
    """Random raion alerts in 5 neighbouring oblasts over 4 days: overlaps, starts mid-minute, 3 still on at the end."""
    rng = np.random.default_rng(seed)
    start = T("2026-09-30 00:00") + pd.to_timedelta(rng.uniform(0, 4 * 86400, n), "s")
    end = start + pd.to_timedelta(rng.uniform(30, 4 * 3600, n), "s")
    r = pd.DataFrame({"oblast_id": rng.choice([8, 5, 27, 14, 31], n), "level": "raion", "start": start, "end": end})
    r.loc[r.start.nlargest(3).index, "end"] = pd.NaT
    return r


WORLD = synthetic_world()
MOMENTS = pd.date_range("2026-10-01 00:00", "2026-10-03 23:30", freq="30min", tz="UTC").append(
    pd.DatetimeIndex([T("2026-10-02 12:07"), T("2026-10-03 03:41")]))
features_at = lambda records, moment: Features(AlertGrid(records, ORIGIN, END)).at([moment])


def test_features_use_nothing_from_t_on():
    assert TruncationCheck(WORLD).mismatches(features_at, MOMENTS) == []


def test_a_planted_leak_is_caught():
    peek = lambda records, moment: Features(AlertGrid(records, ORIGIN, END)).at([moment + pd.Timedelta("1min")])
    caught = TruncationCheck(WORLD).mismatches(peek, MOMENTS)
    assert len(caught) >= 10, f"the check did not bite: {len(caught)} of {len(MOMENTS)} moments"


def test_climatology_uses_nothing_from_t_on():
    def clim_at(records, moment):
        rows = ForecastTable(records, T("2026-09-30 00:00"), END).rows
        return Climatology(28).predict(rows)[rows.ts == moment].reset_index(drop=True)

    later = MOMENTS[MOMENTS >= T("2026-10-02 00:00")]  # by then two days of rows have matured
    assert TruncationCheck(WORLD).mismatches(clim_at, later) == []


# --- the real history (skipped before the first alerts.in.ua pull) ---
import pytest  # noqa: E402

from alerts import data as D  # noqa: E402
from alerts.splits import DECISION  # noqa: E402

need_api = pytest.mark.skipif(not list(D.API_DIR.glob("*/MANIFEST.json")), reason="no alerts.in.ua pull saved yet")


@pytest.fixture(scope="module")
def history():
    return D.history(D.load_map(), D.load_api())


def hard_moments(h):
    """Moments where a look-ahead bug would show: at a start, just after an all-clear, inside a long alert, at both
    DST switches and at the splice. All before the map cutoff."""
    ep = D.episodes(h[h.start < D.MAP_CUTOFF], D.MAP_CUTOFF)
    long = ep[ep.end - ep.start > pd.Timedelta("24h")].iloc[0]
    return [ep.start.iloc[5000].floor("min"), ep.end.iloc[7000].ceil("min") + pd.Timedelta("1min"),
            ep.end.iloc[9000].ceil("min") + pd.Timedelta("2min"), long.start + pd.Timedelta("12h"),
            T("2025-10-26 01:00"), T("2026-03-29 01:00"), D.SPLICE]


@need_api
def test_real_features_and_climatology_use_nothing_from_t_on(history):
    rng = np.random.default_rng(1)
    first, last = T("2025-11-15"), D.MAP_CUTOFF - pd.Timedelta("1h")
    random = [first + pd.Timedelta(minutes=int(m)) for m in rng.integers(0, (last - first) // pd.Timedelta("1min"), 23)]
    moments = hard_moments(history) + random
    origin = T("2025-10-02")
    real_features = lambda r, m: Features(AlertGrid(r, origin, D.MAP_CUTOFF)).at([m])
    check = TruncationCheck(history[history.start < D.MAP_CUTOFF])
    assert check.mismatches(real_features, moments) == []

    def clim_at(r, m):  # 29 days of rows are enough for the 28-day rates
        start = m.tz_convert("Europe/Kyiv").normalize().tz_convert("UTC") - pd.Timedelta("29D")
        rows = ForecastTable(r, start, D.MAP_CUTOFF).rows
        return Climatology(28).predict(rows)[rows.ts == m.floor("30min")].reset_index(drop=True)

    assert check.mismatches(clim_at, [m.floor("30min") for m in moments[:3]]) == []


@need_api
def test_decision_split_purges_every_label_window(history):
    rows = ForecastTable(history, T("2025-11-01"), D.MAP_CUTOFF).rows
    (_, val_start), (_, test_start), _ = DECISION.bounds.values()
    for h in (1, 3, 6):
        late = lambda part: (DECISION.rows(rows, part, h).ts + pd.Timedelta(hours=h)).max()
        assert late("train") <= val_start and late("val") <= test_start
