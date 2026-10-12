"""Historical load and level analytics, censored at the frozen map cutoff."""

def kyiv(t):
    return t.tz_convert("Europe/Kyiv").tz_localize(None)


def analytics(paths):
    """The history analytics up to the map cutoff, nothing from the holdout: the first full Kyiv day `lo`, the daily
    table `d`, the weekly table, `per` (per region and 'all', for the year and 28 days before and after the level
    reform), and the per-region tables around the reform (`reg`) and of the levels since the splice (`lev`)."""
    import pandas as pd
    from alert_outlook.data import history as D
    from alert_outlook.forecasting.features import OBLASTS
    h, _ = D.saved(paths)
    lo = (h.start.min().tz_convert("Europe/Kyiv").normalize() + pd.Timedelta("1D")).tz_convert("UTC")  # first full day
    d = D.daily(h[h.start < D.MAP_CUTOFF], lo, D.MAP_CUTOFF, OBLASTS)  # nothing from the holdout
    names = D.names(paths)

    def load(g):
        known = g[g.red.notna()]
        return pd.Series({"days": g.minutes.sum() / 1440 / g.obl.nunique(), "share under alert": g.alert.sum() / g.minutes.sum(),
                          "starts/region-day": g.starts.sum() / (g.minutes.sum() / 1440),
                          "red share": known.red.sum() / known.alert.sum() if len(known) else float("nan")})

    # 1. load over time
    week = d.assign(week=d.day - pd.to_timedelta(d.day.dt.dayofweek, "D")).groupby("week")[d.columns].apply(load)
    week.index = week.index.strftime("%Y-%m-%d")
    week["note"] = pd.Series({"2025-12-15": "raion-level alerting", f"{kyiv(D.REFORM):%Y-%m-%d}": "yellow/red levels"})
    # 2. per region, around the reform
    window = lambda a, b: d[(d.day >= kyiv(a)) & (d.day < kyiv(b))]
    four = pd.Timedelta("28D")
    parts = {"year": d, "before": window(D.REFORM - four, D.REFORM), "after": window(D.REFORM, D.REFORM + four)}
    per = {k: pd.concat([v.groupby("obl")[d.columns].apply(load), load(v).to_frame("all").T]) for k, v in parts.items()}
    reg = pd.DataFrame({"share, year": per["year"]["share under alert"], "share, before": per["before"]["share under alert"],
                        "share, after": per["after"]["share under alert"],
                        "starts/day, before": per["before"]["starts/region-day"],
                        "starts/day, after": per["after"]["starts/region-day"]})
    reg["share, after - before"] = reg["share, after"] - reg["share, before"]  # a ratio explodes on near-zero western bases
    reg.index = [names.get(o, o) for o in reg.index]
    reg = pd.concat([reg.drop("all").sort_index(), reg.loc[["all"]]])
    # 3. levels since the splice
    lv = d[d.red.notna()]
    lev = pd.concat([lv.groupby("obl")[["alert", "red"]].sum(), lv[["alert", "red"]].sum().to_frame("all").T])
    lev = pd.DataFrame({"alert hours": (lev.alert / 60).round().astype(int), "red hours": (lev.red / 60).round().astype(int),
                        "red share": lev.red / lev.alert})
    lev.index = [names.get(o, o) for o in lev.index]
    lev = pd.concat([lev.drop("all").sort_index(), lev.loc[["all"]]])
    return lo, d, week, per, reg, lev
