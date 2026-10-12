import numpy as np
import pandas as pd

from alerts.baselines import Climatology, RecentLevel
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
from alerts.model import Boosting, CatBoost, ForwardRun, Logistic  # noqa: E402
from alerts.splits import BENCHMARK, CHOOSE, DECISION, Split  # noqa: E402

need_api = pytest.mark.skipif(not list(D.API_DIR.glob("*/MANIFEST.json")), reason="no alerts.in.ua pull saved yet")


@pytest.fixture(scope="module")
def history():
    return D.history(D.load_map(), D.load_api())


@pytest.fixture(scope="module")
def rows(history):
    return ForecastTable(history, T("2025-11-01"), D.MAP_CUTOFF).rows


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
def test_decision_split_purges_every_label_window(rows):
    (_, val_start), (_, test_start), _ = DECISION.bounds.values()
    for h in (1, 3, 6):
        late = lambda part: (DECISION.rows(rows, part, h).ts + pd.Timedelta(hours=h)).max()
        assert late("train") <= val_start and late("val") <= test_start


@need_api
def test_forward_checks_fit_only_on_labels_known_at_each_block_start(rows):
    for a, b, blocks in (CHOOSE, BENCHMARK):
        for h in (1, 3, 6):
            folds = list(DECISION.forward(rows, h, a, b, blocks))
            assert len(folds) == blocks
            for fit, held in folds:
                assert (fit.ts + pd.Timedelta(hours=h)).max() <= held.ts.min()  # held.ts.min() is the block start
                assert held.ts.min() >= a and (held.ts + pd.Timedelta(hours=h)).max() <= b
            block = pd.concat([held.assign(k=k) for k, (_, held) in enumerate(folds)])
            assert (block.groupby("ts").k.nunique() == 1).all()  # a moment is never split between blocks


class Constant:
    """A stub candidate with no model: the run takes seconds and nothing is scored."""
    name = "const"

    def fit(self, rows, hours, asof):
        return self

    def predict(self, rows):
        return np.full(len(rows), 0.5)


@need_api
def test_calibration_follows_decision_4_on_the_real_blocks(rows):
    run = ForwardRun([Constant()])
    for h in (1, 3, 6):
        out = run.run(rows, h, [CHOOSE, BENCHMARK])
        starts, scored = sorted(out.block.unique()), sorted(out[out.scored].block.unique())
        assert len(starts) == 10 and scored == starts[2:]  # CHOOSE 1-2 only warm the calibrator up
        for s in scored:
            win = run.window(out, s, h)
            assert win.ts.min() >= s - pd.Timedelta("14D") and (win.ts + pd.Timedelta(hours=h)).max() <= s
        first = run.window(out, DECISION.bounds["test"][0], h)  # the first benchmark block learns from val forecasts
        assert starts[6] == DECISION.bounds["test"][0] and first.ts.min() >= DECISION.bounds["val"][0]
        assert out[out.scored].obl.nunique() == 24


# A forward run over the synthetic world: rows from 30 September, daily blocks from 1 October, a 1-day window.
FIRST, BLOCKS_FROM = T("2026-09-30 00:00"), T("2026-10-01 00:00")
SMALL = Split(FIRST, END, END, END)
# moments in the scored blocks: block starts and half past, where a leak from the hour before would show, and a later one
SCORED = [T("2026-10-02 00:00"), T("2026-10-02 00:30"), T("2026-10-03 00:00"), T("2026-10-03 21:30")]
# the synthetic world plus a start 10 min after a block start in Zakarpattia, clear until then: the 23:30 row before it
# has y1 = 1, which nobody knew at the block start
SHARP = pd.concat([WORLD, pd.DataFrame({"oblast_id": [11], "level": ["raion"], "start": [T("2026-10-02 00:10")],
                                                "end": [T("2026-10-02 00:40")]})], ignore_index=True)


def forecasts(run):
    """compute(records, T) for TruncationCheck: the calibrated forecasts of `run` at T. Like a forecaster at T, the run
    stops with the block that holds T: later blocks would calibrate on labels nobody has yet."""
    def at(records, moment):
        rows = ForecastTable(records, FIRST, END).rows
        rows = rows.join(Climatology(28).predict(rows)).join(RecentLevel().predict(rows))  # the reference inputs
        days = (moment.floor("D") - BLOCKS_FROM).days + 1
        out = run.run(rows, 1, [(BLOCKS_FROM, BLOCKS_FROM + pd.Timedelta(days=days), days)])
        return out.loc[out.ts == moment, ["obl"] + [c.name for c in run.candidates]].reset_index(drop=True)
    return at


REFS = ["clim28", "recent7"]
V2 = [Boosting(refs=REFS, half_life=30, params=dict(n_estimators=50, num_leaves=7, min_child_samples=5), name="gbm_v2"),
      CatBoost(refs=REFS, half_life=30, params=dict(iterations=50, depth=4), name="catboost_v2"),
      Logistic(refs=REFS, half_life=30, params=dict(C=0.1, class_weight="balanced"), name="logistic_v2")]


@pytest.mark.parametrize("candidate", [Boosting(), Boosting(clim=True), Boosting(half_life=60), CatBoost(), Logistic(), *V2],
                         ids=lambda c: c.name)
def test_a_calibrated_forecast_uses_nothing_from_t_on(candidate):
    run = ForwardRun([candidate], split=SMALL, window=pd.Timedelta("1D"))
    assert TruncationCheck(SHARP).mismatches(forecasts(run), SCORED) == []


def test_a_calibrator_fitted_on_unfinished_labels_is_caught():
    class Unpurged(ForwardRun):
        def window(self, raw, s, hours):  # the planted leak: rows whose label window runs past s
            return raw[(raw.ts >= s - self.window_length) & (raw.ts < s)]

    caught = TruncationCheck(SHARP).mismatches(forecasts(Unpurged([Boosting()], SMALL, pd.Timedelta("1D"))), SCORED)
    assert T("2026-10-02 00:00") in caught, "the check did not bite"
