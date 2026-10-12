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


CLASSES = pd.DataFrame({'ts': pd.date_range('2026-09-01', periods=6, freq='30min', tz='UTC'),
                        'obl': [8, 8, 8, 8, 5, 5], 'y1': [1., 0., 1., 0., 0., 0.],
                        'model': [.9, .6, .4, .1, .2, .7]})


def test_classes_counts_each_region_and_all_at_the_threshold():
    # Volyn at .5: yes for .9 (hit) and .6 (false alarm), no for .4 (miss) -> P = R = F1 = 1/2.
    # AP: recall 1/2 at precision 1, then 1 at 2/3 -> 5/6. AUC: 3 of the 4 (start, no start) pairs ranked right.
    out = Scores(CLASSES, 1).classes('model', .5)
    assert out.loc[8].to_dict() == pytest.approx(dict(n=4, pos=2, base_rate=.5, mean_p=.5, precision=.5, recall=.5,
                                                      f1=.5, f1_always=2 / 3, ap=5 / 6, auc=.75))
    # Rivne has no start: one false alarm, F1 0, and no ranking to score
    assert out.loc[5, ['pos', 'precision', 'recall', 'f1', 'f1_always']].tolist() == [0, 0, 0, 0, 0]
    assert out.loc[5, ['ap', 'auc']].isna().all()
    # all six: 1 hit, 2 false alarms, 1 miss; AP 1/2 * 1 + 1/2 * 2/4; AUC 6 of 8 pairs
    assert out.loc['all', ['precision', 'recall', 'f1', 'f1_always', 'ap', 'auc']].tolist() == pytest.approx(
        [1 / 3, .5, .4, .5, .75, .75])


def test_threshold_maximises_f1_on_the_grid():
    # Volyn: t <= .1 F1 2/3; .1 < t <= .4 F1 4/5 (2 hits, 1 false alarm); .4 < t <= .6 1/2; .6 < t <= .9 2/3.
    assert Scores(CLASSES[CLASSES.obl == 8], 1).threshold('model') == pytest.approx(.11)
