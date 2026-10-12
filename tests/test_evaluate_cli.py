import subprocess
import sys
from pathlib import Path


def test_benchmark_refuses_to_run_before_the_choice_is_registered():
    result = subprocess.run([sys.executable, '-c', 'import alerts.model as m; m.CHOSEN = None; import sys; sys.argv = ["main.py", "evaluate", "benchmark"]; import main; main.main()'],
                            cwd=Path(__file__).resolve().parent.parent, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'pre-register' in result.stderr


def test_retrain_refuses_to_overwrite_v2_artifacts(tmp_path, monkeypatch):
    import pytest
    import main
    (tmp_path / "models/v2").mkdir(parents=True)
    (tmp_path / "models/v2/gbm.joblib").write_text("frozen")
    monkeypatch.setattr(main, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="refusing"):
        main.retrain(None)
    assert (tmp_path / "models/v2/gbm.joblib").read_text() == "frozen"
