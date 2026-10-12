import json

import numpy as np

import pandas as pd
import pytest

from alerts import data as D

T = lambda s: pd.Timestamp(s, tz="UTC")


def pull(root, stamp, files):
    """A saved pull as `api.pull_history` writes its MANIFEST: {uid: (fetched_utc, last_updated_at)}."""
    (root / stamp).mkdir()
    (root / stamp / "MANIFEST.json").write_text(json.dumps({"files": [
        dict(uid=uid, fetched_utc=fetched, last_updated_at=updated) for uid, (fetched, updated) in files.items()]}))


def test_saved_data_end_at_the_earliest_of_the_newest_server_snapshots(tmp_path):
    pull(tmp_path, "20261011T1247Z", {3: ("2026-10-11T12:47:56Z", "2026/10/11 12:46:28 +0000"),
                                      4: ("2026-10-11T12:49:02Z", "2026/10/11 12:48:30 +0000")})
    pull(tmp_path, "20261012T0900Z", {3: ("2026-10-12T09:00:40Z", "2026/10/12 09:00:10 +0000")})  # interrupted
    # uid 4 was last fetched on 10-11, and its server snapshot (not the later fetch) is where its history ends
    assert D.api_asof([3, 4], tmp_path) == T("2026-10-11 12:48")
    with pytest.raises(KeyError):
        D.api_asof([3, 4, 5], tmp_path)  # uid 5 was never fetched


# --- the forecast at T ---
from alerts import live  # noqa: E402
from alerts.model import Forecaster  # noqa: E402

MODEL = Forecaster.load(D.ROOT / "models/logistic.joblib")  # the frozen step-3 forecaster
VOLYN, RIVNE, LVIV = 8, 5, 27
NOW = T("2026-10-01 12:00")


def records(rows):
    """(oblast_id, alert_level, start, end) -> raion-level AIR records; end None = still on."""
    r = pd.DataFrame([dict(oblast_id=o, level="raion", alert_level=lvl, start=T(s), end=T(e) if e else pd.NaT)
                      for o, lvl, s, e in rows])
    return r.assign(end=pd.to_datetime(r.end, utc=True))  # tz-aware even when every alert is still on


WORLD = records([(VOLYN, "yellow", "2026-10-01 11:00", None), (VOLYN, "red", "2026-10-01 11:30", "2026-10-01 11:59:30"),
                 (RIVNE, "yellow", "2026-10-01 11:30", None),
                 (LVIV, "yellow", "2026-10-01 10:00", "2026-10-01 10:20"), (LVIV, "red", "2026-10-01 12:05", None)])


def test_regions_under_alert_now_get_their_level():
    now = live.forecast(WORLD, NOW, MODEL).set_index("obl")
    assert len(now) == 24
    assert now.index[now.under == 1].tolist() == [RIVNE, VOLYN]
    # Volyn's red alert ended at 11:59:30, inside the minute before T; Lviv's red one starts after T
    assert now.level.dropna().to_dict() == {RIVNE: "yellow", VOLYN: "red"}


def test_an_empty_or_negative_red_record_leaves_the_level_yellow():
    world = records([(VOLYN, "yellow", "2026-10-01 11:00", None),
                     (VOLYN, "red", "2026-10-01 11:59:30", "2026-10-01 11:59:30"),  # zero length
                     (VOLYN, "red", "2026-10-01 11:59:40", "2026-10-01 11:59:20")])  # ends before it starts
    assert live.forecast(world, NOW, MODEL).set_index("obl").level.dropna().to_dict() == {VOLYN: "yellow"}


def test_clear_regions_get_the_forecast_and_both_references():
    now = live.forecast(WORLD, NOW, MODEL).set_index("obl")
    p, clear = ["p1", "p3", "p6"], now.under == 0
    assert clear.sum() == 22 and now.loc[clear, p].apply(lambda c: c.between(0, 1)).all().all()
    assert now.loc[[RIVNE, VOLYN], p + ["clim28_1", "recent7_1"]].isna().all().all()  # no forecast while an alert is on
    # recent7: Lviv had 1 start in the 10 060 clear minutes of the last 7 days
    assert now.loc[LVIV, ["recent7_1", "recent7_3", "recent7_6"]].tolist() == pytest.approx(
        [1 - np.exp(-60 * h / 10060) for h in (1, 3, 6)])
    # clim28 is counted at 00:00 Kyiv, as in the benchmark: today's alerts are not in it yet, so no start at all
    assert (now.loc[clear, ["clim28_1", "clim28_3", "clim28_6"]] == 0).all().all()


class EchoRecent7:
    """A stand-in for a v2 forecaster with reference inputs: its forecast is the recent7 input it was given."""

    def predict(self, rows):
        return pd.DataFrame({f"p{h}": rows[f"recent7_{h}"] for h in (1, 3, 6)}, index=rows.index)


def test_a_model_with_reference_inputs_gets_them_at_t():
    now = live.forecast(WORLD, NOW, EchoRecent7()).set_index("obl")
    clear = now.under == 0
    assert (now.loc[clear, ["p1", "p3", "p6"]].to_numpy() == now.loc[clear, ["recent7_1", "recent7_3", "recent7_6"]].to_numpy()).all()
    assert now.loc[LVIV, "p1"] == pytest.approx(1 - np.exp(-60 / 10060))  # Lviv's own rate, as in the test above


def random_world(seed=0, n=150):
    """Random raion alerts of both levels in 5 neighbouring oblasts over 4 days: overlaps, starts mid-minute, 3 still on
    at the end (as in test_leakage)."""
    rng = np.random.default_rng(seed)
    start = T("2026-09-30 00:00") + pd.to_timedelta(rng.uniform(0, 4 * 86400, n), "s")
    r = pd.DataFrame({"oblast_id": rng.choice([8, 5, 27, 14, 31], n), "level": "raion",
                      "alert_level": rng.choice(["yellow", "red"], n), "start": start,
                      "end": start + pd.to_timedelta(rng.uniform(30, 4 * 3600, n), "s")})
    r.loc[r.start.nlargest(3).index, "end"] = pd.NaT
    return r


def test_the_forecast_uses_nothing_from_t_on():
    from alerts.checks import TruncationCheck
    moments = pd.date_range("2026-10-01 00:00", "2026-10-03 23:00", freq="7h13min", tz="UTC").append(
        pd.DatetimeIndex([T("2026-10-03 23:59")]))  # after the alerts still on at the end have started
    at = lambda records, moment: live.forecast(records, moment, MODEL)
    assert TruncationCheck(random_world()).mismatches(at, moments) == []


# --- the log and its score ---
def test_a_moment_is_logged_once(tmp_path):
    path, rows = tmp_path / "forecast_log.csv", live.forecast(WORLD, NOW, MODEL)
    assert live.log(rows, path) and not live.log(rows, path)
    back = pd.read_csv(path, parse_dates=["ts"])
    assert len(back) == 24 and (back.ts == NOW).all()


def logged(world, path, made=NOW):
    """The log of a forecast at NOW, made at `made`, as `predict` writes it and `score` reads it back."""
    live.log(live.forecast(world, NOW, MODEL).assign(made_at=made), path)
    return pd.read_csv(path, parse_dates=["ts", "made_at"])


def test_a_logged_forecast_is_scored_once_its_window_closes(tmp_path):
    world = records([(RIVNE, "yellow", "2026-10-01 11:30", None),  # under alert at T: no forecast to score
                     (VOLYN, "red", "2026-10-01 14:00", "2026-10-01 14:20")])  # a start at T + 2 h
    scored = live.score(logged(world, tmp_path / "log.csv"), world, NOW + pd.Timedelta("4h"), MODEL).set_index("obl")
    assert len(scored) == 23 and RIVNE not in scored.index
    # the 6 h window is still open at T + 4 h
    assert scored.loc[VOLYN, ["y1", "y3", "y6"]].tolist() == pytest.approx([0, 1, np.nan], nan_ok=True)
    assert scored.loc[LVIV, ["y1", "y3", "y6"]].tolist() == pytest.approx([0, 0, np.nan], nan_ok=True)


def test_replays_and_timely_forecasts_are_summarised_apart(tmp_path):
    world = records([(VOLYN, "red", "2026-10-01 14:00", "2026-10-01 14:20")])  # a start at T + 2 h
    # made at T + 1 h, the moment its 1 h window closed: a replay at 1 h, a live forecast at 3 h
    scored = live.score(logged(world, tmp_path / "log.csv", made=NOW + pd.Timedelta("1h")), world,
                        NOW + pd.Timedelta("4h"), MODEL)
    s = live.summary(scored)
    assert s.index.tolist() == [(1, "replay"), (3, "live")]  # the 6 h window is still open at T + 4 h
    assert s.n.tolist() == [24, 24]
    assert s.loc[(1, "replay"), "model"] == pytest.approx((scored.p1 ** 2).mean())  # no start within 1 h
    assert s.loc[(3, "live"), "model"] == pytest.approx(((scored.p3 - (scored.obl == VOLYN)) ** 2).mean())


def test_features_revised_after_the_log_are_flagged(tmp_path):
    from alerts.features import NEIGHBOURS
    first = records([(LVIV, "yellow", "2026-10-01 08:00", "2026-10-01 09:00")])
    final = records([(LVIV, "yellow", "2026-10-01 08:00", "2026-10-01 09:30")])  # the all-clear was revised later
    scored = live.score(logged(first, tmp_path / "log.csv"), final, NOW + pd.Timedelta("1h"), MODEL)
    # Lviv's own minutes under alert, and its 5 neighbours' nb_alert_min_24h
    assert sorted(scored.obl[scored.revised]) == sorted([LVIV] + NEIGHBOURS[LVIV])
    assert scored.filter(like="final_p").notna().all().all()  # the forecasts on the revised features, for their Brier


def test_a_region_revised_into_an_alert_is_compared_on_the_same_rows(tmp_path):
    first = records([(LVIV, "yellow", "2026-10-01 08:00", "2026-10-01 09:00"),
                     (VOLYN, "red", "2026-10-01 12:30", "2026-10-01 12:50")])  # a start inside the 1 h window
    final = records([(LVIV, "yellow", "2026-10-01 08:00", None),  # the all-clear was withdrawn: Lviv was on at T
                     (VOLYN, "red", "2026-10-01 12:30", "2026-10-01 12:50")])
    scored = live.score(logged(first, tmp_path / "log.csv"), final, NOW + pd.Timedelta("1h"), MODEL)
    s = live.summary(scored).loc[(1, "live")]
    # every logged clear row is scored as published; Lviv, under alert at T now, has no recomputed forecast
    assert (s.n, s.still_clear) == (24, 23)
    assert s.model == pytest.approx(((scored.p1 - scored.y1) ** 2).mean())
    rest = scored[scored.obl != LVIV]  # the revision check compares the two forecasts on the same 23 rows
    assert s.model_logged == pytest.approx(((rest.p1 - rest.y1) ** 2).mean())
    assert s.model_recomputed == pytest.approx(((rest.final_p1 - rest.y1) ** 2).mean())


def test_a_log_with_every_region_under_alert_scores_nothing(tmp_path):
    from alerts.features import OBLASTS
    world = records([(o, "yellow", "2026-10-01 11:00", None) for o in OBLASTS])
    log = logged(world, tmp_path / "log.csv")
    scored = live.score(log, world, NOW + pd.Timedelta("7h"), MODEL)
    assert scored.empty and live.summary(scored).empty
    assert scored.columns.tolist() == log.columns.tolist() + ["y1", "y3", "y6", "revised",
                                                              "final_p1", "final_p3", "final_p6"]
    assert scored.dtypes[log.columns].equals(log.dtypes)  # `ts` stays a datetime, as in a non-empty score


# --- the holdout ---
def test_the_holdout_scores_clear_rows_from_lo_whose_windows_close_by_hi():
    world = records([(VOLYN, "red", "2026-10-01 14:00", "2026-10-01 14:20")])
    lo, hi = T("2026-10-01 12:00"), T("2026-10-01 18:00")
    rows = live.holdout(world, lo, hi, MODEL)
    assert (rows.ts.min(), rows.ts.max()) == (lo, T("2026-10-01 17:30")) and set(rows.ts.dt.minute) == {0, 30}
    volyn = rows[rows.obl == VOLYN].set_index("ts")
    assert volyn.loc[lo, ["y1", "y3", "y6"]].tolist() == [0, 1, 1]  # the start at 14:00 is within 3 and 6 h of 12:00
    assert rows.y6.notna().groupby(rows.ts).all().loc[lambda s: s].index.tolist() == [lo]  # 12:00 + 6 h = hi
    assert rows.y3.notna().groupby(rows.ts).all().loc[lambda s: s].index.max() == T("2026-10-01 15:00")
    assert rows.y3[rows.ts > T("2026-10-01 15:00")].isna().all()
    cols = ["p1", "p3", "p6", "clim28_1", "clim28_3", "clim28_6", "recent7_1", "recent7_3", "recent7_6"]
    assert rows[cols].notna().all().all()


# --- the saved alerts.in.ua pulls (skipped before the first one) ---
@pytest.mark.skipif(not list(D.API_DIR.glob("*/MANIFEST.json")), reason="no alerts.in.ua pull saved yet")
def test_the_forecast_on_the_saved_data():
    from main import OBLAST_UIDS
    now = live.forecast(D.history(D.load_map(), D.load_api()), D.api_asof(OBLAST_UIDS), MODEL)
    under = now.under == 1
    assert len(now) == 24 and now.level[under].isin(["yellow", "red"]).all() and now.level[~under].isna().all()
    assert now.loc[~under, ["p1", "p3", "p6"]].apply(lambda c: c.between(0, 1)).all().all()
