"""Theta Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union

import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.models import Theta
from darts.dataprocessing.transformers import MissingValuesFiller
from darts.utils.utils import SeasonalityMode, TrendMode
from darts.metrics import mape

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console


TRENDS = ["L", "E"]
SEASONS = ["N", "A", "M"]
PERIODS = [4, 5, 7]
NORMALIZATION = ["T", "F"]

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_theta_data(
    data: Union[pd.Series, pd.DataFrame],
    trend: str = "L",
    seasonal: str = "M",
    seasonal_periods: int = 7,
    normalization: str = "T",
    n_predict: int = 30,
    start_window: float = 0.65,
    forecast_horizon: int = 3,
) -> Tuple[Any, Any, Any, Any, Any]:

    """Performs Theta forecasting
    An implementation of the 4Theta method with configurable theta parameter.

    https://unit8co.github.io/darts/generated_api/darts.models.forecasting.theta.html

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    trend: str
        Trend component.  One of [L, E]
        Defaults to LINEAR.
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to MULTIPLICATIVE.
    seasonal_periods: int
        Number of seasonal periods in a year
        If not set, inferred from frequency of the series.
    Normalization: str
        Normalize Data
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical

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
    data["date"] = data.index  # add temp column since we need to use index col for date
    ticker_series = TimeSeries.from_dataframe(
        data,
        time_col="date",
        value_cols=["AdjClose"],
        freq="B",
        fill_missing_dates=True,
    )

    ticker_series = filler.transform(ticker_series)
    ticker_series = ticker_series.astype(np.float32)
    train, val = ticker_series.split_before(0.85)

    # if trend == "E":
    #     trend_mode = TrendMode.EXPONENTIAL
    # else:  # Default
    #     trend_mode = TrendMode.LINEAR

    if seasonal == "A":
        seasonal = SeasonalityMode.ADDITIVE
    elif seasonal == "N":
        seasonal = SeasonalityMode.NONE
    else:  # Default
        seasonal = SeasonalityMode.MULTIPLICATIVE

    # normalize = True
    # if normalization == "F":
    #     normalize = False

    thetas = np.linspace(-10, 10, 50)
    best_mape = float("inf")
    best_theta = 0
    for theta in thetas:
        model = Theta(
            theta=theta,
            season_mode=seasonal,
            seasonality_period=seasonal_periods,
        )
        model.fit(train)
        pred_theta = model.predict(len(val))
        res = mape(val, pred_theta)
        if res < best_mape:
            best_mape = res
            best_theta = theta

    console.print(f"Best theta: {best_theta}")
    # Training model based on historical backtesting
    historical_fcast_es = best_theta_model.historical_forecasts(
        ticker_series,
        start=float(start_window),
        forecast_horizon=int(forecast_horizon),
        verbose=True,
    )

    # Show forecast over validation # and then +n_predict afterwards sampled 10 times per point
    probabilistic_forecast = best_theta_model.predict(int(n_predict), num_samples=500)
    precision = mape(val, probabilistic_forecast)  # mape = mean average precision error
    console.print(f"model {best_theta_model} obtains MAPE: {precision:.2f}% \n")  # TODO

    return (
        ticker_series,
        historical_fcast_es,
        probabilistic_forecast,
        precision,
        model_es,
    )
