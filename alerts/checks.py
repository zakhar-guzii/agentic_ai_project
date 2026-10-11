"""Checks on the forecast set-up: leakage (TruncationCheck)."""


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
