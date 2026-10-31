"""Past-only magnetic sequences on the frozen forecast grid."""
import numpy as np
import pandas as pd
from helio24.v2_contract import V2_MEASUREMENTS, utc_to_tai, tai_utc_offset


def extract_sequences(observations, windows):
    """Return float64 values and missing masks without dropping forecast keys.

    Input order of windows is preserved. Absent cadence slots are missing, not
    interpolated. Outcome metadata is never selected. One HARP per call.
    """
    raw = observations[['harp_number', 'obs_start', *V2_MEASUREMENTS.values()]].drop_duplicates().sort_values('obs_start')
    if windows.empty or windows.harp.nunique() != 1:
        raise ValueError('One nonempty forecast HARP required')
    if not raw.empty and (raw.harp_number.nunique() != 1 or raw.harp_number.iloc[0] != windows.harp.iloc[0]):
        raise ValueError('Observation and forecast HARPs must match')
    clocks = pd.DatetimeIndex(raw.obs_start)
    forecasts = pd.DatetimeIndex(windows.forecast_time)
    if clocks.tz is not None or clocks.hasnans or clocks.has_duplicates:
        raise ValueError('Unique naive TAI observation clocks required')
    if forecasts.tz is None or forecasts.hasnans or forecasts.has_duplicates:
        raise ValueError('Unique timezone-aware forecast clocks required')
    if (forecasts >= pd.Timestamp('2024-01-01T00:00Z')).any():
        raise ValueError('Reserved forecast period')
    tai = pd.DatetimeIndex([utc_to_tai(t) for t in forecasts])
    starts = tai - pd.Timedelta(hours=12)
    if any(tai_utc_offset(a) != tai_utc_offset(b) for a,b in zip(starts,tai)):
        raise ValueError('History crossing a leap transition')
    grid = tai.as_unit('ns').asi8[:, None] - np.arange(60,0,-1)[None,:]*pd.Timedelta(minutes=12).value
    indices = clocks.get_indexer(pd.DatetimeIndex(grid.ravel())).reshape(-1,60)
    numeric = raw[list(V2_MEASUREMENTS.values())].apply(pd.to_numeric,errors='coerce').to_numpy(dtype=float,na_value=np.nan,copy=True)
    numeric[~np.isfinite(numeric)] = np.nan
    values = np.full((len(windows),60,24),np.nan)
    present = indices >= 0
    values[present] = numeric[indices[present]]
    return values, ~np.isfinite(values), ~present


def summarize_sequences(values):
    """Independent stable mean/population std/last/delta reconstruction."""
    count = np.isfinite(values).sum(axis=1)
    mean = np.divide(np.nansum(values,axis=1),count,out=np.full(count.shape,np.nan),where=count>0)
    variance = np.divide(np.nansum((values-mean[:,None,:])**2,axis=1),count,out=np.full(count.shape,np.nan),where=count>0)
    return np.stack([mean,np.sqrt(variance),values[:,-1],values[:,-1]-values[:,0]],axis=2).reshape(len(values),96)


def permute_interior(values, missing, seed):
    """Label-independent shuffle; endpoints and joint channel masks preserved."""
    if values.shape != missing.shape or values.ndim != 3 or values.shape[1] != 60:
        raise ValueError('Matching 60-step tensors required')
    rng = np.random.default_rng(seed)
    out, mask = values.copy(), missing.copy()
    for i in range(len(out)):
        order = np.r_[0,rng.permutation(np.arange(1,59)),59]
        out[i], mask[i] = values[i,order], missing[i,order]
    return out, mask
