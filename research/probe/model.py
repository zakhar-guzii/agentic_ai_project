"""Feasibility baselines on the latest period, per oblast.
  (a) new alert starts within H in {1,3,6} h, for oblasts not under alert at T (30-min grid)
  (b) any alert tonight 23:00-07:00 Kyiv, issued 21:00 Kyiv
  (c) daily alert-minutes (Kyiv day), issued 00:00 Kyiv
Baselines: persistence, climatology, LightGBM on past-only features. Purged chronological splits.
usage: python -I model.py F_DIR SERIES [TEST_START TEST_END]   (SERIES = map | splice; dates are Kyiv days)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import glob
import os

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

import common as C

F, SERIES = sys.argv[1], sys.argv[2]
K = lambda s: pd.Timestamp(s, tz=C.KYIV).tz_convert("UTC")
ORIGIN = pd.Timestamp("2025-10-04", tz="UTC")
TRAIN_START = K("2025-11-15")
TEST_START = K(sys.argv[3]) if len(sys.argv) > 3 else K("2026-09-13")
DEV_START = TEST_START - pd.Timedelta(days=15)
TEST_END = K(sys.argv[4]) if len(sys.argv) > 4 else None  # default: data end
TAG = SERIES + (f"_{sys.argv[3]}" if len(sys.argv) > 3 else "")
SPLICE_AT = pd.Timestamp("2026-08-29 04:00", tz="UTC")  # Vadimkin before (its outage starts 04:55), map after
HS = (1, 3, 6)
GRID = 30  # minutes


def data_end():
    last = glob.glob(f"{F}/dl_map/r*_20261011.json")
    return pd.Timestamp(min(os.path.getmtime(f) for f in last), unit="s", tz="UTC").floor("min")


def build_series(end):
    m = C.load_map(F)
    m = m[m.level.isin(["raion", "oblast"]) & (m.start < end)]
    if SERIES == "splice":
        v = C.load_vadimkin(F)
        m = pd.concat([v[v.start < SPLICE_AT], m[m.start >= SPLICE_AT]])
    return C.union(m, end)


def metrics(y, p):
    y, p = np.asarray(y, float), np.clip(np.asarray(p, float), 0, 1)
    return dict(n=len(y), base=y.mean(), brier=np.mean((p - y) ** 2),
                auc=roc_auc_score(y, p) if 0 < y.mean() < 1 else np.nan,
                ap=average_precision_score(y, p) if 0 < y.mean() < 1 else np.nan)


def platt(p_dev, y_dev, p):
    lg = lambda q: np.log(np.clip(q, 1e-4, 1 - 1e-4) / (1 - np.clip(q, 1e-4, 1 - 1e-4))).reshape(-1, 1)
    return LogisticRegression(C=100).fit(lg(p_dev), y_dev).predict_proba(lg(p))[:, 1]


def skill_ci(loss, loss_ref, ts, n=1000):
    """95% day-block bootstrap CI of 1 - mean(loss)/mean(loss_ref) (blocks = Kyiv calendar days)."""
    day = pd.Series(pd.to_datetime(ts).dt.tz_convert(C.KYIV).dt.date.to_numpy())
    g = pd.DataFrame({"d": day, "a": np.asarray(loss, float), "b": np.asarray(loss_ref, float)}).groupby("d").sum()
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(g), (n, len(g)))
    sk = 1 - g.a.to_numpy()[idx].sum(1) / g.b.to_numpy()[idx].sum(1)
    lo, hi = np.percentile(sk, [2.5, 97.5])
    return f"[{lo:+.3f}, {hi:+.3f}]"


GBC = dict(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=200, subsample=0.8,
           subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=0)


def main():
    end = data_end()
    stop = min(end, TEST_END) if TEST_END is not None else end
    ep = build_series(end)
    obls = sorted(C.OBL)
    n = int((end - ORIGIN).total_seconds() // 60)
    S, ST = C.minute_grid(ep, ORIGIN, n, obls)
    # oblasts almost permanently under alert are degenerate for all three targets: decide on train data only
    tr = slice(int((TRAIN_START - ORIGIN).total_seconds() // 60), int((DEV_START - ORIGIN).total_seconds() // 60))
    share = S[:, tr].mean(1)
    keep = [o for o, s in zip(obls, share) if s < 0.8]
    print(f"series={SERIES} data_end={end} episodes={len(ep)}; train share under alert:",
          {C.OBL[o]: round(s, 2) for o, s in zip(obls, share)})
    print("excluded (>=80% of train time under alert):", [C.OBL[o] for o in obls if o not in keep])
    O = len(obls)
    CS = np.zeros((O, n + 1), np.int32); CS[:, 1:] = np.cumsum(S, 1)
    CT = np.zeros((O, n + 1), np.int32); CT[:, 1:] = np.cumsum(ST > 0, 1)
    idx = np.arange(n)
    LA = np.maximum.accumulate(np.where(S, idx, -10 ** 7), 1)  # last minute under alert
    LS = np.maximum.accumulate(np.where(ST > 0, idx, -10 ** 7), 1)  # last start minute
    W = np.zeros((O, O))
    for i, o in enumerate(obls):
        for nb in C.NEIGH[o]:
            W[i, obls.index(nb)] = 1
    W /= W.sum(1, keepdims=True)

    def feats(t):
        """Features at minute indices t (array), all from minutes < t. Returns dict of (O, len(t)) arrays."""
        cap = 7 * 1440
        win = lambda A, w: A[:, t] - A[:, np.maximum(t - w, 0)]
        f = dict(under=S[:, t - 1].astype(float),
                 min_since_alert=np.minimum(t - LA[:, t - 1], cap), min_since_start=np.minimum(t - LS[:, t - 1], cap),
                 starts_3h=win(CT, 180), starts_24h=win(CT, 1440), alert_min_24h=win(CS, 1440), alert_min_7d=win(CS, 7 * 1440))
        f["nb_active"] = W @ f["under"]
        f["nb_starts_1h"] = W @ win(CT, 60)
        f["nb_starts_3h"] = W @ win(CT, 180)
        f["nb_alert_min_24h"] = W @ f["alert_min_24h"]
        f["nb_min_since_start"] = np.vstack([f["min_since_start"][W[i] > 0].min(0) for i in range(O)])
        f["nat_active"] = np.tile(f["under"].sum(0), (O, 1))
        f["nat_active_1h_ago"] = np.tile(S[:, np.maximum(t - 61, 0)].sum(0), (O, 1))
        f["nat_starts_1h"] = np.tile(win(CT, 60).sum(0), (O, 1))
        f["nat_starts_3h"] = np.tile(win(CT, 180).sum(0), (O, 1))
        return f

    def frame(t, extra):
        f = feats(t)
        T = ORIGIN + pd.to_timedelta(t, "min")
        loc = T.tz_convert(C.KYIV)
        d = {k: v.ravel() for k, v in f.items()}
        d.update(obl=np.repeat(obls, len(t)), t=np.tile(t, O),
                 hour=np.tile(loc.hour + loc.minute / 60, O), dow=np.tile(loc.dayofweek, O))
        for k, v in extra.items():
            d[k] = v.ravel()
        df = pd.DataFrame(d)
        df["ts"] = ORIGIN + pd.to_timedelta(df.t, "min")
        return df[df.obl.isin(keep)].reset_index(drop=True)

    mi = lambda ts: int((ts - ORIGIN).total_seconds() // 60)
    FEATS = ["obl", "hour", "dow", "min_since_alert", "min_since_start", "starts_3h", "starts_24h", "alert_min_24h",
             "alert_min_7d", "nb_active", "nb_starts_1h", "nb_starts_3h", "nb_alert_min_24h", "nb_min_since_start",
             "nat_active", "nat_active_1h_ago", "nat_starts_1h", "nat_starts_3h"]
    results, preds = [], []

    # ---------------- (a) new alert start within H, oblasts not under alert ----------------
    t_all = np.arange(mi(TRAIN_START), mi(end) - 6 * 60 + 1, GRID)
    lab = {f"y{H}": (CT[:, np.minimum(t_all + 60 * H, n)] - CT[:, t_all]) > 0 for H in HS}
    for H in HS:
        lab[f"pers{H}"] = (CT[:, t_all] - CT[:, t_all - 60 * H]) > 0
    A = frame(t_all, lab)
    A = A[A.under == 0]
    for H in HS:
        y = f"y{H}"
        tr_ = A[A.ts <= DEV_START - pd.Timedelta(hours=H)]
        dv = A[(A.ts >= DEV_START) & (A.ts <= TEST_START - pd.Timedelta(hours=H))]
        te = A[(A.ts >= TEST_START) & (A.ts <= stop - pd.Timedelta(hours=6))]
        # climatology: oblast x Kyiv hour, last 28 days before the test start (purged), shrunk to oblast mean
        def clim(ref, tgt):
            ref = ref.assign(h=ref.hour.astype(int))
            om = ref.groupby("obl")[y].mean()
            g = ref.groupby(["obl", "h"])[y].agg(["sum", "count"]).reset_index()
            g["p"] = (g["sum"] + 10 * g.obl.map(om)) / (g["count"] + 10)
            key = pd.MultiIndex.from_arrays([tgt.obl, tgt.hour.astype(int)])
            p = g.set_index(["obl", "h"]).p.reindex(key).to_numpy()
            fb = tgt.obl.map(om).fillna(ref[y].mean()).to_numpy()
            return np.where(np.isnan(p), fb, p)
        win28 = lambda a, start: a[(a.ts >= start - pd.Timedelta(days=28)) & (a.ts <= start - pd.Timedelta(hours=H))]
        p_clim = clim(win28(A, TEST_START), te)
        p_clim_long = clim(tr_, te)
        mdl = lgb.LGBMClassifier(**GBC).fit(tr_[FEATS], tr_[y], categorical_feature=["obl"])
        p_dev_raw, p_te_raw = mdl.predict_proba(dv[FEATS])[:, 1], mdl.predict_proba(te[FEATS])[:, 1]
        p_te_cal = platt(p_dev_raw, dv[y], p_te_raw)
        bc = metrics(te[y], p_clim)["brier"]
        for name, p in [("persistence (start in last H)", te[f"pers{H}"]), ("climatology obl x hour, last 28 d", p_clim),
                        ("climatology obl x hour, full train", p_clim_long), ("LightGBM", p_te_raw),
                        ("LightGBM + Platt(dev)", p_te_cal)]:
            r = metrics(te[y], p)
            se = (np.asarray(p, float) - te[y].to_numpy()) ** 2
            results.append(dict(target=f"(a) start within {H} h", model=name, **r, skill=1 - r["brier"] / bc,
                                skill_ci=skill_ci(se, (p_clim - te[y].to_numpy()) ** 2, te.ts)))
        imp = pd.Series(mdl.booster_.feature_importance("gain"), FEATS).sort_values(ascending=False)
        print(f"H={H} rows train/dev/test {len(tr_)}/{len(dv)}/{len(te)}; top gain:", list(imp.index[:6]))
        p_clim_dev = clim(win28(A, DEV_START), dv)
        preds.append(pd.concat([dv.assign(split="dev", p_raw=p_dev_raw, p_clim=p_clim_dev),
                                te.assign(split="test", p_raw=p_te_raw, p_clim=p_clim)])
                     [["split", "obl", "t", "ts", y, "p_raw", "p_clim"]].rename(columns={y: "y"}).assign(target=f"a{H}"))

    # ---------------- (b) any alert tonight 23:00-07:00 Kyiv, issued 21:00 Kyiv ----------------
    days = pd.date_range("2025-10-06", (end.tz_convert(C.KYIV) - pd.Timedelta(hours=31)).strftime("%Y-%m-%d"), freq="D")
    ti = np.array([mi(K(f"{d:%Y-%m-%d} 21:00")) for d in days])
    n0 = np.array([mi(K(f"{d:%Y-%m-%d} 23:00")) for d in days])
    n1 = np.array([mi(K(f"{d + pd.Timedelta(days=1):%Y-%m-%d} 07:00")) for d in days])
    night = (CS[:, n1] - CS[:, n0]) > 0  # (O, nights)
    lastn = np.c_[np.full((O, 1), np.nan), night[:, :-1]].astype(float)
    roll = lambda k: pd.DataFrame(night.T.astype(float)).shift(1).rolling(k).mean().T.to_numpy()
    cnt28 = pd.DataFrame(night.T.astype(float)).shift(1).rolling(28).sum().T.to_numpy()
    extra = dict(y=night, last_night=lastn, nights7=roll(7), nights28=roll(28), clim=(cnt28 + 1) / 30,
                 nb_last_night=W @ np.nan_to_num(lastn), nat_last_night=np.tile(np.nanmean(lastn, 0), (O, 1)),
                 day=np.tile(days.values, (O, 1)))
    B = frame(ti, extra).dropna(subset=["nights28"])
    BF = FEATS + ["under", "last_night", "nights7", "nights28", "nb_last_night", "nat_last_night"]
    BF.remove("hour")
    tr_ = B[(B.ts >= TRAIN_START) & (B.ts < DEV_START - pd.Timedelta(hours=10))]
    dv = B[(B.ts >= DEV_START) & (B.ts < TEST_START - pd.Timedelta(hours=10))]
    te = B[(B.ts >= TEST_START) & (B.ts < stop - pd.Timedelta(hours=10))]
    mdl = lgb.LGBMClassifier(**{**GBC, "num_leaves": 15, "min_child_samples": 50, "n_estimators": 200}).fit(
        tr_[BF], tr_.y, categorical_feature=["obl"])
    p_dev_raw, p_te_raw = mdl.predict_proba(dv[BF])[:, 1], mdl.predict_proba(te[BF])[:, 1]
    bc = metrics(te.y, te.clim)["brier"]
    for name, p in [("persistence (last night)", te.last_night), ("climatology: oblast rate, last 28 nights", te.clim),
                    ("LightGBM", p_te_raw), ("LightGBM + Platt(dev)", platt(p_dev_raw, dv.y, p_te_raw))]:
        r = metrics(te.y, p)
        yy = te.y.to_numpy().astype(float)
        results.append(dict(target="(b) any alert tonight", model=name, **r, skill=1 - r["brier"] / bc,
                            skill_ci=skill_ci((np.asarray(p, float) - yy) ** 2, (te.clim.to_numpy() - yy) ** 2, te.ts)))
    print(f"(b) nights train/dev/test {len(tr_)}/{len(dv)}/{len(te)}; test nights {te.day.min()}..{te.day.max()}")
    preds.append(pd.concat([dv.assign(split="dev", p_raw=p_dev_raw), te.assign(split="test", p_raw=p_te_raw)])
                 [["split", "obl", "t", "ts", "y", "p_raw", "clim"]].rename(columns={"clim": "p_clim"}).assign(target="b"))

    # ---------------- (c) daily alert-minutes, issued 00:00 Kyiv ----------------
    days = pd.date_range("2025-10-05", (end.tz_convert(C.KYIV) - pd.Timedelta(days=1)).strftime("%Y-%m-%d"), freq="D")
    d0 = np.array([mi(K(f"{d:%Y-%m-%d}")) for d in days])
    d1 = np.array([mi(K(f"{d + pd.Timedelta(days=1):%Y-%m-%d}")) for d in days])
    mins = (CS[:, d1] - CS[:, d0]).astype(float)
    M = pd.DataFrame(mins.T)
    ex = {f"lag{k}": M.shift(k).T.to_numpy() for k in range(1, 8)}
    ex.update(mean7=M.shift(1).rolling(7).mean().T.to_numpy(), mean28=M.shift(1).rolling(28).mean().T.to_numpy(),
              y=mins, day=np.tile(days.values, (O, 1)))
    ex["nb_lag1"] = W @ np.nan_to_num(ex["lag1"])
    ex["nat_lag1"] = np.tile(np.nanmean(ex["lag1"], 0), (O, 1))
    D = frame(d0, ex).dropna(subset=["mean28"])
    DF = ["obl", "dow", "under", "alert_min_24h", "starts_24h", "nb_alert_min_24h", "nat_active"] + \
         [f"lag{k}" for k in range(1, 8)] + ["mean7", "mean28", "nb_lag1", "nat_lag1"]
    tr_ = D[(D.ts >= TRAIN_START) & (D.ts < DEV_START)]
    te = D[(D.ts >= TEST_START) & (D.ts < stop - pd.Timedelta(days=1))]
    reg = lgb.LGBMRegressor(objective="l1", n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=50,
                            subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=0)
    reg.fit(pd.concat([tr_, D[(D.ts >= DEV_START) & (D.ts < TEST_START)]])[DF],
            pd.concat([tr_, D[(D.ts >= DEV_START) & (D.ts < TEST_START)]]).y, categorical_feature=["obl"])
    mae_c = np.abs(te.y - te.mean28).mean()
    for name, p in [("persistence (yesterday)", te.lag1), ("climatology: trailing 28-day mean", te.mean28),
                    ("trailing 7-day mean", te.mean7), ("LightGBM (L1), train+dev", reg.predict(te[DF]))]:
        mae = np.abs(te.y - p).mean()
        results.append(dict(target="(c) daily alert-minutes", model=name, n=len(te), base=te.y.mean(),
                            mae=mae, skill=1 - mae / mae_c,
                            skill_ci=skill_ci(np.abs(te.y - p), np.abs(te.y - te.mean28), te.ts)))
    print(f"(c) days test {te.day.min()}..{te.day.max()} mean minutes/oblast/day {te.y.mean():.0f}")

    R = pd.DataFrame(results)
    pd.set_option("display.width", 200)
    print(R.round(3).to_string(index=False))
    R.to_csv(f"{F}/work/results_{TAG}.csv", index=False)
    pd.concat(preds).to_parquet(f"{F}/work/preds_{TAG}.parquet")


if __name__ == "__main__":
    main()
