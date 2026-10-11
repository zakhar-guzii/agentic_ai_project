"""Page back through a public channel's t.me/s/ web preview (no login) and save raw HTML pages.

usage: python -I fetch_tg.py OUT_DIR CHANNEL CUTOFF_UTC(YYYY-MM-DD) [sleep_s]
Stops when the oldest post on a page is older than CUTOFF. Resumable: skips pages already saved.
"""
import re
import sys
import time
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (research; feasibility probe)"}


def main():
    out, ch, cutoff = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    pause = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
    out.mkdir(parents=True, exist_ok=True)
    before, n = None, 0
    while True:
        url = f"https://t.me/s/{ch}" + (f"?before={before}" if before else "")
        f = out / f"page_{before or 'latest'}.html"
        if f.exists():
            html = f.read_text(encoding="utf-8")
        else:
            for attempt in range(4):
                try:
                    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                        html = r.read().decode("utf-8", errors="replace")
                    break
                except Exception as e:  # 429 / transient: back off
                    print("retry", attempt, url, e, flush=True)
                    time.sleep(10 * (attempt + 1))
            else:
                sys.exit(f"giving up at {url}")
            f.write_text(html, encoding="utf-8")
            n += 1
            time.sleep(pause)
        ids = [int(x) for x in re.findall(rf'data-post="{ch}/(\d+)"', html, flags=re.I)]
        dates = re.findall(r'<time datetime="([^"]+)"', html)
        if not ids or not dates:
            print("empty page", url, flush=True)
            break
        oldest = min(dates)
        if n % 20 == 0:
            print(ch, "pages", n, "before", before, "oldest", oldest, flush=True)
        if oldest[:10] < cutoff or min(ids) <= 1:
            print(ch, "done, pages fetched", n, "oldest", oldest, flush=True)
            break
        before = min(ids)


if __name__ == "__main__":
    main()
