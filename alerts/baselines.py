"""Reference forecasts to beat: P(an episode starts in [T, T + H)) for each forecast row, from data before T only."""
import numpy as np
import pandas as pd

from alerts.features import HOURS, WEEK


class Baseline:
    """A reference forecast for every forecast row and horizon H in HOURS, computed only from what was known at T.

    `predict(rows)` returns one column per horizon, `<name>_<H>`, on the index of `rows`.
    """

    name = "baseline"

    def predict(self, rows):
        raise NotImplementedError


class Climatology(Baseline):
    """The share of rows followed by a start, per oblast x Kyiv hour, over the last `days` days (None: all history).

    Only rows whose label window had closed when the rates are counted (T' + H <= that moment): a later outcome was not
    known yet. Each cell is shrunk to its oblast's mean with SHRINK pseudo-rows, so a sparse or empty cell falls back
    towards the oblast. Nothing is trained: the rates are recounted every day at 00:00 Kyiv, or once at `asof`.
    """

    SHRINK = 10

    def __init__(self, days=28):
        self.days, self.name = days, f"clim{days or 'all'}"

    def rates_at(self, rows, asof, hours):
        """Cell counts per (oblast, hour) and the oblast means, from the rows known at `asof`."""
        y, known = f"y{hours}", rows[rows.ts + pd.Timedelta(hours=hours) <= asof]
        if self.days:
            known = known[known.ts >= asof - pd.Timedelta(days=self.days)]
        cells = known.groupby([known.obl, known.hour.astype(int)])[y].agg(["sum", "count"])
        return cells, known.groupby("obl")[y].mean(), known[y].mean()

    def predict(self, rows, asof=None):
        """Each row's oblast x hour rate, counted at 00:00 Kyiv of the row's day, or once at `asof` (rows before
        `asof` then get NaN: their outcomes are in those counts)."""
        midnight = rows.ts.dt.tz_convert("Europe/Kyiv").dt.normalize().dt.tz_convert("UTC")
        count_at = midnight if asof is None else pd.Series(asof, index=rows.index)
        out = pd.DataFrame(index=rows.index)
        for h in HOURS:
            p = pd.Series(np.nan, index=rows.index)
            for when, part in rows.groupby(count_at):
                cells, mean, overall = self.rates_at(rows, when, h)
                key = pd.MultiIndex.from_arrays([part.obl, part.hour.astype(int)])
                s, n = (cells[c].reindex(key).fillna(0).to_numpy() for c in ("sum", "count"))
                m = part.obl.map(mean).fillna(overall).to_numpy()
                p[part.index] = (s + self.SHRINK * m) / (n + self.SHRINK)
            out[f"{self.name}_{h}"] = p.where(rows.ts >= count_at)
        return out


class RecentLevel(Baseline):
    """A constant hazard from the last 7 days: lambda = starts / clear minutes, P = 1 - exp(-lambda * H).

    This is the two-state (clear / alert) Markov chain: it follows the level of the last week and ignores the hour.
    """

    name = "recent7"

    def predict(self, rows):
        rate = rows.starts_7d / (WEEK - rows.alert_min_7d)  # starts per clear minute
        return pd.DataFrame({f"{self.name}_{h}": 1 - np.exp(-rate * 60 * h) for h in HOURS}, index=rows.index)


class Persistence(Baseline):
    """1 if an episode started in [T - H, T), else 0: the next H hours repeat the last H. A sanity line to beat."""

    name = "persist"

    def predict(self, rows):
        return pd.DataFrame({f"{self.name}_{h}": (rows.min_since_start <= 60 * h).astype(float) for h in HOURS},
                            index=rows.index)
