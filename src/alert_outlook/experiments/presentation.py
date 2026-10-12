"""Assemble offline inputs for the pure page renderer."""
import pandas as pd
from mlflow.exceptions import MlflowException
from alert_outlook.data import history as D
from alert_outlook.experiments.prediction import load_models
from alert_outlook.experiments.tracking import Tracking, digest
from alert_outlook.presentation.history import analytics
from alert_outlook.presentation.page import render


def page(paths):
    if not paths.predictions.exists(): raise ValueError('no forecast log; run predict first')
    _, asof = D.saved(paths)
    models = load_models(paths)
    logged = pd.read_csv(paths.predictions, parse_dates=['ts','made_at'])
    parts = []
    for family in models:
        part = logged[(logged.model == family) & (logged.model_sha256 == digest(paths.models / f'{family}.joblib'))
                      & (logged.ts == asof)]
        if len(part) != 24: raise ValueError(f'{family}: current data or weights lack a complete log; run predict first')
        parts.append(part)
    rows = pd.concat(parts, ignore_index=True)
    quality, scores = None, None
    if (paths.tracking / 'tracking.db').exists():
        tracking = Tracking(paths)
        model = next(iter(models.values()))
        source_id = model.meta.get('generation', model.meta.get('migration', {}).get('archive_run_id'))
        try:
            source = tracking.client.get_run(source_id)
        except MlflowException as error:
            if error.error_code != 'RESOURCE_DOES_NOT_EXIST': raise
        else:
            summary = tracking.read_json(source_id, source.data.tags['summary_artifact'])
            quality = pd.DataFrame(summary.get('pooled', []))
        last = next(tracking.completed('score'), None)
        if last: scores = tracking.read_table(last.info.run_id, 'scores.csv')
    html = render(rows, D.names(paths), analytics(paths), quality, scores)
    paths.artifacts.mkdir(parents=True, exist_ok=True)
    out = paths.artifacts / 'outlook.html'
    # Avoid leaving a partially rendered page after an interrupted write.
    import os
    import tempfile
    with tempfile.NamedTemporaryFile(dir=out.parent, delete=False) as tmp:
        staged = __import__('pathlib').Path(tmp.name)
    try:
        staged.write_text(html)
        os.replace(staged, out)
    finally:
        staged.unlink(missing_ok=True)
    return out
