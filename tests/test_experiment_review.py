import pytest
from helio24.experiment_review import annual_contrast


def row(year,arm,**updates):
    return dict(year=year,arm=arm,n=100,positives=10,precision=.2,recall=.9,fp=30,
                average_precision=.3,brier=.1,log_loss=.2,**updates)


def test_missing_year_cannot_be_counted_as_an_improvement():
    a=row(2022,'candidate');a.update(precision=.3,recall=.95,fp=20)
    result=annual_contrast([row(2022,'control'),row(2023,'control'),a],'candidate','control')
    assert result['primary_met_count']==1 and result['missing_years']=='2023'
    assert result['all_year_full'] is False


def test_precision_gain_with_low_recall_is_not_primary_success():
    a=row(2023,'candidate');a.update(precision=.8,recall=.5,fp=5)
    result=annual_contrast([row(2023,'control'),a],'candidate','control')
    assert result['precision_win_count']==1 and result['primary_met_count']==0
    a['n']=101
    with pytest.raises(ValueError):annual_contrast([row(2023,'control'),a],'candidate','control')
