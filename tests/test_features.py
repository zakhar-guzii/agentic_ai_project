import numpy as np
import pandas as pd

from alerts.features import AlertGrid, Features, ForecastTable

T = lambda s: pd.Timestamp(s, tz="UTC")
VOLYN, RIVNE, LVIV = 8, 5, 27  # Volyn borders Rivne and Lviv only


def recs(*rows):
    """rows: (oblast_id, start, end) -> raion-level AIR records; end None = still on."""
    r = pd.DataFrame([dict(oblast_id=o, level="raion", start=T(s), end=e) for o, s, e in rows])
    return r.assign(end=pd.to_datetime(r.end, utc=True))


def at(records, moment, oblast):
    """Features of one oblast at one moment, on a grid that covers the whole day."""
    f = Features(AlertGrid(records, T("2026-10-01 00:00"), T("2026-10-02 00:00"))).at([T(moment)])
    return f[f.obl == oblast].iloc[0]


# Volyn under alert 09:00-09:30, its neighbour Rivne 10:00-10:20
WORLD = recs((VOLYN, "2026-10-01 09:00", "2026-10-01 09:30"), (RIVNE, "2026-10-01 10:00", "2026-10-01 10:20"))


def test_own_recency_and_load_count_minutes_before_t():
    f = at(WORLD, "2026-10-01 10:30", VOLYN)
    assert (f.under, f.min_since_alert, f.min_since_start, f.starts_3h, f.alert_min_24h) == (0, 61, 90, 1, 30)


def test_neighbour_features_average_over_land_neighbours():
    f = at(WORLD, "2026-10-01 10:30", VOLYN)  # Rivne started 30 min ago, Lviv never did
    assert (f.nb_starts_1h, f.nb_starts_3h, f.nb_alert_min_24h, f.nb_min_since_start) == (0.5, 0.5, 10, 30)
    assert at(WORLD, "2026-10-01 10:10", VOLYN).nb_active == 0.5  # Rivne is under alert, Lviv is not


def test_national_wave_counts_every_oblast():
    f = at(WORLD, "2026-10-01 10:30", LVIV)  # the same for every oblast, even one with no alerts of its own
    assert (f.nat_active, f.nat_starts_1h, f.nat_starts_3h) == (0, 1, 2)
    assert f.nat_active_1h_ago == 1  # Volyn was under alert in the minute before 09:30
    assert at(WORLD, "2026-10-01 10:10", LVIV).nat_active == 1


def test_a_start_exactly_at_t_is_not_seen_at_t():
    late = pd.concat([WORLD, recs((LVIV, "2026-10-01 10:30", None))], ignore_index=True)
    for oblast in (LVIV, VOLYN):  # Lviv itself and its neighbour
        assert at(late, "2026-10-01 10:30", oblast).equals(at(WORLD, "2026-10-01 10:30", oblast))
    assert at(late, "2026-10-01 10:31", LVIV).under == 1


def row(table, moment, oblast):
    r = table.rows
    return r[(r.ts == T(moment)) & (r.obl == oblast)].iloc[0]


# Lviv under alert 10:30-10:50, Volyn 11:30-12:00; rows every 30 min from 10:00 to 18:00
DAY = recs((LVIV, "2026-10-01 10:30", "2026-10-01 10:50"), (VOLYN, "2026-10-01 11:30", "2026-10-01 12:00"))


def test_label_is_a_start_in_t_to_t_plus_h():
    tab = ForecastTable(DAY, T("2026-10-01 10:00"), T("2026-10-01 18:00"))
    assert row(tab, "2026-10-01 10:30", LVIV).y1 == 1  # a start exactly at T counts
    volyn = row(tab, "2026-10-01 10:30", VOLYN)
    assert (volyn.y1, volyn.y3) == (0, 1)  # a start exactly at T + 1 h does not


def test_label_past_the_end_of_the_data_is_unknown():
    tab = ForecastTable(DAY, T("2026-10-01 10:00"), T("2026-10-01 18:00"))
    assert row(tab, "2026-10-01 15:00", LVIV).y3 == 0  # [15:00, 18:00) ends exactly at the data end
    late = row(tab, "2026-10-01 15:30", LVIV)
    assert late.y1 == 0 and np.isnan(late.y3) and np.isnan(late.y6)  # 15:30 + 3 h is past 18:00


def test_no_row_for_an_oblast_under_alert_at_t():
    rows = ForecastTable(DAY, T("2026-10-01 10:00"), T("2026-10-01 18:00")).rows
    at_noon = set(rows[rows.ts == T("2026-10-01 12:00")].obl)
    assert VOLYN not in at_noon and LVIV in at_noon  # Volyn is under alert until 12:00


def test_two_starts_in_one_minute_count_twice():
    # a 15-second blip in Volyn and a new alert 20 s later, in the same minute: people hear two sirens
    blip = recs((VOLYN, "2026-10-01 09:00:05", "2026-10-01 09:00:20"),
                (VOLYN, "2026-10-01 09:00:40", "2026-10-01 09:10:00"))
    f = at(blip, "2026-10-01 10:30", VOLYN)
    assert (f.starts_3h, f.starts_24h, f.nat_starts_3h) == (2, 2, 2)
    tab = ForecastTable(blip, T("2026-10-01 08:00"), T("2026-10-01 12:00"))
    assert row(tab, "2026-10-01 08:30", VOLYN).y1 == 1  # the label only says whether a start came


def test_rows_are_in_time_order_with_the_oblasts_of_a_moment_together():
    rows = ForecastTable(DAY, T("2026-10-01 10:00"), T("2026-10-01 18:00")).rows
    assert rows.ts.is_monotonic_increasing
    assert rows.obl[rows.ts == T("2026-10-01 10:00")].is_monotonic_increasing  # a fixed order inside a moment


def test_hour_and_weekday_are_kyiv_local_across_the_dst_switch():
    quiet = recs((VOLYN, "2026-03-27 09:00", "2026-03-27 09:30"))
    rows = ForecastTable(quiet, T("2026-03-29 00:00"), T("2026-03-29 02:00")).rows
    lviv = rows[rows.obl == LVIV].set_index("ts")
    assert lviv.loc[T("2026-03-29 00:30"), "hour"] == 2.5  # 02:30 EET
    assert lviv.loc[T("2026-03-29 01:00"), "hour"] == 4.0  # 04:00 EEST: the clocks jumped an hour
    assert (lviv.dow == 6).all()  # Sunday
