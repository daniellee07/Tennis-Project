# Local use and optional publication

The app is tested locally; no public deployment has been made.

## Local demo

Follow README.md, then run `python -m streamlit run app.py` from the repository
root. The app reads prepared data; it never downloads or trains during page loads.
A current-instance server process does not survive environment publication.

## Compact app data

Run `python -m src.export_app` to write a compact player-row Parquet file. The app
can read that file without the full SQLite database. Test in a temporary directory
with `app.py`, `src/`, `.streamlit/`, `reports/`, requirements and the exported
file. Do not delete your working database just to exercise this path.

## Before public hosting

Review the pinned source README and obtain any needed permission for distribution
of derived records. Raw and processed data are Git-ignored intentionally.
No permission is inferred from the repository being public or from attribution.
If permitted, include only the compact app data needed for the app, with source
attribution and required terms. Do not commit raw annual CSVs or your virtualenv.

The source code is in the Tennis-Project GitHub repository.
For Streamlit Community Cloud, sign in, select your repository and branch, set
`app.py` as the entry point and Python 3.12 as the runtime. Include permitted
precomputed app data; keep training in the offline pipeline. No secrets required.
The small reports are included to display measured results without retraining.

Test the published URL: load all four sections, compare two players, clear the
surface filter, inspect sample counts, and compare model scores with the JSON
report. Only then add the URL to your resume. Record any actual feedback and
changes; do not fabricate user testing or adoption.
