"""Does "threat posts in the last N hours" (Telegram, by post time <= T) add anything?
Stacks on the saved out-of-sample predictions: fit LR on the dev window, score once on the test window.
usage: python -I text.py F_DIR SERIES
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

import common as C

F, SERIES = sys.argv[1], sys.argv[2]
A = "['’]"  # apostrophe variants
PAT = {4: r"Вінниц|Вінниччин", 8: r"Волин|Луцьк|Ковел", 9: rf"Дніпр|Кривий Ріг|Кривого Рогу|Кривому Розі|Нікопол|Павлоград|Кам{A}янськ|Самарівськ|Марган",
       28: rf"Донеччин|Донецьк|Краматорськ|Слов{A}янськ|Покровськ|Дружківк|Костянтинівк", 10: r"Житомир|Бердичів|Звягел|Коростен",
       11: r"Закарпат|Ужгород|Мукачев", 12: r"Запоріж", 13: r"Франківськ|Прикарпат|Калуш",
       14: r"Київщин|Київськ|Бориспіл|Біла Церква|Білої Церкви|Білоцерків|Бровар|Бучанськ|Обухів|Фастів|Вишгород|Ірпін|Васильків",
       31: r"Київ(?!щин|ськ)|Києв|[Сс]толиц", 15: r"Кіровоград|Кропивницьк|Світловодськ", 27: r"Львів|Львов",
       17: r"Миколаїв|Миколаєв|Вознесенськ|Очаків", 18: r"Одес|Ізмаїл|Чорноморськ|Білгород-Дністровськ|Заток",
       19: r"Полтав|Кременчук|Миргород|Лубн", 5: r"Рівн|Сарн|Дубн", 20: r"\bСум(?:и|щин|ськ|\b)|Шостк|Конотоп|Охтирк|Глух|Ромн",
       21: r"Терноп", 22: rf"Харків|Харков|Ізюм|Куп{A}янськ|Чугу|Лозов|Богодух|Балакл", 23: r"Херсон",
       3: rf"Хмельниц|Хмельнич|Кам{A}янець|Шепетівк|Старокостянтин", 24: r"Черкас|Умань|Сміл|Золотонош",
       26: r"Чернівц|Буковин", 25: r"Черніг|Ніжин|Прилук|Корюків|Новгород-Сіверськ"}
THREAT = re.compile(r"БпЛА|[Шш]ахед|[Рр]акет|[Бб]алістик|КАБ|Бандерол|Циркон|Кинджал|Калібр|[Шш]видкісн|[Зз]агроз|[Цц]іль|МіГ|Ту-\d|авіаці|[Вв]ихід|[Пп]уск")


def posts():
    p = pd.read_csv(f"{F}/work/tg_posts.csv")
    p["dt"] = pd.to_datetime(p.dt_utc, utc=True)
    p["text"] = p.text.fillna("")
    p["threat"] = p.text.str.contains(THREAT)
    for o, pat in PAT.items():
        p[f"m{o}"] = p.text.str.contains(pat, regex=True)
    return p


def counts(times, T, hours):
    t = np.sort(times.to_numpy().astype("datetime64[ns]").astype(np.int64))
    q = T.to_numpy().astype("datetime64[ns]").astype(np.int64)
    return np.searchsorted(t, q, "right") - np.searchsorted(t, q - int(hours * 3600e9), "right")


def add_text(df, p, hours):
    T = df["ts"].dt.tz_convert("UTC").dt.tz_localize(None)
    out = {}
    for ch, tag in (("kpszsu", "kp"), ("radar_raketaa", "rr")):
        q = p[(p.channel == ch) & p.threat]
        out[f"{tag}_nat"] = counts(q.dt.dt.tz_localize(None), T, hours)
        obl = np.zeros(len(df))
        for o in PAT:
            sel = df.obl.to_numpy() == o
            if sel.any():
                obl[sel] = counts(q[q[f"m{o}"]].dt.dt.tz_localize(None), T[sel], hours)
        out[f"{tag}_obl"] = obl
    return df.assign(**out)


def logit(x):
    x = np.clip(x, 1e-4, 1 - 1e-4)
    return np.log(x / (1 - x))


def stack(dev, te, base_col, text_cols):
    Xd0, Xt0 = logit(dev[base_col]).to_numpy()[:, None], logit(te[base_col]).to_numpy()[:, None]
    tx = lambda d: np.log1p(d[text_cols].to_numpy())
    Xd1, Xt1 = np.c_[Xd0, tx(dev)], np.c_[Xt0, tx(te)]
    p0 = LogisticRegression(C=1.0, max_iter=1000).fit(Xd0, dev.y).predict_proba(Xt0)[:, 1]
    m1 = LogisticRegression(C=1.0, max_iter=1000).fit(Xd1, dev.y)
    p1 = m1.predict_proba(Xt1)[:, 1]
    y = te.y.to_numpy().astype(float)
    b0, b1 = (p0 - y) ** 2, (p1 - y) ** 2
    day = te["ts"].dt.tz_convert(C.KYIV).dt.date.to_numpy()
    days = np.unique(day)
    rng = np.random.default_rng(0)
    g = pd.DataFrame({"d": day, "x": b1 - b0, "c": 1}).groupby("d").sum()
    boot = []
    for _ in range(2000):  # day-block bootstrap of the Brier difference
        s = g.loc[rng.choice(days, len(days))].sum()
        boot.append(s.x / s.c)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return dict(n_test=len(te), brier_base=b0.mean(), brier_text=b1.mean(), d_brier=b1.mean() - b0.mean(),
                d_ci95=f"[{lo:+.4f}, {hi:+.4f}]", auc_base=roc_auc_score(y, p0), auc_text=roc_auc_score(y, p1),
                coef=np.round(m1.coef_[0], 2).tolist())


def main():
    p = posts()
    for ch, g in p.groupby("channel"):
        ids = g.id.sort_values()
        print(f"{ch}: posts {len(g)}, {g.dt.min()} .. {g.dt.max()}, threat {g.threat.mean():.2f}, edited {g.edited.mean():.2f}, "
              f"id gaps {int(ids.max() - ids.min() + 1 - len(ids))}, with any oblast mention "
              f"{g[[f'm{o}' for o in PAT]].any(axis=1).mean():.2f}, posts/day {len(g) / ((g.dt.max() - g.dt.min()).days + 1):.0f}")
    pr = pd.read_parquet(f"{F}/work/preds_{SERIES}.parquet")
    rows = []
    K = lambda x: pd.Timestamp(x, tz=C.KYIV)
    schemes = {"dev 08-29..09-12 / test 09-13..10-10": lambda d: (d[d.split == "dev"], d[d.split == "test"]),
               # sensitivity: stacker fitted on post-reform rows only (base GBM still trained before 08-29)
               "dev 09-07..09-20 / test 09-21..10-10": lambda d: (d[(d.ts >= K("2026-09-07 09:00")) & (d.ts < K("2026-09-21"))],
                                                                d[d.ts >= K("2026-09-21")])}
    allc = ["kp_nat", "kp_obl", "rr_nat", "rr_obl"]
    for tgt, hours in (("a3", 3), ("a6", 6), ("b", 6)):
        d = add_text(pr[pr.target == tgt].reset_index(drop=True), p, hours)
        for sch, split in schemes.items():
            dev, te = split(d)
            uni = {c: round(roc_auc_score(te.y, te[c]), 3) for c in allc}
            for base in ("p_raw", "p_clim"):
                for cols in (allc, ["kp_obl"]):
                    if base == "p_clim" and len(cols) == 1:
                        continue
                    r = stack(dev, te, base, cols)
                    rows.append(dict(target=tgt, window_h=hours, scheme=sch, on_top_of=("LightGBM" if base == "p_raw" else "climatology"),
                                     text=("+".join(cols) if len(cols) == 1 else "all 4"), **r,
                                     univariate_auc_test=uni if (base == "p_raw" and len(cols) > 1) else ""))
    R = pd.DataFrame(rows)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
    print(R.round(4).to_string(index=False))
    R.to_csv(f"{F}/work/text_{SERIES}.csv", index=False)


if __name__ == "__main__":
    main()
