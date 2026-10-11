# Data sources for forecasting Ukrainian air-raid alerts

Status as of **2026-10-10**. I checked the facts below against primary sources: API docs, repository code, Telegram channels, and files I downloaded and profiled on 2026-10-10 between about 17:00 and 18:30 UTC. Results from my own measurements are tagged **[measured]**. Statements I could not confirm at the source are tagged **unverified**.

---

## 1. TL;DR

**Recommended alert sources (combine them):**

- **History, 2022-03-15 → 2026-09-07: [Vadimkin/ukrainian-air-raid-sirens-dataset](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset), `official_data_*.csv`.** This is the only free, multi-year, multi-level official series (oblast, raion and hromada).
  - It is **frozen at 2026-09-07 05:39 UTC** because its upstream Telegram channel went silent.
  - **38% of its rows are exact duplicates** and must be dropped. [measured]
- **2026-09-06 → now, and live collection: the [alerts.in.ua API](https://devs.alerts.in.ua/)** (free token, issued on request).
  - Its documentation is the only one that describes the new **yellow/red levels** and per-threat types.
  - Its history endpoint only reaches back about **one month on a rolling basis** (`month_ago`). Start a collector now, or the post-freeze gap will fall out of the window.
- **Cross-check and gap-fill: the official [api.ukrainealarm.com](https://api.ukrainealarm.com/) (API of the «Повітряна тривога» / "Air Raid Alert" app).**
  - You can reach it without a key through the [siren.pp.ua](https://github.com/PaulAnnekov/uasiren) proxy.
  - The official map's undocumented date-range endpoint returned district-level alert history covering at least 2025-10-15 → now. [measured]
- **Kyiv city only: [Kyiv Digital open data](https://data.kyivcity.gov.ua/dataset/statystyka-povitrianykh-tryvoh-u-misti-kyievi-dep-municipal).** It is official, keyless, has second-level precision and runs from 2022-02-25 to live, with levels and causes since September 2026.
- **Long oblast-level proxy that is fresh to today: the Vadimkin `volunteer_data_*.csv` (eTryvoga).** Its latest alert ends 2026-10-10 04:59 UTC.
  - It captures only about **35–60% of the official alert time**. Use it for relative patterns, not absolute durations. [measured]

**Recommended auxiliary sources:**

1. **Air Force reports:** the Telegram channel [@kpszsu](https://t.me/s/kpszsu) (real-time threat posts plus a morning summary) and [Petro Ivaniuk's "Massive Missile Attacks on Ukraine"](https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine) (CC BY-NC-SA). The Kaggle dataset ends at an attack window closing 2026-10-10 09:00 Kyiv time and is updated weekly.
2. **Calendar and holidays:** the [`holidays`](https://github.com/vacanza/holidays) package. Under martial law the holidays are in the `workday` category, so request both categories (§3.17).
3. **Weather:** archived *forecasts* from the [Open-Meteo Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api). Its data starts in 2024. Do not use the Historical Forecast API values for the target period, because they are near-analysis.
4. **Public Telegram monitoring channels:** @war_monitor, @deraketaua, @radar_raketaa and @UkraineAlarmSignal. You can read them with Telethon or with no login through the `t.me/s/` web preview, which pages back to the first post.
5. **Lower value:** GDELT (15-minute news volume), VIINA (daily geocoded news events), ISW (published 01:30–06:35 Kyiv time the *next* day) and DeepStateMap (front line). ACLED needs an institutional account and has a lag of days.

**Structural breaks to model explicitly:**

- **Dec 2025:** the switch from oblast-level to raion-level alerting ([PM Svyrydenko, 2025-12-15](https://t.me/svyrydenkoy/1179)).
- **2026-09-07:** yellow (drone) and red (missile or massed) levels start, under [Cabinet of Ministers Resolution 1092 of 2026-09-04](https://www.kmu.gov.ua/npas/deiaki-pytannia-optymizatsii-zakhystu-naselennia-ta-reahuvannia-na-zahrozy-zasobiv-povitrianoho-napadu-1092-040926).
- **2026-09-07 06:09 UTC:** the official Telegram channel stops posting.

---

## 2. Alert sources compared

| Source | Granularity / types | Coverage (latest as of 2026-10-10) | Access | Auth | License / terms |
|---|---|---|---|---|---|
| Vadimkin **official** CSV | oblast, raion, hromada; air raid plus whatever the channel posted | 2022-03-15 16:10 UTC → **2026-09-07 05:39 UTC (frozen)** [measured] | CSV on GitHub | none | MIT (repo) |
| Vadimkin **volunteer** CSV (eTryvoga) | oblast only | 2022-02-25 → **2026-10-10 04:59 UTC**, updated daily [measured] | CSV on GitHub | none | MIT (repo) |
| Telegram [@air_alert_ua](https://t.me/s/air_alert_ua) (official) | oblast, raion, hromada; alert, all-clear, partial and threat notes | 2022-03-15 → **2026-09-07 06:09 UTC (silent since)** [measured] | Telethon or `t.me/s/` scrape | Telegram API ID for Telethon | Telegram ToS |
| [alerts.in.ua API](https://devs.alerts.in.ua/) | oblast, raion, hromada, city; air_raid, artillery_shelling, urban_fights, chemical, nuclear; red/yellow levels; threats | live; history = **rolling ~1 month** | REST | token via [form](https://alerts.in.ua/api-request) | disclaimer only; no license stated |
| [JustJimer archive](https://github.com/JustJimer/ukraine-air-alert-stats) of alerts.in.ua | as above, no threats | 2026-09-06 → 2026-10-10 09:50 UTC, synced daily [measured] | CSV on GitHub | none | no license |
| [api.ukrainealarm.com](https://api.ukrainealarm.com/) (official app API) | State, District, Community; AIR, ARTILLERY, URBAN_FIGHTS, CHEMICAL, NUCLEAR, UNKNOWN; Red/Yellow levels on live alerts | live; `regionHistory` = last ~20–25 alerts only | REST and webhooks | API key via form | not stated (unverified) |
| [siren.pp.ua](https://github.com/PaulAnnekov/uasiren) proxy | same as the official API | live plus `regionHistory` [measured] | REST | none (50 requests/min) | third-party |
| map.ukrainealarm.com ranged history (undocumented) | district/city/hromada; mostly AIR, but also ARTILLERY, NUCLEAR, URBAN_FIGHTS (corrected 2026-10-11, PROCESS_LOG Wrong #3); no levels | at least 2025-10-15 → now; 2025-04-10 empty [measured] | JSON with an anonymous page token | none | undocumented; ToS unclear |
| [Kyiv Digital](https://data.kyivcity.gov.ua/dataset/statystyka-povitrianykh-tryvoh-u-misti-kyievi-dep-municipal) | Kyiv city only; level and cause since 2026-09 | weekly JSON 2022-02-28 → 2026-10-04; history API 2022-02-25 → live [measured] | JSON / XML | none | not stated in portal metadata |
| [air-alarms.in.ua](https://air-alarms.in.ua/) | oblast aggregates | live statistics | web UI only | – | – |
| Kaggle alert copies | oblast | stale (newest is 2025-07-01), apart from a Kyiv Digital mirror | download | Kaggle account | varies |

---

## 3. Sources

### 3.1 Vadimkin / ukrainian-air-raid-sirens-dataset (GitHub)

- **Maintainer and URL:** Vadym Klymenko ([Vadimkin](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset)). MIT license, 88 stars. A daily GitHub Action ([`update_datasets.yml`](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/blob/main/.github/workflows/update_datasets.yml), cron 00:00 UTC) commits at about 03:40–05:30 UTC.
- **How it is built** ([`process.py`](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/blob/main/process.py)): Telethon reads two Telegram channels and pairs start and end messages.
  - **Official:** from `@air_alert_ua`, built by [`official_channel_processor.py`](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/blob/main/processors/official_channel_processor.py). Columns are `oblast, raion, hromada, level, started_at, finished_at, source`. Timestamps are the Telegram `message.date`.
  - **Volunteer:** from eTryvoga's `@UkraineAlarmSignal`, built by [`volunteer_etryvoga_processor.py`](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/blob/main/processors/volunteer_etryvoga_processor.py). It uses keyword matching. Columns are `region, started_at, finished_at, naive`.
- **Timezone:** all times are UTC ([datasets/README](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/blob/main/datasets/README.md)).
- **Ongoing alerts:** these are not written to the CSV until they finish; the processor keeps them in a pickle file. Do **not** unpickle downloaded files.
- **Permanent alerts are excluded:** Luhansk (since 2022-04-04 16:45 UTC) and Crimea (since 2022-12-10 22:22 UTC) are not in the files ([datasets/README](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/blob/main/datasets/README.md)).
- **Heuristics in the code:**
  - If a new start arrives more than 3 h after an unclosed start, the old alert is closed with a synthetic end: start + 1 h (official) or start + 30 min with `naive=True` (volunteer).
  - A new start within 3 h overwrites the old one.
  - Messages that cannot be parsed are skipped.
- **Official file [measured]:**
  - 299,275 rows, of which **113,845 are exact duplicates**; 185,430 rows are unique. The duplicates span 2022-03 to 2026-01.
  - Rows are not sorted.
  - Range: 2022-03-15 16:10 → 2026-09-07 05:28 UTC (start).
  - There are **no rows for 2026-08-30 → 2026-09-01**, and nothing after 2026-09-07. The repo still commits daily, but only to the volunteer files ([issues #6](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/issues/6) and [#7](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/issues/7), both open).
  - 118 raions and 133 hromadas appear.
  - Frontline hromadas have standing alerts lasting months, for example Lypetska hromada at 604 days and Vovchanska at 438 days.
  - 360 rows have a duration of exactly 1 h, which matches the synthetic close.
- **Level shift [measured, deduplicated]:** oblast-level rows fall from about 23 a day (Sep–Oct 2025) to 5.4 a day (Nov 2025) and then 1–3 a day through 2026. Raion-level rows rise to roughly 7–10k a month. The last oblasts to get raion-level alerts were the western ones, on 2025-11-06. Raion- and hromada-level rows exist from 2022-03-15 but were rare before Aug 2025.
  - To make the series comparable across time, merge raion intervals into "any alert in the oblast" episodes. [air-alarms.in.ua](https://air-alarms.in.ua/) describes this same method.
- **Renames:** the code maps Новомосковський → Самарівський and Новоград-Волинський → Звягельський ([`legacy_states.py`](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/blob/main/processors/legacy_states.py)). Червоноградський is still used up to 2026-08. Join on API region IDs (§3.4), not names.
- **Volunteer file [measured]:**
  - 115,793 rows; 2022-02-25 16:36 → 2026-10-10 04:47 UTC (start); 5% `naive`.
  - Append-only: the 2026-06-25 version (101,969 rows) is an exact prefix of today's file.
  - Compared with the official file over 2025-01 → 2026-09 (oblast/raion levels, alerts ≤ 24 h), the volunteer file covers about **35–60%** of the official alert time. The cross-oblast correlation of monthly alert share is 0.75–0.95.
  - Counts per quarter keep rising while the median duration falls from about 34 min to 20 min. This suggests the keyword parser fragments raion-level messages (inference).

### 3.2 Telegram @air_alert_ua («Повітряна тривога», "Air Raid Alert", official)

- **What it is:** the official channel that duplicates notifications from the app. 235K subscribers. [t.me/s/air_alert_ua](https://t.me/s/air_alert_ua)
- **Message formats [measured]:**
  - 🔴 start, 🟢 all-clear, 🟡 partial all-clear ("тривога ще триває у…", "the alert is still on in…").
  - 🔴🔴 "Загроза ударних БпЛА… Підвищений рівень небезпеки" ("Strike drone threat… elevated danger level").
  - 🟠 threat notes.
  - Places are given as hashtags. The text shows local time; the message `date` is UTC.
- **Coverage [measured]:**
  - The first post is id 10, 2022-03-15 16:14 UTC.
  - **Outage:** no posts from 2026-08-29 04:55 UTC to 2026-09-02 13:48 UTC. On 2026-08-30 [post 334745](https://t.me/air_alert_ua/334745) said that publishing was temporarily broken "з технічних причин" ("for technical reasons") and directed software users to [api.ukrainealarm.com](https://api.ukrainealarm.com/).
  - **Last post:** [338380](https://t.me/air_alert_ua/338380), 2026-09-07 06:09:04 UTC. Post 338381 does not exist. This is the same moment the leveled alerts begin; the reason has not been announced.
- **Access:**
  - Telethon needs an `api_id`/`api_hash` from [my.telegram.org](https://docs.telethon.dev/en/stable/basic/signing-in.html). `Message.date` is UTC and `edit_date` gives the last edit ([Telethon docs](https://docs.telethon.dev/en/stable/modules/custom.html)).
  - Alternatively, page through `https://t.me/s/air_alert_ua?before=<id>`, 20 posts per page, with no login. I verified this back to the first post.

### 3.3 alerts.in.ua API (volunteer project «Мапа тривог», "Alert Map")

- **Documentation:** [devs.alerts.in.ua](https://devs.alerts.in.ua/). The data is taken "з офіційних джерел" ("from official sources"): the official API, the @air_alert_ua channel, regional military administrations (ОВА), Suspilne and the State Emergency Service (ДСНС).
- **Auth:** a token, sent as `?token=` or `Authorization: Bearer`, requested through the [form](https://alerts.in.ua/api-request). Without a token the API returns 401: "API token required. Please contact api@alerts.in.ua". [measured]
- **Rate limits:** soft limit 8–10 requests per minute per IP, hard limit 12. **History has a separate limit of 2 requests per minute.** Use `If-Modified-Since`.
- **Endpoints:**
  - `/v1/alerts/active.json`
  - `/v1/iot/active_air_raid_alerts*.json`, which return compact `A`/`P`/`N` status strings
  - `/v1/regions/{uid}/alerts/{period}.json`. The only documented period is **`month_ago`**.
- **Fields:**
  - `id, location_title(_en), location_type` (oblast, raion, city, hromada, unknown)
  - `started_at, finished_at` (ISO strings with `Z`; **`null` means ongoing**) and `updated_at`
  - `alert_type` (air_raid, artillery_shelling, urban_fights, chemical, nuclear)
  - `location_uid, location_oblast(_uid), location_raion, notes`
  - **`alert_level`** (red, yellow)
  - **`threats[]`**, with `threat_type` one of tactic_aircraft_activity, strategic_aircraft_activity, mig31k_departure, ballistic_missiles, cruise_missiles, unspecified_missiles, drones, guided_aerial_bombs, air_defense, unknown.
- **UID mapping:** oblast UIDs are listed in the docs; raions and cities are in a [Google Sheet](https://docs.google.com/spreadsheets/d/1XnTOzcPHd1LZUrarR1Fk43FUyl8Ae6a6M7pcwDRjNdA). Raion UIDs match the ukrainealarm region IDs (for example 127, 92, 43, 60, 38). Crimea differs: 29 here and 9999 there. [measured]
- **Terms:** "Не використовуйте API для критичної інфраструктури" ("Don't use the API for critical infrastructure"). Use is at your own risk, and delays are possible. There is no license or redistribution clause.
- **Python client:** [`alerts-in-ua` 0.3.2](https://pypi.org/project/alerts-in-ua/) (2025-08). It converts times to Europe/Kyiv. It does **not** parse `alert_level`/`threats`, and its default `period='week_ago'` is not in the docs, so use raw JSON.
- **Live-only extra:** [`/v3/alerts/active.md`](https://api.alerts.in.ua/v3/alerts/active.md) returns a keyless Markdown situation report. [measured]
- **Third-party archive [measured]:** [JustJimer/ukraine-air-alert-stats `archive/alerts_in_ua.csv`](https://github.com/JustJimer/ukraine-air-alert-stats).
  - 18,146 raw API records, synced daily since 2026-10-06.
  - Records start 2026-09-04 (plus standing alerts back to 2022).
  - Levels: yellow 10,763, red 7,383. The first yellow is **2026-09-07 05:36 UTC**.
  - Records from before the reform are labelled `red`, which is the default, not a missile signal.
  - `threats` is empty in the history.
  - `month_ago` returns any alert *active* during the window, including standing alerts (inference).
  - The repo has no license.

### 3.4 api.ukrainealarm.com: official API of the «Повітряна тривога» app

- **Owner:** the app is by Ajax Systems and Stfalcon, supported by the Ministry of Digital Transformation; the API was built with Artem Lemeshev ([Ajax, 2022-04-26](https://ajax.systems/ua/blog/air-alert-3-0/)). The key is requested through a form on [api.ukrainealarm.com](https://api.ukrainealarm.com/), which asks for name, company, phone, email, link and purpose ([2022 snapshot](https://web.archive.org/web/20220625084133/https://api.ukrainealarm.com/)).
- **Swagger** (`/swagger/v3/swagger.json`) sits behind a **Cloudflare challenge** and could not be fetched. Endpoints below are from the official generated SDK ([UkraineAlarm/UkraineAlarm-python](https://github.com/UkraineAlarm/UkraineAlarm-python), Jan 2024):
  - `GET /api/v3/alerts`, `/alerts/{regionId}`, `/alerts/status` (last action index for polling)
  - `/alerts/regionHistory?regionId=` — "останніх 25 тривог регіону" ("the region's last 25 alerts")
  - `/regions`
  - webhooks
  - The key goes in the `Authorization` header.
  - Rate limits: **unverified**.
- **Measured through the keyless proxy `https://siren.pp.ua/api/v3/...`** ([uasiren](https://github.com/PaulAnnekov/uasiren); "50 запитів в хвилину з одного IP", i.e. 50 requests per minute per IP):
  - Live alerts carry `type` and `activeAlertLevels[{alertLevel: Red|Yellow, reason: "Дронова загроза (жовтий рівень)" ("drone threat, yellow level") …, createdAt}]`. Home Assistant core added level support on [2026-09-10](https://github.com/home-assistant/core/blob/dev/homeassistant/components/ukraine_alarm/const.py).
  - `regions` returns 29 State, 122 District and 1,455 Community entries.
  - `regionHistory` for Kyiv returned **20 alerts covering about 2 days**, with no level field.
  - Ongoing alerts have `endDate "0001-01-01T00:00:00"` and `isContinue: true`. Timestamps are UTC.
- **Official map ([map.ukrainealarm.com](https://map.ukrainealarm.com/)):**
  - Live updates arrive over a Centrifugo WebSocket.
  - Its date picker calls an undocumented `GET /api/v2/data/mapGetRangedAlerts?startDate=YYYYMMDD&endDate=YYYYMMDD&regionId=<oblast>&apiToken=<token from page HTML>` ([used by ukraine-alarm-pro](https://github.com/ABovsh/ukraine-alarm-pro/blob/main/custom_components/ukraine_alarm_pro/backfill.py)). It returns finished alerts for the region's units plus the ones currently ongoing, with no levels. **[measured]** _Correction 2026-10-11: not AIR only; the snapshot also holds 3,203 ARTILLERY, 12 NUCLEAR and 3 URBAN_FIGHTS rows, so filter on `alertType == "AIR"` (PROCESS_LOG Wrong #3)._
  - For Kyiv it matched Vadimkin to the second on 2026-04-10 and 2025-10-15, and returned data for 2026-09-10. It was **empty** for 2025-04-10 and 2022-03-15/16, dates that do have alerts. The retention is therefore between about 6 and 18 months; the exact figure is **unverified**.
  - It is not an official API, so check terms before relying on it.

### 3.5 eTryvoga (єТривога), volunteer

- **Channel:** [@UkraineAlarmSignal](https://t.me/s/UkraineAlarmSignal), 84.4K subscribers, posts from 2022-02-25 → live (2026-10-10 18:18 UTC). [measured]
- **Content:** free-text messages with yellow/red levels per raion and per-settlement threat notes (🛸 drones, 💣 guided bombs/KABs). The oblast appears in brackets. Posts are often edited.
- **Other outlets:** [app.etryvoga.com](https://app.etryvoga.com/) is down (hosting page) and no public API was found. The related stats site [air-alarms.in.ua](https://air-alarms.in.ua/) gives web-only aggregates ("Дані перевірено: 10.10.2026", "data checked 10.10.2026") and offers custom extracts by email.

### 3.6 Kyiv Digital open data (Kyiv city, Департамент муніципальної безпеки / Department of Municipal Security)

- **Dataset:** [«Статистика повітряних тривог у місті Києві»](https://data.kyivcity.gov.ua/dataset/statystyka-povitrianykh-tryvoh-u-misti-kyievi-dep-municipal) ("Air raid alert statistics in Kyiv").
- **`airalerts.json`** (updated every Monday) [measured]:
  - 2,594 alerts from 2022-02-28 to 2026-10-04.
  - Fields: `CATUTTC, type, level, cause, dateTimeStart, dateTimeEnd`.
  - Since 2026-09-07 the `level` field reads Жовтий/Червоний (yellow/red) and `cause` reads, for example, "Дронова небезпека" (drone danger) or "Загроза балістики" (ballistic threat).
- **Live APIs** (no key) [measured]:
  - [`kyiv.digital/open-api/air-alert/history`](https://kyiv.digital/open-api/air-alert/history) is XML with 5,315 state events (1 = start, 0 = end) from 2022-02-25 to now, with causes drone, missile, ballistic or massive-drone.
  - `/state` returns the current state.
- **Timezone:** times are **naive Kyiv local time**, 1–3 s earlier than the Telegram post times.
- **Completeness:** 2,301 alerts against Vadimkin's 2,265 for Kyiv City over 2022-03-16 → 2026-09-06.
- **License:** not stated in the CKAN metadata (**unverified**).

### 3.7 Kaggle alert datasets (all derivative)

Dates and licenses are from the Kaggle API metadata:

| Dataset | Description | Last updated | License |
|---|---|---|---|
| [mikerudine/kyiv-air-raid-alerts](https://www.kaggle.com/datasets/mikerudine/kyiv-air-raid-alerts) | Kyiv Digital, daily | 2026-10-10 | CC BY 4.0 |
| [dimakyn/air-alarm-ukrain-…](https://www.kaggle.com/datasets/dimakyn/air-alarm-ukrain-2022022420220409) | from @air_alert_ua | 2025-07-01 | CC0 |
| [p0stscriptum/air-raid-dataset](https://www.kaggle.com/datasets/p0stscriptum/air-raid-dataset) | copy of Vadimkin | 2023-02-14 | – |
| [bromotdi/air-raid-sirens-in-the-ukraine-russia-war](https://www.kaggle.com/datasets/bromotdi/air-raid-sirens-in-the-ukraine-russia-war) | copy of Vadimkin | 2024-01 | – |
| [cashncarry/airraid-sirens-in-ukraine](https://www.kaggle.com/datasets/cashncarry/airraid-sirens-in-ukraine) | – | 2022-10 | – |

Prefer the upstream sources. No Hugging Face datasets were found.

### 3.8 Live-only feeds (no history)

- [vadimklimenko.com/map/statuses.json](https://vadimklimenko.com/map/statuses.json): oblast and district states with `enabled_at` in UTC and an `alert_level` field. [measured]
- [ubilling.net.ua/aerialalerts](https://ubilling.net.ua/aerialalerts/): a cache of the Klymenko feed with local time; it returned 429 on repeated requests. [measured]
- [NEPTUN](https://neptun.in.ua/developers): keyless REST and WebSocket feed of threats with coordinates. It is a snapshot only, with no history, and requires attribution.
- alerts.com.ua: returns 404 (dead). [measured]

### 3.9 Air Force @kpszsu (Повітряні Сили ЗСУ, Ukrainian Air Force)

- **Channel:** [@kpszsu](https://t.me/s/kpszsu), 909K subscribers, posts from 2019 → live.
- **Real-time posts:** messages such as "🏍 Реактивний БпЛА на Київ" ("jet drone heading for Kyiv"), KAB and ballistic warnings. Some are edited after posting.
- **Morning summary:** for example [84703](https://t.me/kpszsu/84703), posted 2026-10-10 06:20 UTC. It reads "У ніч на 10 жовтня (з 18:00 09 жовтня)… станом на 09:00" ("On the night of 10 October (from 18:00 on 9 October)… as of 09:00"). So the 18:00 → 09:00 Kyiv window is published at about 09:20 Kyiv, and the attack may still be under way ("Атака триває", "the attack continues").
- **Monthly totals** are also posted (for example on 2026-10-10).

### 3.10 "Massive Missile Attacks on Ukraine" (Petro Ivaniuk, Kaggle)

- **Source:** [Kaggle `piterfm/massive-missile-attacks-on-ukraine`](https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine). Built manually from Air Force and General Staff posts. CC BY-NC-SA 4.0. Version 214, with notes such as "Update 2026-10-10"; updates are roughly weekly.
- **Download:** the Kaggle API download worked without a key. [measured]
- **`missile_attacks_daily.csv` [measured]:**
  - 4,224 rows, from `time_start` 2022-09-28 to `time_end` 2026-10-10 09:00.
  - `time_start`/`time_end` are **Kyiv local event windows**, and 58% have no time of day.
  - Other fields: `model, launch_place, target, launched, destroyed, not_reach_goal, still_attacking, num_hit_location, …, source`.
- **Reporting change:** the dataset notes that "The Ukrainian Air Force has stopped reporting the number of some kind of missiles launched and intercepted since August 10, 2026."
- **Related:** cumulative General Staff losses, including UAVs and cruise missiles, are available from [PetroIvaniuk/2022-Ukraine-Russia-War-Dataset](https://github.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset) (MIT, daily) and the [russianwarship.rip API](https://russianwarship.rip/api/v2/statistics/latest) (day 1690 = 2026-10-10). [measured]

### 3.11 Telegram monitoring channels

All of these are public, active on 2026-10-10, and can be paged back to their first post through `t.me/s/<channel>?before=<id>`. [measured]

| Channel | Subscribers | First post |
|---|---|---|
| @war_monitor ("monitor") | 970K | 2022-04-25 |
| @radar_raketaa («Куди летить?», "Where is it flying?") | 500K | 2022-10-21 |
| @deraketaua («Де Ракета», "Where's the missile") | 156K | 2022-09-29 |
| @UkraineAlarmSignal | 84.4K | 2022-02-25 |

- **Collection:** Telethon (bulk, 100 messages per request; mind FloodWait) or web-preview scraping at 20 posts per page.
- **Edits:** the web preview shows only the *latest* edit and marks edited posts with "edited".

### 3.12 Weather (Open-Meteo, Visual Crossing)

- **Open-Meteo [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api):** "each run's first few hours are stitched" into one series, starting about 2022 (ECMWF IFS 0.4° from 2022-11-07). It is close to analysis, so it **leaks** if used for the target period.
- **Open-Meteo [Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api):** request `var_previous_dayN`, which is the value predicted N×24 h before the valid time. Most models are archived from Jan 2024 (GFS from 2021). The **Single Runs API** returns full runs by initialisation time (`&run=`); its availability dates are **unverified**.
- **Open-Meteo terms:** free non-commercial use under 10,000 calls a day, 5,000 an hour and 600 a minute; data under CC BY 4.0 ([terms](https://open-meteo.com/en/terms)).
- **Visual Crossing:** archived forecasts through `forecastBasisDate`/`forecastBasisDay` ([docs](https://www.visualcrossing.com/resources/documentation/weather-data/how-to-query-weather-forecasts-from-the-past-historical-forecasts/)). Needs a key; plan limits are **unverified**.

### 3.13 ISW daily assessments

- **Source:** [understandingwar.org](https://understandingwar.org/research/russia-ukraine/russian-offensive-campaign-assessment-october-9-2026/). Pages can be scraped with a browser user agent. They contain the Air Force strike numbers in prose.
- **Timing [measured from `article:published_time`]:**
  - The data cutoff is 11:45 AM–12:45 PM ET on day D.
  - Publication runs from **22:29 UTC on D to 03:35 UTC on D+1** (01:29–06:35 Kyiv time).
  - Reports are modified up to about 20 h later (for example, the Oct 5 report was modified 2026-10-06 20:38 UTC).

### 3.14 ACLED

- **API:** [OAuth token API](https://acleddata.com/api-documentation/getting-started) with a myACLED account.
- **Access:** a gmail address gives the "Open" level, which does not include API access according to the [FAQ table](https://acleddata.com/myacled-faqs) (the table scraped garbled, so this is partly **unverified**).
- **Update schedule:** Europe event data is uploaded weekly on Tuesday (covering Saturday–Friday), with an expedited upload on Thursday ([schedule](https://acleddata.com/use-access/when-are-acled-data-updated)).
- **`timestamp`:** the Unix time of upload or update ([codebook](https://acleddata.com/methodology/acled-codebook)).
- **Value here:** low.

### 3.15 GDELT 2.0

- **Feed:** a new file every 15 minutes since 2015-02-18; the latest was `20261010183000`. [measured, [lastupdate.txt](http://data.gdeltproject.org/gdeltv2/lastupdate.txt)]
- **Time fields:** `DATEADDED` is when the event was added, in UTC; `Day` is the event date ([codebook](http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf)).
- **DOC 2.0 API:** a rolling 3-month window, up to 250 records ([announcement](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)).
- **Python client:** `gdeltdoc`.

### 3.16 VIINA 2.0 and DeepStateMap

- **[VIINA](https://github.com/zhukovyuri/VIINA)** (Zhukov, Georgetown University; ODbL):
  - Geocoded news events with `date`/`time` of the *report*, plus daily territorial control.
  - "Data update" commits roughly every 1–6 days (latest 2026-10-09). The files are in Git LFS.
  - Event labels come from a BERT model, and the `*_latest` files are overwritten on each release.
  - The timezone of `time` is **unverified**.
- **[DeepStateMap](https://deepstatemap.live)** (undocumented endpoint `/api/history/public`) [measured]:
  - 1,781 map updates from 2022-04-03 to 2026-10-08, with `createdAt`/`updatedAt`.
  - `/api/history/{id}/geojson` returns polygons.
  - 6% of updates were edited more than 24 h after creation.
  - No terms page was found.

### 3.17 Calendar

- **Holidays:** `holidays` 0.106. Under martial law (Law 2136-IX), `holidays.Ukraine(years=2025)` returns **0** holidays. Use `categories=("public", "workday")`, which gives 11 for 2025/2026. [measured]
- **Astronomical features:** moon phase, sunrise and sunset can be computed deterministically and carry no leakage.

### 3.18 Timeline of breaks and regime changes

| Date | Event |
|---|---|
| 2022-04-04 | Permanent Luhansk alert starts |
| 2022-12-10 | Permanent Crimea alert starts |
| 2024-05 | Standing hromada alerts begin (Lyptsi, Vovchansk) |
| 2025 (from about Aug) | Raion-level pilots; Kyiv oblast in July |
| **2025-12-15** | Nationwide raion-level alerting except Donetsk and Luhansk ([Svyrydenko](https://t.me/svyrydenkoy/1179)); Air Force → ДСНС signal time cut to 8–15 s |
| 2026-08-10 | Air Force stops reporting some missile counts |
| 2026-08-29 → 09-02 | @air_alert_ua outage |
| 2026-09-04 | Resolution 1092: yellow = drone threat, red = missile, missile-drone or massed drone threat |
| **2026-09-07** | First yellow alerts in the data; @air_alert_ua stops |
| 2026-09-15 | Resolution 1128 amends 1092 (secondhand reports; **unverified**) |

---

## 4. Leakage checklist

General rule: a feature is usable at forecast time *T* only if its **availability time** (publication, upload or edit) is at or before *T*. The event time alone is not enough. Store everything in UTC and convert naive Kyiv times with `Europe/Kyiv`, taking care with ambiguous hours at the DST change.

| Source | What to align on | Rules |
|---|---|---|
| Vadimkin official/volunteer | `started_at` (UTC, about the Telegram post time) | Deduplicate. The state at T comes from rows with `started_at ≤ T`; if `finished_at > T`, treat the alert as **ongoing and censored at T**. Never use durations of alerts unfinished at T. Synthetic ends (+1 h, `naive` +30 min) were set *later*; flag them. A row appears only after the alert ends and after the next daily run (about 29 h worst case), so a real-time pipeline must use the API or Telegram. |
| alerts.in.ua / ukrainealarm / map history | `started_at` / `startDate` | Same censoring rule. `finished_at` and `updated_at` fill in later. Snapshot API answers with the retrieval time. Before 2026-09-07 `red` is a default, not a signal. Evaluate the post-reform period separately. |
| Kyiv Digital | local `dateTimeStart` → UTC | The weekly JSON is published on Mondays; use the live XML for real time. |
| Telegram (official, eTryvoga, monitors, @kpszsu) | `message.date` (UTC) | Drop or mask posts with `edit_date > T`; the web preview always shows the latest edit. Deleted posts cannot be recovered, so archive raw posts as you collect them. |
| Air Force summary / Kaggle missile dataset | post time, **not** `time_start`/`time_end` | The 18:00 → 09:00 window is available at about 09:20 Kyiv. For Kaggle rows use `time_end` + 2 h, or 10:00 Kyiv the next day for date-only rows. Kaggle versions are revised; for strict backtests use a version dated before T. Counts change after 2026-08-10. |
| ISW | `datePublished` (UTC) | **A D+1 shift starting at 00:00 Kyiv is not enough:** reports appear 01:29–06:35 Kyiv on D+1 and are edited up to about 20 h later. Use D+1 07:00 Kyiv at the earliest, or D+2 if you scrape the edited text. |
| ACLED | `timestamp` (upload/update) | Filter on `timestamp ≤ T`, not `event_date`; the lag is 3–10 days. |
| GDELT | `DATEADDED` / `MentionTimeDate` (UTC) | Never `Day`/`SQLDATE`. |
| VIINA | report `date`+`time` | Assume Kyiv time and add a margin. Labels can change between releases. |
| DeepStateMap | `createdAt` | The GeoJSON reflects the latest edit (`updatedAt`). |
| Weather | forecast *issue* time | Observations up to T are fine. For the horizon use Previous Runs `_previous_dayN` with N×24 h ≥ the horizon plus the run-publication delay, or Single Runs with the run time before T. Never use the Historical Forecast, archive or ERA5 values for times after T. |
| Holidays / astronomy | – | No leakage. Use the martial-law categories. |
| Region names | numeric region IDs | Not leakage but a join hazard: names were renamed (Красноградський↔Берестинський, Червоноградський→Шептицький, Володимир-Волинський↔Володимирський, Новомосковський→Самарівський). |

---

## 5. Open questions / unverified

1. **ukrainealarm API:** the current Swagger is behind Cloudflare. Still unknown: rate limits; whether a deeper history endpoint exists (one third party claims `/api/history` with one month); license or terms; whether a key has to be renewed.
2. **map.ukrainealarm.com ranged history:** the exact retention (somewhere between 2025-04-10 and 2025-10-15 as the oldest date) and whether automated use is allowed.
3. **@air_alert_ua:** whether the channel will resume and why it stopped. There has been no announcement since the 2026-08-30 outage notice.
4. **alerts.in.ua:** redistribution terms for history, and whether undocumented periods (`week_ago`) still work. I did not call the authenticated API because I have no token.
5. **Licenses:** Kyiv Digital and the JustJimer archive have none stated. The VIINA `time` timezone is not documented.
6. **Other datasets:** data.gov.ua was under maintenance on 2026-10-10, so I could not search it for other official alert datasets. GUR reports and Resolution 1128 were not checked against primary sources.
7. **Duplicates:** the reason for the duplicate block in the Vadimkin official file (2022-03 → 2026-01 rows repeated) is not documented. Deduplicating is safe because rows are identical to the second.
