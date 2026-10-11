"""Alert history: raw map snapshot + alerts.in.ua pulls -> one record table -> per-oblast episodes."""
import glob
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MAP_DIR = ROOT / "data/raw/map"
REGIONS = ROOT / "data/raw/regions.json"


# alerts that start before SPLICE come from the map snapshot, the rest from alerts.in.ua (2026-09-12 00:00 Kyiv)
SPLICE = pd.Timestamp("2026-09-11 21:00", tz="UTC")
MAP_CUTOFF = pd.Timestamp("2026-10-10 19:03", tz="UTC")  # earliest fetch time of the snapshot's last chunks
CITY_QUERIES = {1293: 22, 564: 12}  # Kharkiv and Zaporizhzhia cities are separate "State" entries -> their oblast
LEVEL = {"State": "oblast", "District": "raion", "Community": "hromada"}


def unit_types(regions_path=REGIONS):
    """regions.json tree -> {unit id: regionType}."""
    typ = {}

    def walk(n):
        typ[int(n["regionId"])] = n["regionType"]
        for c in n.get("regionChildIds") or []:
            walk(c)

    for s in json.load(open(regions_path, encoding="utf-8"))["states"]:
        walk(s)
    return typ


def _ts(s):
    return pd.to_datetime(s, utc=True, format="ISO8601")


def load_map(map_dir=MAP_DIR, regions_path=REGIONS):
    """Map snapshot -> records. AIR alerts only."""
    rows = []
    for f in glob.glob(f"{map_dir}/r*.json"):
        q = int(re.match(r"r(\d+)_", Path(f).name).group(1))
        rows += [dict(q=q, **x) for x in json.load(open(f, encoding="utf-8"))]
    m = pd.DataFrame(rows)
    air = m[m.alertType == "AIR"]
    # chunk-boundary days and ongoing alerts appear in several chunk files; the copies are identical
    m = air.drop_duplicates(["regionId", "startDate"])
    cleaning = {"raw rows": len(rows), "not AIR": len(rows) - len(air), "duplicates": len(air) - len(m)}
    uid = m.regionId.astype(int)
    level = uid.map(unit_types(regions_path)).map(LEVEL).where(~m.q.isin(list(CITY_QUERIES)), "city")
    out = pd.DataFrame({"src": "map", "oblast_id": m.q.replace(CITY_QUERIES), "unit_id": uid, "unit": m.regionName,
                         "level": level,
                         "start": _ts(m.startDate),
                         # ongoing alerts carry the sentinel 0001-01-01T00:00:00: end unknown
                         "end": _ts(m.endDate.where(~m.isContinue.astype(bool)))}).reset_index(drop=True)
    out.attrs["cleaning"] = cleaning
    return out


API_DIR = ROOT / "data/raw/alerts_in_ua"


def load_api(api_dir=API_DIR, regions_path=REGIONS):
    """All saved alerts.in.ua pulls -> records. A record seen in several pulls keeps its newest version
    (ends and levels are filled in after the fact); records that rolled out of a newer window are kept."""
    import gzip
    rows = []
    for man in glob.glob(f"{api_dir}/*/MANIFEST.json"):
        for f in json.load(open(man))["files"]:
            body = json.loads(gzip.decompress((Path(man).parent / f["file"]).read_bytes()))
            rows += [dict(a, fetched=f["fetched_utc"]) for a in body["alerts"]]
    a = pd.DataFrame(rows)
    a["fetched"] = _ts(a.fetched)
    a = a.sort_values("fetched").drop_duplicates("id", keep="last")
    n_unique = len(a)
    a = a[a.alert_type == "air_raid"]
    cleaning = {"raw rows": len(rows), "duplicates": len(rows) - n_unique, "not air_raid": n_unique - len(a)}
    # location_oblast_uid holds a raion/hromada id, not the oblast: map the oblast by name
    states = {s["regionName"]: int(s["regionId"]) for s in json.load(open(regions_path, encoding="utf-8"))["states"]
              if int(s["regionId"]) not in CITY_QUERIES}
    oblast = a.location_oblast.map(states)
    assert oblast.notna().all(), f"unknown oblast names: {sorted(a.location_oblast[oblast.isna()].unique())}"
    out = pd.DataFrame({"src": "api", "rec_id": a.id, "oblast_id": oblast.astype(int),
                         "unit_id": a.location_uid.astype(int), "unit": a.location_title, "level": a.location_type,
                         "alert_level": a.alert_level,
                         "start": _ts(a.started_at), "end": _ts(a.finished_at), "fetched": a.fetched}).reset_index(drop=True)
    out.attrs["cleaning"] = cleaning
    return out


def history(map_recs, api_recs):
    """One record per alert: the map before SPLICE, alerts.in.ua from SPLICE on."""
    h = pd.concat([map_recs[map_recs.start < SPLICE], api_recs[api_recs.start >= SPLICE]], ignore_index=True)
    return h.sort_values(["start", "unit_id"], ignore_index=True)


def unmatched(map_recs, api_recs, lo, hi, tol="60s"):
    """Records starting in [lo, hi) with no counterpart for the same unit in the other source: no start within
    `tol`, and no record covering them (the map keeps overlapping records for one raion, alerts.in.ua one)."""
    tol = pd.Timedelta(tol)

    def missing(a, b):
        a = a[(a.start >= lo) & (a.start < hi)].sort_values("start")
        bb = b[["unit_id", "start"]].sort_values("start").assign(hit=True)
        hit = pd.merge_asof(a, bb, on="start", by="unit_id", tolerance=tol, direction="nearest").hit.notna().to_numpy()
        a_end, b_end = a.end.fillna(hi), b.end.fillna(hi)
        for i, r in enumerate(a.itertuples()):
            if not hit[i]:
                hit[i] = ((b.unit_id == r.unit_id) & (b.start <= r.start + tol) & (b_end >= a_end.iloc[i] - tol)).any()
        return a[~hit]
    return pd.concat([missing(map_recs, api_recs), missing(api_recs, map_recs)], ignore_index=True)


def episodes(records, asof, levels=("oblast", "raion")):
    """Per-oblast series: merged [start, end) intervals when some raion (or the whole oblast) is under an AIR alert.
    An episode start is a clear -> alert transition. Ongoing alerts are censored at `asof`."""
    import numpy as np
    r = records[records.level.isin(levels)]
    r = r.assign(end=r.end.fillna(asof).clip(upper=asof))
    r = r[r.end > r.start].sort_values(["oblast_id", "start"])  # also drops zero-length blips
    out = []
    for oid, g in r.groupby("oblast_id"):
        s, e = g.start.to_numpy(), g.end.to_numpy()
        new = np.r_[True, s[1:] > np.maximum.accumulate(e)[:-1]]
        out.append(pd.DataFrame({"oblast_id": oid, "start": pd.to_datetime(s[new], utc=True),
                                 "end": pd.to_datetime(pd.Series(e).groupby(np.cumsum(new)).max().to_numpy(), utc=True)}))
    return pd.concat(out, ignore_index=True)


def minute_grid(ep, origin, n_min, oblasts):
    """state[o, m]: oblast under alert at any time in minute m; starts[o, m]: episode starts in minute m."""
    import numpy as np
    pos = {o: i for i, o in enumerate(oblasts)}
    state = np.zeros((len(oblasts), n_min), dtype=bool)
    starts = np.zeros((len(oblasts), n_min), dtype=np.int16)
    ep = ep[ep.oblast_id.isin(pos)]
    a = np.floor((ep.start - origin).dt.total_seconds().to_numpy() / 60).astype(int)
    b = np.ceil((ep.end - origin).dt.total_seconds().to_numpy() / 60).astype(int)
    for o, i, j in zip(ep.oblast_id.map(pos), a, b):
        if min(j, n_min) > max(i, 0):
            state[o, max(i, 0):min(j, n_min)] = True
        if 0 <= i < n_min:
            starts[o, i] += 1
    return state, starts


def _overlap(a, b):
    """Seconds shared by two sets of disjoint intervals (one oblast's episodes)."""
    import numpy as np
    if a.empty or b.empty:
        return 0.0
    t0 = a.start.min()
    sec = lambda x: (x - t0).dt.total_seconds().to_numpy()
    bs, be = sec(b.start), sec(b.end)
    o = np.argsort(bs)
    bs, be = bs[o], be[o]
    cum = np.r_[0, np.cumsum(be - bs)]

    def covered(t):  # seconds of b before t
        k = np.searchsorted(bs, t, side="right")
        return cum[np.maximum(k - 1, 0)] + np.where(k > 0, np.minimum(t, be[np.maximum(k - 1, 0)]) - bs[np.maximum(k - 1, 0)], 0)

    return float((covered(sec(a.end)) - covered(sec(a.start))).sum())


def compare(a, b, lo, hi, tol_min=2):
    """Agreement of two record tables on [lo, hi): per oblast and 'all'. Episodes are censored at hi.
    a_in_b = share of A's episode starts with a B start within +-tol_min minutes."""
    import numpy as np
    win = lambda r: r[(r.start < hi) & (r.end.isna() | (r.end > lo))]
    ea, eb = episodes(win(a), hi), episodes(win(b), hi)
    obl = sorted(set(ea.oblast_id) | set(eb.oblast_id))
    n = int((hi - lo).total_seconds() // 60)
    (sa, ta), (sb, tb) = minute_grid(ea, lo, n, obl), minute_grid(eb, lo, n, obl)

    def hit(x, y):  # x starts that have a y start within +-tol
        cy = np.concatenate([np.zeros((len(obl), 1)), np.cumsum(y > 0, 1)], 1)
        i = np.arange(n)
        w = cy[:, np.minimum(i + tol_min + 1, n)] - cy[:, np.maximum(i - tol_min, 0)]
        return ((x > 0) & (w > 0)).sum(1)

    rows = pd.DataFrame({"minutes_a": sa.sum(1), "minutes_b": sb.sum(1), "inter": (sa & sb).sum(1),
                         "union": (sa | sb).sum(1), "starts_a": (ta > 0).sum(1), "starts_b": (tb > 0).sum(1),
                         "a_hit": hit(ta, tb), "b_hit": hit(tb, ta)}, index=pd.Index(obl, name="oblast_id"))
    # exact overlap in seconds (no minute rounding), episodes clipped to [lo, hi)
    clip = lambda e: e.assign(start=e.start.clip(lower=lo), end=e.end.clip(upper=hi))
    ca, cb = clip(ea), clip(eb)
    secs = lambda e: (e.end - e.start).dt.total_seconds().groupby(e.oblast_id).sum().reindex(obl, fill_value=0)
    rows["sec_a"], rows["sec_b"] = secs(ca).to_numpy(), secs(cb).to_numpy()
    rows["sec_inter"] = [_overlap(ca[ca.oblast_id == o], cb[cb.oblast_id == o]) for o in obl]
    rows.loc["all"] = rows.sum()
    rows["jaccard"] = rows.inter / rows.union.clip(lower=1)
    rows["jaccard_s"] = rows.sec_inter / (rows.sec_a + rows.sec_b - rows.sec_inter).clip(lower=1)
    rows["a_in_b"] = rows.a_hit / rows.starts_a.clip(lower=1)
    rows["b_in_a"] = rows.b_hit / rows.starts_b.clip(lower=1)
    return rows


def daily_agreement(a, b, lo, hi):
    """Correlation and mean absolute difference of alert-minutes per (oblast, Kyiv calendar day) on [lo, hi).
    Only full Kyiv days inside the window count."""
    import numpy as np
    win = lambda r: r[(r.start < hi) & (r.end.isna() | (r.end > lo))]
    ea, eb = episodes(win(a), hi), episodes(win(b), hi)
    obl = sorted(set(ea.oblast_id) | set(eb.oblast_id))
    n = int((hi - lo).total_seconds() // 60)
    day = (lo + pd.to_timedelta(np.arange(n), "min")).tz_convert("Europe/Kyiv").date
    full = pd.Series(day).value_counts() >= 1380  # 23 h minimum: DST days are 23 or 25 h long
    per_day = lambda e: pd.DataFrame(minute_grid(e, lo, n, obl)[0].T, index=day).groupby(level=0).sum()
    x, y = (per_day(e).loc[lambda d: full[d.index].to_numpy()].to_numpy().ravel() for e in (ea, eb))
    return float(np.corrcoef(x, y)[0, 1]), float(np.abs(x - y).mean())
