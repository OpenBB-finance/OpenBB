"""Trend Indicators View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_adx(
    data: pd.DataFrame,
    window: int = 14,
    scalar: int = 100,
    drift: int = 1,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Plots ADX indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with OHLC price data
    window : int
        Length of window
    scalar : int
        Scalar variable
    drift : int
        Drift variable
    symbol : str
        Ticker
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(adx=dict(length=window, scalar=scalar, drift=drift)),
        f"Average Directional Movement Index (ADX) on {symbol}",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "adx",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_aroon(
    data: pd.DataFrame,
    window: int = 25,
    scalar: int = 100,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Plots Aroon indicator

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe with OHLC price data
    window: int
        Length of window
    symbol: str
        Ticker
    scalar: int
        Scalar variable
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(aroon=dict(length=window, scalar=scalar)),
        f"Aroon on {symbol}",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "aroon",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
