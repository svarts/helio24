import numpy as np
import pandas as pd
import pytest
from helio24.recency_weights import recency_weights


def test_weights_preserve_class_mass_and_favor_recent_rows():
    t=pd.to_datetime(['2015-01-01','2019-01-01','2015-01-01','2019-01-01'],utc=True)
    d=pd.DataFrame({'forecast_time':t,'prediction_end':t+pd.Timedelta(hours=24),'target':[0,0,1,1]})
    w=recency_weights(d,'2020-01-01T00:00:00Z',2)
    np.testing.assert_allclose([w[:2].sum(),w[2:].sum()],[2,2])
    assert w[1]>w[0] and w[3]>w[2]
    np.testing.assert_allclose(w[1]/w[0],4,rtol=.002)
    changed=d.copy();changed.loc[0,'prediction_end']=pd.Timestamp('2020-01-02',tz='UTC')
    with pytest.raises(ValueError):recency_weights(changed,'2020-01-01T00:00:00Z',2)
