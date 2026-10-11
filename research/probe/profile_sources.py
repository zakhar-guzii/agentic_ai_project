"""Quick profile of Vadimkin official (uk), volunteer and JustJimer files. usage: profile_sources.py F_DIR"""
import sys
import pandas as pd

F = sys.argv[1]
off = pd.read_csv(f"{F}/dl_vadimkin/official_data_uk.csv")
print("official rows", len(off), "unique", len(off.drop_duplicates()))
off = off.drop_duplicates()
for c in ("started_at", "finished_at"):
    off[c] = pd.to_datetime(off[c], utc=True, format="ISO8601")
print("oblasts:", sorted(off.oblast.unique()))
print(off.level.value_counts())
print("max start", off.started_at.max(), "max end", off.finished_at.max())
rec = off[off.started_at >= "2026-08-01"]
print("since 2026-08-01 by level:\n", rec.level.value_counts())
rec = rec.assign(dur_h=(rec.finished_at - rec.started_at).dt.total_seconds() / 3600)
print("durations >24h since 2026-08:", (rec.dur_h > 24).sum(), rec[rec.dur_h > 24].groupby(["oblast", "level"]).size().to_string())
print("daily rows by level, last 12 days:\n", rec.groupby([rec.started_at.dt.date, "level"]).size().unstack(fill_value=0).tail(12))

jj = pd.read_csv(f"{F}/dl_justjimer/alerts_in_ua.csv")
print("\nJJ rows", len(jj), "dup ids", jj.id.duplicated().sum())
print(jj.location_type.value_counts(), jj.alert_type.value_counts(), jj.alert_level.value_counts(), sep="\n")
print("oblasts:", sorted(jj.location_oblast.dropna().unique()))
for c in ("started_at", "finished_at"):
    jj[c] = pd.to_datetime(jj[c], utc=True, format="ISO8601")
print("start range", jj.started_at.min(), jj.started_at.max(), "open:", jj.finished_at.isna().sum())
a = jj[jj.alert_type == "air_raid"]
print("air_raid by type x level since 09-04:\n", a[a.started_at >= "2026-09-04"].groupby(["location_type", "alert_level"]).size())
print("daily air_raid starts by level:\n", a[a.started_at >= "2026-09-03"].groupby([a.started_at.dt.date, "alert_level"]).size().unstack(fill_value=0).to_string())
