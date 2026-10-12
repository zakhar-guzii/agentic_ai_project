"""Pure HTML rendering: all three model panels come from logged predictions."""
import html
import pandas as pd
from alert_outlook.presentation import graphics as G
from alert_outlook.presentation.history import kyiv
from alert_outlook.settings import FAMILIES
from alert_outlook.forecasting.features import HOURS
from alert_outlook.forecasting.live import NOTE
from alert_outlook.data.history import MAP_CUTOFF, REFORM, SPLICE


def table(frame, fmt='{:.3f}'):
    return '<div class="scroll">' + frame.to_html(border=0, na_rep='', float_format=fmt.format) + '</div>'


def forecast_table(rows, names):
    return pd.DataFrame({'now': rows.level.map({'red': '🔴 alert', 'yellow': '🟡 alert'}).fillna('clear').to_numpy(),
        **{f'{h} h': (rows[f'p{h}'] * 100).map('{:.0f}%'.format).where(rows.under == 0, '').to_numpy() for h in HOURS}},
        index=pd.Index(rows.obl.map(names), name='region')).sort_index()


def render(rows, names, history, quality=None, scores=None):
    lo, daily, weekly, per, regional, levels = history
    asof = rows.ts.max()
    panels = {}
    for family, label in FAMILIES.items():
        part = rows[rows.model == family]
        if len(part) != 24 or part.obl.nunique() != 24:
            raise ValueError(f'{family}: page requires one logged forecast for every modeled region')
        made = part.made_at.iloc[0]
        kind = 'replay from saved data' if made >= asof + pd.Timedelta('6h') else 'made before the 6 h window closed'
        panel = f'<p class="small">{html.escape(label)}: {kind}; made at {kyiv(made):%Y-%m-%d %H:%M} Kyiv.</p>'
        panel += G.tiles(part, names) + table(forecast_table(part, names))
        if quality is not None and not quality.empty:
            q = quality[quality.forecast.replace('gbm', 'lightgbm') == family]
            columns = [c for c in ['period','horizon','threshold','n','f1','brier','precision','recall','ap','auc'] if c in q]
            if not q.empty:
                panel += '<h3>Historical model quality</h3>' + table(q[columns], '{:.4f}')
        if scores is not None and not scores.empty:
            s = scores[(scores.model == family) & (scores.model_sha256 == part.model_sha256.iloc[0])]
            if not s.empty: panel += '<h3>Logged forecast scores</h3>' + G.scored(s.drop(columns=['model','model_sha256']).rename(
                columns={'model_brier':'model'}).set_index(['hours','forecast']))
        panels[label] = panel
    w = daily.assign(week=daily.day - pd.to_timedelta(daily.day.dt.dayofweek, 'D'), red=daily.red.fillna(0),
            grey=daily.alert.where(daily.red.isna(), 0)).groupby('week')[['minutes','alert','red','grey']].sum()
    weeks = pd.DataFrame({'red': w.red, 'yellow': w.alert - w.red - w.grey, 'grey': w.grey}).div(w.minutes, axis=0)
    weeks.index = weeks.index.strftime('%Y-%m-%d')
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Alert Outlook</title>',
           '<style>' + G.CSS + '</style></head><body><main><header><h1>Alert Outlook</h1>',
           f'<p>Data as of <b>{kyiv(asof):%Y-%m-%d %H:%M} Kyiv</b> ({asof:%H:%M} UTC). '
           'Air-raid alerts in 23 oblasts and Kyiv City.</p></header><section><h2>Now and next hours</h2>',
           '<p>Choose a model with the buttons. Probabilities refer to a new alert within 1, 3 or 6 hours '
           'for regions clear at the forecast time. Regions already under alert have no new-start probability.</p>',
           G.switch(panels), '<p class="small">Historical benchmark and holdout were already examined; '
           'they are descriptive checks, not independent future validation. Regional quality can differ from pooled scores.</p>']
    if quality is None or quality.empty:
        out.append('<p class="small">Historical quality is recorded in the repository README. '
                   'This local MLflow store has no quality results for these weights.</p>')
    out += ['</section><section><h2>History</h2>',
            f'<p>Share under alert: {per["year"].loc["all", "share under alert"]:.1%} from {kyiv(lo):%Y-%m-%d} '
            f'to {kyiv(MAP_CUTOFF):%Y-%m-%d %H:%M} Kyiv. Around the level reform ({kyiv(REFORM):%Y-%m-%d}): '
            f'{regional.loc["all", "share, before"]:.1%} in the 28 days before and '
            f'{regional.loc["all", "share, after"]:.1%} after. These markers do not establish causation.</p>',
            G.bars(weeks, weekly.note.dropna().to_dict()),
            '<p class="small">Red / yellow / grey: red alert, yellow alert, or no historical level before the splice. '
            'Historical levels are final record revisions; the red share is an upper bound.</p>',
            '<details><summary>Per week</summary>' + table(weekly) + '</details>',
            '<details><summary>Per region and reform comparison</summary>' + table(regional) + '</details>',
            f'<details><summary>Alert levels since {kyiv(SPLICE):%Y-%m-%d}</summary>' + table(levels) + '</details>',
            '</section><footer><p class="small">' + html.escape(NOTE) + '</p></footer></main></body></html>']
    return ''.join(out)
