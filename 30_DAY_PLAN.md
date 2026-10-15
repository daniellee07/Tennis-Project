# CourtIQ — 30-day implementation plan

## Outcome and time budget

Target approximately 10–12 hours per week, or 40–50 hours total. This is a planning
estimate, not a guarantee. Use the provided starter to spend more time analyzing,
checking, and understanding rather than setting up repetitive file handling.

End product: a reproducible Python/SQL pipeline, a small interactive analytics
app, one honest pre-match model evaluation, and a written case study. The user is
a tennis fan or player exploring historical professional performance—not a coach
receiving automatically validated training prescriptions.

The central question is: **How does player performance vary by surface, and how
much does a small pre-match model improve on a simple ranking baseline?**

## Feature priorities

Must finish: data-quality audit, saved SQL queries, filtered player/surface metrics,
side-by-side comparison, three supported findings, baseline/model evaluation,
README, source attribution, and a reproducible run.

Target dashboard sections: Overview; Player comparison; Model evaluation; Data
and limitations. Use year, surface, and player filters. Show match counts and
statistic coverage next to percentages. Do not add authentication or a complex UI.

One optional improvement only: surface-aware ranking interactions in the model,
a small usability test with two tennis-playing friends, or prior-form features
with rigorous date tests. Prefer feedback and bug fixes over more features.

Cut from month one: video/computer vision, live scores, automated web scraping,
React, a chatbot, deep learning, betting recommendations, injury predictions,
and paid API integration.

## Week 1 — Data you can trust (10–12 hours)

### Day 1: Environment and first successful run

Follow the README setup. Run the 12 tests. Download 2016–2023 and create the
database. Record the actual number of raw and retained matches. Open the source
manifest and identify the source commit, a file hash, and retrieval time.

Learning: virtual environments, Python modules, relative paths, dependencies.
Do not claim a live download worked until it has actually worked on your computer.

### Days 2–3: Understand and audit the data

Read a small training-year CSV sample with pandas. Learn `head`, `info`,
`isna`, `duplicated`, `value_counts`, and filtering. Inspect the data dictionary.
Manually verify one complete match and one missing-stat record. Trace both through
`prepare_matches`. Explain every exclusion reason in the JSON audit.

Add one new test of your own, such as a zero service-points denominator. Check that
it fails when you intentionally introduce the relevant bug, then restore the code.

Learning: data types, missing values, duplicates, dates, assertions, debugging.

### Days 4–5: Query the SQLite database

Run both supplied queries. Learn `SELECT`, `WHERE`, `GROUP BY`, `HAVING`, `JOIN`,
and `NULLIF`. Add three saved SQL queries: annual match coverage; player/year win
rate; and serve-stat coverage by surface/year. Compare one SQL result against a
pandas calculation.

Learning: table grain, keys, joins, aggregation, ratios of sums, denominator checks.

### Days 6–7: Document and buffer

Write `reports/data_notes.md`: scope, date interpretation, missingness, excluded
rows, match/player-row distinction, and source attribution. Check source coverage
rather than assuming each annual file is complete. Create your own Git repository
and commit the code, queries, source manifest, and documentation. Do not publish
personal account secrets or your virtual environment.

Week 1 acceptance: one repeatable download/preparation command sequence, three
database tables, five SQL queries, at least one test you added and understand,
and an audit whose counts reconcile.

## Week 2 — Answer questions and make the dashboard (10–12 hours)

### Days 8–9: Ask three answerable questions

Use only training years for exploratory choices that could affect the model.
Suggested questions: How does a chosen player's win rate vary by surface? How do
first- and second-serve results differ between two players under matching filters?
Does a player's yearly trend persist when you show match counts and stat coverage?

Write the intended comparison before plotting. Choose a minimum displayed match
count, such as 20, and explain that this is a UI rule, not a significance test.
Keep small samples visible as a warning rather than proof of inferiority.

### Days 10–11: Build four clear charts

Create a yearly win-rate line chart, a surface comparison, a two-player serve-rate
comparison, and a missing-data coverage chart. Label rates and denominators.
Compute pooled rates as pooled counts divided by pooled opportunities. Do not
silently compare one player's grass season with another's all-surface career.

Write a one-sentence observation under each chart. Distinguish correlation from
cause. Do not infer that changing a statistic would necessarily produce more wins.

### Days 12–13: Create `app.py`

Install `requirements-full.txt`. Use Streamlit with a title, short explanation,
sidebar year/surface/player filters, summary metrics, and charts. Create an
Overview and Player comparison section. Keep charts readable and show the date
coverage and sample counts. Add an obvious no-data message for empty selections.

Run `python -m streamlit run app.py` after you create the file. Open the local
address printed in the terminal. Use functions and caching for repeated data loads;
learn those concepts before copying a large app template.

### Day 14: Review and buffer

Check the app against SQL for three filter combinations. Have someone attempt a
basic task, such as comparing two players on clay. Record where they get confused.

Week 2 acceptance: a locally running app with working filters, three original,
supported observations, sample sizes, missingness, and no fabricated user impact.

## Week 3 — Model without accidentally revealing the answer (10–12 hours)

### Days 15–16: Create neutral modeling rows

Read `MODEL_DESIGN.md`. Start from one row per match. Convert winner/loser sides
to neutral A/B using the fixed player-ID convention. Build the target and only
pre-match predictors. Write tests for target balance and forbidden feature names.

Learn binary classification, features vs. target, prediction probabilities, and
why post-match statistics would leak the outcome.

### Days 17–18: Baselines and validation data

Download 2024 using the same saved snapshot:

```bash
python -m src.download_data --start 2024 --end 2024
python -m src.prepare_data --start 2024 --end 2024 --output data/processed/validation.sqlite --report reports/validation_quality.json
```

Keep validation separate from training. Implement the higher-ranked-player rule
and a ranking-only logistic regression. Use the same rank-eligible rows for fair
comparison. Report the excluded share, not just scores on the easiest data.

Learn `fit`, `predict`, `predict_proba`, imputation, scaling, Pipeline, accuracy,
and log loss. Use 2024 for comparison; do not inspect final-test metrics yet.

### Days 19–20: One modest extension

Compare a small expanded logistic regression using age and surface interactions
against the rank-only model. Limit experimentation; do not search many algorithms.
Record which model you chose and why using validation results. Freeze the design.

### Day 21: Explain the model and buffer

Write a short model card: target, source years, eligible matches, features,
baselines, split, metrics, limitations, and the exact code revision being tested.
Practice explaining it without opening generated code.

Week 3 acceptance: reproducible validation results, train-only preprocessing,
non-overlapping time splits, baseline comparison, and no same-match leakage.

## Week 4 — Final test, case study, and publication (10–14 hours)

### Days 22–23: Final historical test

After freezing the design, download 2025 from the same recorded snapshot:

```bash
python -m src.download_data --start 2025 --end 2025
python -m src.prepare_data --start 2025 --end 2025 --output data/processed/test.sqlite --report reports/test_quality.json
```

Follow the predeclared refitting choice in MODEL_DESIGN. Evaluate on the same
eligible 2025 matches for every model. Save the predictions and evaluation report.
Show accuracy, log loss for probability models, the test sample size, and surface
breakdowns where meaningful. Do not tune further based on these final outcomes.

### Days 24–25: Add results and interpretation

Add the Model evaluation and Data/limitations sections to the app. Explain both
improvements and failures. A model that loses to a baseline is still a valid,
completed experiment. Only after the final evaluation is frozen should you expand
the public historical dashboard across the available years.

Write a 600–900-word case study with the question, data, method, three measured
findings, limitations, and what you would try next. Use result placeholders until
you actually run the analysis; never let generated prose invent the findings.

### Days 26–27: Fresh run and usability test

Run all tests and follow your README from a clean environment. Compare the
published metrics to saved results. Ask two or three people to perform specific
app tasks, if available. Log feedback and fix two genuine issues rather than
claiming unmeasured performance improvements.

### Days 28–29: Publish

Follow DEPLOYMENT.md. Export small, precomputed app data rather than making the
host retrain a model on every page load. Include attribution for shared derived
data. Push your code and permitted app data, deploy, and check the public link.
Record a short demo as a backup. Account creation, sign-in, publication decisions,
and permissions are actions you will perform in your accounts.

### Day 30: Resume and interview preparation

Write two or three accurate project bullets. Quantify actual unique matches,
queries, evaluated matches, and measured scores. Do not count two player rows as
two matches. Identify your own contributions and AI assistance honestly.

Practice a 90-second story: why tennis; what problem you investigated; how you
cleaned the data; how you prevented leakage; what the model actually achieved;
and one limitation. Add the project below Education once its claimed features work.

## When the schedule slips

Protect the completed analytics work first. Remove extra models and rolling-form
features. Keep one ranking baseline and one simple logistic regression. If the
model cannot be responsibly finished, publish the analytics version and call it
Tennis Performance Analytics, not an AI predictor. Do not sacrifice correct
metrics, a reproducible run, or your understanding for an extra feature.

## Daily learning routine

Spend about 20 minutes understanding a concept, 60 minutes implementing one
piece, and 15 minutes testing and writing down what you learned. Adjust to your
schedule. Ask ChatGPT to explain a small function, test your understanding, and
review edge cases rather than replacing the entire project each time an error
appears. Keep the traceback, your attempted fix, and the verified solution.
