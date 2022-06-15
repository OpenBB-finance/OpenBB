"""Theta View"""
__docformat__ = "numpy"

import logging
from typing import Union

import pandas as pd

from openbb_terminal.forecasting import theta_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecasting import helpers

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_theta_forecast(
    data: Union[pd.DataFrame, pd.Series],
    ticker_name: str,
    seasonal: str,
    seasonal_periods: int,
    n_predict: int,
    target_col: str,
    start_window: float,
    forecast_horizon: int,
    export: str = "",
):
    """Display Theta forecast

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    ticker_name str
        The name of the ticker to be predicted
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to MULTIPLICATIVE.
    seasonal_periods: int
        Number of seasonal periods in a year
        If not set, inferred from frequency of the series.
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
        historical_fcast,
        predicted_values,
        precision,
        best_theta,
        _model,
    ) = theta_model.get_theta_data(
        data,
        seasonal,
        seasonal_periods,
        n_predict,
        target_col,
        start_window,
        forecast_horizon,
    )
    probabilistic = False
    helpers.plot_forecast(
        f"Theta {best_theta:.2f}",
        target_col,
        historical_fcast,
        predicted_values,
        ticker_series,
        ticker_name,
        data,
        n_predict,
        forecast_horizon,
        None,
        precision,
        probabilistic,
        export,
    )
