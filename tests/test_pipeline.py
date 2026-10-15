import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.prepare_data import prepare_matches
from src.analytics import summarize, filter_rows
from src.model import modeling_rows, RANK, EXPANDED, pipeline


@pytest.fixture
def raw():
    base = dict(tourney_id='2020-1', match_num=1, tourney_date=20200101,
                winner_id='a', loser_id='b', winner_name='Alice', loser_name='Bob',
                surface='Hard', score='6-4 6-4', winner_rank=5, loser_rank=10,
                winner_age=25., loser_age=30.)
    for side in ['w', 'l']:
        base.update({f'{side}_svpt': 60, f'{side}_1stIn': 40,
                     f'{side}_1stWon': 30, f'{side}_2ndWon': 10})
    return pd.DataFrame([base])


def test_two_player_rows_one_match(raw):
    m,p,a=prepare_matches(raw)
    assert len(m)==1 and len(p)==2 and p.won.sum()==1
    assert a['raw_matches']==a['retained_matches']+sum(a['excluded'].values())


@pytest.mark.parametrize('field,value,reason', [
    ('surface','Moon','unknown_surface'), ('tourney_date',20201399,'invalid_date'),
    ('score','W/O','walkover_or_default'), ('winner_id','b','same_player'),
    ('winner_name',None,'missing_player'), ('match_num',None,'missing_key')])
def test_exclusions(raw,field,value,reason):
    raw[field]=value
    _,_,audit=prepare_matches(raw)
    assert audit['retained_matches']==0 and audit['excluded'][reason]==1


def test_duplicate(raw):
    m,_,a=prepare_matches(pd.concat([raw,raw]))
    assert len(m)==1 and a['excluded']['duplicate_match_key']==1


def test_missing_stats_are_not_zero(raw):
    raw['w_svpt']=np.nan
    _,p,_=prepare_matches(raw)
    s=summarize(p[p.won==1],['surface'])
    assert s.coverage.iloc[0]==0 and pd.isna(s.first_serve_won.iloc[0])


def test_zero_denominator(raw):
    raw['w_svpt']=0
    _,p,_=prepare_matches(raw)
    assert p.loc[p.won==1,'stats_available'].iloc[0]==0


def test_impossible_stats(raw):
    raw['w_1stWon']=41
    _,p,_=prepare_matches(raw)
    assert p.stats_available.sum()==1


def test_pooled_rate(raw):
    extra=raw.copy()
    extra['match_num']=2
    extra['w_svpt']=20
    extra['w_1stIn']=10
    extra['w_1stWon']=1
    extra['w_2ndWon']=4
    _,p,_=prepare_matches(pd.concat([raw,extra]))
    result=summarize(p[p.won==1],['player_id'])
    assert result.first_serve_won.iloc[0]==pytest.approx(31/50)


def test_neutral_orientation(raw):
    m,_,_=prepare_matches(raw)
    x=modeling_rows(m)
    assert x.target.iloc[0]==1 and x.log_rank_ratio.iloc[0]>0
    raw['winner_id']='z'
    m,_,_=prepare_matches(raw)
    x=modeling_rows(m)
    assert x.target.iloc[0]==0 and x.log_rank_ratio.iloc[0]<0


def test_missing_rank_excluded(raw):
    raw['winner_rank']=np.nan
    m,_,_=prepare_matches(raw)
    assert modeling_rows(m).empty


def test_predictor_allowlist():
    assert set(EXPANDED)=={'log_rank_ratio','age_difference','rank_clay','rank_grass','rank_carpet'}
    assert RANK==['log_rank_ratio']
    assert not any('won' in c or 'score' in c or 'winner' in c for c in EXPANDED)


def test_filters(raw):
    _,p,_=prepare_matches(raw)
    assert filter_rows(p,(2020,2020),['Hard'],['a']).shape[0]==1
    assert filter_rows(p,(2021,2022),['Hard']).empty
    assert filter_rows(p,(2020,2020),[]).empty


def test_sql_pandas_agree(raw):
    _,p,_=prepare_matches(raw)
    with sqlite3.connect(':memory:') as conn:
        p.to_sql('player_matches',conn,index=False)
        sql=pd.read_sql(Path('sql/05_serve_coverage.sql').read_text(),conn)
    s=summarize(p,['year','surface'])
    assert sql.first_serve_won.iloc[0]==s.first_serve_won.iloc[0]
    assert sql.coverage.iloc[0]==s.coverage.iloc[0]


def test_preprocessing_does_not_fit_on_validation():
    train=pd.DataFrame({'age_difference':[1.,3.,np.nan,2.], 'log_rank_ratio':[-1.,1.,-.5,.5]})
    fitted=pipeline().fit(train,[0,1,0,1])
    median=fitted.steps[0][1].statistics_.copy()
    fitted.predict_proba(pd.DataFrame({'age_difference':[9999.], 'log_rank_ratio':[1.]}))
    np.testing.assert_equal(fitted.steps[0][1].statistics_,median)


def test_no_first_serve_opportunities(raw):
    raw['w_1stIn']=0
    raw['w_1stWon']=0
    _,p,_=prepare_matches(raw)
    s=summarize(p[p.won==1],['player_id'])
    assert pd.isna(s.first_serve_won.iloc[0])
    assert s.second_serve_won.iloc[0]==pytest.approx(10/60)


def test_target_uses_neutral_id_not_winner_side(raw):
    other=raw.copy()
    other['match_num']=2
    other['winner_id']='b'
    other['loser_id']='a'
    m,_,_=prepare_matches(pd.concat([raw,other]))
    x=modeling_rows(m)
    assert x.target.tolist()==[1,0]
    assert x.log_rank_ratio.iloc[0]==-x.log_rank_ratio.iloc[1]
