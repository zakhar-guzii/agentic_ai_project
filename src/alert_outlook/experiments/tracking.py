"""Explicit MLflow runs, metrics and artifacts in the project's local store."""
from contextlib import contextmanager
import hashlib
import json
import math
import logging
import time
from pathlib import Path
import subprocess
import tempfile

from mlflow import MlflowClient
import numpy as np
import pandas as pd

from alert_outlook.settings import Paths


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_commit(paths):
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=paths.root, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else 'unknown'


def fingerprint(paths, settings):
    """Resume only identical data, algorithms and search settings."""
    code = Path(__file__).resolve().parents[1]
    files = [*sorted(p for p in paths.raw.rglob('*') if p.is_file()),
             *sorted(code.joinpath('forecasting').glob('*.py')),
             *sorted(code.joinpath('data').glob('*.py')), Path(__file__).with_name('training.py')]
    hashes = [('data/' + str(p.relative_to(paths.raw)) if p.is_relative_to(paths.raw)
               else 'code/' + str(p.relative_to(code)), digest(p)) for p in files if p.exists()]
    import importlib.metadata
    versions = {name: importlib.metadata.version(name) for name in
                ('numpy','pandas','scipy','scikit-learn','lightgbm','catboost','joblib')}
    return hashlib.sha256(json.dumps([settings, hashes, versions], sort_keys=True).encode()).hexdigest()



def json_value(value):
    if isinstance(value, dict): return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [json_value(v) for v in value]
    if isinstance(value, (np.integer, np.floating)): value = value.item()
    if isinstance(value, float) and not math.isfinite(value): return None
    if isinstance(value, (pd.Timestamp, Path)): return str(value)
    return value


class Tracking:
    def __init__(self, paths=None):
        self.paths = paths or Paths()
        self.paths.tracking.mkdir(parents=True, exist_ok=True)
        self.client = MlflowClient(tracking_uri=self.paths.tracking_uri)
        experiment = self.client.get_experiment_by_name('alert-outlook')
        self.experiment_id = experiment.experiment_id if experiment else self.client.create_experiment(
            'alert-outlook', artifact_location=(self.paths.tracking / 'artifacts').as_uri())

    @contextmanager
    def run(self, stage, tags=None, params=None):
        run = self.client.create_run(self.experiment_id, run_name=stage, tags={
            'stage': stage, 'source_commit': source_commit(self.paths), **(tags or {})})
        run_id = run.info.run_id
        began = time.monotonic()
        logger = logging.getLogger(__name__)
        context = dict(stage=stage, run_id=run_id)
        if tags and 'family' in tags: context['model'] = tags['family']
        logger.info('started MLflow run', extra=context)
        try:
            for key, value in (params or {}).items():
                self.client.log_param(run_id, key, json.dumps(json_value(value), sort_keys=True))
            yield run_id
            self.client.set_tag(run_id, 'complete', 'true')
            self.client.set_terminated(run_id, 'FINISHED')
            logger.info('completed MLflow run', extra=dict(**context, duration=time.monotonic()-began))
        except BaseException:
            self.client.set_terminated(run_id, 'FAILED')
            raise

    def metrics(self, run_id, values):
        from mlflow.entities import Metric
        import time
        metrics = [Metric(k, float(v), int(time.time() * 1000), 0) for k, v in values.items()
                   if v is not None and math.isfinite(float(v))]
        for start in range(0, len(metrics), 500):
            self.client.log_batch(run_id, metrics=metrics[start:start + 500])

    def artifact(self, run_id, path, directory=None):
        self.client.log_artifact(run_id, str(path), artifact_path=directory)

    def json(self, run_id, value, name):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / Path(name).name
            file.write_text(json.dumps(json_value(value), indent=2) + '\n')
            self.artifact(run_id, file, str(Path(name).parent) if '/' in name else None)

    def table(self, run_id, table, name):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / Path(name).name
            table.to_csv(file, index=False, compression='gzip' if name.endswith('.gz') else None)
            self.artifact(run_id, file, str(Path(name).parent) if '/' in name else None)

    def read_json(self, run_id, name):
        with tempfile.TemporaryDirectory() as tmp:
            file = self.client.download_artifacts(run_id, name, tmp)
            return json.loads(Path(file).read_text())

    def read_table(self, run_id, name):
        with tempfile.TemporaryDirectory() as tmp:
            file = self.client.download_artifacts(run_id, name, tmp)
            try:
                table = pd.read_csv(file)
            except pd.errors.EmptyDataError:
                return pd.DataFrame()
        for column in ('ts', 'block', 'made_at'):
            if column in table: table[column] = pd.to_datetime(table[column], utc=True)
        return table

    def completed(self, stage, tags=None):
        # Filter tag values in Python: callers never interpolate untrusted values into MLflow queries.
        found = self.client.search_runs([self.experiment_id],
            filter_string=f"attributes.status = 'FINISHED' AND tags.stage = '{stage}' AND tags.complete = 'true'",
            order_by=['attributes.start_time DESC'], max_results=1000)
        while True:
            for run in found:
                if all(run.data.tags.get(k) == str(v) for k, v in (tags or {}).items()): yield run
            if not found.token: break
            found = self.client.search_runs([self.experiment_id],
                filter_string=f"attributes.status = 'FINISHED' AND tags.stage = '{stage}' AND tags.complete = 'true'",
                order_by=['attributes.start_time DESC'], max_results=1000, page_token=found.token)
