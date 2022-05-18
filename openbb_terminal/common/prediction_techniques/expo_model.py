"""Exponential Probablistic Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union, List

import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.models import ExponentialSmoothing
from darts.dataprocessing.transformers import MissingValuesFiller

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

@log_start_end(log=logger)
def get_expo_data(
    data: Union[pd.Series, pd.DataFrame],
    n_predict: int,
):
#) -> Tuple[List[float], List[float], Any]:

    """Performs Probabalistic Exponential Smoothing forecasting

    Default parameters: 80/20 splot

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    n_predict : int
        Days to predict

    use_log : bool, optional
        Flag to use log returns, by default True

    Returns
    -------
    List[float]
        List of predicted values
    Any
        Fit Expo model object.
    """
    filler = MissingValuesFiller()
    data['date_fixed'] = data.index # add temp column since we need to use index col for date
    print(f"Predicting {n_predict} days in advance. ")

    ticker_series = TimeSeries.from_dataframe(data, time_col='date_fixed', value_cols=['AdjClose'], freq='B', fill_missing_dates=True)
    ticker_series = filler.transform(ticker_series)
    ticker_series = ticker_series.astype(np.float32)

    train, val = ticker_series.split_before(0.85)
    model = ExponentialSmoothing()
    model.fit(train)

    # Show forcast over validation # and then +10 afterwards sampled 10 times per point
    probabilistic_forecast = model.predict(len(val) + n_predict, num_samples=10)

    return ticker_series, probabilistic_forecast, model
