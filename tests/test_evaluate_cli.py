import subprocess
import sys
from pathlib import Path


def test_benchmark_refuses_to_run_before_the_choice_is_registered():
    result = subprocess.run([sys.executable, '-c', 'import alerts.model as m; m.CHOSEN = None; import sys; sys.argv = ["main.py", "evaluate", "benchmark"]; import main; main.main()'],
                            cwd=Path(__file__).resolve().parent.parent, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'pre-register' in result.stderr
