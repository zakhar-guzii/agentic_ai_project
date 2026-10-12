import shutil
import pandas as pd
import pytest
from alert_outlook.settings import Paths, FAMILIES
from alert_outlook.data import history as D
from alert_outlook.forecasting import live
from alert_outlook.forecasting.model import Forecaster
from alert_outlook.experiments.prediction import predict, score
from alert_outlook.experiments.presentation import page
from alert_outlook.experiments.tracking import digest


@pytest.fixture
def workspace(tmp_path):
    source = Paths()
    (tmp_path/'data').mkdir()
    (tmp_path/'data/raw').symlink_to(source.raw, target_is_directory=True)
    shutil.copytree(source.models,tmp_path/'models')
    return Paths(tmp_path)


def test_three_model_predictions_are_idempotent_and_page_survives_empty_mlflow(workspace):
    paths = workspace
    first, appended = predict(paths)
    second, repeated = predict(paths)
    assert appended and not repeated
    assert len(first) == len(second) == len(pd.read_csv(paths.predictions)) == 72
    assert set(first.model) == set(FAMILIES)
    # A fresh clone has no historical runs: rendering must still work.
    output = page(paths).read_text()
    assert output.count('type="radio"') == 3 and 'repository README' in output


def test_scoring_loads_old_weight_snapshot_and_keeps_models_separate(workspace):
    paths = workspace
    predict(paths)  # archives the trusted weights before they change
    records, end = D.saved(paths)
    T = end - pd.Timedelta('1D')
    old_sha = digest(paths.models/'logistic.joblib')
    rows = pd.concat([live.forecast(records,T,Forecaster.load(paths.models/f'{f}.joblib')).assign(
        model=f, made_at=T+pd.Timedelta('10min'), model_sha256=digest(paths.models/f'{f}.joblib'))
        for f in FAMILIES],ignore_index=True)
    live.log(rows,paths.predictions)
    changed = Forecaster.load(paths.models/'logistic.joblib')
    changed.meta['test_revision'] = 'new version'
    changed.save(paths.models/'logistic.joblib')
    predict(paths)
    table = score(paths)
    assert set(table.model) == set(FAMILIES)
    assert set(table.forecast) == {'live'}
    assert set(table.loc[table.model=='logistic','model_sha256']) == {old_sha}
    assert set(table.hours) == {1,3,6}
    assert table.model_brier.between(0,1).all()


def test_mlflow_write_failure_leaves_weights_and_forecast_log_untouched(workspace,monkeypatch):
    from mlflow import MlflowClient
    before = {p.name:digest(p) for p in workspace.models.glob('*.joblib')}
    def unavailable(*args,**kwargs): raise OSError('MLflow unavailable')
    monkeypatch.setattr(MlflowClient,'log_artifact',unavailable)
    with pytest.raises(OSError,match='MLflow unavailable'): predict(workspace)
    assert not workspace.predictions.exists()
    assert before == {p.name:digest(p) for p in workspace.models.glob('*.joblib')}


def test_scoring_rejects_a_model_path_outside_the_three_trusted_files(tmp_path):
    from alert_outlook.experiments.prediction import model_version
    paths = Paths(tmp_path)
    paths.models.mkdir()
    outside = paths.root/'outside.joblib'
    outside.write_bytes(b'not a trusted pickle')
    with pytest.raises(ValueError,match='invalid model identity'):
        model_version(paths,'../outside',digest(outside),None)
