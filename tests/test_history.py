import pandas as pd

from alerts import data

T = lambda s: pd.Timestamp(s, tz="UTC")
S = data.SPLICE  # 2026-09-11 21:00 UTC


def recs(src, *rows):
    """rows: (unit_id, start, end) -> record table in the loader schema (one raion of Kyivska)."""
    return pd.DataFrame([dict(src=src, oblast_id=14, unit_id=u, unit="r", level="raion",
                              alert_level=None if src == "map" else "yellow", start=T(s), end=T(e) if e else pd.NaT,
                              rec_id=None if src == "map" else i)
                         for i, (u, s, e) in enumerate(rows)])


def test_splice_constant_is_kyiv_midnight_of_sept_12():
    assert S == T("2026-09-11 21:00")


def test_before_splice_from_map_after_from_api():
    m = recs("map", (76, "2026-09-10 10:00", "2026-09-10 10:30"), (76, "2026-09-20 10:00", "2026-09-20 10:30"))
    a = recs("api", (76, "2026-09-20 10:00:01", "2026-09-20 10:30"), (76, "2026-10-11 08:00", None))
    h = data.history(m, a)
    assert h[["src", "start"]].values.tolist() == [["map", T("2026-09-10 10:00")], ["api", T("2026-09-20 10:00:01")],
                                                   ["api", T("2026-10-11 08:00")]]


def test_alert_in_both_sources_appears_once():
    m = recs("map", (76, "2026-09-20 10:00", "2026-09-20 10:30"))
    a = recs("api", (76, "2026-09-20 10:00", "2026-09-20 10:30"))
    assert len(data.history(m, a)) == 1


def test_map_alert_running_across_splice_is_kept_whole():
    m = recs("map", (76, "2026-09-11 20:30", "2026-09-11 22:15"))
    a = recs("api", (76, "2026-09-11 20:30:01", "2026-09-11 22:15"))  # same alert, started before the window cut
    h = data.history(m, a)
    assert h[["src", "start", "end"]].values.tolist() == [["map", T("2026-09-11 20:30"), T("2026-09-11 22:15")]]


def test_boundary_starts_each_kept_exactly_once():
    rows = [(76, "2026-09-11 20:59:59", "2026-09-11 21:10"), (77, "2026-09-11 21:00:00", "2026-09-11 21:10"),
            (78, "2026-09-11 21:00:01", "2026-09-11 21:10")]
    h = data.history(recs("map", *rows), recs("api", *rows))
    assert h[["unit_id", "src"]].values.tolist() == [[76, "map"], [77, "api"], [78, "api"]]


def test_record_count_is_conserved():
    m = recs("map", (76, "2026-09-01 10:00", "2026-09-01 11:00"), (76, "2026-09-05 10:00", "2026-09-05 11:00"),
             (76, "2026-09-20 10:00", "2026-09-20 11:00"))
    a = recs("api", (76, "2026-09-11 13:00", "2026-09-11 14:00"), (76, "2026-09-20 10:00", "2026-09-20 11:00"),
             (77, "2026-09-25 10:00", "2026-09-25 11:00"), (76, "2026-10-11 09:00", None))
    assert len(data.history(m, a)) == 2 + 3  # 2 map rows before S + 3 api rows from S


def test_alert_present_in_only_one_source_is_reported_not_silently_lost():
    lo, hi = T("2026-09-12 00:00"), T("2026-10-10 19:00")
    m = recs("map", (76, "2026-09-20 10:00", "2026-09-20 10:30"), (77, "2026-09-21 10:00", "2026-09-21 10:30"))
    a = recs("api", (76, "2026-09-20 10:00:20", "2026-09-20 10:30"), (78, "2026-09-22 10:00", "2026-09-22 10:30"))
    u = data.unmatched(m, a, lo, hi)
    assert u[["src", "unit_id", "start"]].values.tolist() == [["map", 77, T("2026-09-21 10:00")],
                                                               ["api", 78, T("2026-09-22 10:00")]]
