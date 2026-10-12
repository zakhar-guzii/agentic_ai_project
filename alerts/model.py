"""The calibrated forecaster: P(an episode starts in [T, T + H)) for each forecast row."""
import copy
import importlib.metadata
import itertools
import random
import subprocess
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from alerts.checks import AdversarialValidation
from alerts.evaluate import Scores
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


def recency(ts, asof, half_life):
    """0.5 ** (age / half_life) for rows at `ts` fitted at `asof`; None when every row counts the same."""
    if half_life:
        return 0.5 ** ((asof - ts) / pd.Timedelta(days=half_life)).to_numpy()
    return None


# A candidate forecaster has a `name`, `fit(rows, hours, asof)` on rows whose labels were known at `asof`, and
# `predict(rows)`, the raw probability of a start within `hours`. Step 3 fixed every setting; v2 (Decision 12) searches
# them.

class Candidate:
    """What the three model types share. `half_life` (days) weights each fitted row by its age at the fit moment, so
    that recent weeks count more; `refs` adds reference forecasts (`<ref>_<H>`, e.g. clim28) as inputs; `params`
    overrides the fixed settings; `name` labels the variant."""

    columns = Features.NAMES  # a model saved before v2 has no columns of its own

    def __init__(self, half_life=None, refs=(), params=None, name=None):
        self.half_life, self.refs, self.params = half_life, list(refs), dict(params or {})
        self.name = name or self.name

    def inputs(self, hours):
        """The input columns for horizon `hours`, remembered for `predict`."""
        self.columns = Features.NAMES + [f"{r}_{hours}" for r in self.refs]
        return self.columns

    def predict(self, rows):
        return self.model.predict_proba(rows[self.columns])[:, 1]


class Boosting(Candidate):
    """LightGBM at the probe's settings, unless `params` overrides them. `clim` adds the daily clim28 rate as an input."""

    def __init__(self, clim=False, half_life=None, refs=(), params=None, name=None):
        super().__init__(half_life, ["clim28"] * clim + list(refs), params,
                         name or "gbm" + ("_clim" if clim else "") + ("_recent" if half_life else ""))
        self.clim = clim

    def weights(self, ts, asof):
        return recency(ts, asof, self.half_life)

    def fit(self, rows, hours, asof):
        self.model = lgb.LGBMClassifier(**{**AdversarialValidation.SETTINGS, **self.params}).fit(
            rows[self.inputs(hours)], rows[f"y{hours}"], sample_weight=self.weights(rows.ts, asof),
            categorical_feature=["obl"])
        return self


class CatBoost(Candidate):
    """CatBoost at its library defaults (seed 0) unless `params` overrides them, with the oblast as a native category.

    The library chooses the boosting mode; this is not necessarily ordered boosting.
    """

    name = "catboost"

    def fit(self, rows, hours, asof):
        settings = {"random_seed": 0, "verbose": 0, "allow_writing_files": False, **self.params}
        self.model = CatBoostClassifier(**settings, cat_features=["obl"]).fit(
            rows[self.inputs(hours)], rows[f"y{hours}"], sample_weight=recency(rows.ts, asof, self.half_life))
        return self


def _hour_circle(hour):
    """Kyiv hour -> (sin, cos), so that 23:30 sits next to 00:00."""
    a = 2 * np.pi * np.asarray(hour, float) / 24
    return np.c_[np.sin(a), np.cos(a)]


def _logit(p):
    """Probabilities -> log odds, clipped as Platt clips them."""
    q = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    return np.log(q / (1 - q))


class Logistic(Candidate):
    """Logistic regression, a linear model, at sklearn's defaults unless `params` overrides them: the oblast and the
    weekday one-hot, the hour on a circle, counts and minutes as log1p and standardised, reference inputs as log odds
    and standardised (a missing one gets the median of the fitted rows)."""

    name = "logistic"
    NUMERIC = [f for f in Features.NAMES if f not in ("obl", "hour", "dow")]

    def fit(self, rows, hours, asof):
        refs = self.inputs(hours)[len(Features.NAMES):]
        parts = [("category", OneHotEncoder(handle_unknown="ignore"), ["obl", "dow"]),
                 ("hour", FunctionTransformer(_hour_circle), ["hour"]),
                 ("numeric", make_pipeline(FunctionTransformer(np.log1p), StandardScaler()), self.NUMERIC)]
        if refs:
            # a reference is NaN where its history is short (clim28's first days): the median of the fitted rows
            parts.append(("refs", make_pipeline(SimpleImputer(strategy="median"), FunctionTransformer(_logit),
                                                StandardScaler()), refs))
        self.model = make_pipeline(ColumnTransformer(parts), LogisticRegression(**{"max_iter": 1000, **self.params})).fit(
            rows[self.columns], rows[f"y{hours}"], logisticregression__sample_weight=recency(rows.ts, asof, self.half_life))
        return self


# Decision 12, the v2 search. Each family also searches the inputs and the recency half-life; the Platt window
# (WINDOWS, days) is searched by recalibrating each config's raw forecasts, so it is not in a config. FIXED settings
# stay the same in the search and the final fit, so a refit reproduces the search.
REFS = ["clim28", "recent7"]
SHARED = {"refs": [(), tuple(REFS)], "half_life": [None, 30, 60, 120]}
SPACE = {"logistic": {"C": [0.01, 0.1, 1, 10], "class_weight": [None, "balanced"]},
         "gbm": {"n_estimators": [200, 400, 800], "learning_rate": [0.02, 0.05, 0.1], "num_leaves": [15, 31, 63, 127],
                 "min_child_samples": [50, 200, 1000], "subsample": [0.7, 1.0], "colsample_bytree": [0.6, 0.8, 1.0],
                 "reg_lambda": [0, 1, 10]},
         "catboost": {"iterations": [300, 600, 1000], "learning_rate": [0.03, 0.1], "depth": [4, 6],
                      "l2_leaf_reg": [1, 3, 10]}}
FIXED = {"logistic": {}, "gbm": {"n_jobs": 6, "deterministic": True, "force_row_wise": True},
         "catboost": {"thread_count": 7}}
WINDOWS = (7, 14)


def configs(family, seed=0):
    """Every config of `family` ({"refs", "half_life", and the parameters}) in a fixed random order."""
    space = {**SHARED, **SPACE[family]}
    grid = [dict(zip(space, values)) for values in itertools.product(*space.values())]
    random.Random(seed).shuffle(grid)
    return grid


def candidate(family, config):
    """The candidate a config describes, with the family's FIXED settings."""
    c = dict(config)
    model = {"logistic": Logistic, "gbm": Boosting, "catboost": CatBoost}[family]
    return model(half_life=c.pop("half_life"), refs=c.pop("refs"), params={**c, **FIXED[family]}, name=family)


def best(search):
    """The winner per family and horizon (Decision 12): the highest CHOOSE F1; on a tie, the first config in the seeded
    order (then the shorter window)."""
    s = search.sort_values(["family", "hours", "config", "window"], kind="stable")
    return s.loc[s.groupby(["family", "hours"]).f1.idxmax()].set_index(["family", "hours"])


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
        return self.calibrate(pd.concat(held), hours, progress)

    def calibrate(self, raw, hours, progress=False):
        """`raw` (the held rows of `run`) calibrated with this run's window: `scored` and each candidate's calibrated
        forecast, recomputed. The raw forecasts are reused, so another window needs no refit."""
        raw = raw.copy()
        raw["scored"] = raw.block - self.window_length >= raw.ts.min()
        for c in self.candidates:
            raw[c.name] = np.nan
        for s, part in raw[raw.scored].groupby("block"):
            win = self.window(raw, s, hours)
            for c in self.candidates:
                platt = Platt().fit(win[f"raw_{c.name}"], win[f"y{hours}"])
                raw.loc[part.index, c.name] = platt.predict(part[f"raw_{c.name}"])
                if progress:
                    m = Scores(raw.loc[part.index], hours).classes(c.name, .5).loc["all"]
                    print(f"H={hours} block={s} {c.name}: n={int(m.n)} base={m.base_rate:.3f} mean_p={m.mean_p:.3f} "
                          f"brier={Scores(raw.loc[part.index], hours).brier(c.name):.4f} ap={m.ap:.3f} auc={m.auc:.3f}",
                          flush=True)
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
