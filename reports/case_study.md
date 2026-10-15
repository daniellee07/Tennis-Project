# CourtIQ: surface performance and the value of a small model

## Question and scope

CourtIQ investigates two connected questions: how a player's observed performance
varies across court surfaces, and whether a modest pre-match model improves on a
simple ranking rule. The intended user is a tennis fan exploring historical
professional performance. The project does not prescribe training interventions,
predict injuries or recommend bets. Its practical goal is to make comparisons
traceable: a percentage should always come with a sample size, a denominator and
a description of what is missing.

## Data and engineering

The analysis uses ten annual TennisMyLife ATP files covering 2016–2025, pinned to
one Git revision. This replaces the initially intended Jeff Sackmann source,
which was unavailable during implementation. Each successful download records a
SHA256 hash, byte count, retrieval timestamp and immutable URL. Cached files are
verified before reuse. The preparation step checks the hashes again before
building SQLite tables, so later analysis is tied to identifiable input files.

There were 27,772 raw rows and 26,966 retained unique matches. Sequential cleaning
excluded 489 rows without match keys, 135 without recognized surfaces and 182
walkovers or defaults. Retirements remain included. The resulting player-match
table contains 53,932 rows because every match has two participants; that number
must not be described as unique matches. Serve-stat consistency checks retained
usable statistics for 52,202 player rows, or approximately 96.79%. Missing and
invalid serve data remain missing rather than becoming zero-performance records.

Five saved SQL queries cover surface performance, head-to-head results, annual
coverage, player-year win rates and serve-stat coverage. The dashboard uses the
same filtering and aggregation functions as the tests. Three real filter
combinations were checked against SQL, including pooled serve rates. This helps
catch denominator or filtering mistakes that an attractive chart could conceal.

## Three descriptive findings

The exploratory comparisons below use training years only, 2016–2023. First,
Rafael Nadal won 130 of 145 retained clay matches, or 89.66%, versus 153 of 195
hard-court matches, or 78.46%, in this source snapshot. The difference describes
his observed schedule and opponents; it does not estimate what switching a
particular match to clay would cause. The grass sample is smaller: 18 wins from
21 matches, reinforcing the need to show counts alongside rates.

Second, under identical hard-court and year filters, Novak Djokovic won 76.71%
of recorded first-serve points, compared with Nadal's 73.64%. Valid serve records
covered 272 of Djokovic's 281 player-match rows and 192 of Nadal's 195. Their
second-serve point rates were much closer, at 56.28% and 55.94%. These are pooled
point-count ratios, not an average of each match's percentage. Differences in
opponents and tournaments still limit direct interpretation.

Third, retained annual match counts dropped from 2,700 in 2019 to 1,459 in 2020,
then rose to 2,714 in 2021. The database supports that coverage observation. It
does not independently establish why the counts changed or prove full annual
coverage. That distinction matters when comparing yearly performance or treating
more records as stronger evidence.

## Model experiment

The design was written before evaluation: train on 2016–2023, choose between two
logistic regressions on 2024 log loss, refit through 2024, and evaluate 2025.
Both players require positive, finite pre-match ranks. Player A is assigned using
fixed source-ID ordering, avoiding the outcome leak created by always making A
the winner. Predictors include log ranking ratio, with age difference and
surface interactions in the expanded model. Scores, serve statistics and match
duration are never predictors. Imputation and scaling are fitted inside training
pipelines, not across the full dataset.

Validation contained 3,084 eligible matches. It selected the expanded model by a
small log-loss advantage: 0.62995 versus 0.63029. On 2,292 eligible 2025 matches,
the ranking rule achieved 65.23% accuracy. The expanded model achieved 64.18%
accuracy and 0.62671 log loss; rank-only logistic regression achieved 65.23% and
0.62813. Thus the extension slightly improved probability loss while losing on
classification accuracy. Neither result justifies a claim of decisive predictive
superiority. Surface-specific results are saved, including weaker grass results.

## Limits and next steps

The snapshot has missing-key rows and is not an independently verified complete
ATP schedule. Rank eligibility further restricts the evaluated population.
Tournament-week dates prevent claims about exact match timing. No confidence
intervals, user-impact measurements or completed usability interviews are claimed.
A sensible next step is to reconcile coverage and ask two tennis fans to complete
specific comparison tasks before adding features. Source redistribution terms
also need review before public hosting. The code was built with AI assistance;
the learning work is understanding its assumptions, reproducing its outputs and
explaining where its conclusions stop.
