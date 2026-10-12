import subprocess
import sys
from pathlib import Path


def test_help_exposes_current_commands_without_loading_data():
    result = subprocess.run([sys.executable, '-m', 'alert_outlook', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert all(command in result.stdout for command in ('train', 'evaluate', 'predict', 'page'))
    assert 'retrain' not in result.stdout and 'holdout' not in result.stdout


def test_evaluate_requires_run_and_period():
    result = subprocess.run([sys.executable, '-m', 'alert_outlook', 'evaluate'], capture_output=True, text=True)
    assert result.returncode == 2 and '--run-id' in result.stderr and '--period' in result.stderr
