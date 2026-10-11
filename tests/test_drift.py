import numpy as np
import pandas as pd

from alerts.checks import AdversarialValidation

COLUMNS = ["a", "b", "c", "d"]


def sample(seed, shift=0.0):
    """2 000 rows of four independent N(0, 1) features; `shift` moves feature "b"."""
    x = pd.DataFrame(np.random.default_rng(seed).normal(size=(2000, 4)), columns=COLUMNS)
    return x.assign(b=x.b + shift)


def test_two_samples_of_one_distribution_cannot_be_told_apart():
    auc, _ = AdversarialValidation(COLUMNS).run(sample(1), sample(2))
    assert abs(auc - 0.5) < 0.05


def test_a_shifted_feature_is_found():
    auc, importance = AdversarialValidation(COLUMNS).run(sample(1), sample(2, shift=1.0))
    assert auc > 0.7  # the best possible is Phi(1 / sqrt 2) = 0.76
    assert importance.index[0] == "b"
