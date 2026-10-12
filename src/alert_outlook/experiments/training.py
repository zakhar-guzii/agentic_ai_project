"""CHOOSE-only search and forward training; experiments are explicit MLflow runs."""
import json
import logging
import os
from pathlib import Path
import shutil
import tempfile
import time

import numpy as np
import pandas as pd

from alert_outlook.data import history as D
from alert_outlook.forecasting.baselines import Climatology, RecentLevel
from alert_outlook.forecasting.features import ForecastTable, HOURS
from alert_outlook.forecasting.evaluation import Scores
from alert_outlook.forecasting.model import WINDOWS, Forecaster, ForwardRun, best, candidate, configs
from alert_outlook.forecasting.splits import BENCHMARK, CHOOSE, DECISION
from alert_outlook.settings import FAMILIES
from alert_outlook.experiments.tracking import Tracking, digest, fingerprint

logger = logging.getLogger(__name__)


def rows_at(paths, end):
    records, _ = D.saved(paths)
    start = (DECISION.bounds['train'][0] - pd.Timedelta('29D')).tz_convert('Europe/Kyiv').normalize().tz_convert('UTC')
    rows = ForecastTable(records, start, end).rows
    return rows.join(Climatology(28).predict(rows)).join(RecentLevel().predict(rows))


def searches(paths, tracking, family):
    identity = fingerprint(paths, {'search': family, 'seed': 0})
    runs = list(tracking.completed('tune', {'family': family, 'fingerprint': identity}))
    parts = [tracking.read_table(run.info.run_id, 'search.csv') for run in runs]
    return pd.concat(parts, ignore_index=True).drop_duplicates(['family', 'config', 'hours', 'window']) if parts else pd.DataFrame()


def tune(paths, family, minutes=45):
    if family not in FAMILIES or not np.isfinite(minutes) or minutes <= 0:
        raise ValueError('choose a supported family and a positive time limit')
    tracking = Tracking(paths)
    identity = fingerprint(paths, {'search': family, 'seed': 0})
    previous = searches(paths, tracking, family)
    done = set(previous.config) if not previous.empty else set()
    stop = time.monotonic() + 60 * minutes
    pending = [(i, config) for i, config in enumerate(configs(family)) if i not in done]
    if not pending: return 0
    rows = rows_at(paths, CHOOSE[1])
    completed = 0
    for i, config in pending:
        if time.monotonic() >= stop: break
        began, found = time.monotonic(), []
        with tracking.run('tune', {'family': family, 'config': str(i), 'fingerprint': identity}, config) as run_id:
            for h in HOURS:
                c = candidate(family, config)
                raw = ForwardRun([c], window=pd.Timedelta(days=max(WINDOWS))).run(rows, h, [CHOOSE], progress=True)
                first = raw[raw.scored].block.min()
                for w in WINDOWS:
                    cal = ForwardRun([c], window=pd.Timedelta(days=w)).calibrate(raw, h)
                    score = Scores(cal[cal.block >= first], h)
                    threshold = score.threshold(c.name)
                    m = score.classes(c.name, threshold).loc['all']
                    record = dict(family=family, config=i, hours=h, window=w, threshold=threshold,
                                  brier=score.brier(c.name), params=json.dumps(config), **m.to_dict())
                    found.append(record)
                    tracking.metrics(run_id, {f'h{h}/w{w}/{k}': record[k] for k in
                        ('threshold', 'f1', 'precision', 'recall', 'ap', 'auc', 'brier', 'n')})
            tracking.table(run_id, pd.DataFrame(found), 'search.csv')
        completed += 1
        logger.info('completed configuration', extra=dict(stage='tune', model=family, config=i,
                    duration=time.monotonic() - began, run_id=run_id))
    return completed


def activate(paths, staged):
    """Replace a complete generation, rolling back all files on an ordinary write failure."""
    paths.models.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=paths.models.parent) as tmp:
        backup = Path(tmp)
        existing = set()
        for family in FAMILIES:
            target = paths.models / f'{family}.joblib'
            if target.exists():
                shutil.copyfile(target, backup / target.name)
                existing.add(family)
        replaced = []
        try:
            for family in FAMILIES:
                os.replace(Path(staged) / f'{family}.joblib', paths.models / f'{family}.joblib')
                replaced.append(family)
        except BaseException:
            for family in replaced:
                target = paths.models / f'{family}.joblib'
                if family in existing: os.replace(backup / target.name, target)
                else: target.unlink(missing_ok=True)
            raise


def train(paths):
    tracking = Tracking(paths)
    tables = [searches(paths, tracking, family) for family in FAMILIES]
    if any(t.empty for t in tables):
        raise ValueError('completed CHOOSE searches for all three families are required; run tune first')
    winners = best(pd.concat(tables, ignore_index=True))
    _, end = D.saved(paths)
    rows = rows_at(paths, end)
    forecasts, finals = [], {}
    paths.artifacts.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=paths.artifacts) as tmp:
        staged = Path(tmp)
        with tracking.run('train', {'evaluation_source': 'true', 'forecasts_artifact': 'forecasts.csv.gz',
                'summary_artifact': 'summary.json', 'fingerprint': fingerprint(paths, {'train': str(end)})}) as run_id:
            for family in FAMILIES:
                models, calibrators, horizons = {}, {}, {}
                for h in HOURS:
                    w = winners.loc[(family, h)]
                    config = json.loads(w.params)
                    c = candidate(family, config)
                    window = pd.Timedelta(days=int(w.window))
                    forward = ForwardRun([c], window=window)
                    ranges = [CHOOSE, BENCHMARK]
                    if end > D.MAP_CUTOFF: ranges.append((D.MAP_CUTOFF, end, 1))
                    raw = forward.run(rows, h, ranges, progress=True)
                    first = sorted(raw[raw.ts < CHOOSE[1]].block.unique())[2]
                    held = raw[raw.scored & (raw.block >= first)]
                    chosen = Scores(held[held.ts < CHOOSE[1]], h)
                    if abs(chosen.threshold(family) - w.threshold) > 1e-12 or abs(
                            chosen.classes(family, w.threshold).loc['all'].f1 - w.f1) > 1e-9:
                        raise ValueError(f'{family} h{h}: CHOOSE search is not reproduced')
                    part = held[['obl', 'ts', f'y{h}', family, f'clim28_{h}', f'recent7_{h}']].rename(
                        columns={f'y{h}': 'y', family: 'prediction', f'clim28_{h}': 'clim28', f'recent7_{h}': 'recent7'})
                    part = part.assign(hours=h, model=family, period=np.select(
                        [part.ts < CHOOSE[1], part.ts < D.MAP_CUTOFF], ['choose', 'benchmark'], default='holdout'))
                    forecasts.append(part)
                    final = forward.final(rows, {h: raw}, end)[family]
                    models[h], calibrators[h] = final.models[h], final.calibrators[h]
                    horizons[h] = dict(config=config, window_days=int(w.window), threshold=float(w.threshold),
                        choose_f1=float(w.f1), counts=final.meta['counts'][h], columns=list(final.models[h].columns))
                model = Forecaster(models, calibrators, dict(name=family, asof=end, horizons=horizons,
                    train_start=final.meta['train_start'], versions=final.meta['versions'],
                    git_commit=final.meta['git_commit'], generation=run_id))
                file = staged / f'{family}.joblib'
                model.save(file)
                loaded = Forecaster.load(file)
                sample = rows.tail(24)
                if not np.allclose(model.predict(sample), loaded.predict(sample), rtol=0, atol=1e-12):
                    raise RuntimeError(f'{family}: saved model predictions differ')
                tracking.artifact(run_id, file, 'models')
                finals[family] = digest(file)
            long = pd.concat(forecasts, ignore_index=True)
            from alert_outlook.experiments.evaluation import report
            pooled, regions, reliability, correlations = [], [], [], {}
            for period in ('choose', 'benchmark', 'holdout'):
                if not (long.period == period).any(): continue
                result = report(long, winners.reset_index().to_dict('records'), period)
                pooled.extend(result['pooled']); regions.extend(result['regions']); reliability.extend(result['reliability'])
                correlations[period] = result['error_correlations']
            tracking.table(run_id, long, 'forecasts.csv.gz')
            tracking.table(run_id, pd.DataFrame(regions), 'regions.csv')
            tracking.table(run_id, pd.DataFrame(reliability), 'reliability.csv')
            tracking.json(run_id, correlations, 'error_correlations.json')
            summary = dict(end=end, winners=winners.reset_index().to_dict('records'), pooled=pooled,
                           model_sha256=finals, historical_periods=['benchmark', 'holdout'])
            tracking.json(run_id, summary, 'summary.json')
            from alert_outlook.experiments.evaluation import log_pooled
            log_pooled(tracking, run_id, pooled)
        # MLflow has finished successfully before active weights change.
        activate(paths, staged)
    return run_id
