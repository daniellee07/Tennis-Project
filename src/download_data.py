"""Download immutable annual source files with integrity-checked cache reuse."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

SOURCE_COMMIT = 'c5537eed87d8a76f3adb598cdf506d885872923b'
SOURCE = 'https://raw.githubusercontent.com/Tennismylife/TML-Database'


def download(start=2016, end=2025, root=Path('data/raw')):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if manifest and manifest['source_commit'] != SOURCE_COMMIT:
        raise ValueError('Source snapshot changed; use a separate raw directory.')
    manifest.update(source_commit=SOURCE_COMMIT, source_repository='Tennismylife/TML-Database')
    files = manifest.setdefault('files', {})
    for year in range(start, end + 1):
        name = f'{year}.csv'
        path = root / name
        if path.exists():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if name not in files or digest != files[name]['sha256']:
                raise ValueError(f'Unverified or modified cache: {path}')
            print(f'Verified cached {year}')
            continue
        url = f'{SOURCE}/{SOURCE_COMMIT}/{name}'
        with urlopen(url, timeout=60) as response:
            content = response.read()
        if not content.startswith(b'tourney_id,'):
            raise ValueError(f'Unexpected CSV header: {year}')
        path.write_bytes(content)
        files[name] = dict(url=url, sha256=hashlib.sha256(content).hexdigest(),
                           retrieved_at=datetime.now(timezone.utc).isoformat(), bytes=len(content))
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
        print(f'Downloaded {year}: {len(content):,} bytes')
    # Keep a shareable provenance record, without redistributing source CSVs.
    Path('reports').mkdir(exist_ok=True)
    Path('reports/source_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=2016)
    parser.add_argument('--end', type=int, default=2025)
    args = parser.parse_args()
    if not 1968 <= args.start <= args.end <= 2025:
        parser.error('Expected 1968 <= start <= end <= 2025')
    download(args.start, args.end)
