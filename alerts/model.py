"""The calibrated forecaster: P(an episode starts in [T, T + H)) for each forecast row."""
import copy
import importlib.metadata
import subprocess
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from alerts.checks import AdversarialValidation
from alerts.features import Features
from alerts.splits import DECISION

CALIBRATION = pd.Timedelta("14D")  # a calibrator learns from the forecasts of the 14 days before its block
CHOSEN = "logistic"  # set in a pre-registration commit, before the historical benchmark is scored


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


# A candidate forecaster has a `name`, `fit(rows, hours, asof)` on rows whose labels were known at `asof`, and
# `predict(rows)`, the raw probability of a start within `hours`. Settings are fixed: nothing is tuned.

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

    def fit(self, rows, hours, asof):
        self.columns = Features.NAMES + [f"clim28_{hours}"] * self.clim
        self.model = lgb.LGBMClassifier(**AdversarialValidation.SETTINGS).fit(
            rows[self.columns], rows[f"y{hours}"], sample_weight=self.weights(rows.ts, asof), categorical_feature=["obl"])
        return self

    def predict(self, rows):
        return self.model.predict_proba(rows[self.columns])[:, 1]


class CatBoost:
    """CatBoost at its library defaults (seed 0), with the oblast as a native category.

    The library chooses the boosting mode; this is not necessarily ordered boosting.
    """

    name = "catboost"

    def fit(self, rows, hours, asof):
        self.model = CatBoostClassifier(random_seed=0, verbose=0, allow_writing_files=False, cat_features=["obl"]).fit(
            rows[Features.NAMES], rows[f"y{hours}"])
        return self

    def predict(self, rows):
        return self.model.predict_proba(rows[Features.NAMES])[:, 1]


def _hour_circle(hour):
    """Kyiv hour -> (sin, cos), so that 23:30 sits next to 00:00."""
    a = 2 * np.pi * np.asarray(hour, float) / 24
    return np.c_[np.sin(a), np.cos(a)]


class Logistic:
    """Logistic regression, a linear model, at sklearn's defaults: the oblast and the weekday one-hot, the hour on a
    circle, counts and minutes as log1p and standardised."""

    name = "logistic"
    NUMERIC = [f for f in Features.NAMES if f not in ("obl", "hour", "dow")]

    def fit(self, rows, hours, asof):
        x = ColumnTransformer([("category", OneHotEncoder(handle_unknown="ignore"), ["obl", "dow"]),
                               ("hour", FunctionTransformer(_hour_circle), ["hour"]),
                               ("numeric", make_pipeline(FunctionTransformer(np.log1p), StandardScaler()), self.NUMERIC)])
        self.model = make_pipeline(x, LogisticRegression(max_iter=1000)).fit(rows[Features.NAMES], rows[f"y{hours}"])
        return self

    def predict(self, rows):
        return self.model.predict_proba(rows[Features.NAMES])[:, 1]


class ForwardRun:
    """Sequential forecast checks with the calibration in time order (PROCESS_LOG, Decision 4).

    In each block of `split.forward`, every candidate is fitted on the block's `fit` (rows whose labels were known at
    the block start s) and forecasts the block's held rows: out-of-fold raw forecasts. The block is then calibrated by a
    Platt fitted on the raw forecasts of the `window` before s whose labels were known at s. A block whose window reaches
    back before the first raw forecast is a warm-up block: it is not calibrated and not scored.
    """

    def __init__(self, candidates, split=DECISION, window=CALIBRATION):
        self.candidates, self.split, self.window_length = list(candidates), split, window

    def window(self, raw, s, hours):
        """The raw-forecast rows a calibrator at s may learn from: s - window <= T and T + H <= s."""
        return raw[(raw.ts >= s - self.window_length) & (raw.ts + pd.Timedelta(hours=hours) <= s)]

    def run(self, rows, hours, ranges, progress=False):
        """The held rows of every block of `ranges` ((a, b, blocks), in time order), with `block` (its start s),
        `scored`, and for each candidate `raw_<name>` and the calibrated `<name>`."""
        held = []
        for a, b, blocks in ranges:
            for fit, part in self.split.forward(rows, hours, a, b, blocks):
                s = part.ts.min()
                part = part.assign(block=s)
                for c in self.candidates:
                    if progress:
                        print(f"H={hours} block={s} candidate={c.name} fit={len(fit)} held={len(part)}", flush=True)
                    part[f"raw_{c.name}"] = c.fit(fit, hours, s).predict(part)
                held.append(part)
        raw = pd.concat(held)
        raw["scored"] = raw.block - self.window_length >= raw.ts.min()
        for c in self.candidates:
            raw[c.name] = np.nan
        for s, part in raw[raw.scored].groupby("block"):
            win = self.window(raw, s, hours)
            for c in self.candidates:
                platt = Platt().fit(win[f"raw_{c.name}"], win[f"y{hours}"])
                raw.loc[part.index, c.name] = platt.predict(part[f"raw_{c.name}"])
        return raw

    def final(self, rows, raws, asof):
        """Fit each candidate for use at `asof`, with a separate model and OOF calibrator per horizon."""
        result = {}
        for candidate in self.candidates:
            models, calibrators, counts = {}, {}, {}
            for h, raw in sorted(raws.items()):
                fit = rows[(rows.ts >= self.split.bounds["train"][0]) &
                           (rows.ts + pd.Timedelta(hours=h) <= asof)]
                win = self.window(raw, asof, h)
                models[h] = copy.deepcopy(candidate).fit(fit, h, asof)
                calibrators[h] = Platt().fit(win[f"raw_{candidate.name}"], win[f"y{h}"])
                counts[h] = {"fit": len(fit), "calibration": len(win)}
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parent.parent,
                                    capture_output=True, text=True, check=True).stdout.strip()
            meta = dict(name=candidate.name, train_start=self.split.bounds["train"][0], asof=asof,
                        calibration_days=self.window_length / pd.Timedelta("1D"), counts=counts,
                        features=Features.NAMES + ([f"clim28_{h}" for h in models] if getattr(candidate, "clim", False) else []),
                        versions={p: importlib.metadata.version(p) for p in
                                  ("numpy", "pandas", "lightgbm", "catboost", "scikit-learn", "scipy", "joblib")},
                        git_commit=commit)
            result[candidate.name] = Forecaster(models, calibrators, meta)
        return result


class Forecaster:
    """Saved models plus their OOF calibrators. Load only trusted project artifacts (joblib uses pickle)."""

    def __init__(self, models, calibrators, meta):
        self.models, self.calibrators, self.meta = models, calibrators, meta

    def predict(self, rows):
        return pd.DataFrame({f"p{h}": self.calibrators[h].predict(model.predict(rows))
                             for h, model in sorted(self.models.items())}, index=rows.index)

    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path, compress=3)

    @staticmethod
    def load(path):
        return joblib.load(path)
