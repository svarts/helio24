import numpy as np
import pandas as pd
import pytest
from helio24.sequences import extract_sequences, summarize_sequences, permute_interior
from helio24.v2_contract import V2_MEASUREMENTS


def fixture():
    raw=pd.DataFrame({'harp_number':7,'obs_start':pd.date_range('2022-06-01 00:00:37',periods=61,freq='12min')})
    for j,c in enumerate(V2_MEASUREMENTS.values()):raw[c]=np.arange(61,dtype=float)+j
    keys=pd.DataFrame({'harp':[7],'forecast_time':[pd.Timestamp('2022-06-01T12:00Z')]})
    return raw,keys


def test_future_exclusion_and_missing_slots():
    raw,keys=fixture()
    x,m,g=extract_sequences(raw,keys)
    assert x[0,-1,0]==59 and not m.any() and not g.any()
    raw.loc[60,list(V2_MEASUREMENTS.values())]=1e30
    raw=raw.drop(index=10)
    y,mask,gaps=extract_sequences(raw,keys)
    assert gaps.sum()==1 and mask.sum()==24
    assert np.isnan(y[0,10]).all()
    np.testing.assert_equal(y[0,-1],x[0,-1])
    empty,mask,gaps=extract_sequences(raw.iloc[:0],keys)
    assert mask.all() and gaps.all() and len(empty)==len(keys)


def test_rejects_conflicting_clocks_and_reserved_forecasts():
    raw,keys=fixture();bad=raw.iloc[[0]].copy();bad.iloc[0,2]=123
    with pytest.raises(ValueError):extract_sequences(pd.concat([raw,bad]),keys)
    keys.forecast_time=pd.to_datetime(['2024-01-01'],utc=True)
    with pytest.raises(ValueError,match='Reserved'):extract_sequences(raw,keys)


def test_shuffle_preserves_summaries_and_masks():
    raw,keys=fixture();raw.iloc[5,2]=np.nan
    x,m,_=extract_sequences(raw,keys);y,mask=permute_interior(x,m,24)
    np.testing.assert_allclose(summarize_sequences(x),summarize_sequences(y),equal_nan=True)
    np.testing.assert_equal(np.isnan(y),mask)
    assert not np.array_equal(x[:,1:-1],y[:,1:-1],equal_nan=True)
    np.testing.assert_equal(y,permute_interior(x,m,24)[0])


def test_leap_transition_and_timezone_validation():
    raw,keys=fixture()
    keys.forecast_time=pd.to_datetime(['2017-01-01T06:00Z'])
    with pytest.raises(ValueError,match='leap'):extract_sequences(raw,keys)
    raw,keys=fixture();keys.forecast_time=keys.forecast_time.dt.tz_localize(None)
    with pytest.raises(ValueError,match='timezone-aware'):extract_sequences(raw,keys)
