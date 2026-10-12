import pandas as pd
import pytest
from alert_outlook.experiments.evaluation import report


def test_evaluation_uses_choose_threshold_and_scores_frozen_rows():
    rows = pd.DataFrame(dict(obl=[14,14], ts=pd.to_datetime(['2026-09-20T00:00Z','2026-09-20T00:30Z']),
        hours=[1,1], model=['logistic']*2, period=['benchmark']*2,
        y=[0,1], prediction=[.2,.8], clim28=[.5,.5], recent7=[.5,.5]))
    result = report(rows, [dict(family='logistic',hours=1,threshold=.5)], 'benchmark')
    metric = result['pooled'][0]
    assert metric['threshold'] == .5 and metric['f1'] == 1
    assert metric['brier'] == pytest.approx(.04)
    assert metric['skill_clim28'] == pytest.approx(.84)
    assert metric['skill_clim28_low'] == pytest.approx(.84)
    assert result['regions'][0]['quality'] == 'quality not verified'
