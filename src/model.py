"""Pre-match logistic baselines with chronological model selection."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RANK = ['log_rank_ratio']
EXPANDED = RANK + ['age_difference', 'rank_clay', 'rank_grass', 'rank_carpet']


def modeling_rows(matches):
    m = matches.copy()
    wr = pd.to_numeric(m.winner_rank, errors='coerce')
    lr = pd.to_numeric(m.loser_rank, errors='coerce')
    eligible = (wr > 0) & (lr > 0) & np.isfinite(wr) & np.isfinite(lr)
    m = m.loc[eligible].copy()
    a_wins = m.winner_id.astype(str) < m.loser_id.astype(str)
    wr, lr = wr.loc[eligible], lr.loc[eligible]
    a_rank, b_rank = np.where(a_wins, wr, lr), np.where(a_wins, lr, wr)
    wa = pd.to_numeric(m.winner_age, errors='coerce')
    la = pd.to_numeric(m.loser_age, errors='coerce')
    result = m[['match_id', 'year', 'surface']].copy()
    result['target'] = a_wins.astype(int)
    result['log_rank_ratio'] = np.log(b_rank / a_rank)
    result['age_difference'] = np.where(a_wins, wa - la, la - wa)
    for surface in ['Clay', 'Grass', 'Carpet']:
        result[f'rank_{surface.lower()}'] = result.log_rank_ratio * result.surface.eq(surface)
    result['baseline'] = (a_rank <= b_rank).astype(int)
    return result


def pipeline():
    return make_pipeline(SimpleImputer(strategy='median', keep_empty_features=True),
                         StandardScaler(), LogisticRegression(C=1, max_iter=1000, random_state=42))


def scores(y, probability):
    return {'accuracy': float(accuracy_score(y, probability >= .5)),
            'log_loss': float(log_loss(y, probability, labels=[0, 1]))}


def evaluate(force=False):
    output = Path('reports/model_evaluation.json')
    if output.exists() and not force:
        raise FileExistsError('Final evaluation exists. Preserve it; use --force only for a documented correction.')
    with sqlite3.connect('data/processed/courtiq.sqlite') as conn:
        matches = pd.read_sql('SELECT * FROM matches', conn)
    rows = modeling_rows(matches)
    splits = {name: rows.loc[rows.year.between(lo, hi)] for name, lo, hi in
              [('train', 2016, 2023), ('validation', 2024, 2024), ('test', 2025, 2025)]}
    if any(len(frame) == 0 or frame.target.nunique() < 2 for frame in splits.values()):
        raise ValueError('All chronological splits must contain matches and both outcomes.')
    train, val, test = [splits[k] for k in ['train', 'validation', 'test']]
    designs = {'rank_only': RANK, 'expanded': EXPANDED}
    validation = {}
    for name, columns in designs.items():
        fitted = pipeline().fit(train[columns], train.target)
        validation[name] = scores(val.target, fitted.predict_proba(val[columns])[:, 1])
    chosen = min(designs, key=lambda k: validation[k]['log_loss'])
    refit = pd.concat([train, val])
    predictions = test[['match_id', 'year', 'surface', 'target', 'baseline']].copy()
    final = {'ranking_rule': {'accuracy': float(accuracy_score(test.target, test.baseline))}}
    by_surface = {}
    for name, columns in designs.items():
        fitted = pipeline().fit(refit[columns], refit.target)
        p = fitted.predict_proba(test[columns])[:, 1]
        predictions[name] = p
        final[name] = scores(test.target, p)
    for surface, group in predictions.groupby('surface'):
        by_surface[surface] = {'matches': len(group),
                              'ranking_rule_accuracy': float(accuracy_score(group.target, group.baseline)),
                              **{name: scores(group.target, group[name]) for name in designs}}
    report = dict(selected_model=chosen, validation=validation, final_test=final,
                  source_commit=json.loads(Path('reports/source_manifest.json').read_text())['source_commit'],
                  refit_years=[2016, 2024], splits={}, surface_breakdown=by_surface,
                  code_sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                               [Path('MODEL_DESIGN.md'), *sorted(Path('src').glob('*.py'))]})
    for name, lo, hi in [('train', 2016, 2023), ('validation', 2024, 2024), ('test', 2025, 2025)]:
        retained = int(matches.year.between(lo, hi).sum())
        report['splits'][name] = dict(retained_matches=retained, eligible_matches=len(splits[name]),
                                     excluded_matches=retained-len(splits[name]),
                                     a_win_share=float(splits[name].target.mean()))
    predictions.to_csv('data/processed/test_predictions.csv', index=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true')
    evaluate(**vars(parser.parse_args()))
