"""CourtIQ: local, read-only exploration of precomputed historical tennis data."""
import json
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
from src.analytics import filter_rows, summarize

st.set_page_config(page_title='CourtIQ · Tennis analytics', page_icon='🎾', layout='wide')
st.caption('COURTIQ / HISTORICAL ATP ANALYTICS')
st.title('Same player. Different court.')
st.write('Explore surface performance, compare serve results, and test what rankings can tell us before a match.')
DB = Path('data/processed/courtiq.sqlite')
APP_DATA = Path('data/processed/app_data.parquet')
if not DB.exists() and not APP_DATA.exists():
    st.info('Prepare the historical database first. Follow the Quick start in README.md.')
    st.code('python -m src.download_data\npython -m src.prepare_data\npython -m src.model')
    st.stop()


@st.cache_data
def load_data(path, modified):
    if path.endswith('.parquet'):
        return pd.read_parquet(path)
    with sqlite3.connect(path) as conn:
        return pd.read_sql('SELECT * FROM player_matches', conn)


input_path = DB if DB.exists() else APP_DATA
rows = load_data(str(input_path), input_path.stat().st_mtime_ns)
st.sidebar.header('Explore the data')
years = st.sidebar.slider('Tournament years', int(rows.year.min()), int(rows.year.max()),
                          (int(rows.year.min()), int(rows.year.max())))
surfaces = st.sidebar.multiselect('Surfaces', sorted(rows.surface.unique()), default=sorted(rows.surface.unique()))
players = rows[['player_id', 'player_name']].drop_duplicates('player_id').sort_values('player_name')
labels = dict(zip(players.player_id, players.player_name))
defaults = [p for p in players.player_id if labels[p] in ['Novak Djokovic', 'Rafael Nadal']]
if len(defaults) < 2:
    defaults = list(players.player_id.head(2))
selected = st.sidebar.multiselect('Compare players (choose two)', list(players.player_id),
                                  default=defaults[:2], format_func=lambda x: f'{labels[x]} · {x}', max_selections=2)
section = st.sidebar.radio('Section', ['Overview', 'Player comparison', 'Model evaluation', 'Data and limitations'])
st.sidebar.caption('Samples below 20 matches are flagged, not hidden. This threshold is a display rule, not a significance test.')
filtered = filter_rows(rows, years, surfaces)
st.caption(f'Tournament weeks: {years[0]}–{years[1]} · {", ".join(surfaces) or "No surfaces selected"}')


def table(frame):
    st.dataframe(frame, hide_index=True, use_container_width=True)


def small_sample(frame):
    if (frame.matches < 20).any():
        st.warning('Some groups have fewer than 20 matches. Treat those percentages as small-sample descriptions.')


if section == 'Overview':
    if filtered.empty:
        st.info('No matches for this selection. Choose at least one surface or widen the year range.')
    else:
        a, b, c = st.columns(3)
        a.metric('Unique matches', f'{filtered.match_id.nunique():,}')
        b.metric('Players', f'{filtered.player_id.nunique():,}')
        c.metric('Valid serve-stat coverage', f'{filtered.stats_available.mean():.1%}')
        st.caption('Coverage counts player-match rows; every match contributes two player rows.')
        st.subheader('How much serve data is available?')
        coverage = summarize(filtered, ['year', 'surface'])
        st.line_chart(coverage.pivot(index='year', columns='surface', values='coverage'), y_label='Coverage (0–1)')
        best = coverage.loc[coverage.coverage.idxmax()]
        st.write(f'The highest covered year/surface group in this selection is {int(best.year)} {best.surface}: {best.coverage:.1%} of {int(best.matches):,} player rows.')
        table(coverage[['year', 'surface', 'matches', 'stat_matches', 'coverage']])
        st.subheader('Player surface records')
        summary = summarize(filtered, ['player_name', 'surface'])
        table(summary.sort_values('matches', ascending=False))
        st.caption('Rates use pooled point counts. No missing serve statistics are imputed.')
elif section == 'Player comparison':
    chosen = filter_rows(rows, years, surfaces, selected)
    if chosen.empty:
        st.info('No matches for these filters. Select players with records in the selected years and surfaces.')
    else:
        if len(selected) != 2:
            st.info('Choose two players in the sidebar for a side-by-side comparison.')
        st.subheader('Win rate over time')
        yearly = summarize(chosen, ['year', 'player_name'])
        st.line_chart(yearly.pivot(index='year', columns='player_name', values='win_rate'), y_label='Win rate (0–1)')
        st.caption('Yearly changes describe observed results; opponent strength and event schedules also change.')
        small_sample(yearly)
        table(yearly[['year', 'player_name', 'matches', 'wins', 'win_rate', 'coverage']])
        st.subheader('Surface performance')
        surface = summarize(chosen, ['surface', 'player_name'])
        st.bar_chart(surface.pivot(index='surface', columns='player_name', values='win_rate'), y_label='Win rate (0–1)')
        st.caption('Both players use the same year and surface filters; schedules and opponents can still differ.')
        small_sample(surface)
        table(surface[['surface', 'player_name', 'matches', 'wins', 'win_rate', 'coverage']])
        st.subheader('Serve points won')
        serve = summarize(chosen, ['player_name'])
        st.bar_chart(serve.set_index('player_name')[['first_serve_won', 'second_serve_won']], y_label='Points won / opportunities')
        st.caption('First-serve rate uses first serves in; second-serve rate includes double faults among opportunities. Missing/inconsistent records are excluded from both rates.')
        table(serve)
elif section == 'Model evaluation':
    st.subheader('A deliberately small pre-match experiment')
    st.info('These are fixed chronological evaluation results. Sidebar filters do not retrain or alter the model.')
    path = Path('reports/model_evaluation.json')
    if not path.exists():
        st.warning('No measured evaluation yet. Run python -m src.model after preparing all years.')
    else:
        report = json.loads(path.read_text())
        st.write(f'Train: 2016–2023 · validation: 2024 · final test: 2025. Selected on validation log loss: **{report["selected_model"]}**. Refit: 2016–2024.')
        st.subheader('Validation — model selection')
        table(pd.DataFrame(report['validation']).T.reset_index(names='model'))
        st.subheader('Final historical test')
        table(pd.DataFrame(report['final_test']).T.reset_index(names='model'))
        st.caption('Lower log loss is better. The deterministic ranking rule has no probability log loss. The non-selected model is shown for transparency; test scores did not select the model.')
        table(pd.DataFrame(report['splits']).T.reset_index(names='split'))
        st.subheader('Final test by surface')
        for surface, result in report['surface_breakdown'].items():
            st.write(f'**{surface}** · {result["matches"]:,} eligible matches · ranking rule accuracy {result["ranking_rule_accuracy"]:.1%}')
            table(pd.DataFrame({k:v for k,v in result.items() if isinstance(v,dict)}).T.reset_index(names='model'))
else:
    st.subheader('Read the denominators before the percentages')
    st.markdown('''- Source: [TennisMyLife historical ATP database](https://github.com/Tennismylife/TML-Database), inspired by Jeff Sackmann. Educational, non-commercial use; see source terms before redistribution.
- Tournament dates identify tournament weeks, not exact match dates. Annual file coverage is audited, not guaranteed complete.
- Walkovers/defaults, invalid keys/dates/players, duplicates, and unknown surfaces are excluded sequentially. Retirements remain included.
- A match appears once in `matches` and twice in `player_matches`. Missing or inconsistent serve counts remain missing.
- Surface differences are descriptive, not causal. No coaching, injury, or betting claims.
- Models use pre-match rankings/ages only; current-match statistics never enter predictors. Historical accuracy does not guarantee future performance.''')
    quality = Path('reports/data_quality.json')
    if quality.exists():
        st.json(json.loads(quality.read_text()))
    st.caption('Source revision and SHA256 hashes are recorded in reports/source_manifest.json. No account, API key, or live data service is required.')
