"""Quantile Anomaly Detector View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import anom_model, helpers
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_anomaly_detection(
    data: Union[pd.Series, pd.DataFrame],
    dataset_name="",
    target_column: str = "close",
    train_split: float = 0.6,
    export: str = "",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
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
    export: (str, optional)
        Export data to csv, jpg, png, or pdf. Defaults to "".
    start_date: (Optional[datetime], optional)
        Start date. Defaults to None.
    end_date: (Optional[datetime], optional)
        End date. Defaults to None.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[None, go.Figure]
        None if external_axes is True, otherwise the figure object
    """
    data = helpers.clean_data(data, start_date, end_date, target_column)
    if not helpers.check_data(data, target_column):
        return None

    (ticker_series, _, binary_anom) = anom_model.get_anomaly_detection_data(
        data=data,
        target_column=target_column,
        train_split=train_split,
    )

    ticker_max = np.max(ticker_series.values())
    df_ticker = ticker_series.pd_dataframe()[target_column]
    df_binary_anom = binary_anom.pd_dataframe()

    fig = OpenBBFigure(xaxis_title="Date")
    fig.set_title(f"Quantile Anomaly Detection for {dataset_name}")

    fig.add_scatter(x=df_ticker.index, y=df_ticker, name=target_column, mode="lines")

    for column in df_binary_anom.columns:
        fig.add_scatter(
            x=df_binary_anom.index,
            y=df_binary_anom[column] * int(ticker_max),
            name="detected binary anomaly",
            mode="lines",
            line=dict(color="red"),
        )

    console.print(
        f" [green]Quantile Anomaly Detection for {dataset_name} calculated.[/green]"
    )

    # user wants to export plot
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{dataset_name}_Anomaly_Detection",
        figure=fig,
    )

    return fig.show(external=external_axes)
