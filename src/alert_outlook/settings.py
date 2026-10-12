"""One place for repository paths and runtime configuration."""
import os
from dataclasses import dataclass, field
from pathlib import Path

FAMILIES = {'logistic': 'Logistic', 'lightgbm': 'LightGBM', 'catboost': 'CatBoost'}
OBLAST_UIDS = [3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 31]


def default_root():
    source_root = Path(__file__).resolve().parents[2]
    return Path(os.environ.get('ALERT_OUTLOOK_HOME', source_root if (source_root / 'data/raw').exists() else Path.cwd())).resolve()


@dataclass(frozen=True)
class Paths:
    root: Path = field(default_factory=default_root)

    def __post_init__(self):
        object.__setattr__(self, 'root', Path(self.root).resolve())

    @property
    def raw(self): return self.root / 'data/raw'
    @property
    def models(self): return self.root / 'models'
    @property
    def artifacts(self): return self.root / 'artifacts'
    @property
    def predictions(self): return self.artifacts / 'predictions/forecasts.csv'
    @property
    def tracking(self): return self.root / 'mlruns'
    @property
    def tracking_uri(self): return 'sqlite:///' + str(self.tracking / 'tracking.db')

    def secrets(self):
        values = {}
        env = self.root / '.env'
        if env.exists():
            for line in env.read_text().splitlines():
                if '=' in line and not line.lstrip().startswith('#'):
                    key, value = line.split('=', 1)
                    values[key.strip()] = value.strip().strip('\"\'')
        values.update({k: v for k, v in os.environ.items() if k.endswith(('TOKEN', 'SECRET', 'PASSWORD', 'API_KEY'))})
        return values

    def token(self):
        token = self.secrets().get('ALERTS_IN_UA_TOKEN')
        if not token:
            raise ValueError('ALERTS_IN_UA_TOKEN is not set (see .env.example)')
        return token
