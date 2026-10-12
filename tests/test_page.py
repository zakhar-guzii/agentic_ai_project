import xml.etree.ElementTree as ET

import pandas as pd
import pytest

from alerts import page
from alerts.features import OBLASTS


def marks(svg, tag, cls):
    """The elements of one tag and class in an SVG string."""
    return [e for e in ET.fromstring(svg).iter(tag) if e.get("class") == cls]


def box(rect):
    return {k: float(rect.get(k)) for k in ("x", "y", "width", "height")}


def test_weekly_bars_stack_red_then_yellow_on_one_scale_and_grey_has_no_level():
    # week A: before the splice, no level known; week B: red 0.10 and yellow 0.30 of the time
    weeks = pd.DataFrame({"red": [0.0, 0.10], "yellow": [0.0, 0.30], "grey": [0.25, 0.0]},
                         index=["2026-08-31", "2026-09-14"])
    svg = page.bars(weeks, {})
    grey, red, yellow = (marks(svg, "rect", c) for c in ("grey", "red", "yellow"))
    assert (len(grey), len(red), len(yellow)) == (1, 1, 1)  # no empty segments: A has no red or yellow, B no grey
    grey, red, yellow = box(grey[0]), box(red[0]), box(yellow[0])
    full = red["height"] + yellow["height"]  # week B, 0.4 of the time
    assert grey["height"] / full == pytest.approx(0.625)
    assert red["height"] / full == pytest.approx(0.25)
    assert yellow["y"] + yellow["height"] == pytest.approx(red["y"])  # yellow sits on red
    assert grey["y"] + grey["height"] == pytest.approx(red["y"] + red["height"])  # one baseline
    assert grey["x"] < red["x"]  # weeks in order
    grid = sorted(float(g.get("y1")) for g in marks(svg, "line", "grid"))
    assert len(grid) == 5 and grid[0] == pytest.approx(yellow["y"])  # gridlines at 0-40%; B reaches the top one


def test_reliability_puts_each_bin_at_its_mean_forecast_and_observed_share():
    t = pd.DataFrame({"n": [10, 20], "forecast": [0.3, 0.2], "observed": [0.3, 0.6]})
    svg = page.reliability({3: t})
    diag, pts = marks(svg, "line", "diag"), marks(svg, "circle", "h3")
    assert (len(diag), len(pts)) == (1, 2)
    x0, y0, x1, y1 = (float(diag[0].get(k)) for k in ("x1", "y1", "x2", "y2"))  # from (0, 0) to (1, 1)
    at = [((float(c.get("cx")) - x0) / (x1 - x0), (float(c.get("cy")) - y0) / (y1 - y0)) for c in pts]
    assert at == [pytest.approx((0.3, 0.3)), pytest.approx((0.2, 0.6))]  # a calibrated bin sits on the diagonal
    assert float(pts[1].get("cy")) < float(pts[0].get("cy"))  # a higher share is drawn higher


def test_the_map_has_one_tile_per_region_coloured_by_its_state_now():
    assert set(page.TILES) == set(OBLASTS) and len(set(page.TILES.values())) == len(OBLASTS)  # distinct cells
    rows = pd.DataFrame({"obl": OBLASTS, "under": 0, "level": None, "p3": 0.5})
    rows.loc[rows.obl == 8, ["under", "level", "p3"]] = [1, "red", float("nan")]  # Volynska
    rows.loc[rows.obl == 5, ["under", "level", "p3"]] = [1, "yellow", float("nan")]  # Rivnenska
    rows.loc[rows.obl == 27, "p3"] = 0.344  # Lvivska, clear
    names = {o: f"r{o} область" for o in OBLASTS}
    tiles = {t.text: (t.get("class"), t.find("b").text) for t in ET.fromstring(page.tiles(rows, names)).iter("div")
             if "tile" in t.get("class").split()}
    assert len(tiles) == 24
    assert (tiles["r8"][0], tiles["r5"][0], tiles["r27"]) == ("tile red", "tile yellow", ("tile clear", "34%"))


def test_the_live_score_shows_replays_apart_with_the_revision_check():
    s = pd.DataFrame({"hours": [1, 3], "forecast": ["replay", "live"], "n": [11, 11], "moments": [1, 1],
                      "base_rate": [0.2, 0.4], "model": [0.1, 0.2], "clim28": [0.12, 0.22], "recent7": [0.11, 0.21],
                      "revised_rows": [0, 2], "still_clear": [11, 10], "model_logged": [0.1, 0.19],
                      "model_recomputed": [0.1, 0.18]}).set_index(["hours", "forecast"])
    table = ET.fromstring(page.scored(s))
    heads = [th.text for th in table.iter("th")]
    assert [h for h in heads if h in ("replay", "live")] == ["replay", "live"]  # one row per kind, never pooled
    for col in ("still clear", "Brier, logged", "Brier, recomputed", "revised rows"):
        assert col in heads
    assert "0.1800" in [td.text for td in table.iter("td")]  # the recomputed Brier of the live 3 h row


def test_the_model_switch_has_one_button_per_panel_and_shows_the_first_panel_first():
    out = page.switch({"v1 logistic": "<p>one</p>", "v2 <LightGBM>": "<p>two</p>"})
    assert out.count('type="radio"') == 2 and out.count(" checked") == 1 and 'id="m0" checked' in out
    assert '<label for="m1">v2 &lt;LightGBM&gt;</label>' in out  # labels are escaped
    assert '<div class="panel p0"><p>one</p></div>' in out and '<div class="panel p1"><p>two</p></div>' in out
    # CSS only: every panel is hidden unless the radio before it is checked
    assert ".panel{display:none}" in page.CSS and all(f"#m{i}:checked~.p{i}" in page.CSS for i in range(2))
