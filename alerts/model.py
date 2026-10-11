"""The calibrated forecaster: P(an episode starts in [T, T + H)) for each forecast row."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression


class Platt:
    """Rescales one model's probabilities with a logistic regression on their logit (as in the probe). It fixes the
    scale of a forecast; it ranks nothing new and combines nothing."""

    def fit(self, p, y):
        self.lr = LogisticRegression(C=100).fit(self._logit(p), y)
        return self

    def predict(self, p):
        return self.lr.predict_proba(self._logit(p))[:, 1]

    @staticmethod
    def _logit(p):
        q = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
        return np.log(q / (1 - q)).reshape(-1, 1)


class Boosting:
    """LightGBM at the probe's fixed settings. `clim` adds the daily clim28 rate as a feature; `half_life` (days) weights
    each row by its age at the fit moment, so that recent weeks count more."""

    def __init__(self, clim=False, half_life=None):
        self.clim, self.half_life = clim, half_life
        self.name = "gbm" + ("_clim" if clim else "") + ("_recent" if half_life else "")

    def weights(self, ts, asof):
        """0.5 ** (age / half_life) for rows at `ts` fitted at `asof`; None when every row counts the same."""
        if self.half_life:
            return 0.5 ** ((asof - ts) / pd.Timedelta(days=self.half_life)).to_numpy()
        return None
