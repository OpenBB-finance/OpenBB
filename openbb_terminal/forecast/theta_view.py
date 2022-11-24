"""Theta View"""
__docformat__ = "numpy"

import logging
from typing import Union, Optional, List
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from openbb_terminal.forecast import theta_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_theta_forecast(
    data: Union[pd.DataFrame, pd.Series],
    target_column: str = "close",
    dataset_name: str = "",
    seasonal: str = "M",
    seasonal_periods: int = 7,
    n_predict: int = 5,
    start_window: float = 0.85,
    forecast_horizon: int = 5,
    export: str = "",
    residuals: bool = False,
    forecast_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    naive: bool = False,
    export_pred_raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
):
    """Display Theta forecast

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    target_column: Optional[str]:
        Target column to forecast. Defaults to "close".
    dataset_name: str
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
    naive: bool
        Whether to show the naive baseline. This just assumes the closing price will be the same
        as the previous day's closing price. Defaults to False.
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    """

    data = helpers.clean_data(data, start_date, end_date, target_column, None)
    if not helpers.check_data(data, target_column, None):
        return
    (
        ticker_series,
        historical_fcast,
        predicted_values,
        precision,
        best_theta,
        _model,
    ) = theta_model.get_theta_data(
        data=data,
        seasonal=seasonal,
        seasonal_periods=seasonal_periods,
        n_predict=n_predict,
        target_column=target_column,
        start_window=start_window,
        forecast_horizon=forecast_horizon,
    )
    if ticker_series == []:
        return

    probabilistic = False
    helpers.plot_forecast(
        name=f"THETA_{best_theta:.2f}",
        target_col=target_column,
        historical_fcast=historical_fcast,
        predicted_values=predicted_values,
        ticker_series=ticker_series,
        ticker_name=dataset_name,
        data=data,
        n_predict=n_predict,
        forecast_horizon=forecast_horizon,
        past_covariates=None,
        precision=precision,
        probabilistic=probabilistic,
        export=export,
        forecast_only=forecast_only,
        naive=naive,
        export_pred_raw=export_pred_raw,
        external_axes=external_axes,
    )

    if residuals:
        # TODO: Figure out why residuals do not work with Theta
        console.print(
            "[red]Theta residual is currently not supported. Please stay tuned![/red]"
        )
