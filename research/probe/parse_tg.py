"""Parse saved t.me/s/ pages into one CSV: channel,id,dt_utc,edited,text (deduplicated by id).

usage: python -I parse_tg.py OUT_CSV PAGE_DIR [PAGE_DIR ...]
"""
import csv
import html
import re
import sys
from pathlib import Path

POST = re.compile(r'data-post="([^"/]+)/(\d+)"(.*?)(?=data-post="|\Z)', re.S)


def text_of(body):
    m = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', body, re.S)
    if not m:
        return ""
    t = re.sub(r"<br\s*/?>", "\n", m.group(1))
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def main():
    rows = {}
    for d in sys.argv[2:]:
        for f in Path(d).glob("page_*.html"):
            for ch, pid, body in POST.findall(f.read_text(encoding="utf-8")):
                dt = re.search(r'<time datetime="([^"]+)"', body)
                if not dt:
                    continue
                edited = bool(re.search(r'tgme_widget_message_meta">\s*edited', body)) or ">edited<" in body
                rows[(ch.lower(), int(pid))] = (ch.lower(), int(pid), dt.group(1), int(edited), text_of(body))
    with open(sys.argv[1], "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["channel", "id", "dt_utc", "edited", "text"])
        for k in sorted(rows):
            w.writerow(rows[k])
    print("posts:", len(rows))


if __name__ == "__main__":
    main()
