"""Chronological train / val / test parts of the forecast rows, purged so that no label window crosses a boundary."""
import pandas as pd

from alerts.data import MAP_CUTOFF

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


# Every step-3 decision is made on this split. Train starts once raion-level alerts had reached every oblast
# (2025-11-06); val is the 15 days before the window the feasibility probe already scored, which is the test part.
DECISION = Split(KYIV_DAY("2025-11-15"), KYIV_DAY("2026-08-29"), KYIV_DAY("2026-09-13"), MAP_CUTOFF)
