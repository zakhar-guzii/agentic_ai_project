"""The outlook page's pieces: one self-contained HTML file, with inline SVG charts and no script."""
import datetime as dt
import html
import math

W, H, LEFT, TOP, BOTTOM = 720, 180, 36, 16, 20  # weekly chart: width, plot height and margins, in px


def bars(weeks, notes):
    """Weekly columns of the share of time under alert: red, then yellow, then grey where no level is known (before the
    splice). `weeks`: one row per Kyiv week, indexed by its Monday ('YYYY-MM-DD'), with the red, yellow and grey shares
    of time; `notes`: {week: label}, drawn as marker lines. The axis tops at the next 10% at or above the tallest week;
    hovering a week shows its numbers."""
    top = math.ceil(round(weeks.sum(axis=1).max() * 10, 9)) / 10
    y = lambda v: TOP + H * (1 - v / top)
    slot = (W - LEFT) / len(weeks)
    out = [f'<svg viewBox="0 0 {W} {TOP + H + BOTTOM}" role="img" aria-label="Share of time under alert, per week">']
    for k in range(round(top * 10) + 1):
        out.append(f'<line class="grid" x1="{LEFT}" x2="{W}" y1="{y(k / 10):.1f}" y2="{y(k / 10):.1f}"/>'
                   f'<text class="tick" x="{LEFT - 4}" y="{y(k / 10) + 3:.1f}" text-anchor="end">{k * 10}%</text>')
    labelled = False
    for i, (week, r) in enumerate(weeks.iterrows()):
        x, base, parts = LEFT + i * slot, 0.0, []
        for cls, name in (("red", "red"), ("yellow", "yellow"), ("grey", "no level")):
            if r[cls] > 0:
                out.append(f'<rect class="{cls}" x="{x + 1:.1f}" y="{y(base + r[cls]):.1f}" width="{slot - 2:.1f}" '
                           f'height="{H * r[cls] / top:.1f}"/>')
                base += r[cls]
                parts.append(f"{name} {r[cls]:.1%}")
        out.append(f'<rect class="hit" x="{x:.1f}" y="{TOP}" width="{slot:.1f}" height="{H}"><title>Week of {week}: '
                   f'under alert {base:.1%} ({", ".join(parts)})</title></rect>')
        d = dt.date.fromisoformat(week)
        if d.day <= 7:  # a month label under its first Monday; the year on the first label and in January
            label = f"{d:%b %Y}" if d.month == 1 or not labelled else f"{d:%b}"
            out.append(f'<text class="tick" x="{x:.1f}" y="{TOP + H + 14}">{label}</text>')
            labelled = True
        if week in notes:
            end = x > W / 2  # a label near the right edge runs leftwards
            out.append(f'<line class="marker" x1="{x:.1f}" x2="{x:.1f}" y1="{TOP - 2}" y2="{TOP + H}"/>'
                       f'<text class="note" x="{x + (-3 if end else 3):.1f}" y="{TOP - 5}" '
                       f'text-anchor="{"end" if end else "start"}">{html.escape(notes[week])}</text>')
    return "".join(out) + "</svg>"


S, PAD = 220, 34  # reliability chart: plot side and margin, in px


def reliability(tables):
    """Calibration per horizon: each probability bin at its mean forecast (x) and the share of its moments followed by
    a new alert (y). A calibrated forecaster lies on the diagonal. `tables`: {hours: Scores.reliability(...)};
    hovering a point shows its bin."""
    pos = lambda f, o: (PAD + S * f, 10 + S * (1 - o))
    (x0, y0), (x1, y1) = pos(0, 0), pos(1, 1)
    out = [f'<svg class="square" viewBox="0 0 {PAD + S + 10} {S + 10 + PAD}" role="img" '
           'aria-label="Reliability: mean forecast against the observed share">']
    for v in (0, 0.5, 1):
        gx, gy = pos(v, v)
        out.append(f'<line class="grid" x1="{x0}" x2="{x1}" y1="{gy:.1f}" y2="{gy:.1f}"/>'
                   f'<line class="grid" x1="{gx:.1f}" x2="{gx:.1f}" y1="{y0}" y2="{y1}"/>'
                   f'<text class="tick" x="{x0 - 4}" y="{gy + 3:.1f}" text-anchor="end">{v:.0%}</text>'
                   f'<text class="tick" x="{gx:.1f}" y="{y0 + 14}" text-anchor="middle">{v:.0%}</text>')
    out.append(f'<line class="diag" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}"/>')
    for h, t in tables.items():
        pts = [pos(r.forecast, r.observed) for r in t.itertuples()]
        out.append(f'<polyline class="h{h}" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}"/>')
        out += [f'<circle class="h{h}" cx="{x:.1f}" cy="{y:.1f}" r="4"><title>{h} h: mean forecast {r.forecast:.1%}, '
                f'observed {r.observed:.1%}, n = {r.n:,}</title></circle>' for (x, y), r in zip(pts, t.itertuples())]
    return "".join(out) + "</svg>"


# region id -> (row, column) on a schematic map of Ukraine, west to east and north to south. Kyiv City sits above
# Kyivska, which surrounds it; Luhansk and Crimea are not forecast.
TILES = {8: (0, 0), 5: (0, 1), 10: (0, 2), 31: (0, 3), 25: (0, 4), 20: (0, 5),
         27: (1, 0), 21: (1, 1), 3: (1, 2), 14: (1, 3), 19: (1, 4), 22: (1, 5),
         11: (2, 0), 13: (2, 1), 4: (2, 2), 24: (2, 3), 9: (2, 4), 28: (2, 5),
         26: (3, 1), 18: (3, 2), 15: (3, 3), 12: (3, 4),
         17: (4, 3), 23: (4, 4)}


def tiles(rows, names):
    """The schematic map at T: one tile per region in its TILES cell, coloured by its state then (a red or yellow
    alert, or clear); a clear tile shows P(a new alert starts within 3 h). `rows`: one forecast row per region."""
    rows = rows.set_index("obl")
    out = ['<div class="map" lang="uk">']
    for obl, (r, c) in TILES.items():
        x = rows.loc[obl]
        state = x.level if x.under else "clear"
        value = {"red": "🔴 alert", "yellow": "🟡 alert"}.get(state, f"{x.p3:.0%}")
        out.append(f'<div class="tile {state}" style="grid-area:{r + 1}/{c + 1}" title="{html.escape(names[obl])}">'
                   f'{html.escape(names[obl].replace(" область", ""))}<b>{value}</b></div>')
    return "".join(out) + "</div>"


# alert levels wear the status colours (critical, warning) and always come with an icon or a label; the three horizons
# take categorical slots 1-3, validated all-pairs in both modes
CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink-2:#52514e;--muted:#898781;
--grid:#e1e0d9;--tile:#f0efec;--red:#d03b3b;--yellow:#fab219;--h1:#2a78d6;--h3:#eb6834;--h6:#1baf7a}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;
--ink-2:#c3c2b7;--grid:#2c2c2a;--tile:#2c2c2a;--h1:#3987e5;--h3:#d95926;--h6:#199e70}}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:880px;margin:0 auto;padding:16px}
section{background:var(--surface);border-radius:12px;padding:16px;margin:16px 0}
h1{font-size:26px;margin:8px 0 0}h2{font-size:19px;margin:0 0 8px}
p,li{color:var(--ink-2)}.small{font-size:13px}footer{overflow-wrap:anywhere}
.scroll{overflow-x:auto}
table{border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums;margin:8px 0}
th,td{padding:4px 10px;border-bottom:1px solid var(--grid);text-align:right;white-space:nowrap}
tbody th{text-align:left;font-weight:normal}
svg{display:block;width:100%;height:auto;margin:8px 0}svg.square{max-width:300px}
svg text{fill:var(--muted);font-size:10px}svg .note{fill:var(--ink-2)}
.grid,.diag{stroke:var(--grid);stroke-width:1}.diag{stroke:var(--muted)}.marker{stroke:var(--ink-2);stroke-width:1}
rect.red{fill:var(--red)}rect.yellow{fill:var(--yellow)}rect.grey{fill:var(--muted)}
rect.hit{fill:transparent}rect.hit:hover{fill:var(--ink);fill-opacity:.07}
polyline{fill:none;stroke-width:2;stroke-linejoin:round}
polyline.h1{stroke:var(--h1)}polyline.h3{stroke:var(--h3)}polyline.h6{stroke:var(--h6)}
circle{stroke:var(--surface);stroke-width:2}circle.h1{fill:var(--h1)}circle.h3{fill:var(--h3)}circle.h6{fill:var(--h6)}
.map{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px;max-width:640px;margin:8px 0}
.tile{background:var(--tile);border-radius:6px;padding:6px;min-height:48px;font-size:12px;line-height:1.25;
hyphens:auto;overflow-wrap:anywhere}
.tile b{display:block;font-size:15px;margin-top:2px}
.tile.red{background:var(--red);color:#fff}.tile.yellow{background:var(--yellow);color:#0b0b0b}
.key{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 4px 0 10px}
.key.red{background:var(--red)}.key.yellow{background:var(--yellow)}.key.grey{background:var(--muted)}
.key.clear{background:var(--tile);outline:1px solid var(--muted)}
.key.h1{background:var(--h1)}.key.h3{background:var(--h3)}.key.h6{background:var(--h6)}
details{margin:8px 0}summary{cursor:pointer;color:var(--ink-2)}
@media (max-width:480px){.tile{font-size:10px;padding:4px}.tile b{font-size:13px}}
"""
