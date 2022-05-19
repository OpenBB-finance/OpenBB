"""Exponential Probablistic Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union, List
from matplotlib import ticker

import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.models import ExponentialSmoothing
from darts.dataprocessing.transformers import MissingValuesFiller
from darts.utils.utils import ModelMode, SeasonalityMode
from darts.metrics import mape

from openbb_terminal.decorators import log_start_end

TRENDS = ["N", "A", "M"]
SEASONS = ["N", "A", "M"]
PERIODS = [4,5,7]
DAMPED = ["T", "F"]

logger = logging.getLogger(__name__)

@log_start_end(log=logger)
def get_expo_data(
    data: Union[pd.Series, pd.DataFrame],
    trend: str = "A",
    seasonal: str = "A",
    seasonal_periods: int = 7,
    damped: str = "F", 
    n_predict: int=5,
) -> Tuple[List[float], List[float], Any, Any]:

    """Performs Probabalistic Exponential Smoothing forecasting
    This is a wrapper around statsmodels Holt-Winters' Exponential Smoothing; 
    we refer to this link for the original and more complete documentation of the parameters.
    
    https://unit8co.github.io/darts/generated_api/darts.models.forecasting.exponential_smoothing.html?highlight=exponential

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    trend: str
        Trend component.  One of [N, A, M]
        Defaults to ADDITIVE.
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to ADDITIVE.
    seasonal_periods: int
        Number of seasonal periods in a year
        If not set, inferred from frequency of the series.
    n_predict: int
        Number of days to forecast

    Returns
    -------
    List[float]
        Adjusted Data series
    List[float]
        List of predicted values
    Any
        Fit Prob. Expo model object.
    """

    filler = MissingValuesFiller()
    data['date'] = data.index # add temp column since we need to use index col for date
    ticker_series = TimeSeries.from_dataframe(data, time_col='date', value_cols=['AdjClose'], freq='B', fill_missing_dates=True)
    
    ticker_series = filler.transform(ticker_series)
    ticker_series = ticker_series.astype(np.float32)
    train, val = ticker_series.split_before(0.85)
    

    if trend == "M":
        trend = ModelMode.MULTIPLICATIVE
    elif trend == "N":
        trend = ModelMode.NONE
    else: # Default
        trend = ModelMode.ADDITIVE 

    if seasonal == "M":
        seasonal = SeasonalityMode.MULTIPLICATIVE
    elif seasonal == "N":
        seasonal = SeasonalityMode.NONE
    else: # Default
        seasonal = SeasonalityMode.ADDITIVE
    
    if damped == "T":
        damped = True
    else:
        damped = False

    # print(f"Prediction days {n_predict}")
    # print(f"Trend {trend}")
    # print(f"Seasonal {seasonal}")
    # print(f"Seasonal_periods {seasonal_periods}")
    # print(f"damped {damped} with type {type(damped)}")
    model = ExponentialSmoothing(trend=trend, 
                                seasonal=seasonal, 
                                seasonal_periods=seasonal_periods, 
                                damped=damped)
    
    model.fit(train)
    #model.backtest(ticker_series, val)

    # Show forcast over validation # and then +10 afterwards sampled 10 times per point
    probabilistic_forecast = model.predict(len(val) + n_predict, num_samples=10)
    precision = mape(val, probabilistic_forecast)
    #print("model {} obtains MAPE: {:.2f}%".format(model, mape(val, probabilistic_forecast)))

    return ticker_series, probabilistic_forecast, precision,  model
