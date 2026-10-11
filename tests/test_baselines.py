import numpy as np
import pandas as pd
import pytest

from alerts.baselines import Climatology, Persistence, RecentLevel

K = lambda s: pd.Timestamp(s, tz="Europe/Kyiv").tz_convert("UTC")
VOLYN = 8


def table(*rows):
    """rows: (oblast, Kyiv time, label) -> forecast rows with that label at every horizon."""
    r = pd.DataFrame([dict(obl=o, ts=K(s), y1=y, y3=y, y6=y) for o, s, y in rows])
    local = r.ts.dt.tz_convert("Europe/Kyiv")
    return r.assign(hour=local.dt.hour + local.dt.minute / 60)


def p(rows, baseline, moment, hours=1):
    """The baseline's forecast for the Volyn row at `moment` (Kyiv time)."""
    out = baseline.predict(rows)
    return out.loc[(rows.ts == K(moment)) & (rows.obl == VOLYN), f"{baseline.name}_{hours}"].item()


# Volyn before 1 October: at 10:00 a start followed 3 times out of 4; overall 4 times out of 10 (m = 0.4).
# The 23:30 row on 30 September is not yet known at 00:00 on 1 October: its label window runs past midnight.
HISTORY = [(VOLYN, f"2026-09-{d} 10:00", y) for d, y in zip((26, 27, 28, 29), (1, 1, 1, 0))] + \
          [(VOLYN, f"2026-09-{d} 15:00", y) for d, y in zip((25, 26, 27, 28, 29, 30), (1, 0, 0, 0, 0, 0))] + \
          [(VOLYN, "2026-09-30 23:30", 1)]
OCT1 = table(*HISTORY, (VOLYN, "2026-10-01 10:00", 1), (VOLYN, "2026-10-01 12:00", 0), (VOLYN, "2026-10-01 23:00", 0))


def test_climatology_shrinks_the_cell_to_the_oblast_mean():
    assert p(OCT1, Climatology(28), "2026-10-01 10:00") == 0.5  # (3 + 10 * 0.4) / (4 + 10)


def test_a_cell_with_nothing_known_falls_back_to_the_oblast_mean():
    assert p(OCT1, Climatology(28), "2026-10-01 12:00") == 0.4  # no rows at 12:00
    for h in (1, 3, 6):  # the only 23:xx row ends its label window after midnight
        assert p(OCT1, Climatology(28), "2026-10-01 23:00", h) == 0.4


TWO_DAYS = table((VOLYN, "2026-10-01 10:00", 1), (VOLYN, "2026-10-01 15:00", 0), (VOLYN, "2026-10-02 10:00", 0))


def test_refit_every_day_at_midnight_kyiv():
    assert np.isnan(p(TWO_DAYS, Climatology(28), "2026-10-01 15:00"))  # nothing was known at 00:00 on 1 October
    assert p(TWO_DAYS, Climatology(28), "2026-10-02 10:00") == 6 / 11  # 1 October counts from 2 October on


def test_a_single_fit_at_asof_serves_only_the_rows_after_it():
    out = Climatology(28).predict(TWO_DAYS, asof=K("2026-10-02 00:00")).clim28_1
    assert out.isna().tolist()[:2] == [True, True]  # the 1 October rows are what the fit learned from
    assert out.iloc[2] == 6 / 11


def test_the_28_day_window_forgets_older_rows_and_the_full_history_does_not():
    rows = pd.concat([table((VOLYN, "2026-08-20 10:00", 1)), OCT1], ignore_index=True)  # 42 days before 1 October
    assert p(rows, Climatology(28), "2026-10-01 10:00") == 0.5
    assert p(rows, Climatology(None), "2026-10-01 10:00") == 94 / 165  # (4 + 10 * 5/11) / (5 + 10)


def test_recent_level_is_a_constant_hazard_from_the_last_7_days():
    out = RecentLevel().predict(pd.DataFrame({"starts_7d": [2, 0], "alert_min_7d": [80, 0]}))
    assert out.recent7_1[0] == pytest.approx(0.011928, abs=1e-6)  # 2 starts in 10 000 clear minutes: 1 - e^-0.012
    assert out.recent7_6[0] == pytest.approx(0.069469, abs=1e-6)  # 1 - e^-0.072
    assert out.recent7_1[1] == 0


def test_persistence_says_yes_if_a_start_came_in_the_last_h():
    out = Persistence().predict(pd.DataFrame({"min_since_start": [60, 61, 400]}))  # minutes since the last start
    assert out.persist_1.tolist() == [1, 0, 0]  # a start exactly 1 h ago is inside [T - 1 h, T)
    assert out.persist_3.tolist() == [1, 1, 0]
    assert out.persist_6.tolist() == [1, 1, 0]
