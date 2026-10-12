import json

import pandas as pd
import pytest

from alerts import data as D

T = lambda s: pd.Timestamp(s, tz="UTC")


def pull(root, stamp, files):
    """A saved pull as `api.pull_history` writes its MANIFEST: {uid: (fetched_utc, last_updated_at)}."""
    (root / stamp).mkdir()
    (root / stamp / "MANIFEST.json").write_text(json.dumps({"files": [
        dict(uid=uid, fetched_utc=fetched, last_updated_at=updated) for uid, (fetched, updated) in files.items()]}))


def test_saved_data_end_at_the_earliest_of_the_newest_server_snapshots(tmp_path):
    pull(tmp_path, "20261011T1247Z", {3: ("2026-10-11T12:47:56Z", "2026/10/11 12:46:28 +0000"),
                                      4: ("2026-10-11T12:49:02Z", "2026/10/11 12:48:30 +0000")})
    pull(tmp_path, "20261012T0900Z", {3: ("2026-10-12T09:00:40Z", "2026/10/12 09:00:10 +0000")})  # interrupted
    # uid 4 was last fetched on 10-11, and its server snapshot (not the later fetch) is where its history ends
    assert D.api_asof([3, 4], tmp_path) == T("2026-10-11 12:48")
    with pytest.raises(KeyError):
        D.api_asof([3, 4, 5], tmp_path)  # uid 5 was never fetched
