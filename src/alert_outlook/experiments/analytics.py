"""Persist data checks and historical analytics as MLflow results."""
import pandas as pd
from alert_outlook.data import history as D
from alert_outlook.data.validation import AdversarialValidation, api_update_lag
from alert_outlook.forecasting.features import Features, ForecastTable
from alert_outlook.forecasting.splits import DECISION
from alert_outlook.experiments.tracking import Tracking
from alert_outlook.presentation.history import analytics


def check(paths):
    regions = paths.raw / 'regions.json'
    m, a = D.load_map(paths.raw / 'map', regions), D.load_api(paths.raw / 'alerts_in_ua', regions)
    h = D.history(m, a)
    mc, ac, hc = (x[x.level.isin(['oblast', 'raion'])] for x in (m, a, h))
    seam = D.compare(mc, ac, D.SPLICE, D.MAP_CUTOFF)
    unmatched = D.unmatched(mc[mc.level == 'raion'], ac[ac.level == 'raion'], D.SPLICE, D.MAP_CUTOFF)
    splice = D.compare(hc, mc, D.SPLICE - pd.Timedelta('12h'), D.SPLICE + pd.Timedelta('12h'))
    corr, mae = D.daily_agreement(mc, ac, D.SPLICE, D.MAP_CUTOFF)
    rows = ForecastTable(h[h.start < D.MAP_CUTOFF], DECISION.bounds['train'][0], D.MAP_CUTOFF).rows
    av = AdversarialValidation(Features.NAMES)
    aucs, importance = av.run(DECISION.rows(rows, 'train', 6), DECISION.rows(rows, 'test', 6))
    metrics = dict(jaccard=seam.loc['all', 'jaccard'], jaccard_seconds=seam.loc['all', 'jaccard_s'],
                   min_region_jaccard=seam.drop('all').jaccard.min(), unmatched_records=len(unmatched),
                   daily_correlation=corr, daily_mae=mae, drift_auc=aucs.mean(),
                   splice_jaccard=splice.loc['all', 'jaccard'],
                   regions_both_sides=len(set(hc[hc.start < D.SPLICE].oblast_id) & set(hc[hc.start >= D.SPLICE].oblast_id)),
                   empty_six_hour_bins=int((hc.set_index('start').resample('6h').size() == 0).sum()))
    tracking = Tracking(paths)
    with tracking.run('check') as run_id:
        tracking.metrics(run_id, metrics)
        lag = api_update_lag(paths.raw / 'alerts_in_ua')
        tracking.metrics(run_id, {f'revision_lag/{k}': v for k,v in lag.items() if isinstance(v,(int,float))})
        tracking.json(run_id, lag, 'revision_lag.json')
        for name, table in [('seam', seam.reset_index()), ('unmatched', unmatched), ('splice', splice.reset_index()),
                            ('importance', importance.rename('importance').rename_axis('feature').reset_index())]:
            tracking.table(run_id, table, f'{name}.csv')
        tracking.json(run_id, {'metrics': metrics, 'drift_folds': aucs.tolist(),
            'cleaning': {'map': m.attrs['cleaning'], 'api': a.attrs['cleaning']}}, 'summary.json')
    return run_id, metrics


def history(paths):
    lo, daily, weekly, per, regional, levels = analytics(paths)
    tracking = Tracking(paths)
    with tracking.run('history', {'start': str(lo), 'end': str(D.MAP_CUTOFF)}) as run_id:
        for name, table in [('daily', daily), ('weekly', weekly.reset_index()), ('regional', regional.reset_index()),
                            ('levels', levels.reset_index())]:
            tracking.table(run_id, table, f'{name}.csv')
        for period, table in per.items():
            tracking.metrics(run_id, {f'{period}/{k}': v for k, v in table.loc['all'].items()})
    return run_id, weekly
