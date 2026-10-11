import pandas as pd
import pytest

from alerts import data

T = lambda s: pd.Timestamp(s, tz="UTC")
LO, HI = T("2026-10-01 00:00"), T("2026-10-02 00:00")


def recs(*rows):
    """rows: (oblast_id, start, end) -> raion-level record table."""
    return pd.DataFrame([dict(src="x", oblast_id=o, unit_id=i, unit="u", level="raion", alert_level=None, start=T(s),
                              end=T(e), rec_id=i) for i, (o, s, e) in enumerate(rows)])


def test_identical_sources_agree_perfectly():
    r = recs((14, "2026-10-01 10:00", "2026-10-01 10:30"), (31, "2026-10-01 12:00", "2026-10-01 13:00"))
    s = data.compare(r, r, LO, HI).loc["all"]
    assert s.jaccard == 1.0 and s.jaccard_s == 1.0 and s.minutes_a == 90 and s.starts_a == 2
    assert s.a_in_b == 1.0 and s.b_in_a == 1.0


def test_five_minute_shift_breaks_start_match_and_lowers_jaccard():
    a = recs((14, "2026-10-01 10:00", "2026-10-01 10:30"))
    b = recs((14, "2026-10-01 10:05", "2026-10-01 10:35"))
    s = data.compare(a, b, LO, HI).loc[14]
    assert s.jaccard == pytest.approx(25 / 35) and s.a_in_b == 0 and s.b_in_a == 0


def test_one_minute_shift_still_counts_as_matched_start():
    a = recs((14, "2026-10-01 10:00", "2026-10-01 10:30"))
    b = recs((14, "2026-10-01 10:01:30", "2026-10-01 10:30"))
    assert data.compare(a, b, LO, HI).loc[14, "a_in_b"] == 1.0


def test_exact_jaccard_in_seconds_ignores_minute_rounding():
    a = recs((14, "2026-10-01 10:00:00", "2026-10-01 10:00:50"))
    b = recs((14, "2026-10-01 10:00:10", "2026-10-01 10:01:00"))
    s = data.compare(a, b, LO, HI).loc[14]
    assert s.jaccard == 1.0  # the minute grid sees the same single minute
    assert s.jaccard_s == pytest.approx(40 / 60)  # exact: 40 s shared out of 60 s


def test_daily_alert_minutes_agree_by_kyiv_day():
    lo, hi = T("2026-09-30 21:00"), T("2026-10-02 21:00")  # Oct 1 and Oct 2, Kyiv time (UTC+3)
    a = recs((14, "2026-10-01 05:00", "2026-10-01 06:00"), (31, "2026-10-01 07:00", "2026-10-01 07:30"),
             (31, "2026-10-01 22:00", "2026-10-01 23:30"))  # 22:00 UTC = Oct 2 01:00 Kyiv
    b = recs((14, "2026-10-01 05:00", "2026-10-01 05:50"), (31, "2026-10-01 07:00", "2026-10-01 07:30"),
             (31, "2026-10-01 22:00", "2026-10-01 23:30"))
    corr, mae = data.daily_agreement(a, b, lo, hi)
    assert mae == pytest.approx(10 / 4)  # cells (14,d1) 60 vs 50; (14,d2) 0/0; (31,d1) 30/30; (31,d2) 90/90
    assert data.daily_agreement(a, a, lo, hi) == (pytest.approx(1.0), 0.0)
