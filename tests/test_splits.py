import pandas as pd

from alert_outlook.forecasting.splits import Split

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


# two oblasts at every half hour from 00:00 to 02:30
TWO = pd.DataFrame({"obl": [8, 27] * 6,
                    "ts": pd.date_range("2026-08-29 00:00", periods=6, freq="30min", tz="UTC").repeat(2)})


def test_forward_checks_fit_each_block_on_what_was_known_at_its_start():
    folds = list(SPLIT.forward(TWO, 1, T("2026-08-29 01:00"), T("2026-08-29 03:00"), 2))
    hhmm = lambda r: sorted({f"{t:%H:%M}" for t in r.ts})
    assert [hhmm(fit) for fit, _ in folds] == [["00:00"], ["00:00", "00:30", "01:00"]]  # T + 1 h <= block start
    assert [hhmm(held) for _, held in folds] == [["01:00", "01:30"], ["02:00"]]  # 02:30 + 1 h is past 03:00
    assert all((held.groupby("ts").obl.nunique() == 2).all() for _, held in folds)  # a moment is never split
