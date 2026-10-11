import pandas as pd

from alerts import data

T = lambda s: pd.Timestamp(s, tz="UTC")
ASOF = T("2026-10-11 12:00")


def recs(*rows):
    """rows: (oblast_id, level, start, end) -> record table."""
    return pd.DataFrame([dict(src="api", oblast_id=o, unit_id=i, unit="u", level=lv, alert_level="red", start=T(s),
                              end=T(e) if e else pd.NaT, rec_id=i) for i, (o, lv, s, e) in enumerate(rows)])


def spans(ep):
    return ep[["oblast_id", "start", "end"]].values.tolist()


def test_overlapping_raions_make_one_episode():
    r = recs((14, "raion", "2026-10-01 10:00", "2026-10-01 10:30"), (14, "raion", "2026-10-01 10:20", "2026-10-01 11:00"))
    assert spans(data.episodes(r, ASOF)) == [[14, T("2026-10-01 10:00"), T("2026-10-01 11:00")]]


def test_nested_interval_does_not_create_a_start():
    r = recs((14, "raion", "2026-10-01 10:00", "2026-10-01 12:00"), (14, "raion", "2026-10-01 10:30", "2026-10-01 11:00"),
             (14, "oblast", "2026-10-01 11:30", "2026-10-01 11:45"))
    assert spans(data.episodes(r, ASOF)) == [[14, T("2026-10-01 10:00"), T("2026-10-01 12:00")]]


def test_one_minute_gap_gives_two_episodes():
    r = recs((14, "raion", "2026-10-01 10:00", "2026-10-01 10:30"), (14, "raion", "2026-10-01 10:31", "2026-10-01 10:50"))
    assert len(data.episodes(r, ASOF)) == 2


def test_ongoing_alert_is_censored_at_asof():
    r = recs((31, "oblast", "2026-10-11 11:00", None), (14, "raion", "2026-10-11 11:30", "2026-10-11 13:00"))
    assert spans(data.episodes(r, ASOF)) == [[14, T("2026-10-11 11:30"), ASOF], [31, T("2026-10-11 11:00"), ASOF]]


def test_city_and_hromada_rows_are_not_in_the_series():
    r = recs((22, "hromada", "2026-03-10 14:01", None), (22, "city", "2026-10-01 09:00", "2026-10-01 09:20"),
             (22, "raion", "2026-10-01 10:00", "2026-10-01 10:30"))
    assert spans(data.episodes(r, ASOF)) == [[22, T("2026-10-01 10:00"), T("2026-10-01 10:30")]]
