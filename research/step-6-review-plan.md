# Step-6 review fixes, then a live view: refresh button and a real map

Approved by the user on 2026-10-12.

## Context

The step-6 review (6de1891...9936766) found one spec issue and asked for a live scenario:

- **[P2] Live log hides what was scored.** [main.py:491](../main.py#L491) keeps only `n, moments, base_rate, model, clim28, recent7, revised_rows` from `live.summary`. It drops `made_before_window_closed` and the revision check (`still_clear`, `model_logged`, `model_recomputed`). After step 7's fetch, the 2026-10-11 replay (made 20.3 h after T) is scored together with timely forecasts. The table would not show that mix. Decision 6.4 already promised: "Step 7 reports the two separately".
- **Refresh.** The page is a static file. The only refresh path is `fetch` (about 13 min, 2 requests/min) → `predict` → `page`.
- **The user, 2026-10-12, chose the full scope:** the fix, a local server with a "Refresh" button for the current state, and real oblast outlines instead of tiles.

Constraints: aim 20:00 Kyiv, deadline 23:59. The step-7 holdout stays untouched until step 7. The token never reaches the browser, the log or the chat. No new dependency.

## Order and time boxes

| # | Part | Branch | Box |
|---|---|---|---|
| A | Live log fix | `step-6-review` | 30 min |
| B | Step 7 (its own plan, as CLAUDE.md requires) | `step-7-final` | ~1.5 h |
| C | `main.py serve` with a Refresh button | `step-6b-live` | 1 h |
| D | Real oblast map | `step-6b-live` | 1 h |
| E | Step 8 | `step-8-submission` | ~1 h |

- **Cut rule.** If C or D is not merged by 19:00 Kyiv, stop it and go to E. Record the unfinished part as future work in the reflection.
- **Why this order.** The reviewer's priority: fix the Live log and finish the final evaluation first. C and D change only how the page looks, never a score. They come after the scores are frozen and are checked against them.
- **Optional speed-up.** Start `fetch` in the background during A. It only saves data: nothing is predicted or scored until step 7.

---

## A. Live log: replay and timely forecasts reported separately

**`alerts/live.py` `summary`** ([live.py:56](../alerts/live.py#L56))
- Group per horizon and per kind: `live` when `made_at < ts + H`, otherwise `replay`, as Decision 6.4 defines it.
- The index becomes `(hours, forecast)`. Drop `made_before_window_closed`, because the index now carries it.
- All other columns stay, revision check included.
- `main.py score` prints the new table unchanged in form, with one more sentence: "replay = made after its window closed".

**Page** ([main.py:488-491](../main.py#L488-L491))
- Show the full summary with readable headers: n, moments, base rate, Brier model / clim28 / recent7, revised rows, still clear, Brier logged / recomputed.
- Add the same explanatory sentence as `score`.
- The rendering moves to a pure helper, `page.scored(summary)`, so it can be tested without real data.

**Tests (TDD, `tests/test_live.py`, `tests/test_page.py`)**
1. Worked example (red first): log at NOW with `made_at = NOW + 2h`, scored at `asof = NOW + 4h`. The rows are `(1, "replay")` and `(3, "live")`, and the 6 h window is still open. Each group's n and Brier are computed by hand.
2. Update `test_a_region_revised_into_an_alert...`: `.loc[1]` → `.loc[(1, "live")]`.
3. `page.scored`: a synthetic two-row summary renders both kinds and the still-clear / logged / recomputed headers.
4. Mutation: classify by `made_at <= ts + H`, i.e. flip the boundary. A row made exactly at T + H must be a replay.

**Docs:** add PROCESS_LOG "Code review of step 6" → **Wrong #20**, then merge into `main`.

## B. Step 7: the final run

Not planned here: it gets `research/step-7-plan.md` first. What A changes for it:

- After a fresh `fetch` + `predict`, the 2026-10-11 moment is scored as `replay`, and the new moment as `live` once its windows close.
- A second `fetch` about 3 h after the first scores the live 1 h and 3 h windows before the deadline.

## C. `main.py serve`: a local page with a Refresh button

**Decision 9 (PROCESS_LOG).** A local server for viewing only.
- Decisions 1 and 8 stand for the committed artifact: `main.py page` stays offline and byte-deterministic.
- The current state comes from `/v1/alerts/active.json`: one request, normal rate limit 8–10/min. The forecast stays at T, where the saved history ends, because the model needs history up to its moment.
- The page shows both times.

**Code**
- `alerts/api.py`: `active(tok)` → `get("/v1/alerts/active.json", tok)`, which returns the alerts and the fetch time. Reuses `get` and its token redaction.
- `alerts/data.py`: split the normalisation out of `load_api` (air_raid filter, oblast by name, columns) into `_records(alerts, fetched)`. `load_api` keeps its output byte for byte; `active.json` records go through the same rule.
- `alerts/live.py`: extract the level rule from `forecast` ([live.py:16-19](../alerts/live.py#L16-L19)) into `levels(records, at)`: oblast + raion union in the minute before `at`, red when a red record covers it. `forecast` calls it too, so the map "now" and the logged level share one rule.
- `main.py outlook(now=None)`:
  - when `now` is given (a snapshot of `levels` + its time), the map shows the state at that time;
  - the table gets a column "now (HH:MM Kyiv)" next to "at T";
  - the header names both times.
  - With `now=None`, the output is byte-identical to today's.
- `main.py serve`: about 35 lines of stdlib `http.server`, bound to `127.0.0.1` only.
  - `GET /` serves `outlook(now=last)`. `POST /refresh` fetches `active`, then redirects to `/`.
  - A Refresh `<form>` button, no JavaScript.
  - On error the page keeps the last good snapshot and shows a banner with the error and that snapshot's time.
  - A refresh within 60 s of the last one reuses it (the rate limit).
  - Nothing is saved to `data/`: `load_api` and `api_asof` glob that directory.
  - `ponytail:` single-user and in-memory. Add a lock if anyone ever serves this to more than one viewer.

**Tests**
1. `_records` on a hand-written `active.json` body: the oblast comes from `location_oblast`, not `location_oblast_uid` (data trap); `artillery_shelling` is dropped.
2. `levels`: Volyn with a yellow oblast record and a red raion record → red. Rivne with only a hromada record → clear, because only oblast and raion records count. An alert still on (no end) → under.
3. Server, with a fake `active` injected:
   - POST /refresh, then GET / shows the snapshot's time;
   - a failing fetch keeps the old time and shows the banner;
   - the token string never appears in any response.
4. The existing step-6 acceptance test still passes: no `<script`, nothing external, deterministic `page`.

## D. Real oblast outlines instead of tiles

**Source:** geoBoundaries gbOpen UKR ADM1, commit `9469f09`, simplified GeoJSON, from OpenStreetMap.
- 27 units: Crimea, Sevastopol and Kyiv City included.
- Licence: ODbL 1.0. Attribution "© OpenStreetMap contributors" goes in the footer and README.
- Save it to `data/raw/geo/` with a MANIFEST: URL, commit, SHA-256, licence, fetch time.

**`alerts/page.py`**
- `GEO = {shapeName: region id}`, 24 entries, written from the file's names.
- `outline(geojson)` → `{id: SVG path d}`:
  - equirectangular projection × cos(48.5°);
  - points rounded to 0.5 px and repeats dropped, to keep the page small;
  - computed at render time from the raw file, so no derived file is committed.
- `regions(rows, names)` replaces `tiles(rows, names)` with the same signature, so C does not care which one is in use.
  - Each path gets the class red / yellow / clear and a `<title>` with the name and state or P(3 h).
  - The p3 % label sits at the vertex mean. `ponytail:` not a true centroid; switch to a polylabel point if a label falls outside its region.
  - Kyiv City is drawn after Kyivska.
  - Luhansk, Crimea and Sevastopol are grey hatched, "not modelled: permanent alert".
- Delete `TILES` and `tiles` and their CSS.

**Tests:** replace test 3 in `test_page.py`.
- `GEO` covers the 24 `OBLASTS`, each region once.
- On a two-square toy GeoJSON, west stays left and north stays up.
- With Volyn red, Rivne yellow and Lviv at 0.344, the paths carry those classes, and Lviv shows "34%".
- The real-data test: the page stays under about 150 KB.

**Check:** rerun `page` after B. The model-quality and live-log sections must be byte-identical to step 7's frozen page; only the map changes. Then look at it in light and dark mode and at 390 px, as in step 6.

## E. Step 8 additions

README:
- the offline page vs `serve`;
- the refresh path `fetch → predict → page`, about 13 min, with why the forecast lags;
- data licences (ODbL attribution).

The reflection names what C and D do not do: the forecast "now" needs history kept up to now (a collector), which is outside the brief's time.

## Critical files

- [alerts/live.py](../alerts/live.py): `summary`, `levels`
- [alerts/page.py](../alerts/page.py): `scored`, `regions`, `outline`, `GEO`
- [alerts/data.py](../alerts/data.py): `_records`
- [alerts/api.py](../alerts/api.py): `active`
- [main.py](../main.py): `outlook`, `score`, `serve`
- [tests/test_live.py](../tests/test_live.py), [tests/test_page.py](../tests/test_page.py), [tests/test_real_data.py](../tests/test_real_data.py)
- PROCESS_LOG.md (Wrong #20, Decision 9) and CLAUDE.md (Code section, step notes)

## Verification

- `.venv/bin/pytest`: the 112 old tests (two updated) plus the new ones pass. Each test that passes at once gets a mutation, `PYTHONDONTWRITEBYTECODE=1`, caught on the assertion (Wrong #18).
- `main.py page` twice gives the same `shasum`. After A, the only diff in `outlook.html` is the Live log section; after D, only the map.
- `main.py history` and `check`: their reports are byte-identical. `load_api` output is unchanged after the split: compare `D.load_api().equals(...)` against `main`.
- `main.py serve` + `curl -s -X POST localhost:8000/refresh` + `curl -s localhost:8000/`: the snapshot time shows, and `grep -c` of the token in the response is 0. Run it once by hand with the real API.
- Before merging C: `git grep` for the token, and the files under `data/` are unchanged.
