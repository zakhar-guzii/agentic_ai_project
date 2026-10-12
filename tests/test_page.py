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
