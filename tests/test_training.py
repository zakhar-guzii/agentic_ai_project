from pathlib import Path
import pytest
from alert_outlook.settings import Paths
from alert_outlook.experiments.training import activate


def test_failed_activation_restores_all_three_weights(tmp_path, monkeypatch):
    import os
    paths = Paths(tmp_path)
    paths.models.mkdir()
    staged = tmp_path / 'staged'
    staged.mkdir()
    for name in ('logistic', 'lightgbm', 'catboost'):
        (paths.models / f'{name}.joblib').write_bytes(b'old')
        (staged / f'{name}.joblib').write_bytes(b'new')
    replace = os.replace
    failed = False
    def fail_second(source, target):
        nonlocal failed
        if Path(target).name == 'lightgbm.joblib' and not failed:
            failed = True
            raise OSError('disk error')
        return replace(source, target)
    monkeypatch.setattr(os, 'replace', fail_second)
    with pytest.raises(OSError, match='disk error'):
        activate(paths, staged)
    assert all(p.read_bytes() == b'old' for p in paths.models.glob('*.joblib'))
