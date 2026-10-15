"""Export compact app input locally; publication requires source-term review."""
import sqlite3
from pathlib import Path
import pandas as pd


def export(database='data/processed/courtiq.sqlite', output='data/processed/app_data.parquet'):
    with sqlite3.connect(database) as conn:
        rows = pd.read_sql('SELECT * FROM player_matches', conn)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    rows.to_parquet(output, index=False)
    print(f'Exported {len(rows):,} player rows to {output} ({Path(output).stat().st_size:,} bytes)')


if __name__ == '__main__':
    export()
