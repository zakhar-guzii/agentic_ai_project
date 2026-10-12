import pytest
from alert_outlook.settings import Paths
from alert_outlook.experiments.tracking import Tracking


def test_tracking_persists_metrics_and_marks_failed_runs(tmp_path):
    tracking = Tracking(Paths(tmp_path))
    with tracking.run('check', {'source': 'test'}) as run_id:
        tracking.metrics(run_id, {'jaccard': .9994})
        tracking.json(run_id, {'source': 'test'}, 'summary.json')
    saved = tracking.client.get_run(run_id)
    assert saved.info.status == 'FINISHED'
    assert saved.data.metrics['jaccard'] == .9994
    assert tracking.read_json(run_id, 'summary.json') == {'source': 'test'}
    with pytest.raises(RuntimeError):
        with tracking.run('check') as failed:
            raise RuntimeError('storage failed')
    assert tracking.client.get_run(failed).info.status == 'FAILED'


def test_resume_fingerprint_changes_when_raw_data_changes(tmp_path):
    from alert_outlook.experiments.tracking import fingerprint
    paths = Paths(tmp_path)
    paths.raw.mkdir(parents=True)
    data = paths.raw/'snapshot.json'
    data.write_text('{"alerts":[]}')
    before = fingerprint(paths, {'search':'logistic','seed':0})
    data.write_text('{"alerts":[1]}')
    assert fingerprint(paths, {'search':'logistic','seed':0}) != before


def test_historical_import_verifies_artifacts_and_is_idempotent(tmp_path):
    import json
    from alert_outlook.experiments.migration import import_history
    from alert_outlook.experiments.tracking import digest
    source = tmp_path/'legacy'
    (source/'results/v2').mkdir(parents=True)
    summary = source/'results/v2/summary.json'
    summary.write_text(json.dumps({'pooled':[{'forecast':'logistic','period':'benchmark','horizon':1,'f1':.64}]}))
    source.joinpath('original.json').write_text(json.dumps({'commit':'original','files':{
        'results/v2/summary.json':digest(summary)}}))
    paths = Paths(tmp_path/'workspace')
    first = import_history(source,paths)
    assert import_history(source,paths) == first
    tracking = Tracking(paths)
    assert len(list(tracking.completed('migration'))) == 1
    run = tracking.client.get_run(first)
    assert run.data.metrics['logistic/benchmark/h1/f1'] == .64
    assert run.data.tags['imported'] == 'true' and run.data.tags['source_commit'] == 'original'
    summary.write_text('{}')
    # An already imported snapshot is immutable; source corruption is irrelevant to a completed verified run.
    assert import_history(source,paths) == first
