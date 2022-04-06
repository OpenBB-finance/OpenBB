"""ETS Prediction Model"""
__docformat__ = "numpy"

import logging
from typing import Union

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

TRENDS = ["N", "A", "Ad"]
SEASONS = ["N", "A", "M"]


@log_start_end(log=logger)
def get_exponential_smoothing_model(
    data: Union[pd.Series, np.ndarray],
    trend: str = "N",
    seasonal: str = "N",
    seasonal_periods: int = 5,
    n_predict: int = 5,
):
    """
    Perform exponential smoothing
    Parameters
    ----------
    data: Union[pd.Series, np.ndarray]
        Series of closing values
    trend: str
        Trend component.  One of [N, A, Ad]
    seasonal: str
        Seasonal component.  One of [N, A, M]
    seasonal_periods: int
        Number of seasonal periods in a year
    n_predict: int
        Number of days to forecast

    Returns
    -------
    model:
        Exponential smoothing model
    title: str
        String describing selected model
    forecast : List[float]
        List of predictions
    """
    if trend == "N":  # None
        if seasonal == "N":  # None
            title = "Trend='N',  Seasonal='N': Simple Exponential Smoothing"
            ETS = ExponentialSmoothing(
                data,
                trend=None,
                damped_trend=False,
                seasonal=None,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, damping_trend=None
            )

        elif seasonal == "A":  # Additive
            title = "Trend='N',  Seasonal='A': Exponential Smoothing"
            ETS = ExponentialSmoothing(
                data,
                trend=None,
                damped_trend=False,
                seasonal="add",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(smoothing_level=None, smoothing_seasonal=None)

        elif seasonal == "M":  # Multiplicative
            title = "Trend='N',  Seasonal='M': Exponential Smoothing"
            ETS = ExponentialSmoothing(
                data,
                trend=None,
                damped_trend=False,
                seasonal="mul",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(smoothing_level=None, smoothing_seasonal=None)

    elif trend == "A":  # Additive
        if seasonal == "N":  # None
            title = "Trend='A',  Seasonal='N': Holt’s linear method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=False,
                seasonal=None,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, damping_trend=None
            )

        elif seasonal == "A":  # Additive
            title = "Trend='A',  Seasonal='A': Additive Holt-Winters’ method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=False,
                seasonal="add",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, smoothing_seasonal=None
            )

        elif seasonal == "M":  # Multiplicative
            title = "Trend='A',  Seasonal='M': Multiplicative Holt-Winters’ method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=False,
                seasonal="mul",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, smoothing_seasonal=None
            )

    elif trend == "Ad":  # Additive damped
        if seasonal == "N":  # None
            title = "Trend='Ad', Seasonal='N': Additive damped trend method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=True,
                seasonal=None,
            )
            model = ETS.fit(
                smoothing_level=None, smoothing_trend=None, damping_trend=None
            )

        elif seasonal == "A":  # Additive
            title = "Trend='Ad', Seasonal='A': Exponential Smoothing"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=True,
                seasonal="add",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(
                smoothing_level=None,
                smoothing_trend=None,
                damping_trend=None,
                smoothing_seasonal=None,
            )

        elif seasonal == "M":  # Multiplicative
            title = "Trend='Ad', Seasonal='M': Holt-Winters’ damped method"
            ETS = ExponentialSmoothing(
                data,
                trend="add",
                damped_trend=True,
                seasonal="mul",
                seasonal_periods=seasonal_periods,
            )
            model = ETS.fit(
                smoothing_level=None,
                smoothing_trend=None,
                damping_trend=None,
                smoothing_seasonal=None,
            )

    if model.mle_retvals.success:
        forecast = [max(i, 0) for i in model.forecast(n_predict)]

    else:
        forecast = []

    return model, title, forecast
