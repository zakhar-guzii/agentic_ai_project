import pandas as pd

from alerts.features import AlertGrid, Features

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
