# Validation record

Executed 2026-10-15 in the cloud workspace with Python 3.12.14.

- Installed pinned dependencies in /workspace/courtiq-venv; pip check passed.
- Downloaded all ten immutable annual files over verified HTTPS.
- Verified cache hashes and rebuilt SQLite a second time: counts unchanged.
- Audit reconciled 27,772 raw rows to 26,966 retained unique matches.
- Ran five SQL queries; every query returned results.
- Compared SQL and pandas for three year/surface filter combinations: agreement.
- Unit and Streamlit suite: 25 passed, zero failed, zero skipped with prepared data.
- All four actual Streamlit pages executed without exceptions; empty surfaces
  produced the expected no-data message.
- Started the Streamlit HTTP server; health endpoint returned `ok`.
- Exported compact Parquet input and executed the app in a separate directory
  without SQLite: displayed 26,966 unique matches.
- Created a separate clean virtual environment from requirements-lock.txt,
  copied the source into /tmp/courtiq-reproduction, downloaded fresh files,
  rebuilt the database, reran modeling, all 25 tests and SQL integration checks.
  Metrics reproduced exactly; code and input provenance remain recorded.
- Both virtual environments passed pip check.

One non-failing upstream warning: Streamlit 1.45.1 invokes Altair's deprecated
theme API. No tests, security verification or assertions were disabled.

GitHub Actions configuration is included but has not run on GitHub. No public
app or user interviews were performed during initial validation. GitHub upload
and environment publication are subsequent actions, separate from these checks.
Saved cloud install/start instructions are a draft, not proof of publication or
restoration in a future cloud task. Source distribution permissions remain a
prerequisite for public data hosting; local educational workflow is verified.
