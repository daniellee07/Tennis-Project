"""Integration checks: saved SQL and pandas agree on real filtered data."""
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from src.analytics import filter_rows, summarize


def main():
    with sqlite3.connect('data/processed/courtiq.sqlite') as conn:
        for path in sorted(Path('sql').glob('*.sql')):
            result = pd.read_sql(path.read_text(), conn)
            if result.empty:
                raise AssertionError(f'No results from {path}')
            print(f'{path.name}: {len(result):,} rows')
        rows = pd.read_sql('SELECT * FROM player_matches', conn)
        for lo, hi, surface in [(2016, 2023, 'Clay'), (2024, 2024, 'Hard'), (2025, 2025, 'Grass')]:
            frame = filter_rows(rows, (lo, hi), [surface])
            actual = summarize(frame, ['surface']).iloc[0]
            expected = pd.read_sql('''SELECT COUNT(*) n, AVG(won) win_rate,
                AVG(stats_available) coverage, 1.0*SUM("1stWon")/NULLIF(SUM("1stIn"),0) serve
                FROM player_matches WHERE year BETWEEN ? AND ? AND surface=?''', conn,
                params=(lo, hi, surface)).iloc[0]
            assert actual.matches == expected.n
            np.testing.assert_allclose([actual.win_rate,actual.coverage,actual.first_serve_won],
                                       [expected.win_rate,expected.coverage,expected.serve])
            print(f'SQL/pandas agree: {lo}–{hi} {surface}, {int(expected.n):,} player rows')
        assert len(rows) == 2 * rows.match_id.nunique()
    print('Integration checks passed.')


if __name__ == '__main__':
    main()
