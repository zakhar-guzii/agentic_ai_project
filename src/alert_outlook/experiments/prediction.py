"""Versioned offline predictions and scoring, with trusted model snapshots in MLflow."""
import logging
import re
from pathlib import Path
import tempfile

import pandas as pd

from alert_outlook.data import history as D
from alert_outlook.forecasting import live
from alert_outlook.forecasting.model import Forecaster
from alert_outlook.settings import FAMILIES
from alert_outlook.experiments.tracking import Tracking, digest

logger = logging.getLogger(__name__)


def load_models(paths):
    models = {family: Forecaster.load(paths.models / f'{family}.joblib') for family in FAMILIES}
    generations = {m.meta.get('generation', m.meta.get('migration', {}).get('archive_run_id')) for m in models.values()}
    if None in generations or len(generations) != 1:
        raise ValueError('active models are not one complete generation; restore all three files together')
    return models


def predict(paths):
    records, asof = D.saved(paths)
    made = pd.Timestamp.now(tz='UTC').floor('s')
    models = load_models(paths)
    parts = [live.forecast(records, asof, model).assign(model=family, made_at=made,
                model_sha256=digest(paths.models / f'{family}.joblib')) for family, model in models.items()]
    rows = pd.concat(parts, ignore_index=True)
    keys = ['obl', 'ts', 'model', 'model_sha256']
    if paths.predictions.exists():
        previous = pd.read_csv(paths.predictions, parse_dates=['ts'])
        pending = rows[~pd.MultiIndex.from_frame(rows[keys]).isin(pd.MultiIndex.from_frame(previous[keys]))]
        if pending.empty:
            # Preserve the original made_at shown on the page.
            selected = previous[pd.MultiIndex.from_frame(previous[keys]).isin(pd.MultiIndex.from_frame(rows[keys]))]
            return selected, False
    tracking = Tracking(paths)
    with tracking.run('predict', {'asof': str(asof), **{f'sha256/{f}': parts[i].model_sha256.iloc[0]
                          for i, f in enumerate(FAMILIES)}}) as run_id:
        for family in FAMILIES: tracking.artifact(run_id, paths.models / f'{family}.joblib', 'models')
        tracking.table(run_id, rows, 'forecasts.csv.gz')
        tracking.metrics(run_id, {'regions': 24, 'models': 3})
    appended = live.log(rows, paths.predictions)
    logger.info('saved predictions', extra=dict(stage='predict', rows=len(rows), run_id=run_id, asof=str(asof)))
    return rows, appended


def model_version(paths, family, sha256, tracking):
    if family not in FAMILIES or not isinstance(sha256,str) or not re.fullmatch(r'[0-9a-f]{64}',sha256):
        raise ValueError('invalid model identity in the forecast log')
    file = paths.models / f'{family}.joblib'
    if file.exists() and digest(file) == sha256: return Forecaster.load(file)
    for run in tracking.completed('predict', {f'sha256/{family}': sha256}):
        with tempfile.TemporaryDirectory() as tmp:
            saved = Path(tracking.client.download_artifacts(run.info.run_id, f'models/{family}.joblib', tmp))
            if digest(saved) != sha256: raise RuntimeError('saved model snapshot checksum differs')
            return Forecaster.load(saved)
    raise ValueError(f'no trusted weights for {family} version {sha256}; restore its MLflow snapshot')


def score(paths):
    if not paths.predictions.exists(): raise ValueError('no forecast log; run predict first')
    records, asof = D.saved(paths)
    logged = pd.read_csv(paths.predictions, parse_dates=['ts', 'made_at'])
    tracking = Tracking(paths)
    tables, scored_rows = [], []
    for (family, sha256), part in logged.groupby(['model', 'model_sha256'], sort=False):
        model = model_version(paths, family, sha256, tracking)
        scored = live.score(part, records, asof, model)
        scored_rows.append(scored)
        result = live.summary(scored)
        if not result.empty:
            tables.append(result.rename(columns={'model':'model_brier'}).reset_index().assign(
                model=family, model_sha256=sha256))
    result = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()
    with tracking.run('score', {'asof': str(asof)}) as run_id:
        tracking.table(run_id, pd.concat(scored_rows, ignore_index=True), 'scored_forecasts.csv.gz')
        tracking.table(run_id, result, 'scores.csv')
        for row in result.to_dict('records'):
            prefix = f"{row['model']}/{row['model_sha256']}/{row['forecast']}/h{row['hours']}"
            tracking.metrics(run_id, {f'{prefix}/{k}': v for k, v in row.items() if isinstance(v, (int, float))})
    return result
