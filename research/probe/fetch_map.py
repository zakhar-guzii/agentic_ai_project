"""Fetch map.ukrainealarm.com ranged AIR-alert history (undocumented, anonymous page token).

usage: python -I fetch_map.py OUT_DIR START(YYYYMMDD) END(YYYYMMDD, exclusive-ish) [chunk_days] [region ids...]
Saves one raw JSON per (region, chunk) so nothing is re-requested on rerun.
"""
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

MAP = "https://map.ukrainealarm.com/"
UA = {"User-Agent": "Mozilla/5.0 (research; feasibility probe)"}
OBLASTS = [4, 8, 9, 28, 10, 11, 12, 13, 14, 15, 16, 27, 17, 18, 19, 5, 20, 21, 22, 23, 3, 24, 26, 25, 31]


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
        return r.status, r.read().decode("utf-8")


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    start = dt.datetime.strptime(sys.argv[2], "%Y%m%d").date()
    end = dt.datetime.strptime(sys.argv[3], "%Y%m%d").date()
    chunk = int(sys.argv[4]) if len(sys.argv) > 4 else 31
    regions = [int(x) for x in sys.argv[5:]] or OBLASTS
    _, page = get(MAP)
    token = re.search(r'id="api-token"[^>]*value="([^"]+)"', page).group(1)
    for rid in regions:
        a = start
        while a < end:
            b = min(a + dt.timedelta(days=chunk), end)
            f = out / f"r{rid}_{a:%Y%m%d}_{b:%Y%m%d}.json"
            if not f.exists():
                q = urllib.parse.urlencode({"startDate": f"{a:%Y%m%d}", "endDate": f"{b:%Y%m%d}", "regionId": rid, "apiToken": token})
                t0 = time.time()
                status, body = get(MAP + "api/v2/data/mapGetRangedAlerts?" + q)
                data = json.loads(body)
                data = json.loads(data) if isinstance(data, str) else data
                f.write_text(json.dumps(data, ensure_ascii=False))
                print(rid, a, b, status, len(data), f"{time.time() - t0:.1f}s", flush=True)
                time.sleep(1.0)  # be polite; rate limits are undocumented
            a = b


if __name__ == "__main__":
    main()
