# Tennis Project

A project for tennis players.

---

# CourtIQ 🎾

**How does tennis performance vary by surface—and can a small pre-match model improve on rankings?**

CourtIQ is a reproducible Python/SQL analytics project with an interactive
Streamlit app, an audited historical ATP dataset, and a chronological model
comparison. Built with AI assistance; review and understand the implementation
before representing it in an interview.

## What works

- Immutable annual data downloads, SHA256 provenance, integrity-checked cache.
- Sequential exclusion audit and three SQLite tables with explicit row grains.
- Five saved SQL queries, pooled serve rates, missing-data coverage and sample sizes.
- Four dashboard sections: Overview, Player comparison, Model evaluation, Data and limitations.
- Four chart types with shared year/surface/player filters and empty-state handling.
- Pre-match ranking baseline and two logistic regressions; train-only preprocessing.
- Chronological train/validation/test evaluation, saved predictions and code hashes.
- Unit, SQL integration and real Streamlit execution tests.

## Quick start

Python **3.12** is the tested runtime. Run every command from this repository root.
No paid APIs, credentials or external database service are required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m src.download_data --start 2016 --end 2025
python -m src.prepare_data
python -m pytest -q
python -m src.verify
python -m streamlit run app.py
```

The download is about 6 MB. The downloader pins source commit
`c5537eed87d8a76f3adb598cdf506d885872923b` and verifies cached files.
It needs HTTPS access to `raw.githubusercontent.com`; installation needs PyPI.
Do not silently switch to the latest source version when reproducing results.

The checked-in `reports/model_evaluation.json` is the frozen measured run.
To **independently reproduce** it, first preserve that report elsewhere, then run
`python -m src.model --force`. The overwrite flag is deliberately explicit:
never retune the model using 2025 test outcomes. Predictions are written locally
to `data/processed/test_predictions.csv`. See [MODEL_DESIGN.md](MODEL_DESIGN.md).

## Measured results

| Item | Result |
|---|---:|
| Raw source rows, 2016–2025 | 27,772 |
| Retained unique matches | 26,966 |
| Player-match rows (not unique matches) | 53,932 |
| Valid serve-stat player rows | 52,202 (96.79%) |
| Training eligible matches, 2016–2023 | 21,154 |
| Validation eligible matches, 2024 | 3,084 |
| Final eligible matches, 2025 | 2,292 |
| Ranking rule test accuracy | 65.23% |
| Rank-only logistic test accuracy / log loss | 65.23% / 0.62813 |
| Expanded logistic test accuracy / log loss | 64.18% / 0.62671 |

Validation log loss selected the expanded design, not final-test accuracy.
It **did not beat the ranking rule on accuracy**. No statistically significant
improvement or real user impact is claimed. This snapshot is historical and
incomplete in places; these counts are not official season totals.

## Repository map

```text
app.py                    Streamlit dashboard (reads precomputed data)
src/download_data.py      Pinned downloads and source manifest
src/prepare_data.py       Cleaning, audit and SQLite build
src/analytics.py          Shared filters and pooled metric calculations
src/model.py              Pre-match time-split experiment
src/verify.py             SQL/pandas checks on real data
src/export_app.py         Compact local app-data export
sql/                      Five executable analysis queries
tests/                    Unit and Streamlit tests
reports/                  Source manifest, audit, evaluation and written findings
```

`matches` has one row per match; `player_matches` has two; `players` has one per
source player ID. Keys, exclusions, dates and missingness are documented in
[reports/data_notes.md](reports/data_notes.md). The [case study](reports/case_study.md)
and [resume notes](RESUME.md) explain the measured findings and interview topics.

## Source attribution and publication

Source: [TennisMyLife/TML-Database](https://github.com/Tennismylife/TML-Database),
inspired by Jeff Sackmann's tennis_atp work and based on ATP records and other
sources. The original Sackmann endpoint returned 404 during implementation, so
this source substitution is explicit. Source terms describe educational,
analytical, non-commercial use and restrict redistribution without permission.
Raw CSVs, SQLite data and individual prediction files are ignored by Git.
Do not assume a public repository grants unrestricted data rights.

This project is **implemented and tested locally in the cloud workspace**. The source code is available in this GitHub repository. The dashboard has not
been deployed publicly. See [DEPLOYMENT.md](DEPLOYMENT.md)
for the publication steps and data permission requirement. No usability tests
with friends, completed 30-day learning schedule, or public user adoption are claimed.
