"""Quantile Anomaly Detector View"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import anom_model, helpers
from openbb_terminal.helper_funcs import plot_autoscale
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_anomaly_detection(
    data: Union[pd.Series, pd.DataFrame],
    dataset_name="",
    target_column: str = "close",
    train_split: float = 0.6,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    external_axes: Optional[List[plt.axes]] = None,
):
    """Display Quantile Anomaly Detection

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame]

    Input Data
    ----------
    target_column: str
        Target column to forecast. Defaults to "close".
    train_split: (float, optional)
        Train/val split. Defaults to 0.85.
    forecast_horizon: (int, optional)
        Forecast horizon. Defaults to 5.
    export: (str, optional)
        Export data to csv. Defaults to "".
    start_date: (Optional[datetime], optional)
        Start date. Defaults to None.
    end_date: (Optional[datetime], optional)
        End date. Defaults to None.
    external_axes: (Optional[List[plt.axes]], optional)
        External axes. Defaults to None.

    Returns
    -------
    None
    """
    data = helpers.clean_data(data, start_date, end_date, target_column)
    if not helpers.check_data(data, target_column):
        return

    (ticker_series, _, binary_anom) = anom_model.get_anomaly_detection_data(
        data=data,
        target_column=target_column,
        train_split=train_split,
    )

    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    ticker_series.plot(label=target_column, ax=ax)

    ticker_max = np.max(ticker_series.values())
    (binary_anom * int(ticker_max)).plot(
        label="detected binary anomaly", c="red", ax=ax
    )
    # set min and max for y axis
    ax.set_ylim([-1, ticker_max * 1.1])

    ax.set_title(f"Quantile Anomaly Detection for {dataset_name}")
    ax.set_xlabel("Date")

    console.print(
        f" [green]Quantile Anomaly Detection for {dataset_name} calculated.[/green]"
    )

    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()
