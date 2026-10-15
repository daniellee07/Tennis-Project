# Resume and interview notes

Use these only after you can reproduce the commands and explain the code.
The implementation was created with AI assistance; describe your own subsequent
analysis, validation and design contributions accurately. Do not imply you spent
30 days building it, deployed it, or tested with real users unless you did.

**CourtIQ — Tennis Performance Analytics | Python, pandas, SQL, Streamlit, scikit-learn**

- Built and validated an audited Python/SQLite pipeline for 26,966 historical tennis matches, recording source hashes, exclusion reasons and missing-stat coverage.
- Created an interactive tennis analytics dashboard with player, year and surface filters, pooled serve metrics and five reusable SQL analyses.
- Evaluated pre-match logistic models on 2,292 held-out 2025 matches using chronological splits; reported 64.18% accuracy for the selected model versus 65.23% for the ranking rule, with improved probability log loss over rank-only logistic regression.

## Explain it in 90 seconds

“I wanted to understand surface performance without hiding sample sizes or missing
records. CourtIQ downloads a fixed historical snapshot, audits its rows, and
builds match-level and player-level SQL tables. I can compare players using the
same filters and inspect the opportunity counts behind serve rates. I also tested
whether adding age and surface interactions improves a ranking-based model.
Training, validation and testing use different years, and current-match stats are
excluded. The expanded model slightly improved log loss but lost to the ranking
rule on accuracy. That taught me to distinguish probability quality from a
thresholded prediction. The main limitation is incomplete source coverage.”

## Before adding this to your resume

1. Run the README commands yourself and compare report values.
2. Trace one complete and one missing-stat record through preparation.
3. Explain why `matches` and `player_matches` have different row counts.
4. Modify a saved SQL query and explain its denominator.
5. Add a test you understand; verify it catches an intentional local bug, then restore the code.
6. Explain validation versus test data and why a model can improve log loss while losing accuracy.
7. Push and deploy only when you are ready; include a real public link only after testing it.
