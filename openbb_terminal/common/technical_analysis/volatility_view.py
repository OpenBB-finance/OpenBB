"""Volatility Technical Indicators View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.common.technical_analysis import volatility_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale, reindex_dates
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_bbands(
    ohlc: pd.DataFrame,
    ticker: str = "",
    length: int = 15,
    n_std: float = 2,
    mamode: str = "sma",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show bollinger bands

    Parameters
    ----------
    ohlc : pd.DataFrame
        Dataframe of stock prices
    ticker : str
        Ticker
    length : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_ta = volatility_model.bbands(ohlc["Adj Close"], length, n_std, mamode)
    plot_data = pd.merge(ohlc, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(
        plot_data.index,
        plot_data["Adj Close"].values,
    )
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        theme.down_color,
        linewidth=0.7,
    )
    ax.plot(plot_data.index, plot_data[df_ta.columns[1]].values, ls="--", linewidth=0.7)
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[2]].values,
        theme.up_color,
        linewidth=0.7,
    )
    ax.set_title(f"{ticker} Bollinger Bands")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.legend([ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
    ax.fill_between(
        df_ta.index, df_ta.iloc[:, 0].values, df_ta.iloc[:, 2].values, alpha=0.1
    )
    theme.style_primary_axis(
        ax,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "bbands",
        df_ta,
    )


@log_start_end(log=logger)
def display_donchian(
    ohlc: pd.DataFrame,
    ticker: str = "",
    upper_length: int = 20,
    lower_length: int = 20,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show donchian channels

    Parameters
    ----------
    ohlc : pd.DataFrame
        Dataframe of stock prices
    ticker : str
        Ticker
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_ta = volatility_model.donchian(
        ohlc["High"], ohlc["Low"], upper_length, lower_length
    )
    plot_data = pd.merge(ohlc, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(plot_data.index, plot_data["Adj Close"].values)
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        linewidth=0.7,
        label="Upper",
    )
    ax.plot(plot_data.index, plot_data[df_ta.columns[1]].values, linewidth=0.7, ls="--")
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[2]].values,
        linewidth=0.7,
        label="Lower",
    )
    ax.fill_between(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        plot_data[df_ta.columns[2]].values,
        alpha=0.1,
    )
    ax.set_title(f"{ticker} donchian")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Price ($)")
    ax.legend([ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
    theme.style_primary_axis(
        ax,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "donchian",
        df_ta,
    )


@log_start_end(log=logger)
def view_kc(
    ohlc: pd.DataFrame,
    length: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """View Keltner Channels Indicator

    Parameters
    ----------

    ohlc : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window
    mamode: str
        Type of filter
    offset : int
        Offset value
    s_ticker : str
        Ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = volatility_model.kc(
        ohlc["High"],
        ohlc["Low"],
        ohlc["Adj Close"],
        length,
        scalar,
        mamode,
        offset,
    )
    plot_data = pd.merge(ohlc, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(plot_data.index, plot_data["Adj Close"].values)
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        linewidth=0.7,
        label="Upper",
    )
    ax.plot(plot_data.index, plot_data[df_ta.columns[1]].values, linewidth=0.7, ls="--")
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[2]].values,
        linewidth=0.7,
        label="Lower",
    )
    ax.fill_between(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        plot_data[df_ta.columns[2]].values,
        alpha=0.1,
    )
    ax.set_title(f"{s_ticker} Keltner Channels")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Price")
    ax.legend([s_ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
    theme.style_primary_axis(
        ax,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "kc",
        df_ta,
    )
