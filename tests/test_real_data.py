"""Acceptance checks (plan §6) on the real snapshot and the saved alerts.in.ua pulls. Not TDD: the bar was set
before the data was checked. Skipped where the API pull is missing (e.g. a fresh clone before `fetch`)."""
import gzip
import json
import os
from pathlib import Path

import pandas as pd
import pytest

from alert_outlook.data import history as D

ROOT = Path(__file__).resolve().parent.parent
PULLS = sorted(D.API_DIR.glob("*/MANIFEST.json"))
need_api = pytest.mark.skipif(not PULLS, reason="no alerts.in.ua pull saved yet (alert-outlook fetch)")
CORE = ["oblast", "raion"]


@pytest.fixture(scope="module")
def m():
    return D.load_map()


@pytest.fixture(scope="module")
def a():
    return D.load_api()


def test_map_snapshot_is_clean(m):
    assert m.level.notna().all()  # every unit found in the regions.json tree
    assert not m.duplicated(["unit_id", "start"]).any()
    neg = m[m.end < m.start]
    assert len(neg) == 2 and ((neg.start - neg.end).dt.total_seconds() < 10).all()  # zero-length blips only
    assert m.oblast_id.nunique() == 24


@need_api
def test_api_pulls_complete_and_token_free():
    tok = os.environ.get("ALERTS_IN_UA_TOKEN") or next(
        (l.split("=", 1)[1].strip().strip("\"'") for l in (ROOT / ".env").read_text().splitlines()
         if l.startswith("ALERTS_IN_UA_TOKEN=")), None) if (ROOT / ".env").exists() else None
    for man in PULLS:
        files = json.loads(man.read_text())["files"]
        assert len(files) == 24 and all(f["status"] == 200 for f in files)
        if tok:
            assert tok not in man.read_text()
            assert not any(tok.encode() in gzip.decompress((man.parent / f["file"]).read_bytes()) for f in files)


@need_api
def test_seam_meets_the_bar(m, a):
    s = D.compare(m[m.level.isin(CORE)], a[a.level.isin(CORE)], D.SPLICE, D.MAP_CUTOFF)
    assert s.loc["all", "jaccard"] >= 0.99
    assert s.loc["all", "a_in_b"] >= 0.98 and s.loc["all", "b_in_a"] >= 0.98
    # per oblast on exact seconds: the minute grid adds up to 1 min per episode edge, which dominates quiet
    # oblasts (Zakarpattia: 65 alert-minutes -> 0.956 on minutes, 0.990 exact); original snapshot acceptance value
    assert (s.drop("all").jaccard_s >= 0.97).all(), s.jaccard_s[s.jaccard_s < 0.97].to_dict()


@need_api
def test_splice_keeps_every_alert(m, a):
    h = D.history(m, a)
    assert len(h) == (m.start < D.SPLICE).sum() + (a.start >= D.SPLICE).sum()
    mr, ar = m[m.level == "raion"], a[a.level == "raion"]
    u = D.unmatched(mr, ar, D.SPLICE, D.MAP_CUTOFF)
    in_win = lambda r: r.start.between(D.SPLICE, D.MAP_CUTOFF, inclusive="left").sum()
    assert (u.src == "map").sum() <= 0.01 * in_win(mr) and (u.src == "api").sum() <= 0.01 * in_win(ar)
    hc, mc = h[h.level.isin(CORE)], m[m.level.isin(CORE)]
    w = D.compare(hc, mc, D.SPLICE - pd.Timedelta("12h"), D.SPLICE + pd.Timedelta("12h"))
    assert (w.jaccard >= 0.99).all(), w.jaccard[w.jaccard < 0.99].to_dict()
    assert hc[hc.start < D.SPLICE].oblast_id.nunique() == hc[hc.start >= D.SPLICE].oblast_id.nunique() == 24
    assert (hc.set_index("start").resample("6h").size() > 0).all()


@need_api
def test_labels_and_baselines_reproduce_the_feasibility_probe(m, a):
    """Historical feasibility acceptance values: the probe's test window, its 21 oblasts, its numbers. The bar was set before
    the run; the data differ slightly (alerts.in.ua after the splice, AIR only, regions.json levels)."""
    from alert_outlook.forecasting.baselines import Climatology, Persistence
    from alert_outlook.forecasting.features import ForecastTable
    start, last = pd.Timestamp("2026-09-12 21:00", tz="UTC"), pd.Timestamp("2026-10-10 13:00", tz="UTC")
    rows = ForecastTable(D.history(m, a), pd.Timestamp("2026-08-01", tz="UTC"), D.MAP_CUTOFF).rows
    rows = rows[~rows.obl.isin([9, 22, 28])]  # the probe's train-only exclusion: >= 80% of the time under alert
    clim = Climatology(28).predict(rows, asof=start)
    pers = Persistence().predict(rows)
    w = (rows.ts >= start) & (rows.ts <= last)
    assert abs(w.sum() - 18214) <= 0.01 * 18214
    brier = lambda p, y: float(((p[w] - rows.loc[w, y]) ** 2).mean())
    for h, base, b_pers, b_clim in [(1, 0.234, 0.237, 0.144), (3, 0.414, 0.270, 0.165), (6, 0.531, 0.249, 0.160)]:
        assert abs(rows.loc[w, f"y{h}"].mean() - base) <= 0.005
        assert abs(brier(pers[f"persist_{h}"], f"y{h}") - b_pers) <= 0.005
        assert abs(brier(clim[f"clim28_{h}"], f"y{h}") - b_clim) <= 0.003


@need_api
def test_daily_history_adds_up(m, a):
    """Step 5: the per-day table neither loses nor invents alert time or starts, up to the map cutoff."""
    from alert_outlook.forecasting.features import OBLASTS
    h = D.history(m, a)
    h = h[h.start < D.MAP_CUTOFF]
    lo = pd.Timestamp("2025-10-04", tz="Europe/Kyiv").tz_convert("UTC")
    d = D.daily(h, lo, D.MAP_CUTOFF, OBLASTS)
    ep = D.episodes(h, D.MAP_CUTOFF)
    assert (d.groupby("obl").starts.sum() == ep[ep.start >= lo].groupby("oblast_id").size().reindex(OBLASTS, fill_value=0)).all()
    assert (d.groupby("obl").minutes.sum() == (D.MAP_CUTOFF - lo) // pd.Timedelta("1min")).all()
    assert (d.alert <= d.minutes).all() and (d.red.isna() | (d.red <= d.alert)).all()
    assert d.red.isna().eq(d.day < pd.Timestamp("2026-09-12")).all()  # levels exist from the splice only
    # alert time from the splice on = the minutes `compare` counts on the same window (another code path, data report)
    hc = h[h.level.isin(CORE)]
    assert d[d.day >= pd.Timestamp("2026-09-12")].alert.sum() == D.compare(hc, hc, D.SPLICE, D.MAP_CUTOFF).loc["all", "minutes_a"]




@need_api
def test_the_outlook_has_three_models_and_history_stops_at_map_cutoff():
    import re
    from alert_outlook.forecasting import live
    from alert_outlook.forecasting.model import Forecaster
    from alert_outlook.presentation.history import analytics
    from alert_outlook.presentation.page import render
    from alert_outlook.settings import Paths, FAMILIES, OBLAST_UIDS
    from alert_outlook.experiments.tracking import digest
    paths = Paths()
    records, T = D.saved(paths)
    rows = pd.concat([live.forecast(records,T,Forecaster.load(paths.models/f'{f}.joblib')).assign(
        model=f, made_at=T+pd.Timedelta('1D'), model_sha256=digest(paths.models/f'{f}.joblib'))
        for f in FAMILIES], ignore_index=True)
    page = render(rows, D.names(paths), analytics(paths))
    assert not re.search(r'<script|src=|<link|@import|url\(',page)
    assert page.count('type="radio"') == 3
    assert all(page.count(D.names(paths)[o]) >= 6 for o in OBLAST_UIDS)
    assert f'{T.tz_convert("Europe/Kyiv"):%Y-%m-%d %H:%M} Kyiv' in page
    weeks = re.findall(r'<title>Week of (\d{4}-\d{2}-\d{2})', page)
    assert (weeks[0],weeks[-1],len(weeks)) == ('2025-09-29','2026-10-05',54)
    days = float(re.search(r'<th>2026-10-05</th>\s*<td>([\d.]+)</td>',page).group(1))
    assert days == round((D.MAP_CUTOFF-pd.Timestamp('2026-10-05',tz='Europe/Kyiv'))/pd.Timedelta('1D'),3)
