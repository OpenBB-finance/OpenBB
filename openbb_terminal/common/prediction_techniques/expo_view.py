"""Probabilistic Exponential Smoothing View"""
__docformat__ = "numpy"

import logging
import os
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.common.prediction_techniques import expo_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
)
from openbb_terminal.rich_config import console
from openbb_terminal.common.prediction_techniques.pred_helper import (
    print_pretty_prediction,
)

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


def dt_format(x):
    """Convert any Timestamp to YYYY-MM-DD
    Args:
        x: Pandas Timestamp of any length
    Returns:
        x: formatted string
    """
    x = x.strftime("%Y-%m-%d")
    return x


@log_start_end(log=logger)
def display_expo_forecast(
    data: Union[pd.DataFrame, pd.Series],
    ticker_name: str,
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
    # add temp column since we need to use index col for date
    data["date"] = data.index
    # reformat the date column to remove any hour/min/sec
    data["date"] = data["date"].apply(dt_format)

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
        start_window,
        forecast_horizon,
    )

    # Plotting with Matplotlib
    external_axes = None
    if not external_axes:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item.\n[/red]")
            return
        ax = external_axes

    # ax = fig.get_axes()[0] # fig gives list of axes (only one for this case)
    ticker_series.plot(label="Actual Close", figure=fig)
    historical_fcast_es.plot(
        label="Back-test 3-Days ahead forecast (Exp. Smoothing)", figure=fig
    )
    predicted_values.plot(
        label="Probabilistic Forecast", low_quantile=0.1, high_quantile=0.9, figure=fig
    )
    ax.set_title(
        f"PES for ${ticker_name} for next [{n_predict}] days (MAPE={round(precision,2)}%)"
    )
    ax.set_ylabel("Closing")
    ax.set_xlabel("Date")
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    numeric_forecast = predicted_values.quantile_df()["Close_0.5"].tail(n_predict)
    print_pretty_prediction(numeric_forecast, data["Close"].iloc[-1])

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "expo")
