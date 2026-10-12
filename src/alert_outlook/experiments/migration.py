"""One-time, idempotent import of a trusted pre-redesign snapshot into MLflow."""
import json
from pathlib import Path
import re

import pandas as pd

from alert_outlook.experiments.tracking import Tracking, digest, fingerprint


def numeric_values(value, prefix=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from numeric_values(item, f'{prefix}/{key}' if prefix else str(key))
    elif isinstance(value, list):
        for i, item in enumerate(value): yield from numeric_values(item, f'{prefix}/{i}')
    elif isinstance(value, (int, float)):
        yield re.sub(r'[^\w/ .-]', '_', prefix), value


def import_history(source, paths):
    source = Path(source)
    original = json.loads((source / 'original.json').read_text())
    identity = digest(source / 'original.json')
    tracking = Tracking(paths)
    previous = next(tracking.completed('migration', {'snapshot': identity}), None)
    if previous:
        return previous.info.run_id
    files = [p for p in source.rglob('*') if p.is_file()]
    for p in files:
        key = p.relative_to(source).as_posix()
        if key in original['files'] and digest(p) != original['files'][key]:
            raise ValueError(f'legacy artifact checksum differs: {key}')
    with tracking.run('migration', {'snapshot': identity, 'imported': 'true',
            'source_commit': original['commit'], 'evaluation_source': 'true',
            'forecasts_artifact': 'legacy/results/v2/forecasts.csv.gz',
            'summary_artifact': 'legacy/results/v2/summary.json'}) as run_id:
        checksums = {}
        for p in files:
            key = p.relative_to(source).as_posix()
            tracking.artifact(run_id, p, str(Path('legacy') / p.relative_to(source).parent))
            checksums[key] = digest(p)
            if p.suffix == '.json' and key.startswith('results/'):
                tracking.metrics(run_id, dict(numeric_values(json.loads(p.read_text()), key.removesuffix('.json'))))
        summary = json.loads((source / 'results/v2/summary.json').read_text())
        for row in summary['pooled']:
            name = str(row['forecast']).replace('gbm', 'lightgbm')
            prefix = f"{name}/{row['period']}/h{row['horizon']}"
            tracking.metrics(run_id, {f'{prefix}/{k}': v for k, v in row.items() if isinstance(v, (int, float))})
        tracking.json(run_id, checksums, 'checksums.json')
        # Verify copies, not just the source paths, before allowing cleanup.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tracking.client.download_artifacts(run_id, 'legacy', tmp))
            for key, expected in checksums.items():
                if digest(folder / key) != expected:
                    raise RuntimeError(f'MLflow artifact verification failed: {key}')
    return run_id


def import_searches(source, paths):
    """Import completed historical trials in the same shape used by tune's resume."""
    tracking = Tracking(paths)
    for p in sorted(Path(source).glob('results/v2/search_*.csv')):
        table = pd.read_csv(p)
        family = table.family.iloc[0].replace('gbm', 'lightgbm')
        identity = fingerprint(paths, {'search': family, 'seed': 0})
        for config_id, part in table.groupby('config', sort=True):
            tags = {'family': family, 'config': str(config_id), 'fingerprint': identity}
            if next(tracking.completed('tune', tags), None): continue
            if set(zip(part.hours, part.window)) != {(h, w) for h in (1, 3, 6) for w in (7, 14)}:
                continue
            part = part.assign(family=family)
            with tracking.run('tune', {**tags, 'imported': 'true'},
                    json.loads(part.params.iloc[0])) as run_id:
                tracking.table(run_id, part, 'search.csv')
                for row in part.to_dict('records'):
                    prefix = f"h{row['hours']}/w{row['window']}"
                    tracking.metrics(run_id, {f'{prefix}/{k}': row[k] for k in
                        ('threshold', 'f1', 'precision', 'recall', 'ap', 'auc', 'brier', 'n')})
