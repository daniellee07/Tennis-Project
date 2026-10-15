import numpy as np
import pandas as pd


def filter_rows(rows, years, surfaces, players=None):
    selected = rows[rows.year.between(*years) & rows.surface.isin(surfaces)]
    if players is not None:
        selected = selected[selected.player_id.isin(players)]
    return selected.copy()


def summarize(rows, groups):
    result = rows.groupby(groups, observed=True).agg(
        matches=('won', 'size'), wins=('won', 'sum'), stat_matches=('stats_available', 'sum'))
    result['win_rate'] = result.wins / result.matches
    result['coverage'] = result.stat_matches / result.matches
    # min_count preserves missing data instead of silently presenting 0%.
    counts = rows.groupby(groups, observed=True)[['svpt', '1stIn', '1stWon', '2ndWon']].sum(min_count=1)
    result['first_serve_won'] = counts['1stWon'] / counts['1stIn'].replace(0, np.nan)
    result['second_serve_won'] = counts['2ndWon'] / (counts.svpt - counts['1stIn']).replace(0, np.nan)
    result['first_serve_opportunities'] = counts['1stIn']
    result['second_serve_opportunities'] = counts.svpt - counts['1stIn']
    return result.reset_index()
