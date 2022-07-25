"""Theta View"""
__docformat__ = "numpy"

import logging
from typing import Union, Optional
from datetime import datetime

import pandas as pd

from openbb_terminal.forecasting import theta_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecasting import helpers
from openbb_terminal.rich_config import console

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
    residuals: bool = False,
    forecast_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
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
    residuals: bool
        Whether to show residuals for the model. Defaults to False.
    forecast_only: bool
        Whether to only show dates in the forecasting range. Defaults to False.
    start_date: Optional[datetime]
        The starting date to perform analysis, data before this is trimmed. Defaults to None.
    end_date: Optional[datetime]
        The ending date to perform analysis, data after this is trimmed. Defaults to None.
    """

    data = helpers.clean_data(data, start_date, end_date)
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
        forecast_only=forecast_only,
    )
    if residuals:
        # TODO: Figure out why residuals do not work with Theta
        console.print(
            "[red]Theta residual is currently not supported. Please stay tuned![/red]"
        )
