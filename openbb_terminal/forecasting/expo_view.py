"""Probabilistic Exponential Smoothing View"""
__docformat__ = "numpy"

import logging
from typing import Union

import pandas as pd

from openbb_terminal.forecasting import expo_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecasting import helpers

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_expo_forecast(
    data: Union[pd.DataFrame, pd.Series],
    ticker_name: str,
    target_col: str,
    trend: str,
    seasonal: str,
    seasonal_periods: int,
    dampen: str,
    n_predict: int,
    start_window: float,
    forecast_horizon: int,
    export: str = "",
):
    """Display Probabilistic Exponential Smoothing forecast

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    ticker_name str
        The name of the ticker to be predicted
    trend: str
        Trend component.  One of [N, A, M]
        Defaults to ADDITIVE.
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to ADDITIVE.
    seasonal_periods: int
        Number of seasonal periods in a year
        If not set, inferred from frequency of the series.
    dampen: str
        Dampen the function
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None
    """

    # reformat the date column to remove any hour/min/sec
    data["date"] = data["date"].apply(helpers.dt_format)

    (
        ticker_series,
        historical_fcast_es,
        predicted_values,
        precision,
        _,
    ) = expo_model.get_expo_data(
        data,
        trend,
        seasonal,
        seasonal_periods,
        dampen,
        n_predict,
        target_col,
        start_window,
        forecast_horizon,
    )

    helpers.plot_forecast(
        "PES",
        target_col,
        historical_fcast_es,
        predicted_values,
        ticker_series,
        ticker_name,
        data,
        n_predict,
        forecast_horizon,
        None,
        precision,
        export,
    )
