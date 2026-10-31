"""Training-only temporal weights preserving total weight within each class."""
import numpy as np
import pandas as pd


def recency_weights(frame, cutoff, half_life_years):
    cutoff=pd.Timestamp(cutoff)
    if half_life_years<=0 or cutoff.tz is None:
        raise ValueError('Positive half-life and timezone-aware cutoff required')
    if not frame.forecast_time.lt(cutoff).all() or not frame.prediction_end.le(cutoff).all():
        raise ValueError('Training windows cross the cutoff')
    if set(frame.target.unique())!={0,1}:
        raise ValueError('Both training classes required')
    age=(cutoff-frame.forecast_time).dt.total_seconds().to_numpy()/(365.25*86400)
    weights=np.exp2(-age/half_life_years)
    for label in [0,1]:
        mask=frame.target.eq(label).to_numpy()
        weights[mask]/=weights[mask].mean()
    if not np.isfinite(weights).all() or not (weights>0).all():
        raise ValueError('Invalid temporal weights')
    return weights
