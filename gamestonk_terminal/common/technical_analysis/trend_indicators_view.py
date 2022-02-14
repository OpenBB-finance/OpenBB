"""Trend Indicators View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.common.technical_analysis import trend_indicators_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale, reindex_dates
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_adx(
    ohlc: pd.DataFrame,
    length: int = 14,
    scalar: int = 100,
    drift: int = 1,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot ADX indicator

    Parameters
    ----------
    ohlc : pd.DataFrame
        Dataframe with OHLC price data
    length : int
        Length of window
    scalar : int
        Scalar variable
    drift : int
        Drift variable
    s_ticker : str
        Ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = trend_indicators_model.adx(
        high_values=ohlc["High"],
        low_values=ohlc["Low"],
        close_values=ohlc["Adj Close"],
        length=length,
        scalar=scalar,
        drift=drift,
    )
    plot_data = pd.merge(ohlc, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
        ax1, ax2 = axes
    else:
        if len(external_axes) != 2:
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        ax1, ax2 = external_axes

    ax1.plot(plot_data.index, plot_data["Close"].values)
    ax1.set_title(f"Average Directional Movement Index (ADX) on {s_ticker}")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values)
    ax2.plot(plot_data.index, plot_data[df_ta.columns[1]].values, color=theme.up_color)
    ax2.plot(
        plot_data.index, plot_data[df_ta.columns[2]].values, color=theme.down_color
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.axhline(25, ls="--")
    ax2.legend(
        [
            f"ADX ({df_ta.columns[0]})",
            f"+DI ({df_ta.columns[1]})",
            f"-DI ({df_ta.columns[2]})",
        ]
    )
    ax2.set_ylim([0, 100])
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "adx",
        df_ta,
    )


@log_start_end(log=logger)
def display_aroon(
    ohlc: pd.DataFrame,
    length: int = 25,
    scalar: int = 100,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Aroon indicator

    Parameters
    ----------
    ohlc : pd.DataFrame
        Dataframe with OHLC price data
    length:int
        Length of window
    s_ticker : str
        Ticker
    scalar : int
        Scalar variable
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    df_ta = trend_indicators_model.aroon(
        high_values=ohlc["High"],
        low_values=ohlc["Low"],
        length=length,
        scalar=scalar,
    )
    plot_data = pd.merge(ohlc, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 3 axes
    if not external_axes:
        _, axes = plt.subplots(
            3, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
        ax1, ax2, ax3 = axes
    else:
        if len(external_axes) != 3:
            console.print("[red]Expected list of 3 axis items./n[/red]")
            return
        ax1, ax2, ax3 = external_axes

    ax1.plot(plot_data.index, plot_data["Adj Close"].values)
    ax1.set_title(f"Aroon on {s_ticker}")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values, theme.down_color)
    ax2.plot(plot_data.index, plot_data[df_ta.columns[1]].values, theme.up_color)
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.axhline(50, ls="--")
    ax2.legend([f"Aroon DOWN ({df_ta.columns[0]})", f"Aroon UP ({df_ta.columns[1]})"])
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3.plot(plot_data.index, plot_data[df_ta.columns[2]].values)
    ax3.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax3.legend([f"Aroon OSC ({df_ta.columns[2]})"])
    ax3.set_ylim([-100, 100])
    theme.style_primary_axis(
        ax3,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "aroon",
        df_ta,
    )
