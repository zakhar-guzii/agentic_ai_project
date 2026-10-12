"""Score saved out-of-fold rows; thresholds always come from CHOOSE."""
import pandas as pd

from alert_outlook.forecasting.evaluation import Scores
from alert_outlook.experiments.tracking import Tracking
from alert_outlook.settings import FAMILIES


def normalise(rows):
    if 'prediction' in rows: return rows
    parts = []
    for family in FAMILIES:
        column = 'gbm' if family == 'lightgbm' else family
        parts.append(rows[['obl', 'ts', 'hours', 'period', 'y', column, 'clim28', 'recent7']].rename(
            columns={column: 'prediction'}).assign(model=family))
    return pd.concat(parts, ignore_index=True)


def report(rows, winners, period):
    rows = normalise(rows)
    thresholds = {(r['family'].replace('gbm', 'lightgbm'), int(r['hours'])): float(r['threshold']) for r in winners}
    pooled, regions, reliability, correlations = [], [], [], {}
    for (family, h), part in rows[rows.period == period].groupby(['model', 'hours'], sort=False):
        part = part.rename(columns={'y': f'y{h}', 'clim28': f'clim28_{h}', 'recent7': f'recent7_{h}'})
        score = Scores(part, int(h))
        threshold = thresholds[(family, int(h))]
        row = dict(forecast=family, horizon=int(h), period=period, threshold=threshold,
                   brier=score.brier('prediction'), **score.classes('prediction', threshold).loc['all'].to_dict())
        row['n'], row['pos'] = int(row['n']), int(row['pos'])
        for reference in ('clim28', 'recent7'):
            point, low, high = score.skill('prediction', f'{reference}_{h}')
            row.update({f'skill_{reference}': point, f'skill_{reference}_low': low, f'skill_{reference}_high': high})
        pooled.append(row)
        regional = score.per_oblast('prediction').join(score.classes('prediction', threshold), rsuffix='_classes')
        regional = regional.loc[:, ~regional.columns.str.endswith('_classes')].reset_index().assign(
            model=family, hours=h, period=period, threshold=threshold)
        regions.extend(regional.to_dict('records'))
        reliability.extend(score.reliability('prediction').reset_index().assign(
            model=family, hours=h, period=period).to_dict('records'))
        correlations[f'{family}/h{h}'] = score.error_correlation(
            ['prediction', f'clim28_{h}', f'recent7_{h}']).to_dict()
    if not pooled: raise ValueError(f'no mature saved forecasts for {period}')
    return dict(pooled=pooled, regions=regions, reliability=reliability, error_correlations=correlations)


def log_pooled(tracking, run_id, pooled):
    for row in pooled:
        prefix = f"{row['forecast']}/{row['period']}/h{row['horizon']}"
        tracking.metrics(run_id, {f'{prefix}/{key}': value for key, value in row.items()
                                  if isinstance(value, (int, float))})


def evaluate(paths, source_run_id, period):
    tracking = Tracking(paths)
    source = tracking.client.get_run(source_run_id)
    if source.info.status != 'FINISHED' or source.data.tags.get('evaluation_source') != 'true':
        raise ValueError('evaluation requires a completed train or imported historical run')
    forecasts = tracking.read_table(source_run_id, source.data.tags['forecasts_artifact'])
    summary = tracking.read_json(source_run_id, source.data.tags['summary_artifact'])
    result = report(forecasts, summary['winners'], period)
    with tracking.run('evaluate', {'source_run_id': source_run_id, 'period': period,
            'historical': str(period != 'choose').lower(), 'summary_artifact': 'summary.json'}) as run_id:
        log_pooled(tracking, run_id, result['pooled'])
        tracking.table(run_id, pd.DataFrame(result['regions']), 'regions.csv')
        tracking.table(run_id, pd.DataFrame(result['reliability']), 'reliability.csv')
        tracking.json(run_id, result, 'summary.json')
    return run_id, pd.DataFrame(result['pooled'])
