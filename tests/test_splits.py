import pandas as pd

from alerts.splits import Split

T = lambda s: pd.Timestamp(s, tz="UTC")
SPLIT = Split(T("2026-08-01 00:00"), T("2026-08-29 00:00"), T("2026-09-13 00:00"), T("2026-10-10 00:00"))
ROWS = pd.DataFrame({"ts": pd.date_range("2026-08-28 20:00", "2026-08-29 01:00", freq="30min", tz="UTC")})


def times(part, hours):
    return [f"{t:%H:%M}" for t in SPLIT.rows(ROWS, part, hours).ts]


def test_purge_drops_rows_whose_label_window_crosses_into_val():
    assert times("train", 1)[-1] == "23:00"  # 23:00 + 1 h = 00:00: the label window ends inside train
    assert "23:30" not in times("train", 1) + times("val", 1)  # 23:30 + 1 h crosses midnight: in no part
    assert times("train", 3)[-1] == "21:00"  # 23:00 + 3 h crosses too
    assert times("val", 1)[0] == "00:00"


def test_no_row_is_in_two_parts():
    for hours in (1, 3, 6):
        train, val, test = (set(SPLIT.rows(ROWS, p, hours).ts) for p in ("train", "val", "test"))
        assert not (train & val or val & test or train & test)
