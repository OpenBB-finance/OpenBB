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
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_cci(
    df: pd.DataFrame,
    length: int = 14,
    scalar: float = 0.0015,
    s_ticker: str = "",
    export: str = "",
):
    """Display CCI Indicator

    Parameters
    ----------

    ohlc_df : pd.DataFrame
        Dataframe of OHLC
    length : int
        Length of window
    scalar : float
        Scalar variable
    s_ticker : str
        Stock ticker
    export : str
        Format to export data
    """
    df_ta = momentum_model.cci(df["High"], df["Low"], df["Adj Close"], length, scalar)

    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} CCI")
    ax.plot(
        df.index,
        df["Adj Close"].values,
    )
    ax.set_xlim(df.index[0], df.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.yaxis.set_label_position("right")
    ax.grid(visible=True, zorder=0)

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.values)
    ax2.set_xlim(df.index[0], df.index[-1])
    ax2.axhspan(100, ax2.get_ylim()[1], facecolor=theme.down_color, alpha=0.2)
    ax2.axhspan(ax2.get_ylim()[0], -100, facecolor=theme.up_color, alpha=0.2)

    ax2.tick_params(axis="x", rotation=10)

    ax2.grid(visible=True, zorder=0)

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.axhline(100, color=theme.down_color, ls="--")
    ax3.axhline(-100, color=theme.up_color, ls="--")

    ax2.set_yticks([-100, 100])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

    if gtff.USE_ION:
        plt.ion()

    fig.tight_layout(pad=1)
    plt.show()

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cci",
        df_ta,
    )


@log_start_end(log=logger)
def display_macd(
    values: pd.Series,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
    s_ticker: str = "",
    export: str = "",
):
    """Plot MACD signal

    Parameters
    ----------
    values : pd.DataFrame
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
    """
    df_ta = momentum_model.macd(values, n_fast, n_slow, n_signal)

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} MACD")
    ax.plot(values.index, values.values)
    ax.set_xlim(values.index[0], values.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.yaxis.set_label_position("right")
    ax.grid(visible=True, zorder=0)

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.iloc[:, 0].values)
    ax2.plot(df_ta.index, df_ta.iloc[:, 2].values, color=theme.down_color)
    ax2.bar(df_ta.index, df_ta.iloc[:, 1].values, color=theme.up_color)
    ax2.legend(
        [
            f"MACD Line {df_ta.columns[0]}",
            f"Signal Line {df_ta.columns[2]}",
            f"Histogram {df_ta.columns[1]}",
        ]
    )
    ax2.set_xlim(values.index[0], values.index[-1])
    ax2.tick_params(axis="x", rotation=10)
    ax2.grid(visible=True, zorder=0)

    if gtff.USE_ION:
        plt.ion()

    fig.tight_layout(pad=1)

    plt.show()
    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "macd",
        df_ta,
    )


@log_start_end(log=logger)
def display_rsi(
    prices: pd.Series,
    length: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
    s_ticker: str = "",
    export: str = "",
):
    """Display RSI Indicator

    Parameters
    ----------
    prices : pd.Series
        Dataframe of prices
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
    """
    df_ta = momentum_model.rsi(prices, length, scalar, drift)

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.plot(prices.index, prices.values)
    ax.set_title(f"{s_ticker} RSI{length}")
    ax.set_xlim(prices.index[0], prices.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.yaxis.set_label_position("right")
    ax.grid(visible=True, zorder=0)

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.values)
    ax2.set_xlim(prices.index[0], prices.index[-1])
    ax2.axhspan(0, 30, facecolor=theme.up_color, alpha=0.2)
    ax2.axhspan(70, 100, facecolor=theme.down_color, alpha=0.2)
    ax2.grid(visible=True, zorder=0)
    ax2.tick_params(axis="x", rotation=10)

    ax2.set_ylim([0, 100])
    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.axhline(30, color=theme.up_color, ls="--")
    ax3.axhline(70, color=theme.down_color, ls="--")
    ax2.set_yticks([30, 70])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

    if gtff.USE_ION:
        plt.ion()

    fig.tight_layout(pad=1)
    plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "rsi",
        df_ta,
    )


@log_start_end(log=logger)
def display_stoch(
    df_stock: pd.DataFrame,
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
    df_stock : pd.DataFrame
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
        df_stock["High"],
        df_stock["Low"],
        df_stock["Adj Close"],
        fastkperiod,
        slowdperiod,
        slowkperiod,
    )
    # This plot has 1 axis
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
        ax1, ax2 = axes
        ax3 = ax2.twinx()
    else:
        if len(external_axes) != 3:
            console.print("[red]Expected list of 3 axis items./n[/red]")
            return
        ax1, ax2, ax3 = external_axes
    ax1.plot(df_stock.index, df_stock["Adj Close"].values)

    ax1.set_title(f"Stochastic Relative Strength Index (STOCH RSI) on {s_ticker}")
    ax1.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(ax1)

    ax2.plot(df_ta.index, df_ta.iloc[:, 0].values)
    ax2.plot(df_ta.index, df_ta.iloc[:, 1].values, ls="--")
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    theme.style_primary_axis(ax2)

    ax3.set_ylim(ax2.get_ylim())
    ax3.axhspan(80, 100, facecolor=theme.down_color, alpha=0.2)
    ax3.axhspan(0, 20, facecolor=theme.up_color, alpha=0.2)
    ax3.axhline(80, color=theme.down_color, ls="--")
    ax3.axhline(20, color=theme.up_color, ls="--")
    theme.style_twin_axis(ax3)

    ax2.set_yticks([20, 80])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])
    ax2.legend([f"%K {df_ta.columns[0]}", f"%D {df_ta.columns[1]}"])

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "stoch",
        df_ta,
    )


@log_start_end(log=logger)
def display_fisher(
    df_stock: pd.DataFrame,
    length: int = 14,
    s_ticker: str = "",
    export: str = "",
):
    """Display Fisher Indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    length : int
        Length of window
    s_ticker : str
        Ticker string
    export : str
        Format to export data
    """
    df_ta = momentum_model.fisher(df_stock["High"], df_stock["Low"], length)

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} Fisher Transform")
    ax.plot(df_stock.index, df_stock["Adj Close"].values)
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Price")
    ax.yaxis.set_label_position("right")
    ax.grid(visible=True, zorder=0)

    ax2 = axes[1]
    ax2.plot(
        df_ta.index,
        df_ta.iloc[:, 0].values,
        label="Fisher",
    )
    ax2.plot(
        df_ta.index,
        df_ta.iloc[:, 1].values,
        label="Signal",
    )

    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.axhspan(2, plt.gca().get_ylim()[1], facecolor=theme.down_color, alpha=0.2)
    ax2.axhspan(plt.gca().get_ylim()[0], -2, facecolor=theme.up_color, alpha=0.2)
    ax2.axhline(2, color=theme.down_color, ls="--")
    ax2.axhline(-2, color=theme.up_color, ls="--")

    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.axhspan(2, plt.gca().get_ylim()[1], facecolor=theme.down_color, alpha=0.2)
    ax2.axhspan(plt.gca().get_ylim()[0], -2, facecolor=theme.up_color, alpha=0.2)
    ax2.axhline(2, color=theme.down_color, ls="--")
    ax2.axhline(-2, color=theme.up_color, ls="--")
    ax2.grid(visible=True, zorder=0)
    ax2.tick_params(axis="x", rotation=10)

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())

    ax2.set_yticks([-2, 0, 2])
    ax2.set_yticklabels(["-2 STDEV", "0", "+2 STDEV"])
    ax2.legend()

    if gtff.USE_ION:
        plt.ion()

    fig.tight_layout(pad=1)

    plt.show()

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "fisher",
        df_ta,
    )


@log_start_end(log=logger)
def display_cg(
    values: pd.Series,
    length: int = 14,
    s_ticker: str = "",
    export: str = "",
):
    """Display center of gravity Indicator

    Parameters
    ----------
    values : pd.Series
        Series of values
    length : int
        Length of window
    s_ticker : str
        Stock ticker
    export : str
        Format to export data
    """
    df_ta = momentum_model.cg(values, length)

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} Centre of Gravity")
    ax.plot(values.index, values.values)
    ax.set_xlim(values.index[0], values.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.yaxis.set_label_position("right")
    ax.grid(visible=True, zorder=0)

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.values, label="CG")
    # shift cg 1 bar forward for signal
    signal = df_ta.values
    signal = np.roll(signal, 1)
    ax2.plot(df_ta.index, signal, label="Signal")
    ax2.set_xlim(values.index[0], values.index[-1])
    ax2.grid(visible=True, zorder=0)
    ax2.tick_params(axis="x", rotation=10)

    if gtff.USE_ION:
        plt.ion()

    fig.tight_layout(pad=1)
    plt.legend()
    plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cg",
        df_ta,
    )
