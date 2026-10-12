import numpy as np
import pandas as pd
import pytest

from alert_outlook.data.validation import AdversarialValidation

COLUMNS = ["a", "b", "c", "d"]
DAYS = lambda start, n: pd.date_range(start, periods=n, freq="D", tz="UTC")


def test_folds_hold_a_time_block_of_each_set_and_fit_nothing_within_a_week_of_it():
    a, b = pd.DataFrame({"ts": DAYS("2026-01-01", 40)}), pd.DataFrame({"ts": DAYS("2026-03-01", 20)})
    ts = pd.concat([a.ts, b.ts], ignore_index=True)
    folds = list(AdversarialValidation(COLUMNS).folds(a, b))
    assert len(folds) == 4 and (sum(held.astype(int) for _, held in folds) == 1).all()  # every row held once
    for fit, held in folds:
        assert held[:40].any() and held[40:].any()  # both sets in every fold
        assert np.abs(ts[fit].to_numpy()[:, None] - ts[held].to_numpy()[None, :]).min() >= pd.Timedelta("7D")
    fit, held = folds[1]  # a's second block (11-20 January) and b's (6-10 March)
    days = lambda mask: [f"{t:%m-%d}" for t in ts[mask]]
    assert days(held) == [f"01-{d}" for d in range(11, 21)] + [f"03-{d:02d}" for d in range(6, 11)]
    assert days(fit) == [f"01-{d:02d}" for d in range(1, 5)] + [f"01-{d}" for d in range(27, 32)] + \
        [f"02-{d:02d}" for d in range(1, 10)] + [f"03-{d}" for d in range(17, 21)]  # 7 days clear of both blocks



def test_a_held_row_is_never_fitted_even_with_no_gap():
    a, b = pd.DataFrame({"ts": DAYS("2026-01-01", 40)}), pd.DataFrame({"ts": DAYS("2026-03-01", 20)})
    for fit, held in AdversarialValidation(COLUMNS, gap=pd.Timedelta(0)).folds(a, b):
        assert not (fit & held).any() and (fit | held).all()  # with no gap, the fit is every row not held

def sample(seed, start, shift=0.0):
    """4 000 rows every 30 min from `start` (83 days) of four independent N(0, 1) features; `shift` moves "b"."""
    x = pd.DataFrame(np.random.default_rng(seed).normal(size=(4000, 4)), columns=COLUMNS)
    return x.assign(b=x.b + shift, ts=pd.date_range(start, periods=4000, freq="30min", tz="UTC"))


def test_two_samples_of_one_distribution_cannot_be_told_apart():
    aucs, _ = AdversarialValidation(COLUMNS).run(sample(1, "2026-01-01"), sample(2, "2026-04-01"))
    assert len(aucs) == 4 and abs(aucs.mean() - 0.5) < 0.05


def test_a_shifted_feature_is_found():
    aucs, importance = AdversarialValidation(COLUMNS).run(sample(1, "2026-01-01"), sample(2, "2026-04-01", shift=1.0))
    assert aucs.mean() > 0.7  # the best possible is Phi(1 / sqrt 2) = 0.76
    assert importance.index[0] == "b"


def test_sets_too_short_for_the_gap_are_refused():
    short = sample(2, "2026-04-01").iloc[:720]  # 15 days, like val: a held block leaves under 1 000 rows outside the gap
    with pytest.raises(ValueError, match="too short"):
        AdversarialValidation(COLUMNS).run(sample(1, "2026-01-01"), short)
