"""The live forecast: every region at the moment T where the saved history ends."""
import numpy as np
import pandas as pd

from alerts.baselines import Climatology, RecentLevel
from alerts.features import AlertGrid, Features, ForecastTable


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
