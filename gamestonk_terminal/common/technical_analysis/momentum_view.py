"""Momentum View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale, reindex_dates
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_cci(
    ohlc: pd.DataFrame,
    length: int = 14,
    scalar: float = 0.0015,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display CCI Indicator

    Parameters
    ----------

    ohlc : pd.DataFrame
        Dataframe of OHLC
    length : int
        Length of window
    scalar : float
        Scalar variable
    s_ticker : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = momentum_model.cci(
        ohlc["High"], ohlc["Low"], ohlc["Adj Close"], length, scalar
    )
    plot_data = pd.merge(ohlc, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if external_axes is None:
        _, (ax1, ax2) = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        ax1, ax2 = external_axes

    ax1.set_title(f"{s_ticker} CCI")
    ax1.plot(
        plot_data.index,
        plot_data["Adj Close"].values,
    )
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")

    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values)
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.axhspan(100, ax2.get_ylim()[1], facecolor=theme.down_color, alpha=0.2)
    ax2.axhspan(ax2.get_ylim()[0], -100, facecolor=theme.up_color, alpha=0.2)

    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.axhline(100, color=theme.down_color, ls="--")
    ax3.axhline(-100, color=theme.up_color, ls="--")

    theme.style_twin_axis(ax3)

    ax2.set_yticks([-100, 100])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cci",
        df_ta,
    )


@log_start_end(log=logger)
def display_macd(
    series: pd.Series,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot MACD signal

    Parameters
    ----------
    series : pd.Series
        Values to input
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    s_ticker : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = momentum_model.macd(series, n_fast, n_slow, n_signal)
    plot_data = pd.merge(series, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if external_axes is None:
        _, (ax1, ax2) = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        ax1, ax2 = external_axes

    ax1.set_title(f"{s_ticker} MACD")
    ax1.plot(plot_data.index, plot_data.iloc[:, 1].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data.iloc[:, 2].values)
    ax2.plot(plot_data.index, plot_data.iloc[:, 4].values, color=theme.down_color)
    ax2.bar(
        plot_data.index,
        plot_data.iloc[:, 3].values,
        width=theme.volume_bar_width,
        color=theme.up_color,
    )
    ax2.legend(
        [
            f"MACD Line {plot_data.columns[2]}",
            f"Signal Line {plot_data.columns[4]}",
            f"Histogram {plot_data.columns[3]}",
        ]
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
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
        "macd",
        df_ta,
    )


@log_start_end(log=logger)
def display_rsi(
    series: pd.Series,
    length: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display RSI Indicator

    Parameters
    ----------
    series : pd.Series
        Values to input
    length : int
        Length of window
    scalar : float
        Scalar variable
    drift : int
        Drift variable
    s_ticker : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = momentum_model.rsi(series, length, scalar, drift)

    # This plot has 2 axes
    if external_axes is None:
        _, (ax1, ax2) = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        ax1, ax2 = external_axes

    plot_data = pd.merge(series, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    ax1.plot(plot_data.index, plot_data.iloc[:, 1].values)
    ax1.set_title(f"{s_ticker} RSI{length}")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax=ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values)
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.axhspan(0, 30, facecolor=theme.up_color, alpha=0.2)
    ax2.axhspan(70, 100, facecolor=theme.down_color, alpha=0.2)
    ax2.set_ylim([0, 100])

    theme.style_primary_axis(
        ax=ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.axhline(30, color=theme.up_color, ls="--")
    ax3.axhline(70, color=theme.down_color, ls="--")
    ax2.set_yticks([30, 70])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "rsi",
        df_ta,
    )


@log_start_end(log=logger)
def display_stoch(
    ohlc: pd.DataFrame,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plot stochastic oscillator signal

    Parameters
    ----------
    ohlc : pd.DataFrame
        Dataframe of prices
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    s_ticker : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    df_ta = momentum_model.stoch(
        ohlc["High"],
        ohlc["Low"],
        ohlc["Adj Close"],
        fastkperiod,
        slowdperiod,
        slowkperiod,
    )
    # This plot has 3 axes
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
        ax1, ax2 = axes
        ax3 = ax2.twinx()
    else:
        if len(external_axes) != 3:
            logger.error("Expected list of three axis items.")
            console.print("[red]Expected list of 3 axis items./n[/red]")
            return
        ax1, ax2, ax3 = external_axes

    plot_data = pd.merge(ohlc, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    ax1.plot(plot_data.index, plot_data["Adj Close"].values)

    ax1.set_title(f"Stochastic Relative Strength Index (STOCH RSI) on {s_ticker}")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values)
    ax2.plot(plot_data.index, plot_data[df_ta.columns[1]].values, ls="--")
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3.set_ylim(ax2.get_ylim())
    ax3.axhspan(80, 100, facecolor=theme.down_color, alpha=0.2)
    ax3.axhspan(0, 20, facecolor=theme.up_color, alpha=0.2)
    ax3.axhline(80, color=theme.down_color, ls="--")
    ax3.axhline(20, color=theme.up_color, ls="--")
    theme.style_twin_axis(ax3)

    ax2.set_yticks([20, 80])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])
    ax2.legend([f"%K {df_ta.columns[0]}", f"%D {df_ta.columns[1]}"])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "stoch",
        df_ta,
    )


@log_start_end(log=logger)
def display_fisher(
    ohlc: pd.DataFrame,
    length: int = 14,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display Fisher Indicator

    Parameters
    ----------
    ohlc : pd.DataFrame
        Dataframe of prices
    length : int
        Length of window
    s_ticker : str
        Ticker string
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    df_ta = momentum_model.fisher(ohlc["High"], ohlc["Low"], length)
    plot_data = pd.merge(ohlc, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 3 axes
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
        ax1, ax2 = axes
        ax3 = ax2.twinx()
    else:
        if len(external_axes) != 3:
            logger.error("Expected list of three axis items.")
            console.print("[red]Expected list of 3 axis items./n[/red]")
            return
        ax1, ax2, ax3 = external_axes

    ax1.set_title(f"{s_ticker} Fisher Transform")
    ax1.plot(plot_data.index, plot_data["Adj Close"].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Price")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        label="Fisher",
    )
    ax2.plot(
        plot_data.index,
        plot_data[df_ta.columns[1]].values,
        label="Signal",
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3.set_ylim(ax2.get_ylim())
    ax3.axhspan(2, ax2.get_ylim()[1], facecolor=theme.down_color, alpha=0.2)
    ax3.axhspan(ax2.get_ylim()[0], -2, facecolor=theme.up_color, alpha=0.2)
    ax3.axhline(2, color=theme.down_color, ls="--")
    ax3.axhline(-2, color=theme.up_color, ls="--")
    theme.style_twin_axis(ax3)

    ax2.set_yticks([-2, 0, 2])
    ax2.set_yticklabels(["-2 STDEV", "0", "+2 STDEV"])
    ax2.legend()

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "fisher",
        df_ta,
    )


@log_start_end(log=logger)
def display_cg(
    series: pd.Series,
    length: int = 14,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display center of gravity Indicator

    Parameters
    ----------
    series : pd.Series
        Series of values
    length : int
        Length of window
    s_ticker : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = momentum_model.cg(series, length)
    plot_data = pd.merge(series, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if external_axes is None:
        _, (ax1, ax2) = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        ax1, ax2 = external_axes

    ax1.set_title(f"{s_ticker} Centre of Gravity")
    ax1.plot(plot_data.index, plot_data[series.name].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values, label="CG")
    # shift cg 1 bar forward for signal
    signal = np.roll(plot_data[df_ta.columns[0]].values, 1)
    ax2.plot(plot_data.index, signal, label="Signal")
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.legend()
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
        "cg",
        df_ta,
    )
