"""Checks on the forecast set-up: leakage (TruncationCheck) and drift between two sets of rows
(AdversarialValidation)."""
import numpy as np
import pandas as pd


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
    tuning) learns to guess the set. Every row is scored by a model that did not see it (stratified k-fold), and the
    ROC AUC of those scores says how far the sets differ: about 0.5 means the same distribution, near 1 strong drift.
    The mean gain per feature names what drifted. This checks drift, not leakage: a feature that sees the future can
    have the same distribution in both sets and pass unnoticed. Leakage is TruncationCheck's job.
    """

    SETTINGS = dict(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=200, subsample=0.8,
                    subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=0)

    def __init__(self, features, folds=5):
        self.features, self.folds = list(features), folds

    def run(self, a, b):
        """(out-of-fold AUC, share of the total gain per feature, largest first)."""
        import lightgbm as lgb
        from sklearn.metrics import roc_auc_score
        from sklearn.model_selection import StratifiedKFold
        x = pd.concat([a[self.features], b[self.features]], ignore_index=True)
        y = np.r_[np.zeros(len(a)), np.ones(len(b))]
        score, gain = np.zeros(len(x)), np.zeros(len(self.features))
        for fit, held in StratifiedKFold(self.folds, shuffle=True, random_state=0).split(x, y):
            model = lgb.LGBMClassifier(**self.SETTINGS).fit(x.iloc[fit], y[fit])
            score[held] = model.predict_proba(x.iloc[held])[:, 1]
            gain += model.booster_.feature_importance("gain")
        importance = pd.Series(gain / gain.sum(), index=self.features).sort_values(ascending=False)
        return roc_auc_score(y, score), importance
