"""Chronological train / val / test parts of the forecast rows, purged so that no label window crosses a boundary,
and sequential (forward) checks inside them."""
import numpy as np
import pandas as pd

from alert_outlook.data.history import MAP_CUTOFF

KYIV_DAY = lambda day: pd.Timestamp(day, tz="Europe/Kyiv").tz_convert("UTC")


class Split:
    """Train, val and test parts over forecast rows (anything with a `ts` column), in time order.

    A row at T with horizon H belongs to a part [a, b) only if a <= T and T + H <= b: its label window closes
    inside the part, so a model is never fitted on outcomes from a later part (the purge). Rows whose window
    crosses a boundary belong to no part.
    """

    def __init__(self, train_start, val_start, test_start, test_end):
        self.bounds = {"train": (train_start, val_start), "val": (val_start, test_start), "test": (test_start, test_end)}

    def rows(self, table_rows, part, hours):
        """The rows of `part` ("train", "val" or "test") for the horizon `hours`."""
        a, b = self.bounds[part]
        ts = table_rows.ts
        return table_rows[(ts >= a) & (ts + pd.Timedelta(hours=hours) <= b)]

    def forward(self, table_rows, hours, a, b, blocks):
        """Sequential checks over [a, b), in time order: train on the past, score the next block.

        The unique moments T in [a, b) are cut into `blocks` consecutive blocks, so all oblasts of a moment stay
        together. Each block starting at s yields (fit, held): fit is every row known at s (train start <= T and
        T + H <= s), held is the block's rows with T + H <= b, so no label leaves [a, b). No gap is needed between
        fit and held: past history in the features is what a forecaster at s has, only immature labels are not.

        Step 3 must also keep the calibration in time order (the original forward-calibration contract): a block's calibrator is fitted
        only on out-of-fold forecasts from the 14 days before s with T + H <= s; calibrated models are compared only
        on blocks their calibrator did not see; scores on blocks that chose the model are not independent.
        """
        ts, h = table_rows.ts, pd.Timedelta(hours=hours)
        moments = pd.DatetimeIndex(ts[(ts >= a) & (ts < b)].unique()).sort_values()
        starts = [block[0] for block in np.array_split(moments, blocks)]
        for s, e in zip(starts, starts[1:] + [b]):
            yield (table_rows[(ts >= self.bounds["train"][0]) & (ts + h <= s)],
                   table_rows[(ts >= s) & (ts < e) & (ts + h <= b)])


# Train starts once raion-level alerts had reached every oblast (2025-11-06); val is the 15 days before the window the
# feasibility probe already scored, which is the test part. Test is a historical benchmark, scored once and reported
# as seen; the final check is the untouched holdout after MAP_CUTOFF (step 7).
DECISION = Split(KYIV_DAY("2025-11-15"), KYIV_DAY("2026-08-29"), KYIV_DAY("2026-09-13"), MAP_CUTOFF)

# Step 3's forward checks, as (a, b, blocks): the model is chosen on six weekly blocks before test, the first two of
# which only warm the calibrator up (15 days of val cannot both fit a calibrator and compare calibrated models on
# blocks it did not see); the benchmark is then scored once on four weekly blocks of test.
CHOOSE = (KYIV_DAY("2026-08-02"), DECISION.bounds["test"][0], 6)
BENCHMARK = (DECISION.bounds["test"][0], MAP_CUTOFF, 4)
