"""Acceptance checks (plan §6) on the real snapshot and the saved alerts.in.ua pulls. Not TDD: the bar was set
before the data was checked. Skipped where the API pull is missing (e.g. a fresh clone before `fetch`)."""
import gzip
import json
import os
from pathlib import Path

import pandas as pd
import pytest

from alerts import data as D

ROOT = Path(__file__).resolve().parent.parent
PULLS = sorted(D.API_DIR.glob("*/MANIFEST.json"))
need_api = pytest.mark.skipif(not PULLS, reason="no alerts.in.ua pull saved yet (python main.py fetch)")
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
    # oblasts (Zakarpattia: 65 alert-minutes -> 0.956 on minutes, 0.990 exact); see PROCESS_LOG
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
    """research/feasibility.md section 3: the probe's test window, its 21 oblasts, its numbers. The bar was set before
    the run; the data differ slightly (alerts.in.ua after the splice, AIR only, regions.json levels)."""
    from alerts.baselines import Climatology, Persistence
    from alerts.features import ForecastTable
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
    from alerts.features import OBLASTS
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
def test_the_outlook_page_is_self_contained_and_draws_no_week_after_the_map_cutoff():
    """Step 6: the page loads nothing from outside, shows every region at the newest logged moment, and its history
    stops at the map cutoff (everything after it is the holdout)."""
    import re
    import main
    from alerts.features import OBLASTS
    page = main.outlook()
    assert not re.search(r"<script|src=|<link|@import|url\(", page)
    names = {int(x["regionId"]): x["regionName"] for x in json.loads(D.REGIONS.read_text())["states"]}
    assert all(names[o] in page for o in OBLASTS)
    T = pd.read_csv(main.LOG, parse_dates=["ts"]).ts.max()
    assert f"{T.tz_convert('Europe/Kyiv'):%Y-%m-%d %H:%M} Kyiv" in page
    weeks = re.findall(r"<title>Week of (\d{4}-\d{2}-\d{2})", page)
    assert (weeks[0], weeks[-1], len(weeks)) == ("2025-09-29", "2026-10-05", 54)  # the cutoff, 10-10, is in the last
    # ... and so is T, 10-11: the last week must end at the cutoff, Monday 00:00 Kyiv + 5 d 22:03 = 5.919 days
    days = float(re.search(r"<th>2026-10-05</th>\s*<td>([\d.]+)</td>", page).group(1))
    assert days == round((D.MAP_CUTOFF - pd.Timestamp("2026-10-05", tz="Europe/Kyiv")) / pd.Timedelta("1D"), 3)
    if (ROOT / "results/v2/summary.json").exists():  # v2 (Decision 12): a button per model, each panel with every region
        assert page.count('type="radio"') == 4 and all(page.count(names[o]) >= 8 for o in OBLASTS)


@pytest.mark.skipif(not (D.API_DIR / "20261011T1247Z").exists(), reason="the frozen step-3 pull is missing")
def test_the_holdout_path_rebuilds_the_benchmark_references(m):
    """Step 7: `live.holdout` builds rows and references as the benchmark did. On the last benchmark week, from the
    frozen pull, its clim28 and recent7 equal the frozen benchmark CSV's. Nothing after the map cutoff is read."""
    import main
    from alerts import live
    from alerts.features import HOURS
    from alerts.model import Forecaster
    records = D.history(m, main._frozen_api(D.API_DIR / "20261011T1247Z"))
    lo = D.MAP_CUTOFF - pd.Timedelta("7D")
    rows = live.holdout(records[records.start < D.MAP_CUTOFF], lo, D.MAP_CUTOFF, Forecaster.load(main.MODEL))
    b = pd.read_csv(ROOT / "results/benchmark_forecasts.csv.gz", parse_dates=["ts"])
    for h in HOURS:
        want = b[(b.hours == h) & b.scored & (b.ts >= lo)]
        got = rows[rows[f"y{h}"].notna()].merge(want, on=["obl", "ts"], suffixes=("", "_b"))
        assert len(got) == len(want) == rows[f"y{h}"].notna().sum() > 3000
        assert (got[f"y{h}"] == got.y).all()
        for ref in ("clim28", "recent7"):
            assert got[f"{ref}_{h}"].to_numpy() == pytest.approx(got[ref].to_numpy(), abs=1e-12)


@pytest.mark.skipif(not (ROOT / "results/holdout_summary.json").exists(), reason="the step-7 holdout run is missing")
def test_the_registered_model_still_forecasts_its_frozen_holdout(m, a):
    """v2 changes the model classes. The pickled v1 runs on the current class code, so it must still give exactly the
    forecasts step 7 froze, on the same rows (the window end is the registered one)."""
    import main
    from alerts import live
    from alerts.features import HOURS
    from alerts.model import Forecaster
    end = pd.Timestamp(json.loads((ROOT / "results/holdout_summary.json").read_text())["end"])
    rows = live.holdout(D.history(m, a), D.MAP_CUTOFF, end, Forecaster.load(main.MODEL))
    frozen = pd.read_csv(ROOT / "results/holdout_forecasts.csv.gz", parse_dates=["ts"])
    for h in HOURS:
        want = frozen[frozen.hours == h]
        got = rows.merge(want, on=["obl", "ts"])
        assert len(got) == len(want) > 900
        assert got[f"p{h}"].to_numpy() == pytest.approx(got.model.to_numpy(), abs=1e-12)
