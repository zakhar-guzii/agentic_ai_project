"""The live forecast: every region at the moment T where the saved history ends."""
from pathlib import Path

import numpy as np
import pandas as pd

from alerts.baselines import Climatology, RecentLevel
from alerts.features import HOURS, AlertGrid, Features, ForecastTable


def forecast(records, T, model):
    """One row per region at T, from the records known at T only: the features, `under` (an alert in the minute before
    T) and its `level`, red if any oblast or raion record covering that minute is red. A clear region also gets the
    model's p1/p3/p6 and the registered references: clim28, counted at 00:00 Kyiv as in the benchmark, and recent7."""
    known = records[records.start < T]
    rows = Features(AlertGrid(known, T - pd.Timedelta("8D"), T)).at([T])
    on = known[known.level.isin(["oblast", "raion"]) & ~(known.end <= T - pd.Timedelta("1min"))]
    red = rows.obl.isin(on.oblast_id[on.alert_level == "red"])
    rows["level"] = pd.Series(np.where(red, "red", "yellow"), rows.index).where(rows.under == 1)
    midnight = T.tz_convert("Europe/Kyiv").normalize().tz_convert("UTC")
    past = ForecastTable(known, midnight - pd.Timedelta("28D"), T).rows
    clim = Climatology(28).predict(pd.concat([past, rows], ignore_index=True), asof=midnight).tail(len(rows))
    p = pd.concat([model.predict(rows), clim.set_axis(rows.index), RecentLevel().predict(rows)], axis=1)
    return rows.join(p.where(rows.under == 0))  # the model forecasts a new start, so only for a clear region


def log(rows, path):
    """Append the rows of a moment T to the CSV log, unless T is logged already: the forecast is deterministic, so a
    second run at the same T would only repeat it. Returns whether it appended."""
    if Path(path).exists():
        logged = pd.read_csv(path, parse_dates=["ts"])
        if logged.ts.isin(rows.ts).any():
            return False
        rows = rows[logged.columns]  # the log's column order; a column it lacks raises
    rows.to_csv(path, mode="a", header=not Path(path).exists(), index=False)
    return True


def score(log, records, asof, model):
    """The logged forecasts of clear regions with their outcomes y1/y3/y6: an episode start in [T, T + H) in the
    current records, NaN while T + H is after `asof`. Late API revisions (Decision 4): `revised` marks a row whose
    features at T, recomputed from the current records, differ from the logged ones; final_p1/p3/p6 are the forecasts
    on the recomputed features."""
    out, cols = [], ["under"] + Features.NAMES[1:]
    for T, rows in log[log.under == 0].groupby("ts"):
        grid = AlertGrid(records, T, asof)
        y = pd.DataFrame({f"y{h}": grid.start_within(grid.index([T]), 60 * h)[:, 0] for h in HOURS}, grid.oblasts)
        final = forecast(records, T, model).set_index("obl").loc[rows.obl]
        revised = ~np.isclose(rows[cols].to_numpy(float), final[cols].to_numpy(float)).all(axis=1)
        out.append(rows.join(y, on="obl").assign(revised=revised, **{f"final_p{h}": final[f"p{h}"].to_numpy()
                                                                      for h in HOURS}))
    return pd.concat(out, ignore_index=True)
