"""Volatility Technical Indicators View"""
__docformat__ = "numpy"

import logging
import os

import pandas as pd

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_bbands(
    data: pd.DataFrame,
    symbol: str = "",
    window: int = 15,
    n_std: float = 2,
    mamode: str = "sma",
    export: str = "",
    sheet_name: str = None,
    external_axes: bool = False,
):
    """Plots bollinger bands

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    export : str
        Format of export file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(bbands=dict(length=window, scalar=n_std, mamode=mamode)),
        f"{symbol} Bollinger Bands",
        False,
        volume=False,
    )

    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "bbands",
        ta.df_ta,
        sheet_name,
    )

    fig.show(external=external_axes)


@log_start_end(log=logger)
def display_donchian(
    data: pd.DataFrame,
    symbol: str = "",
    upper_length: int = 20,
    lower_length: int = 20,
    export: str = "",
    sheet_name: str = None,
    external_axes: bool = False,
):
    """Plots donchian channels

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel
    export : str
        Format of export file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(donchian=dict(upper_length=upper_length, lower_length=lower_length)),
        f"{symbol} Donchian Channels",
        False,
        volume=False,
    )

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "donchian",
        ta.df_ta,
        sheet_name,
    )

    fig.show(external=external_axes)


@log_start_end(log=logger)
def view_kc(
    data: pd.DataFrame,
    window: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
    symbol: str = "",
    export: str = "",
    sheet_name: str = None,
    external_axes: bool = False,
):
    """Plots Keltner Channels Indicator

    Parameters
    ----------

    data: pd.DataFrame
        Dataframe of ohlc prices
    window: int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset: int
        Offset value
    symbol: str
        Ticker symbol
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
        dict(kc=dict(length=window, scalar=scalar, mamode=mamode, offset=offset)),
        f"{symbol} Keltner Channels",
        False,
        volume=False,
    )

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "kc",
        ta.df_ta,
        sheet_name,
    )

    fig.show(external=external_axes)


@log_start_end(log=logger)
def display_atr(
    data: pd.DataFrame,
    symbol: str = "",
    window: int = 14,
    mamode: str = "sma",
    offset: int = 0,
    export: str = "",
    sheet_name: str = None,
    external_axes: bool = False,
):
    """Plots ATR

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate upper channel
    export : str
        Format of export file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(atr=dict(length=window, mamode=mamode, offset=offset)),
        f"{symbol} Average True Range",
        False,
        volume=False,
    )

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "atr",
        ta.df_ta,
        sheet_name,
    )

    fig.show(external=external_axes)
