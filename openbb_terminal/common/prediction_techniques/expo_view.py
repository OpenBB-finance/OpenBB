"""Probablistic Exponential Smoothing View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from openbb_terminal.config_terminal import theme
from openbb_terminal.common.prediction_techniques import expo_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    get_next_stock_market_days,
    plot_autoscale,
)
from openbb_terminal.rich_config import console
from openbb_terminal.common.prediction_techniques.pred_helper import (
    print_pretty_prediction,
    plot_data_predictions
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_expo_forecast(
    data: Union[pd.DataFrame, pd.Series],
    ticker_name: str,
    n_predict: int,
    trend: str,
    seasonal: str,
    seasonal_periods: int,
    damped: str,
    export: str = "",
):
    """Display Probalistic Exponential Smoothing forecasting

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    n_predict : int
        Number of days to forecast
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None
    """
    ticker_series, predicted_values, precision, _ = expo_model.get_expo_data(data, trend, seasonal, seasonal_periods, damped, n_predict)
    
    # Plotting with Matplotlib 
    external_axes = None
    if not external_axes:
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item.\n[/red]")
            return
        (ax,) = external_axes

    #ax = fig.get_axes()[0] # fig gives list of axes (only one for this case)
    ticker_series.plot(label="Actual AdjClose", figure=fig)
    predicted_values.plot(label="Probabilistic Forecast", low_quantile=0.1, high_quantile=0.9, figure=fig)
    ax.set_title(f"PES for ${ticker_name} for next [{n_predict}] days MAP={round(precision,2)}%")
    ax.set_ylabel("Adj. Closing")
    ax.set_xlabel("Date")
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()
    
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "expo")
