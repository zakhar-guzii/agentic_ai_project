"""Human stderr messages and rotating JSONL logs with secret redaction."""
from datetime import datetime, timezone
import json
import logging
from logging.handlers import RotatingFileHandler
import re
import os

FIELDS = ('command', 'stage', 'model', 'horizon', 'duration', 'rows', 'run_id', 'asof', 'config', 'block')


class SafeFormatter(logging.Formatter):
    def __init__(self, secrets=(), json_output=False):
        super().__init__()
        self.secrets = sorted((s for s in secrets if s), key=len, reverse=True)
        self.json_output = json_output

    def redact(self, text):
        for secret in self.secrets: text = text.replace(secret, '<redacted>')
        return re.sub(r'(?i)(Authorization\s*[:=]\s*)([^\r\n]+)', r'\1<redacted>', text)

    def format(self, record):
        message = self.redact(record.getMessage())
        if record.exc_info: message += '\n' + self.redact(self.formatException(record.exc_info))
        if not self.json_output: return f'{record.levelname} {record.name}: {message}'
        values = dict(time=datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
                      level=record.levelname, logger=record.name, message=message)
        for field in FIELDS:
            if hasattr(record, field):
                value = getattr(record, field)
                values[field] = self.redact(str(value)) if isinstance(value, str) else value
        return json.dumps(values, ensure_ascii=False, default=str)


def configure(paths, level='INFO'):
    os.environ.setdefault('MLFLOW_DISABLE_AGENT_HINT', '1')
    os.environ.setdefault('MPLCONFIGDIR', str(paths.artifacts / '.cache/matplotlib'))
    folder = paths.root / 'logs'
    folder.mkdir(parents=True, exist_ok=True)
    secrets = paths.secrets().values()
    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, '_alert_outlook', False):
            root.removeHandler(handler)
            handler.close()
    console = logging.StreamHandler()
    console.setFormatter(SafeFormatter(secrets))
    file = RotatingFileHandler(folder / 'operations.jsonl', maxBytes=2_000_000, backupCount=3, encoding='utf-8')
    file.setFormatter(SafeFormatter(secrets, json_output=True))
    for handler in (console, file):
        handler._alert_outlook = True
        root.addHandler(handler)
    root.setLevel(level)
    logging.getLogger('mlflow').setLevel(logging.WARNING)
