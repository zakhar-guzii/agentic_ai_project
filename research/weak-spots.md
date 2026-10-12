# Weak spots of the frozen model, and what to improve

Post hoc (PROCESS_LOG, Decision 11). Every number is in `results/metrics_report.md` (`python main.py metrics`), computed
from the frozen forecast files. Alarm threshold t: max F1 on CHOOSE, applied unchanged later (1 h 0.26, 3 h 0.38, 6 h 0.31).
Nothing here changed the model; the holdout is spent, so none of the fixes below can be checked honestly before submission.

## Where it stands

| | benchmark 1 h | holdout 1 h | benchmark 3 h | holdout 3 h | benchmark 6 h | holdout 6 h |
|---|---|---|---|---|---|---|
| P / R / F1, logistic | .52 / .82 / **.64** | .52 / .85 / **.65** | .74 / .85 / **.79** | .80 / .86 / **.82** | .77 / .91 / **.83** | .87 / .91 / **.89** |
| F1 recent7 / clim28 | .615 / .613 | .639 / .607 | .773 / .777 | .826 / .821 | .841 / .836 | .910 / .865 |
| AP logistic / recent7 | .648 / .621 | .590 / .600 | .842 / .833 | .870 / .870 | .915 / .913 | .954 / .961 |
| AUC logistic / recent7 | .863 / .842 | .780 / .771 | .886 / .876 | .841 / .846 | .903 / .899 | .890 / .906 |

The edge is real but small at 1 h, thin at 3 h and absent at 6 h; on the holdout recent7 matches or beats it from 3 h.

## Weak spots

1. **It ranks regions, not moments.** Pooled AUC is .863 at 1 h, but within one region it is .51–.81 (benchmark). Most
   of the pooled skill is "Kharkiv is busier than Lviv". On the holdout at 3 h, within-region AUC falls below .5 in
   Chernivtsi (.30), Ivano-Frankivsk (.32), Khmelnytskyi (.39), Ternopil (.44): the ranking is inverted there.
2. **The front line: always yes.** Kharkiv, Zaporizhzhia, Donetsk, Chernihiv, Dnipro, Sumy, Poltava, Kherson, Odesa,
   Mykolaiv: recall ≈ 1 and F1 equals the always-yes F1 (f1_lift ≤ .005). The model adds nothing a constant doesn't.
3. **The far west: never yes.** Lviv, Ivano-Frankivsk, Zakarpattia: F1 = 0 at 1 h (rare starts, 0.4–2.3%); AUC .73–.77
   says there is some ranking, but one pooled threshold never fires there. On the holdout (a massed strike reached the
   west) Volyn, Chernivtsi, Ivano-Frankivsk, Lviv, Ternopil have f1_lift −.23 to −.35 at 3 h.
   The real gain is in the middle band: Khmelnytskyi, Volyn, Rivne, Vinnytsia, Kyiv City (f1_lift +.05 to +.11 at 1 h).
4. **Level lags under high load.** Holdout mean p vs base rate: 3 h .545 vs .600, 6 h .666 vs .753 (benchmark: .427 vs
   .422, .541 vs .536). The global Platt learns from the 14 days before the cutoff and the model is frozen; recent7
   moves with the week. That is the holdout's loss to recent7 at 3 and 6 h.
5. **Region bias a global calibrator can't fix.** Benchmark 1 h: Kherson mean p .461 vs base .346 (skill < 0 vs both
   references); Kyiv oblast .465 vs .712 (skill vs recent7 −.21 at 1 h, −.86 at 3 h). One Platt for 24 regions.
6. **6 h ranks no better than climatology.** AP .915 vs clim28 .913, AUC .903 vs .898 (benchmark). Whatever skill there is
   at 6 h comes from the level, which is what point 4 breaks.
7. **Evening 21–24 Kyiv.** Benchmark 1 h skill vs recent7 +.007 in that slot (others +.03…+.08); with 00–03 it has the
   lowest F1 (.58). The hour enters the linear model as one sin/cos pair for all regions, while night strikes start
   regionally (south and east first).
8. **Reporting.** Per-region skill against a reference with Brier ≈ 0 explodes (Kharkiv 3 h: −4,327 in the benchmark
   table); F1 per region without the always-yes reference reads as good where the model does nothing.

## What to improve, by expected gain per hour of work

1. **Recalibrate per region and more often** (points 4, 5): a per-region (or region-group) Platt intercept and a
   shorter or exponentially weighted window (3–7 days), refitted daily in `predict`. Cheap; targets the exact loss to
   recent7 on the holdout.
2. **Let regions differ** (points 1, 7): obl × hour and obl × recent-load interactions in the logistic model, or
   gbm_clim with per-region calibration (second on CHOOSE: mean skill vs clim28 .093, logistic .107).
3. **Blend with recent7 at 6 h, or drop the 6 h claim** (point 6). A fixed 50/50 blend needs no tuning.
4. **Classification view per region** (points 2, 3): per-region thresholds chosen on CHOOSE, or report AP / f1_lift
   instead of F1 as the regional number; set skill to NaN when the reference Brier is ~0.
5. **Features for within-region ranking** (points 1, 2): raion-level counts and the threat type (`threats` is live only,
   so it must first be logged forward in time).
6. **An honest check needs new data:** register a new untouched period (e.g. two weeks after submission) before any of
   1–5 is fitted, and keep `forecast_log.csv` running for live scores.
