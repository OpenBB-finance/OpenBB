"""Probabilistic Exponential Smoothing View"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import expo_model, helpers
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_expo_forecast(
    data: Union[pd.DataFrame, pd.Series],
    target_column: str = "close",
    dataset_name: str = "",
    trend: str = "A",
    seasonal: str = "A",
    seasonal_periods: int = 7,
    dampen: str = "F",
    n_predict: int = 5,
    start_window: float = 0.85,
    forecast_horizon: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    residuals: bool = False,
    forecast_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    naive: bool = False,
    export_pred_raw: bool = False,
    metric: str = "mape",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Display Probabilistic Exponential Smoothing forecast

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    dataset_name: str
        The name of the ticker to be predicted
    target_column: Optional[str]:
        Target column to forecast. Defaults to "close".
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
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
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
    export_pred_raw: bool
        Whether to export the raw predicted values. Defaults to False.
    metric: str
        The metric to use when backtesting. Defaults to "mape".
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data = helpers.clean_data(data, start_date, end_date, target_column, None)
    if not helpers.check_data(data, target_column, None):
        return None

    (
        ticker_series,
        historical_fcast,
        predicted_values,
        precision,
        _model,
    ) = expo_model.get_expo_data(
        data=data,
        target_column=target_column,
        trend=trend,
        seasonal=seasonal,
        seasonal_periods=seasonal_periods,
        dampen=dampen,
        n_predict=n_predict,
        start_window=start_window,
        forecast_horizon=forecast_horizon,
        metric=metric,
    )

    if ticker_series == []:
        return None

    probabilistic = True
    fig = helpers.plot_forecast(
        name="PES",
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
        sheet_name=sheet_name,
        forecast_only=forecast_only,
        naive=naive,
        export_pred_raw=export_pred_raw,
        metric=metric,
        external_axes=external_axes,
    )
    if residuals:
        console.print("[red]Expo model does not support residuals at this time[/red]\n")
        # helpers.plot_residuals(
        #     _model, None, ticker_series, forecast_horizon=forecast_horizon
        # )

    return fig
