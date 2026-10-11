"""Shared loaders: every alert source -> records(src, oblast_id, unit, level, start, end) in UTC,
then per-oblast union ("any part of the oblast under an air-raid alert") on a minute grid."""
import glob
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

KYIV = "Europe/Kyiv"
EXCLUDE = {16, 9999}  # Luhansk, Crimea: permanent alerts since 2022 (not in Vadimkin either)
# 24 oblasts + Kyiv city, ukrainealarm state ids
OBL = {4: "Vinnytska", 8: "Volynska", 9: "Dnipropetrovska", 28: "Donetska", 10: "Zhytomyrska", 11: "Zakarpatska",
       12: "Zaporizka", 13: "Ivano-Frankivska", 14: "Kyivska", 15: "Kirovohradska", 27: "Lvivska", 17: "Mykolaivska",
       18: "Odeska", 19: "Poltavska", 5: "Rivnenska", 20: "Sumska", 21: "Ternopilska", 22: "Kharkivska",
       23: "Khersonska", 3: "Khmelnytska", 24: "Cherkaska", 26: "Chernivetska", 25: "Chernihivska", 31: "Kyiv City"}
_N = {"Vinnytska": "Zhytomyrska Kyivska Cherkaska Kirovohradska Odeska Chernivetska Khmelnytska",
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
      "Kyiv City": "Kyivska Zhytomyrska Chernihivska Poltavska Cherkaska Vinnytska"}  # Kyiv city: Kyivska ring
_ID = {v: k for k, v in OBL.items()}
NEIGH = {_ID[o]: [_ID[n.replace("_", " ")] for n in ns.split()] for o, ns in _N.items()}
assert all(o in NEIGH[n] or o == 31 or n == 31 for o in NEIGH for n in NEIGH[o]), "adjacency not symmetric"


def uk_names(F):
    """Ukrainian state name -> id, from the ukrainealarm regions list."""
    r = json.load(open(f"{F}/dl_regions/regions.json", encoding="utf-8"))
    return {s["regionName"]: int(s["regionId"]) for s in r["states"]}


def _ts(s):
    return pd.to_datetime(s, utc=True, format="ISO8601", errors="coerce")


def load_vadimkin(F, levels=("oblast", "raion")):
    d = pd.read_csv(f"{F}/dl_vadimkin/official_data_uk.csv").drop_duplicates()
    d = d[d.level.isin(levels)]
    ids = uk_names(F)
    return pd.DataFrame({"src": "vadimkin", "oblast_id": d.oblast.map(ids).astype(int),
                         "unit": d.raion.fillna(d.oblast), "level": d.level,
                         "start": _ts(d.started_at), "end": _ts(d.finished_at)})


def load_volunteer(F):
    en = pd.read_csv(f"{F}/dl_vadimkin/official_data_en.csv", usecols=["oblast"])
    uk = pd.read_csv(f"{F}/dl_vadimkin/official_data_uk.csv", usecols=["oblast"])
    e2u = dict(zip(en.oblast, uk.oblast))
    ids = uk_names(F)
    d = pd.read_csv(f"{F}/dl_vadimkin/volunteer_data_en.csv")
    oid = d.region.map(e2u).map(ids)
    d = d[oid.notna()].assign(oid=oid.dropna().astype(int))
    return pd.DataFrame({"src": "volunteer", "oblast_id": d.oid, "unit": d.region, "level": "oblast",
                         "start": _ts(d.started_at), "end": _ts(d.finished_at), "naive": d.naive})


def load_map(F, d="dl_map"):
    rows = []
    for f in glob.glob(f"{F}/{d}/r*.json"):
        rid = int(re.match(r"r(\d+)_", Path(f).name).group(1))
        for x in json.load(open(f, encoding="utf-8")):
            rows.append((rid, x["regionId"], x["regionName"], x["startDate"], x["endDate"], x["isContinue"]))
    m = pd.DataFrame(rows, columns=["q", "unit_id", "unit", "s", "e", "cont"]).drop_duplicates(["unit_id", "s"])
    end = _ts(m.e).where(~m.cont)  # ongoing alerts: end unknown (NaT) -> censored at snapshot time
    end = end.where(end > pd.Timestamp("2000-01-01", tz="UTC"))
    # the state query also returns hromada units with standing alerts (e.g. Lypetska since 2026-03-10): tag them so the
    # oblast union can leave them out, like the Vadimkin oblast+raion union does
    level = np.select([m.q.isin([1293, 564]), m.unit.str.contains("громад"), m.unit.str.contains("област")],
                      ["city", "hromada", "oblast"], "raion")
    return pd.DataFrame({"src": "map", "oblast_id": m.q.replace({1293: 22, 564: 12}), "unit": m.unit,
                         "unit_id": m.unit_id.astype(int), "level": level, "start": _ts(m.s), "end": end})


def load_jj(F):
    d = pd.read_csv(f"{F}/dl_justjimer/alerts_in_ua.csv")
    d = d[(d.alert_type == "air_raid") & (d.location_type.isin(["raion", "oblast"]) |
                                          ((d.location_type == "city") & (d.location_oblast == "м. Київ")))]
    ids = uk_names(F)
    return pd.DataFrame({"src": "jj", "oblast_id": d.location_oblast.map(ids).astype(int), "unit": d.location_title,
                         "unit_id": d.location_uid, "level": d.location_type, "alert_level": d.alert_level,
                         "start": _ts(d.started_at), "end": _ts(d.finished_at)})


def union(rec, snapshot):
    """Per-oblast merged episodes [start, end). Open alerts are censored at `snapshot`."""
    out = []
    r = rec.assign(end=rec.end.fillna(snapshot).clip(upper=snapshot))
    r = r[r.end > r.start].sort_values(["oblast_id", "start"])
    for oid, g in r.groupby("oblast_id"):
        s, e = g.start.to_numpy(), g.end.to_numpy()
        run_end = np.maximum.accumulate(e)
        new = np.r_[True, s[1:] > run_end[:-1]]
        grp = np.cumsum(new) - 1
        ends = pd.Series(e).groupby(grp).max().to_numpy()
        out.append(pd.DataFrame({"oblast_id": oid, "start": s[new], "end": ends}))
    return pd.concat(out, ignore_index=True)


def minute_grid(ep, origin, n_min, oblasts):
    """state[o, m]: oblast under alert at any time in minute m;  starts[o, m]: episode starts in minute m."""
    pos = {o: i for i, o in enumerate(oblasts)}
    state = np.zeros((len(oblasts), n_min), dtype=bool)
    starts = np.zeros((len(oblasts), n_min), dtype=np.int16)
    sec = lambda t: (t - origin).dt.total_seconds().to_numpy()
    ep = ep[ep.oblast_id.isin(pos)]
    a = np.floor(sec(ep.start) / 60).astype(int)
    b = np.ceil(sec(ep.end) / 60).astype(int)
    for o, i, j in zip(ep.oblast_id.map(pos), a, b):
        i2, j2 = max(i, 0), min(j, n_min)
        if j2 > i2:
            state[o, i2:j2] = True
        if 0 <= i < n_min:
            starts[o, i] += 1
    return state, starts
