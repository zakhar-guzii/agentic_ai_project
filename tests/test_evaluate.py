import numpy as np
import pandas as pd
import pytest

from alerts.evaluate import Scores


def test_skill_bootstraps_whole_kyiv_days_with_their_row_counts():
    # Kyiv day 1: loss .75 / reference .5 -> skill -.5; day 2: .25 / .5 -> +.5.
    # The 21:30 UTC row is in the NEXT Kyiv day, even though the UTC date is the same.
    rows = pd.DataFrame({'ts': pd.to_datetime(['2026-09-01 19:00Z', '2026-09-01 20:00Z',
                                             '2026-09-01 20:30Z', '2026-09-01 21:30Z']),
                         'obl': 8, 'y1': 0., 'model': .5, 'ref': [.5, .5, 0., np.sqrt(.5)]})
    score = Scores(rows, 1)
    assert score.brier('model') == .25
    assert score.skill('model', 'ref') == pytest.approx((0., -.5, .5))


def test_per_oblast_flags_99_rows_but_not_100():
    rows = pd.DataFrame({'ts': pd.date_range('2026-09-01', periods=199, freq='30min', tz='UTC'),
                         'obl': [8] * 99 + [5] * 100, 'y1': 0., 'model': .5,
                         'clim28_1': .5, 'recent7_1': .5})
    out = Scores(rows, 1).per_oblast('model')
    assert out.loc[8, ['n', 'quality']].tolist() == [99, 'quality not verified']
    assert out.loc[5, ['n', 'quality']].tolist() == [100, 'n >= 100; pooled CI only']
    assert out.loc[8, ['base_rate', 'brier', 'skill_clim28', 'skill_recent7']].tolist() == [0., .25, 0., 0.]


def test_bar_requires_both_references_on_at_least_two_horizons():
    from alerts.evaluate import bar
    skills = {h: {'clim28': (.1, .01, .2), 'recent7': (.1, .01, .2)} for h in (1, 3, 6)}
    skills[6]['clim28'] = (.1, 0., .2)  # strictly positive, not >= 0
    assert bar(skills) == ({1: True, 3: True, 6: False}, True)
    skills[3]['recent7'] = (.1, -.01, .2)
    assert bar(skills) == ({1: True, 3: False, 6: False}, False)
    skills[1]['recent7'] = (.1, np.nan, np.nan)
    assert bar(skills) == ({1: False, 3: False, 6: False}, False)


def test_reliability_includes_probability_one_and_errors_use_the_same_rows():
    rows = pd.DataFrame({'ts': pd.date_range('2026-09-01', periods=4, freq='30min', tz='UTC'),
                         'obl': 8, 'y1': [0, 1, 0, 1], 'model': [0., 1., .25, .75], 'other': .5})
    score = Scores(rows, 1)
    rel = score.reliability('model')
    assert rel.n.sum() == 4 and rel.loc[9, ['n', 'forecast', 'observed']].tolist() == [1., 1., 1.]
    assert rel.loc[2, ['n', 'forecast', 'observed']].tolist() == [1., .25, 0.]
    assert score.error_correlation(['model', 'other']).loc['model', 'other'] == pytest.approx(np.sqrt(.5))
