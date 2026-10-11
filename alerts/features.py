"""Forecast-time features on a per-oblast minute grid. Everything computed for a moment T reads minutes before T only."""
import numpy as np
import pandas as pd

from alerts.data import episodes, minute_grid

WEEK = 7 * 1440  # minutes
HOURS = (1, 3, 6)  # forecast horizons
NEVER = -10 ** 7  # "last minute" index when nothing happened yet

# land borders between the 23 oblasts and Kyiv City (ukrainealarm state ids), from research/probe/common.py.
# Luhansk and Crimea are not in the series. Kyiv City borders only Kyivska, so it gets the Kyivska ring as well.
_ID = {"Vinnytska": 4, "Volynska": 8, "Dnipropetrovska": 9, "Donetska": 28, "Zhytomyrska": 10, "Zakarpatska": 11,
       "Zaporizka": 12, "Ivano-Frankivska": 13, "Kyivska": 14, "Kirovohradska": 15, "Lvivska": 27, "Mykolaivska": 17,
       "Odeska": 18, "Poltavska": 19, "Rivnenska": 5, "Sumska": 20, "Ternopilska": 21, "Kharkivska": 22,
       "Khersonska": 23, "Khmelnytska": 3, "Cherkaska": 24, "Chernivetska": 26, "Chernihivska": 25, "Kyiv_City": 31}
_BORDERS = {"Vinnytska": "Zhytomyrska Kyivska Cherkaska Kirovohradska Odeska Chernivetska Khmelnytska",
            "Volynska": "Rivnenska Lvivska",
            "Dnipropetrovska": "Kharkivska Donetska Zaporizka Khersonska Mykolaivska Kirovohradska Poltavska",
            "Donetska": "Kharkivska Dnipropetrovska Zaporizka",
            "Zhytomyrska": "Rivnenska Khmelnytska Vinnytska Kyivska",
            "Zakarpatska": "Lvivska Ivano-Frankivska",
            "Zaporizka": "Dnipropetrovska Donetska Khersonska",
            "Ivano-Frankivska": "Lvivska Zakarpatska Chernivetska Ternopilska",
            "Kyivska": "Zhytomyrska Vinnytska Cherkaska Poltavska Chernihivska Kyiv_City",
            "Kirovohradska": "Vinnytska Cherkaska Poltavska Dnipropetrovska Mykolaivska Odeska",
            "Lvivska": "Volynska Rivnenska Ternopilska Ivano-Frankivska Zakarpatska",
            "Mykolaivska": "Odeska Kirovohradska Dnipropetrovska Khersonska",
            "Odeska": "Mykolaivska Kirovohradska Vinnytska",
            "Poltavska": "Kyivska Chernihivska Sumska Kharkivska Dnipropetrovska Kirovohradska Cherkaska",
            "Rivnenska": "Volynska Lvivska Ternopilska Khmelnytska Zhytomyrska",
            "Sumska": "Chernihivska Poltavska Kharkivska",
            "Ternopilska": "Lvivska Rivnenska Khmelnytska Chernivetska Ivano-Frankivska",
            "Kharkivska": "Sumska Poltavska Dnipropetrovska Donetska",
            "Khersonska": "Mykolaivska Dnipropetrovska Zaporizka",
            "Khmelnytska": "Rivnenska Zhytomyrska Vinnytska Chernivetska Ternopilska",
            "Cherkaska": "Kyivska Poltavska Kirovohradska Vinnytska",
            "Chernivetska": "Ivano-Frankivska Ternopilska Khmelnytska Vinnytska",
            "Chernihivska": "Kyivska Poltavska Sumska",
            "Kyiv_City": "Kyivska Zhytomyrska Chernihivska Poltavska Cherkaska Vinnytska"}
NEIGHBOURS = {_ID[o]: [_ID[n] for n in ns.split()] for o, ns in _BORDERS.items()}
assert all(o in NEIGHBOURS[n] or 31 in (o, n) for o in NEIGHBOURS for n in NEIGHBOURS[o]), "borders not symmetric"
OBLASTS = sorted(NEIGHBOURS)


class AlertGrid:
    """Each oblast's alert state minute by minute on [origin, end), as known from `records`.

    The state is the per-oblast union of oblast- and raion-level alerts (`data.episodes`); alerts still on at `end`
    are censored there. Minute index t stands for the forecast moment T = origin + t minutes, and every query for t
    reads minutes before t only, so nothing from T on can reach a feature.
    """

    def __init__(self, records, origin, end, oblasts=OBLASTS):
        self.origin, self.oblasts = origin, list(oblasts)
        self.n = int((end - origin) / pd.Timedelta("1min"))
        state, starts = minute_grid(episodes(records[records.start < end], end), origin, self.n, self.oblasts)
        minute = np.arange(self.n, dtype=np.int32)
        # column t of each running array describes the minutes before t, so t = 0 .. n are all valid
        before = lambda a, first: np.hstack([np.full((len(a), 1), first, a.dtype), a])
        self._alert = before(np.cumsum(state, 1, dtype=np.int32), 0)
        self._start = before(np.cumsum(starts > 0, 1, dtype=np.int32), 0)
        self._last_alert = before(np.maximum.accumulate(np.where(state, minute, NEVER), 1), NEVER)
        self._last_start = before(np.maximum.accumulate(np.where(starts > 0, minute, NEVER), 1), NEVER)

    def index(self, moments):
        """Minute index t of each moment T, floored to the minute."""
        t = np.floor((pd.DatetimeIndex(moments) - self.origin) / pd.Timedelta("1min")).to_numpy().astype(int)
        assert ((t >= 0) & (t <= self.n)).all(), "moment outside the grid"
        return t

    def alert_minutes(self, t, w):
        """Minutes under alert in [T - w, T)."""
        return self._alert[:, t] - self._alert[:, np.maximum(t - w, 0)]

    def under(self, t):
        """Under alert at any time in the minute before T."""
        return self.alert_minutes(t, 1) > 0

    def starts(self, t, w):
        """Minutes with an episode start in [T - w, T)."""
        return self._start[:, t] - self._start[:, np.maximum(t - w, 0)]

    def minutes_since_alert(self, t):
        """Minutes from the last minute under alert to T, capped at 7 days."""
        return np.minimum(t - self._last_alert[:, t], WEEK)

    def minutes_since_start(self, t):
        """Minutes from the last episode start to T, capped at 7 days."""
        return np.minimum(t - self._last_start[:, t], WEEK)

    def start_within(self, t, w):
        """The label, looking ahead on purpose: 1.0 if an episode starts in [T, T + w); NaN if T + w is past the end."""
        y = (self._start[:, np.minimum(t + w, self.n)] - self._start[:, t] > 0).astype(float)
        y[:, t + w > self.n] = np.nan
        return y


class Features:
    """Forecast-time features of all 24 oblasts at moments T, read from an AlertGrid (minutes before T only).

    Calendar: Kyiv local hour (with the half hour) and weekday. Own: recency and load. Neighbours (`nb_*`): the mean
    over the oblast's land neighbours, except `nb_min_since_start`, the minimum. Nation (`nat_*`): all 24 oblasts.
    """

    NAMES = ["obl", "hour", "dow", "min_since_alert", "min_since_start", "starts_3h", "starts_24h", "starts_7d",
             "alert_min_24h", "alert_min_7d", "nb_active", "nb_starts_1h", "nb_starts_3h", "nb_alert_min_24h",
             "nb_min_since_start", "nat_active", "nat_active_1h_ago", "nat_starts_1h", "nat_starts_3h"]

    def __init__(self, grid):
        self.grid = grid
        borders = np.array([[n in NEIGHBOURS[o] for n in grid.oblasts] for o in grid.oblasts], dtype=float)
        self._mean = borders / borders.sum(1, keepdims=True)  # row o averages over o's neighbours

    def at(self, moments):
        """One row per (oblast, T): `under` (alert in the minute before T) and the features."""
        g, t, nb = self.grid, self.grid.index(moments), self._mean
        f = dict(under=g.under(t).astype(int), min_since_alert=g.minutes_since_alert(t),
                 min_since_start=g.minutes_since_start(t), starts_3h=g.starts(t, 180), starts_24h=g.starts(t, 1440),
                 starts_7d=g.starts(t, WEEK), alert_min_24h=g.alert_minutes(t, 1440),
                 alert_min_7d=g.alert_minutes(t, WEEK))
        f.update(nb_active=nb @ f["under"], nb_starts_1h=nb @ g.starts(t, 60), nb_starts_3h=nb @ f["starts_3h"],
                 nb_alert_min_24h=nb @ f["alert_min_24h"],
                 nb_min_since_start=np.vstack([f["min_since_start"][row > 0].min(0) for row in nb]))
        nation = lambda a: np.tile(a.sum(0), (len(g.oblasts), 1))  # the same value in every oblast's row
        f.update(nat_active=nation(f["under"]), nat_active_1h_ago=nation(g.under(np.maximum(t - 60, 0))),
                 nat_starts_1h=nation(g.starts(t, 60)), nat_starts_3h=nation(f["starts_3h"]))
        moments, k = pd.DatetimeIndex(moments), len(g.oblasts)
        local = moments.tz_convert("Europe/Kyiv")
        rows = pd.DataFrame({"obl": np.repeat(g.oblasts, len(t)), "ts": np.tile(moments, k),
                             "hour": np.tile(local.hour + local.minute / 60, k), "dow": np.tile(local.dayofweek, k),
                             **{name: v.ravel() for name, v in f.items()}})  # oblast-major, like the arrays
        return rows[["obl", "ts", "under"] + self.NAMES[1:]]


class ForecastTable:
    """Rows for training and evaluation: one per (oblast, T) for moments T every `step` in [start, end) where the
    oblast is clear at T (no alert in the minute before), with the features and the labels y1, y3, y6 (an episode
    start in [T, T + H)).

    The grid starts 8 days before `start`, so the 7-day windows of the first rows are full.
    """

    def __init__(self, records, start, end, step="30min"):
        self.grid = AlertGrid(records, start - pd.Timedelta("8D"), end)
        moments = pd.date_range(start, end, freq=step, inclusive="left")
        rows, t = Features(self.grid).at(moments), self.grid.index(moments)
        for h in HOURS:
            rows[f"y{h}"] = self.grid.start_within(t, 60 * h).ravel()
        self.rows = rows[rows.under == 0].drop(columns="under").reset_index(drop=True)
