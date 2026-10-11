"""Seam checks: do the alert sources agree on overlapping windows?  usage: python -I seam.py F_DIR"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

import common as C

OBLS = sorted(C.OBL)


def window(rec, lo, hi):
    return rec[(rec.start < hi) & (rec.end.isna() | (rec.end > lo))]


def unit_match(a, b, lo, hi, tol_s=60):
    """Share of A's raw records (start in window) that B has for the same unit with |dstart|<=tol."""
    a = a[(a.start >= lo) & (a.start < hi)].sort_values("start")
    b = b.sort_values("start")[["unit", "start", "end"]].rename(columns={"start": "sb", "end": "eb"})
    m = pd.merge_asof(a, b.assign(start=b.sb).sort_values("start"), on="start", by="unit",
                      tolerance=pd.Timedelta(seconds=tol_s), direction="nearest")
    hit = m.sb.notna()
    de = (m.end - m.eb).abs().dt.total_seconds()[hit & m.end.notna() & m.eb.notna()]
    return len(a), hit.mean(), de.median(), (de <= 60).mean()


def compare(A, B, lo, hi, label, tol=2):
    lo, hi = pd.Timestamp(lo, tz="UTC"), pd.Timestamp(hi, tz="UTC")
    n = int((hi - lo).total_seconds() // 60)
    grids = []
    for r in (A, B):
        ep = C.union(window(r[r.oblast_id.isin(OBLS)], lo, hi), hi)
        grids.append(C.minute_grid(ep, lo, n, OBLS))
    (sa, ta), (sb, tb) = grids
    inter, uni = (sa & sb).sum(1), (sa | sb).sum(1)
    jac = np.where(uni > 0, inter / np.maximum(uni, 1), np.inf)  # no alerts in either source: not a disagreement

    def recall(x, y):  # share of x's episode starts with a y start within +-tol minutes
        cy = np.concatenate([np.zeros((len(OBLS), tol + 1)), np.cumsum(y > 0, 1), np.repeat(np.cumsum(y > 0, 1)[:, -1:], tol, 1)], 1)
        win = cy[:, 2 * tol + 1:] - cy[:, : -2 * tol - 1]
        return ((x > 0) & (win > 0)).sum() / max((x > 0).sum(), 1)

    mins = pd.Timestamp(lo) + pd.to_timedelta(np.arange(n), "min")
    day = mins.tz_convert(C.KYIV).date
    da = pd.DataFrame(sa.T, index=day).groupby(level=0).sum()
    db = pd.DataFrame(sb.T, index=day).groupby(level=0).sum()
    full = pd.Series(day).value_counts().reindex(da.index) >= 1380  # complete days only
    da, db = da[full.values], db[full.values]
    x, y = da.to_numpy().ravel(), db.to_numpy().ravel()
    res = dict(window=f"{lo:%Y-%m-%d %H:%M} -> {hi:%Y-%m-%d %H:%M}", days=round(n / 1440, 1),
               minutes_A=int(sa.sum()), minutes_B_over_A=round(sb.sum() / max(sa.sum(), 1), 3),
               jaccard=round(inter.sum() / max(uni.sum(), 1), 3),
               jaccard_min_obl=f"{jac.min():.2f} ({C.OBL[OBLS[int(jac.argmin())]]})",
               starts_A=int((ta > 0).sum()), starts_B=int((tb > 0).sum()),
               startsA_in_B=round(recall(ta, tb), 3), startsB_in_A=round(recall(tb, ta), 3),
               daily_corr=round(np.corrcoef(x, y)[0, 1], 3) if len(x) > 2 else None,
               daily_MAE_min=round(np.abs(x - y).mean(), 1) if len(x) else None)
    print(f"\n## {label}\n" + "\n".join(f"  {k}: {v}" for k, v in res.items()), flush=True)
    return res


def main():
    F = sys.argv[1]
    v, m, j, vo = C.load_vadimkin(F), C.load_map(F), C.load_jj(F), C.load_volunteer(F)
    m_core = m[m.level.isin(["raion", "oblast"])]  # city queries + hromada units (standing alerts) left out, as in Vadimkin
    print("map rows by level:", m.level.value_counts().to_dict(), "| hromada units:", m[m.level == "hromada"].unit.nunique())
    T = lambda s: pd.Timestamp(s, tz="UTC")
    out = {}
    # 1. Vadimkin official vs map (11-month overlap), split around the @air_alert_ua outage
    out["vad_vs_map_pre"] = compare(v, m_core, "2025-10-04", "2026-08-29 04:00", "A=Vadimkin official, B=map: 2025-10-04 .. outage")
    out["vad_vs_map_outage"] = compare(v, m_core, "2026-08-29 05:00", "2026-09-02 14:00", "A=Vadimkin, B=map: @air_alert_ua outage")
    out["vad_vs_map_post"] = compare(v, m_core, "2026-09-02 14:00", "2026-09-07 05:00", "A=Vadimkin, B=map: outage .. freeze")
    # per-month Jaccard, Vadimkin vs map
    for lo, hi in [("2025-10-04", "2025-11-01"), ("2025-11-01", "2025-12-01"), ("2025-12-01", "2026-01-01"),
                   ("2026-03-01", "2026-04-01"), ("2026-06-01", "2026-07-01"), ("2026-08-01", "2026-08-29")]:
        compare(v, m_core, lo, hi, f"A=Vadimkin, B=map month {lo[:7]}")
    print("\nunit-level (raion name) match, Vadimkin raion rows found in map (n, share, median |dEnd| s, share |dEnd|<=60s):",
          unit_match(v[v.level == "raion"], m_core, T("2025-12-01"), T("2026-08-29")))
    # 2. map vs JustJimer (alerts.in.ua) after the reform; then red-only
    out["map_vs_jj"] = compare(m_core, j, "2026-09-06 12:00", "2026-10-10 09:00", "A=map, B=JustJimer alerts.in.ua (red+yellow)")
    compare(m_core, j[j.alert_level == "red"], "2026-09-08", "2026-10-10 09:00", "A=map, B=JustJimer RED only")
    compare(m_core, j[j.alert_level == "yellow"], "2026-09-08", "2026-10-10 09:00", "A=map, B=JustJimer YELLOW only")
    print("\nunit-level match map->JJ:", unit_match(m_core[m_core.level == "raion"], j[j.level == "raion"], T("2026-09-08"), T("2026-10-10 09:00")))
    print("unit-level match JJ->map:", unit_match(j[j.level == "raion"], m_core[m_core.level == "raion"], T("2026-09-08"), T("2026-10-10 09:00")))
    # 3. JustJimer vs Vadimkin: the only direct overlap (~17 h)
    out["vad_vs_jj"] = compare(v, j, "2026-09-06 12:00", "2026-09-07 05:00", "A=Vadimkin, B=JustJimer: direct overlap")
    # 4. volunteer (eTryvoga) vs map, recent months
    for lo, hi in [("2025-10-04", "2026-01-01"), ("2026-01-01", "2026-04-01"), ("2026-04-01", "2026-07-01"),
                   ("2026-07-01", "2026-09-07"), ("2026-09-07", "2026-10-10 04:00")]:
        compare(m_core, vo, lo, hi, f"A=map, B=volunteer {lo}..{hi}")
    pd.DataFrame(out).T.to_csv(f"{F}/work/seam_summary.csv")


if __name__ == "__main__":
    main()
