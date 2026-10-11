"""alerts.in.ua client. The token is sent only in the Authorization header and never printed or saved."""
import http.client
import time
import urllib.error
import urllib.request

BASE = "https://api.alerts.in.ua"
UA = "alert-outlook/0.1 (KSE research project)"


def get(path, tok, tries=3):
    """GET BASE+path -> (status, body text). Retries on 429 and on dropped connections; any other HTTP error
    raises with the token redacted."""
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {tok}", "User-Agent": UA})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                time.sleep(60)
                continue
            body = e.read().decode("utf-8", "replace")[:300].replace(tok, "<redacted>")
            raise RuntimeError(f"HTTP {e.code} for {path}: {body}") from None
        except (http.client.IncompleteRead, urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == tries - 1:
                raise RuntimeError(f"network error for {path}: {type(e).__name__} {getattr(e, 'reason', '')}".replace(tok, "<redacted>")) from None
            time.sleep(30)


def pull_history(uids, out_root, tok, pause=31, into=None):
    """Save month_ago history for each oblast uid as raw gzip + MANIFEST.json in out_root/<UTC stamp>/.
    History is limited to 2 requests per minute, hence the pause. Pass `into` to resume an interrupted pull."""
    import datetime as dt
    import gzip
    import hashlib
    import json
    from pathlib import Path

    d = Path(into) if into else Path(out_root) / dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ")
    d.mkdir(parents=True, exist_ok=True)
    man = d / "MANIFEST.json"
    files = json.loads(man.read_text())["files"] if man.exists() else []
    done = {f["uid"] for f in files}
    for uid in uids:
        if uid in done:
            continue
        path = f"/v1/regions/{uid}/alerts/month_ago.json"
        if files:
            time.sleep(pause)
        status, body = get(path, tok)
        fetched = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        raw = body.encode("utf-8")
        name = f"r{uid}_month_ago.json.gz"
        (d / name).write_bytes(gzip.compress(raw, mtime=0))
        js = json.loads(body)
        files.append(dict(file=name, uid=uid, url=BASE + path, status=status, fetched_utc=fetched,
                          records=len(js["alerts"]), sha256=hashlib.sha256(raw).hexdigest(),
                          last_updated_at=js.get("meta", {}).get("last_updated_at")))
        print(uid, status, len(js["alerts"]), flush=True)
        man.write_text(json.dumps(dict(source=BASE + "/v1/regions/<uid>/alerts/month_ago.json",
                                       note="raw responses, gzip; token sent in a header, not stored",
                                       files=files), indent=1, ensure_ascii=False))
    return d
