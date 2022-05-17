"""Monte Carlo View"""
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
    lambda_price_prediction_backtesting_color,
    print_prediction_kpis,
    print_pretty_prediction,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_expo_forecast(
    data: Union[pd.DataFrame, pd.Series],
    n_predict: int,
    export: str = "",
):
    """Display Probalistic Exponential Smoothing forecasting

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    n_predict : int
        Number of days to forecast
    fig_title : str
        Figure title
    export: str
        Format to export data
    time_res : str
        Resolution for data, allowing for predicting outside of standard market days
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None
    """
    ticker_series, predicted_values, _ = expo_model.get_expo_data(data, n_predict)
    
    ticker_series.plot(label="Actual AdjClose")
    predicted_values.plot(label="Probabilistic Forecast", low_quantile=0.05, high_quantile=0.95)
    plt.legend()
    plt.show()


    #export_data(export, os.path.dirname(os.path.abspath(__file__)), "expo")
