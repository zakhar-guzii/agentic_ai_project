import pandas as pd

from alert_outlook.data import history as data

T = lambda s: pd.Timestamp(s, tz="UTC")


def recs(*rows):
    """rows: (start, end[, alert_level]) -> raion records of Kyivska (14) in the loader schema."""
    out = pd.DataFrame([dict(src="api", oblast_id=14, unit_id=76, unit="r", level="raion",
                             alert_level=r[2] if len(r) > 2 else "yellow", start=T(r[0]), end=r[1]) for r in rows])
    return out.assign(end=pd.to_datetime(out.end, utc=True))  # tz-aware even when every alert is still on


def test_days_are_kyiv_calendar_days():
    # 20:30-21:30 UTC is 23:30-00:30 Kyiv: half on each Kyiv day (UTC days would put all 60 min on 09-20)
    d = data.daily(recs(("2026-09-20 20:30", "2026-09-20 21:30")), T("2026-09-19 21:00"), T("2026-09-21 21:00"), [14])
    d = d.set_index("day")
    assert d.loc["2026-09-20", ["alert", "starts"]].tolist() == [30, 1]
    assert d.loc["2026-09-21", ["alert", "starts"]].tolist() == [30, 0]


DAY = T("2026-09-19 21:00"), T("2026-09-20 21:00")  # 2026-09-20, Kyiv


def test_overlapping_records_count_once():
    # since the reform the map keeps overlapping records for one raion (Wrong #5): count the union, not records
    d = data.daily(recs(("2026-09-20 10:00", "2026-09-20 11:00"), ("2026-09-20 10:30", "2026-09-20 11:30")), *DAY, [14])
    assert d[["alert", "starts"]].values.tolist() == [[90, 1]]


def test_restart_after_all_clear_is_a_new_start():
    d = data.daily(recs(("2026-09-20 10:00", "2026-09-20 10:30"), ("2026-09-20 10:31", "2026-09-20 11:00")), *DAY, [14])
    assert d[["alert", "starts"]].values.tolist() == [[59, 2]]


def test_red_minutes_are_the_union_of_red_records():
    d = data.daily(recs(("2026-09-20 10:00", "2026-09-20 12:00"), ("2026-09-20 11:00", "2026-09-20 11:30", "red")),
                   *DAY, [14])
    assert d[["alert", "red"]].values.tolist() == [[120, 30]]


def test_red_is_unknown_before_the_splice():
    # the map has no levels: 09-10 (Kyiv) is before SPLICE (09-12 00:00 Kyiv), so its red share is unknown, not zero
    d = data.daily(recs(("2026-09-10 10:00", "2026-09-10 11:00", None)), T("2026-09-09 21:00"), T("2026-09-10 21:00"), [14])
    assert d.alert.tolist() == [60] and d.red.isna().all()


def test_minutes_follow_kyiv_days_and_the_window():
    # 2026-03-29 is the spring DST day in Kyiv (23 h); the window ends 03-30 12:00 Kyiv, so that day is partial
    d = data.daily(recs(("2026-03-29 10:00", "2026-03-29 10:30")), T("2026-03-28 22:00"), T("2026-03-30 09:00"), [14])
    d = d.set_index("day")
    assert d.minutes.to_dict() == {pd.Timestamp("2026-03-29"): 1380, pd.Timestamp("2026-03-30"): 720}


def test_alert_still_on_is_censored_at_hi_and_a_quiet_region_gets_zeros():
    d = data.daily(recs(("2026-09-20 20:00", None)), T("2026-09-19 21:00"), T("2026-09-20 20:45"), [14, 31])
    assert d.set_index("obl")[["alert", "starts", "red"]].to_dict("index") == {
        14: dict(alert=45, starts=1, red=0), 31: dict(alert=0, starts=0, red=0)}
