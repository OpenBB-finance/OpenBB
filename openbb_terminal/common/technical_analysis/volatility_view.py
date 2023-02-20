"""Volatility Technical Indicators View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.common.technical_analysis import ta_helpers, volatility_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    reindex_dates,
)

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
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_ta = volatility_model.bbands(data, window, n_std, mamode)
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return
    ax.plot(
        plot_data.index,
        plot_data[close_col].values,
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
    ax.set_title(f"{symbol} Bollinger Bands")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.legend([symbol, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
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
        sheet_name,
    )


@log_start_end(log=logger)
def display_donchian(
    data: pd.DataFrame,
    symbol: str = "",
    upper_length: int = 20,
    lower_length: int = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_ta = volatility_model.donchian(data, upper_length, lower_length)
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    ax.plot(plot_data.index, plot_data[close_col].values)
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
    ax.set_title(f"{symbol} donchian")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Price ($)")
    ax.legend([symbol, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
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
        sheet_name,
    )


@log_start_end(log=logger)
def view_kc(
    data: pd.DataFrame,
    window: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = volatility_model.kc(
        data,
        window,
        scalar,
        mamode,
        offset,
    )
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    ax.plot(plot_data.index, plot_data[close_col].values)
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
    ax.set_title(f"{symbol} Keltner Channels")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Price")
    ax.legend([symbol, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
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
        sheet_name,
    )


@log_start_end(log=logger)
def display_atr(
    data: pd.DataFrame,
    symbol: str = "",
    window: int = 14,
    mamode: str = "sma",
    offset: int = 0,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_ta = volatility_model.atr(data, window=window, mamode=mamode, offset=offset)

    # This plot has 2 axes
    if external_axes is None:
        _, axes = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
        (ax1, ax2) = axes
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    ax1.plot(plot_data.index, plot_data.iloc[:, 1].values, color=theme.get_colors()[0])
    ax1.set_title(f"{symbol} ATR")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax=ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(
        plot_data.index, plot_data[df_ta.columns[0]].values, color=theme.get_colors()[1]
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.set_ylabel("ATR")
    theme.style_primary_axis(
        ax=ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "atr",
        df_ta,
        sheet_name,
    )
