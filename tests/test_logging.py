import json
import logging
from alert_outlook.logging import SafeFormatter


def test_json_log_redacts_tokens_headers_and_exception_text():
    secret = 'test-secret-123'
    record = logging.LogRecord('test', logging.ERROR, __file__, 1,
        'request failed token=%s Authorization: Bearer hidden-value', (secret,), None)
    record.model = 'logistic'
    record.run_id = secret
    result = SafeFormatter([secret], json_output=True).format(record)
    assert secret not in result and 'hidden-value' not in result
    payload = json.loads(result)
    assert payload['model'] == 'logistic'
    assert payload['run_id'] == '<redacted>'
