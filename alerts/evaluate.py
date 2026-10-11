"""Forecast losses and uncertainty: a bootstrap resamples whole Kyiv calendar days, never individual rows."""
import numpy as np
import pandas as pd


class Scores:
    def __init__(self, rows, hours):
        self.rows, self.hours = rows, hours
        self.y = rows[f'y{hours}']
        if rows.empty or self.y.isna().any() or not self.y.isin([0, 1]).all():
            raise ValueError('scores require nonempty rows with mature binary labels')

    def loss(self, col):
        p = self.rows[col]
        if not p.between(0, 1).all():
            raise ValueError(f'{col}: forecasts must be finite probabilities')
        return (self.y - p) ** 2

    def brier(self, col):
        return float(self.loss(col).mean())

    def skill(self, col, ref):
        """(point, lower, upper) for 1 - Brier / Brier_ref; 1,000 day-block resamples, seed 0."""
        days = self.rows.ts.dt.tz_convert('Europe/Kyiv').dt.date
        g = pd.DataFrame({'day': days, 'a': self.loss(col), 'b': self.loss(ref)}).groupby('day').sum()
        if g.b.sum() == 0:
            return (np.nan, np.nan, np.nan)  # skill relative to a perfect reference is undefined
        rng = np.random.default_rng(0)
        idx = rng.integers(0, len(g), (1000, len(g)))
        a, b = g.a.to_numpy()[idx].sum(1), g.b.to_numpy()[idx].sum(1)
        # A zero-loss reference in any sampled period makes the interval undefined, not a win.
        if (b == 0).any():
            return (float(1 - g.a.sum() / g.b.sum()), np.nan, np.nan)
        lo, hi = np.percentile(1 - a / b, [2.5, 97.5])
        return float(1 - g.a.sum() / g.b.sum()), float(lo), float(hi)

    def per_oblast(self, col):
        out = []
        for obl, part in self.rows.groupby('obl'):
            score = Scores(part, self.hours)
            b = score.brier(col)
            refs = [score.brier(f'{name}_{self.hours}') for name in ('clim28', 'recent7')]
            out.append(dict(obl=obl, n=len(part), base_rate=float(score.y.mean()), brier=b,
                            skill_clim28=1 - b / refs[0] if refs[0] else np.nan,
                            skill_recent7=1 - b / refs[1] if refs[1] else np.nan,
                            quality='quality not verified' if len(part) < 100 else 'n >= 100; pooled CI only'))
        return pd.DataFrame(out).set_index('obl')

    def reliability(self, col):
        self.loss(col)  # validate probabilities before assigning bins
        bins = np.minimum((self.rows[col] * 10).astype(int), 9)
        return pd.DataFrame({'bin': bins, 'forecast': self.rows[col], 'observed': self.y}).groupby('bin').agg(
            n=('observed', 'size'), forecast=('forecast', 'mean'), observed=('observed', 'mean'))

    def error_correlation(self, cols):
        for col in cols:
            self.loss(col)
        return self.rows[cols].rsub(self.y, axis=0).corr()


def bar(skills):
    """The registered bar: both lower CI bounds > 0 on at least two of the three horizons."""
    passed = {h: all(np.isfinite(skills[h][ref][1]) and skills[h][ref][1] > 0
                     for ref in ('clim28', 'recent7')) for h in (1, 3, 6)}
    return passed, sum(passed.values()) >= 2
