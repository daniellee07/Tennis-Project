# Model design — frozen before evaluation

Question: do pre-match age and surface interactions improve on ranking alone?
One row per retained match. Player A has the lexicographically smaller source
player ID (IDs are strings); y=1 if A wins. This fixed rule does not use outcome.
Target balance is reported, not assumed to be 50/50.

Training: 2016–2023. Validation: 2024. Untouched final historical test: 2025.
No random splitting. Dates are tournament-week dates, not exact match timestamps.
No rolling-form features are used. Only positive, finite ranks on both sides
are eligible. All models use identical eligible rows; exclusion counts are saved.

Baseline: lower numerical rank wins; ties predict A. This deterministic rule has
accuracy only, not a fabricated probability or log loss. Rank-only logistic
regression uses log(rank_B/rank_A). Expanded logistic regression adds age_A-age_B
and interactions between ranking difference and surface. Missing age is imputed
using training medians; all scaling and imputation are fitted inside pipelines.
No score, winner indicator, serve stats, duration, seed, or current-match result
is a predictor. Coefficients use L2 regularization with C=1, max_iter=1000.

Selection: lowest 2024 log loss, rank-only on ties. No parameter search. Refit the
chosen design on 2016–2024 once, then evaluate 2025 once. Final report includes
both probability designs for transparent comparison, but selection is never
changed by test outcomes. Save model-design SHA256, source revision, code hashes,
split sizes, exclusions, accuracy, log loss, surface breakdowns, and predictions.
The pipeline refuses to overwrite a final report unless --force is supplied.
This historical experiment is not a betting product or causal analysis.
