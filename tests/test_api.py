import io
import urllib.error

import pytest

from alerts import api

TOK = "secret-token-123"


class FakeResp(io.BytesIO):
    status = 200
    headers = {}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_token_goes_in_header_not_url(monkeypatch):
    seen = []

    def fake_urlopen(req, timeout=None):
        seen.append(req)
        return FakeResp(b'{"alerts": []}')

    monkeypatch.setattr(api.urllib.request, "urlopen", fake_urlopen)
    status, body = api.get("/v1/alerts/active.json", tok=TOK)
    assert status == 200 and body == '{"alerts": []}'
    assert TOK not in seen[0].full_url
    assert seen[0].get_header("Authorization") == f"Bearer {TOK}"


def test_error_body_with_token_is_redacted(monkeypatch):
    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {},
                                     io.BytesIO(f"bad token {TOK}".encode()))

    monkeypatch.setattr(api.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError) as e:
        api.get("/v1/alerts/active.json", tok=TOK)
    assert TOK not in str(e.value)
    assert "<redacted>" in str(e.value) and "401" in str(e.value)


def _fake_history(calls):
    def fake_urlopen(req, timeout=None):
        calls.append(req.full_url)
        uid = req.full_url.split("/regions/")[1].split("/")[0]
        body = '{"alerts": [{"id": %s}, {"id": 2}], "meta": {"last_updated_at": "2026/10/11 11:56:19 +0000"}}' % uid
        return FakeResp(body.encode())
    return fake_urlopen


def test_pull_history_writes_gzip_and_manifest_without_token(monkeypatch, tmp_path):
    import gzip, hashlib, json
    calls = []
    monkeypatch.setattr(api.urllib.request, "urlopen", _fake_history(calls))
    d = api.pull_history([14, 31], tmp_path, tok=TOK, pause=0)
    raw = gzip.decompress((d / "r14_month_ago.json.gz").read_bytes())
    assert json.loads(raw)["alerts"][0]["id"] == 14
    man = json.loads((d / "MANIFEST.json").read_text())
    f = {x["file"]: x for x in man["files"]}["r14_month_ago.json.gz"]
    assert f["status"] == 200 and f["records"] == 2 and f["sha256"] == hashlib.sha256(raw).hexdigest()
    assert f["url"] == "https://api.alerts.in.ua/v1/regions/14/alerts/month_ago.json"
    assert f["last_updated_at"] == "2026/10/11 11:56:19 +0000" and f["fetched_utc"].endswith("Z")
    for p in d.iterdir():
        data = gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes()
        assert TOK.encode() not in data


def test_resumed_pull_skips_saved_uids_and_keeps_manifest(monkeypatch, tmp_path):
    import json
    calls = []
    monkeypatch.setattr(api.urllib.request, "urlopen", _fake_history(calls))
    d = api.pull_history([14], tmp_path, tok=TOK, pause=0)
    d2 = api.pull_history([14, 31], tmp_path, tok=TOK, pause=0, into=d)
    assert d2 == d
    assert [u.split("/regions/")[1].split("/")[0] for u in calls] == ["14", "31"]  # 14 fetched once
    man = json.loads((d / "MANIFEST.json").read_text())
    assert sorted(x["uid"] for x in man["files"]) == [14, 31]


def test_dropped_connection_is_retried(monkeypatch):
    import http.client
    calls = []

    def flaky_urlopen(req, timeout=None):
        calls.append(1)
        if len(calls) == 1:
            raise http.client.IncompleteRead(b"partial")
        return FakeResp(b'{"alerts": []}')

    monkeypatch.setattr(api.urllib.request, "urlopen", flaky_urlopen)
    monkeypatch.setattr(api.time, "sleep", lambda s: None)
    assert api.get("/v1/regions/14/alerts/month_ago.json", tok=TOK) == (200, '{"alerts": []}')
    assert len(calls) == 2


def test_token_cut_at_the_length_limit_is_still_redacted(monkeypatch):
    def fake_urlopen(req, timeout=None):  # the body is cut at 300 chars, in the middle of the token
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, io.BytesIO(("x" * 295 + TOK).encode()))

    monkeypatch.setattr(api.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError) as e:
        api.get("/v1/alerts/active.json", tok=TOK)
    assert TOK[:5] not in str(e.value)
