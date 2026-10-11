"""Acceptance checks (plan §6) on the real snapshot and the saved alerts.in.ua pulls. Not TDD: the bar was set
before the data was checked. Skipped where the API pull is missing (e.g. a fresh clone before `fetch`)."""
import gzip
import json
import os
from pathlib import Path

import pandas as pd
import pytest

from alerts import data as D

ROOT = Path(__file__).resolve().parent.parent
PULLS = sorted(D.API_DIR.glob("*/MANIFEST.json"))
need_api = pytest.mark.skipif(not PULLS, reason="no alerts.in.ua pull saved yet (python main.py fetch)")
CORE = ["oblast", "raion"]


@pytest.fixture(scope="module")
def m():
    return D.load_map()


@pytest.fixture(scope="module")
def a():
    return D.load_api()


def test_map_snapshot_is_clean(m):
    assert m.level.notna().all()  # every unit found in the regions.json tree
    assert not m.duplicated(["unit_id", "start"]).any()
    neg = m[m.end < m.start]
    assert len(neg) == 2 and ((neg.start - neg.end).dt.total_seconds() < 10).all()  # zero-length blips only
    assert m.oblast_id.nunique() == 24


@need_api
def test_api_pulls_complete_and_token_free():
    tok = os.environ.get("ALERTS_IN_UA_TOKEN") or next(
        (l.split("=", 1)[1].strip().strip("\"'") for l in (ROOT / ".env").read_text().splitlines()
         if l.startswith("ALERTS_IN_UA_TOKEN=")), None) if (ROOT / ".env").exists() else None
    for man in PULLS:
        files = json.loads(man.read_text())["files"]
        assert len(files) == 24 and all(f["status"] == 200 for f in files)
        if tok:
            assert tok not in man.read_text()
            assert not any(tok.encode() in gzip.decompress((man.parent / f["file"]).read_bytes()) for f in files)


@need_api
def test_seam_meets_the_bar(m, a):
    s = D.compare(m[m.level.isin(CORE)], a[a.level.isin(CORE)], D.SPLICE, D.MAP_CUTOFF)
    assert s.loc["all", "jaccard"] >= 0.99
    assert s.loc["all", "a_in_b"] >= 0.98 and s.loc["all", "b_in_a"] >= 0.98
    # per oblast on exact seconds: the minute grid adds up to 1 min per episode edge, which dominates quiet
    # oblasts (Zakarpattia: 65 alert-minutes -> 0.956 on minutes, 0.990 exact); see PROCESS_LOG
    assert (s.drop("all").jaccard_s >= 0.97).all(), s.jaccard_s[s.jaccard_s < 0.97].to_dict()


@need_api
def test_splice_keeps_every_alert(m, a):
    h = D.history(m, a)
    assert len(h) == (m.start < D.SPLICE).sum() + (a.start >= D.SPLICE).sum()
    mr, ar = m[m.level == "raion"], a[a.level == "raion"]
    u = D.unmatched(mr, ar, D.SPLICE, D.MAP_CUTOFF)
    in_win = lambda r: r.start.between(D.SPLICE, D.MAP_CUTOFF, inclusive="left").sum()
    assert (u.src == "map").sum() <= 0.01 * in_win(mr) and (u.src == "api").sum() <= 0.01 * in_win(ar)
    hc, mc = h[h.level.isin(CORE)], m[m.level.isin(CORE)]
    w = D.compare(hc, mc, D.SPLICE - pd.Timedelta("12h"), D.SPLICE + pd.Timedelta("12h"))
    assert (w.jaccard >= 0.99).all(), w.jaccard[w.jaccard < 0.99].to_dict()
    assert hc[hc.start < D.SPLICE].oblast_id.nunique() == hc[hc.start >= D.SPLICE].oblast_id.nunique() == 24
    assert (hc.set_index("start").resample("6h").size() > 0).all()
