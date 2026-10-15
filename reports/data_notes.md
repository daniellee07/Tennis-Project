# Data notes and audit

## Source and scope

Ten annual files (2016–2025) were successfully downloaded from a single immutable
TennisMyLife Git revision. `source_manifest.json` records the revision, URLs,
retrieval timestamps, byte counts and SHA256 hashes. The downloader rehashes
cache entries; preparation independently checks the manifest before reading.
The original Jeff Sackmann repository was unavailable (404), so this is a documented
source substitution, not a claim that Sackmann files were downloaded.

The files contain historical men's professional match records across source
competition levels, including Davis Cup and Olympics where present. We have not
reconciled them against a complete official ATP schedule. Dates identify the
start/week of a tournament, not exact match timestamps. No same-day rolling-form
features are attempted. Coverage counts are evidence of the supplied snapshot,
not proof that every tournament or season is complete.

## Row grains and exclusions

`matches`: one row per tournament ID + match number. `player_matches`: one per
match and participant, with won=1/0. `players`: one source ID and latest observed
name in file order. Player IDs are strings; names are display labels, not keys.

27,772 raw rows = 26,966 retained matches + 489 missing-key rows + 135
unknown-surface rows + 182 walkovers/defaults. Other audited exclusion categories
were zero. Exclusions are sequential and mutually exclusive; order is explicit
in `prepare_matches`. Duplicate detection uses tournament ID and match number.
Missing keys are dropped rather than assigned potentially misleading identities.
Retirements remain included, so not every retained match is a completed contest.
The 489 missing-key rows occur in the supplied 2025 file; final-test coverage is
therefore restricted beyond rank eligibility. This matters when interpreting scores.

53,932 player-match rows represent 26,966 matches, not twice as much evidence.
52,202 player rows have usable serve counts (96.79%). Twelve complete stat rows
failed consistency rules; the remainder of uncovered rows have missing counts.
Serve counts must be nonnegative, service points positive, first serves in no
greater than points, first-serve wins no greater than serves in, and second-serve
wins no greater than remaining points. Invalid/missing stat sets become missing
as a group; the match outcome remains available for win-rate analysis.

## Metric dictionary

- Win rate: wins / retained matches played within shared filters.
- First-serve points won: sum(first-serve wins) / sum(first serves in).
- Second-serve points won: sum(second-serve wins) / sum(service points − first serves in).
  Double faults remain among second-serve opportunities.
- Coverage: valid-stat player rows / all selected player rows.
- Zero opportunities: missing rate, never a fabricated zero percent.
- Match counts below 20: warning only; not a confidence or significance threshold.

Pooled rates are ratios of summed counts, not averages of match percentages.
Every rate can be traced to its opportunity totals in the comparison table.
No missing serve rates are filled with player averages.

## Model eligibility

Both players need finite, positive pre-match rankings. Rank exclusions are 321
training matches, 54 validation matches and 61 final-test matches. The test uses
2,292 of 2,353 retained 2025 matches (97.41%); this percentage does not include
matches excluded earlier in cleaning. Age is median-imputed inside the training
pipeline. Player A is assigned by fixed lexicographic ID order, not winner order.
A-win shares are 50.24%, 50.16%, and 52.09% across chronological splits.

## Verification and limits

All five saved SQL queries ran. SQL and pandas agree on match/player counts,
win rate, coverage and pooled first-serve rate for 2016–2023 Clay, 2024 Hard and
2025 Grass. Automated tests also cover duplicates, invalid stats, zero points,
missing values, empty filters, predictor orientation and preprocessing isolation.

Surface performance is descriptive: schedule, opponent strength, age and event
selection can confound comparisons. Small differences have no uncertainty claim.
The model is not calibrated for current seasons, coaching, injuries or betting.
Source conditions apply to raw and potentially derived data. Attribution alone
does not supply redistribution permission. No raw data is committed here.
