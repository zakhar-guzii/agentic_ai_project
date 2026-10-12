"""The live forecast: every region at the moment T where the saved history ends."""
from pathlib import Path

import numpy as np
import pandas as pd

from alerts.baselines import Climatology, RecentLevel
from alerts.features import HOURS, AlertGrid, Features, ForecastTable


def forecast(records, T, model):
    """One row per region at T, from the records known at T only: the features, `under` (an alert in the minute before
    T) and its `level`, red if any oblast or raion record covering that minute is red. Red is read by the same rule
    as `under`, so a record of zero or negative length covers nothing. A clear region also gets the model's p1/p3/p6
    and the registered references: clim28, counted at 00:00 Kyiv as in the benchmark, and recent7."""
    known = records[records.start < T]
    rows = Features(AlertGrid(known, T - pd.Timedelta("8D"), T)).at([T])
    red = AlertGrid(known[known.alert_level == "red"], T - pd.Timedelta("1min"), T).under(1)  # same rule as `under`
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
    on the recomputed features. Empty, with the same columns, when no logged region was clear."""
    out, cols = [], ["under"] + Features.NAMES[1:]
    for T, rows in log[log.under == 0].groupby("ts"):
        grid = AlertGrid(records, T, asof)
        y = pd.DataFrame({f"y{h}": grid.start_within(grid.index([T]), 60 * h)[:, 0] for h in HOURS}, grid.oblasts)
        final = forecast(records, T, model).set_index("obl").loc[rows.obl]
        revised = ~np.isclose(rows[cols].to_numpy(float), final[cols].to_numpy(float)).all(axis=1)
        out.append(rows.join(y, on="obl").assign(revised=revised, **{f"final_p{h}": final[f"p{h}"].to_numpy()
                                                                      for h in HOURS}))
    new = [f"y{h}" for h in HOURS] + ["revised"] + [f"final_p{h}" for h in HOURS]
    return pd.concat(out, ignore_index=True) if out else log.iloc[:0].reindex(columns=[*log.columns, *new])


def summary(scored):
    """Per horizon whose windows have closed: n, and the Brier score of the model, clim28 and recent7 on all those
    rows, as logged. The revision check compares the logged and the recomputed forecasts on the same rows: those
    still clear at T in the current records (`still_clear`); a region revised into an alert at T has no recomputed
    forecast."""
    out = []
    for h in HOURS:
        part = scored[scored[f"y{h}"].notna()]
        same = part[part[f"final_p{h}"].notna()]
        brier = lambda col, rows=part: float(((rows[col] - rows[f"y{h}"]) ** 2).mean())
        if len(part):
            out.append(dict(hours=h, n=len(part), moments=part.ts.nunique(),
                            made_before_window_closed=int((part.made_at < part.ts + pd.Timedelta(hours=h)).sum()),
                            base_rate=float(part[f"y{h}"].mean()), model=brier(f"p{h}"), clim28=brier(f"clim28_{h}"),
                            recent7=brier(f"recent7_{h}"), revised_rows=int(part.revised.sum()), still_clear=len(same),
                            model_logged=brier(f"p{h}", same), model_recomputed=brier(f"final_p{h}", same)))
    return pd.DataFrame(out).set_index("hours") if out else pd.DataFrame()
