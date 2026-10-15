"""Audited match cleaning and SQLite export; never impute match outcomes or stats."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

KEY = ['tourney_id', 'match_num']
STATS = ['svpt', '1stIn', '1stWon', '2ndWon']


def prepare_matches(raw):
    raw = raw.copy()
    counts = {'raw_matches': len(raw), 'excluded': {}}
    def exclude(mask, reason):
        nonlocal raw
        counts['excluded'][reason] = int(mask.sum())
        raw = raw.loc[~mask].copy()
    exclude(raw[KEY].isna().any(axis=1), 'missing_key')
    exclude(raw.duplicated(KEY), 'duplicate_match_key')
    exclude(raw[['winner_id', 'loser_id', 'winner_name', 'loser_name']].isna().any(axis=1), 'missing_player')
    exclude(raw.winner_id.astype(str).eq(raw.loser_id.astype(str)), 'same_player')
    raw['date'] = pd.to_datetime(raw.tourney_date.astype(str), format='%Y%m%d', errors='coerce')
    exclude(raw.date.isna(), 'invalid_date')
    exclude(~raw.surface.isin(['Hard', 'Clay', 'Grass', 'Carpet']), 'unknown_surface')
    exclude(raw.score.fillna('').str.contains(r'W/O|DEF', case=False, regex=True), 'walkover_or_default')
    raw['year'] = raw.date.dt.year
    raw['match_id'] = raw.tourney_id.astype(str) + ':' + raw.match_num.astype(str)
    raw['date'] = raw.date.dt.strftime('%Y-%m-%d')
    rows = []
    invalid = 0
    for side, opponent, won in [('w', 'l', 1), ('l', 'w', 0)]:
        label = 'winner' if won else 'loser'
        other = 'loser' if won else 'winner'
        frame = raw[['match_id', 'date', 'year', 'surface']].copy()
        frame['player_id'] = raw[f'{label}_id'].astype(str)
        frame['player_name'] = raw[f'{label}_name']
        frame['opponent_id'] = raw[f'{other}_id'].astype(str)
        frame['won'] = won
        for stat in STATS:
            frame[stat] = pd.to_numeric(raw[f'{side}_{stat}'], errors='coerce')
        complete = frame[STATS].notna().all(axis=1)
        valid = complete & (frame[STATS] >= 0).all(axis=1)
        valid &= (frame.svpt > 0) & (frame['1stIn'] <= frame.svpt)
        valid &= (frame['1stWon'] <= frame['1stIn']) & (frame['2ndWon'] <= frame.svpt - frame['1stIn'])
        invalid += int((complete & ~valid).sum())
        frame['stats_available'] = valid.astype(int)
        frame.loc[~valid, STATS] = np.nan
        rows.append(frame)
    players = pd.concat(rows, ignore_index=True)
    counts.update(retained_matches=len(raw), player_rows=len(players),
                  invalid_complete_stat_rows=invalid,
                  valid_stat_player_rows=int(players.stats_available.sum()),
                  by_year={str(k): int(v) for k, v in raw.groupby('year').size().items()},
                  missing_rank_matches=int((pd.to_numeric(raw.winner_rank, errors='coerce').isna() |
                                            pd.to_numeric(raw.loser_rank, errors='coerce').isna()).sum()))
    assert counts['raw_matches'] == counts['retained_matches'] + sum(counts['excluded'].values())
    return raw, players, counts


def build(start=2016, end=2025, output='data/processed/courtiq.sqlite', report='reports/data_quality.json'):
    manifest = json.loads(Path('data/raw/manifest.json').read_text())
    frames = []
    for year in range(start, end + 1):
        path = Path(f'data/raw/{year}.csv')
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['files'][path.name]['sha256']:
            raise ValueError(f'Source hash mismatch: {path}')
        frames.append(pd.read_csv(path, dtype={'winner_id': str, 'loser_id': str}))
    matches, players, audit = prepare_matches(pd.concat(frames, ignore_index=True))
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output) as connection:
        matches.to_sql('matches', connection, index=False, if_exists='replace')
        players.to_sql('player_matches', connection, index=False, if_exists='replace')
        players[['player_id', 'player_name']].drop_duplicates('player_id', keep='last').to_sql(
            'players', connection, index=False, if_exists='replace')
        connection.execute('CREATE UNIQUE INDEX match_key ON matches(match_id)')
        connection.execute('CREATE UNIQUE INDEX player_match_key ON player_matches(match_id,player_id)')
    Path(report).parent.mkdir(parents=True, exist_ok=True)
    Path(report).write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=2016)
    parser.add_argument('--end', type=int, default=2025)
    parser.add_argument('--output', default='data/processed/courtiq.sqlite')
    parser.add_argument('--report', default='reports/data_quality.json')
    build(**vars(parser.parse_args()))
