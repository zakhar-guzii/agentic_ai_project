"""Checks on the forecast set-up: leakage (TruncationCheck) and drift between two sets of rows
(AdversarialValidation)."""
import numpy as np
import pandas as pd

from alerts.features import WEEK


class TruncationCheck:
    """Proves that a forecast-time computation uses nothing from the moment T on.

    It runs the computation twice: on all records, and on the records as they were known at T (`known_at`). Any
    difference means the first run saw something that happened at or after T. This is the brief's no-leakage rule
    tested directly, row by row, with exact equality.
    """

    def __init__(self, records):
        self.records = records

    @staticmethod
    def known_at(records, moment):
        """Records as known at `moment`: only alerts that started before it; an end after it is not known yet,
        so such alerts are still on and are clipped at `moment`."""
        r = records[records.start < moment]
        return r.assign(end=r.end.fillna(moment).clip(upper=moment))

    def mismatches(self, compute, moments):
        """The moments where compute(all records, T) differs from compute(records known at T, T)."""
        return [m for m in moments
                if not compute(self.records, m).equals(compute(self.known_at(self.records, m), m))]


class AdversarialValidation:
    """Can a classifier tell two sets of forecast rows apart from their features alone?

    The rows of `a` are labelled 0 and those of `b` 1, and a LightGBM classifier (the probe's fixed settings, no
    tuning) learns to guess the set. Each set is cut into k consecutive time blocks; fold j holds block j of both
    sets, and its model is fitted on no row less than `gap` (the longest feature window) from a held moment, so no
    fitted row shares a minute of history with a held one. Random row folds did, and a held row was recognised by
    its neighbours in time (Wrong #10). The ROC AUC of each fold says how far the sets differ: about 0.5 means the
    same distribution, near 1 strong drift; the mean gain per feature names what drifted.

    The fit may hold later blocks than the held ones: the class is the period itself, not a future outcome, and a
    forward-only scheme cannot work (its first fit would hold one class only). So this is a drift diagnostic, not a
    check of forecasting the future; forecast quality comes only from Split.forward. Nor does it check leakage: a
    feature that sees the future can have the same distribution in both sets. Leakage is TruncationCheck's job.
    """

    SETTINGS = dict(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=200, subsample=0.8,
                    subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=0)
    MIN_FIT = 5 * SETTINGS["min_child_samples"]  # rows of each set a fold's fit needs: five of the smallest leaves

    def __init__(self, features, k=4, gap=pd.Timedelta(minutes=WEEK)):
        self.features, self.k, self.gap = list(features), k, gap

    def folds(self, a, b):
        """(fit, held) masks over the rows of a, then b. Fold j holds the j-th of k consecutive time blocks of each set
        (all rows of a moment in one block) and fits no row less than `gap` from a held moment."""
        ts = pd.concat([a.ts, b.ts], ignore_index=True)
        block = np.r_[self._blocks(a.ts), self._blocks(b.ts)]
        first = np.r_[np.ones(len(a), bool), np.zeros(len(b), bool)]
        for j in range(self.k):
            held, near = block == j, np.zeros(len(ts), bool)
            for side in (first, ~first):
                t = ts[held & side]
                near |= ((ts > t.min() - self.gap) & (ts < t.max() + self.gap)).to_numpy()
            yield ~near & ~held, held  # with gap = 0, `near` would leave out the block's first and last moments

    def _blocks(self, ts):
        """Block number 0 .. k-1 of each row: its moment's place among the set's moments, in time order."""
        codes, moments = pd.factorize(ts, sort=True)
        return codes * self.k // len(moments)

    def run(self, a, b):
        """(ROC AUC of each fold, share of the total gain per feature, largest first)."""
        import lightgbm as lgb
        from sklearn.metrics import roc_auc_score
        x = pd.concat([a[self.features], b[self.features]], ignore_index=True)
        y = np.r_[np.zeros(len(a)), np.ones(len(b))]
        aucs, gain = [], np.zeros(len(self.features))
        for j, (fit, held) in enumerate(self.folds(a, b)):
            if min((y[fit] == 0).sum(), (y[fit] == 1).sum()) < self.MIN_FIT:
                raise ValueError(f"fold {j}: under {self.MIN_FIT} rows of a set lie outside the gap; a set is too short")
            model = lgb.LGBMClassifier(**self.SETTINGS).fit(x[fit], y[fit])
            aucs.append(roc_auc_score(y[held], model.predict_proba(x[held])[:, 1]))
            gain += model.booster_.feature_importance("gain")
        importance = pd.Series(gain / gain.sum(), index=self.features).sort_values(ascending=False)
        return pd.Series(aucs, name="auc"), importance
