import json

import pandas as pd

from alerts import data

T = lambda s: pd.Timestamp(s, tz="UTC")
REGIONS = {"states": [
    {"regionId": "22", "regionName": "Харківська область", "regionType": "State", "regionChildIds": [
        {"regionId": "127", "regionName": "Красноградський район", "regionType": "District", "regionChildIds": [
            {"regionId": "1001", "regionName": "Липецька територіальна громада", "regionType": "Community"}]}]},
    {"regionId": "1293", "regionName": "м. Харків та Харківська територіальна громада", "regionType": "State",
     "regionChildIds": []},
    {"regionId": "31", "regionName": "м. Київ", "regionType": "State", "regionChildIds": []},
    {"regionId": "14", "regionName": "Київська область", "regionType": "State", "regionChildIds": [
        {"regionId": "76", "regionName": "Обухівський район", "regionType": "District", "regionChildIds": []}]}]}


def rec(uid, name, start, end="2026-10-08T01:00:00Z", typ="AIR", cont=False):
    return dict(regionId=str(uid), regionName=name, startDate=start, endDate=end, duration="", alertType=typ,
                isContinue=cont)


def write_map(tmp_path, chunks):
    """chunks: {filename: [records]} -> (map_dir, regions_path)"""
    m = tmp_path / "map"
    m.mkdir()
    for name, rows in chunks.items():
        (m / name).write_text(json.dumps(rows, ensure_ascii=False))
    r = tmp_path / "regions.json"
    r.write_text(json.dumps(REGIONS, ensure_ascii=False))
    return m, r


def test_map_keeps_only_air_alerts(tmp_path):
    m, r = write_map(tmp_path, {"r22_20261008_20261011.json": [
        rec(127, "Красноградський район", "2026-10-08T00:10:00Z"),
        rec(127, "Красноградський район", "2026-10-08T00:20:00Z", typ="NUCLEAR"),
        rec(1001, "Липецька територіальна громада", "2026-10-08T00:30:00Z", typ="ARTILLERY")]})
    d = data.load_map(m, r)
    assert len(d) == 1
    assert d.start.iloc[0] == T("2026-10-08 00:10")


def test_map_ongoing_alert_has_no_end(tmp_path):
    m, r = write_map(tmp_path, {"r14_20261008_20261011.json": [
        rec(76, "Обухівський район", "2026-10-10T18:00:00Z", end="0001-01-01T00:00:00", cont=True)]})
    d = data.load_map(m, r)
    assert d.end.isna().all() and d.start.iloc[0] == T("2026-10-10 18:00")


def test_map_same_alert_in_two_chunks_is_kept_once(tmp_path):
    a = rec(76, "Обухівський район", "2026-10-08T05:16:48Z", end="2026-10-08T05:38:25Z")
    b = rec(76, "Обухівський район", "2026-10-08T07:00:00Z", end="2026-10-08T07:30:00Z")
    m, r = write_map(tmp_path, {"r14_20260907_20261008.json": [a], "r14_20261008_20261011.json": [a, b]})
    d = data.load_map(m, r)
    assert len(d) == 2
    assert sorted(d.start) == [T("2026-10-08 05:16:48"), T("2026-10-08 07:00")]


def test_map_level_and_oblast_come_from_region_tree(tmp_path):
    m, r = write_map(tmp_path, {
        "r22_20261008_20261011.json": [rec(127, "Красноградський район", "2026-10-08T00:10:00Z"),
                                       rec(1001, "Липецька територіальна громада", "2026-10-08T00:20:00Z")],
        "r1293_20261008_20261011.json": [rec(1293, "м. Харків та Харківська територіальна громада", "2026-10-08T00:30:00Z")],
        "r31_20261008_20261011.json": [rec(31, "м. Київ", "2026-10-08T00:40:00Z")]})
    d = data.load_map(m, r).set_index("unit_id")
    assert d.loc[127, ["level", "oblast_id"]].tolist() == ["raion", 22]
    assert d.loc[1001, ["level", "oblast_id"]].tolist() == ["hromada", 22]
    assert d.loc[1293, ["level", "oblast_id"]].tolist() == ["city", 22]
    assert d.loc[31, ["level", "oblast_id"]].tolist() == ["oblast", 31]


def api_rec(id_, start, end, oblast="Київська область", uid="76", ltype="raion", atype="air_raid", level="yellow",
            oblast_uid=76):
    return dict(id=id_, location_title="x", location_type=ltype, started_at=start, finished_at=end,
                updated_at=start, alert_type=atype, location_oblast=oblast, location_uid=uid, notes=None,
                country=None, alert_level=level, location_title_en="x", location_oblast_uid=oblast_uid)


def write_pull(root, stamp, fetched, alerts):
    import gzip
    d = root / stamp
    d.mkdir(parents=True)
    (d / "r14_month_ago.json.gz").write_bytes(gzip.compress(json.dumps({"alerts": alerts}).encode()))
    (d / "MANIFEST.json").write_text(json.dumps({"files": [{"file": "r14_month_ago.json.gz", "uid": 14,
                                                           "fetched_utc": fetched}]}))


def test_api_same_id_in_two_pulls_keeps_newest_version(tmp_path):
    root = tmp_path / "api"
    write_pull(root, "20261011T1200Z", "2026-10-11T12:00:00Z",
               [api_rec(1, "2026-10-11T10:00:00Z", None), api_rec(2, "2026-09-12T10:00:00Z", "2026-09-12T11:00:00Z")])
    write_pull(root, "20261012T1200Z", "2026-10-12T12:00:00Z",
               [api_rec(1, "2026-10-11T10:00:00Z", "2026-10-11T10:40:00Z", level="red")])
    _, r = write_map(tmp_path, {})
    d = data.load_api(root, r).set_index("rec_id")
    assert sorted(d.index) == [1, 2]  # id 2 rolled out of the newer window but is kept from the older pull
    assert d.loc[1, "end"] == T("2026-10-11 10:40") and d.loc[1, "alert_level"] == "red"


def test_api_oblast_comes_from_name_not_oblast_uid(tmp_path):
    root = tmp_path / "api"
    write_pull(root, "20261011T1200Z", "2026-10-11T12:00:00Z", [
        api_rec(1, "2026-10-11T10:00:00Z", None, oblast="Харківська область", uid="127", oblast_uid=124),
        api_rec(2, "2026-10-11T10:05:00Z", None, oblast="м. Київ", uid="31", ltype="oblast", oblast_uid=31),
        api_rec(3, "2026-10-11T10:06:00Z", None, oblast="Харківська область", uid="6293", ltype="city", oblast_uid=1293)])
    _, r = write_map(tmp_path, {})
    d = data.load_api(root, r).set_index("rec_id")
    assert d.loc[1, ["oblast_id", "unit_id", "level"]].tolist() == [22, 127, "raion"]
    assert d.loc[2, ["oblast_id", "unit_id", "level"]].tolist() == [31, 31, "oblast"]
    assert d.loc[3, ["oblast_id", "unit_id", "level"]].tolist() == [22, 6293, "city"]


def test_api_keeps_only_air_raid(tmp_path):
    root = tmp_path / "api"
    write_pull(root, "20261011T1200Z", "2026-10-11T12:00:00Z", [
        api_rec(1, "2026-10-11T10:00:00Z", None),
        api_rec(2, "2024-05-20T09:31:37Z", None, ltype="hromada", atype="artillery_shelling"),
        api_rec(3, "2024-05-20T09:31:41Z", None, ltype="hromada", atype="urban_fights")])
    _, r = write_map(tmp_path, {})
    assert data.load_api(root, r).rec_id.tolist() == [1]


def test_map_reports_what_cleaning_removed(tmp_path):
    a = rec(76, "Обухівський район", "2026-10-08T05:16:48Z")
    m, r = write_map(tmp_path, {"r14_20260907_20261008.json": [a],
                                "r14_20261008_20261011.json": [a, rec(76, "x", "2026-10-08T07:00:00Z", typ="NUCLEAR")]})
    assert data.load_map(m, r).attrs["cleaning"] == {"raw rows": 3, "not AIR": 1, "duplicates": 1}


def test_api_reports_what_cleaning_removed(tmp_path):
    root = tmp_path / "api"
    write_pull(root, "20261011T1200Z", "2026-10-11T12:00:00Z",
               [api_rec(1, "2026-10-11T10:00:00Z", None), api_rec(2, "2024-05-20T09:31:37Z", None, atype="urban_fights")])
    write_pull(root, "20261012T1200Z", "2026-10-12T12:00:00Z", [api_rec(1, "2026-10-11T10:00:00Z", "2026-10-11T10:40:00Z")])
    _, r = write_map(tmp_path, {})
    assert data.load_api(root, r).attrs["cleaning"] == {"raw rows": 3, "duplicates": 1, "not air_raid": 1}
