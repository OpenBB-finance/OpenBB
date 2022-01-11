"""Momentum View"""
__docformat__ = "numpy"

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale

register_matplotlib_converters()


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

    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} CCI")
    ax.plot(df.index, df["Adj Close"].values, "k", lw=2)
    ax.set_xlim(df.index[0], df.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.values, "b", lw=2)
    ax2.set_xlim(df.index[0], df.index[-1])
    ax2.axhspan(100, plt.gca().get_ylim()[1], facecolor="r", alpha=0.2)
    ax2.axhspan(plt.gca().get_ylim()[0], -100, facecolor="g", alpha=0.2)
    ax2.axhline(100, linewidth=3, color="r", ls="--")
    ax2.axhline(-100, linewidth=3, color="g", ls="--")
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.set_yticks([-100, 100])
    ax3.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)
    plt.show()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cci",
        df_ta,
    )


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

    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} MACD")
    ax.plot(values.index, values.values, "k", lw=2)
    ax.set_xlim(values.index[0], values.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.iloc[:, 0].values, "b", lw=2)
    ax2.plot(df_ta.index, df_ta.iloc[:, 2].values, "r", lw=2)
    ax2.bar(df_ta.index, df_ta.iloc[:, 1].values, color="g")
    ax2.legend(
        [
            f"MACD Line {df_ta.columns[0]}",
            f"Signal Line {df_ta.columns[2]}",
            f"Histogram {df_ta.columns[1]}",
        ],
        loc="upper left",
    )
    ax2.set_xlim(values.index[0], values.index[-1])
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.show()
    print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "macd",
        df_ta,
    )


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

    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.plot(prices.index, prices.values, "k", lw=2)
    ax.set_title(f" {s_ticker} RSI{length} ")
    ax.set_xlim(prices.index[0], prices.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.values, "b", lw=2)
    ax2.set_xlim(prices.index[0], prices.index[-1])
    ax2.axhspan(70, 100, facecolor="r", alpha=0.2)
    ax2.axhspan(0, 30, facecolor="g", alpha=0.2)
    ax2.axhline(70, linewidth=3, color="r", ls="--")
    ax2.axhline(30, linewidth=3, color="g", ls="--")
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")
    ax2.set_ylim([0, 100])
    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.set_yticks([30, 70])
    ax3.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)
    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "rsi",
        df_ta,
    )


def display_stoch(
    df_stock: pd.DataFrame,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
    s_ticker: str = "",
    export: str = "",
):
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
    """
    df_ta = momentum_model.stoch(
        df_stock["High"],
        df_stock["Low"],
        df_stock["Adj Close"],
        fastkperiod,
        slowdperiod,
        slowkperiod,
    )

    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)

    ax.set_title(f"Stochastic Relative Strength Index (STOCH RSI) on {s_ticker}")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_xticklabels([])
    ax.set_ylabel("Share Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.iloc[:, 0].values, "k", lw=2)
    ax2.plot(df_ta.index, df_ta.iloc[:, 1].values, "b", lw=2, ls="--")
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.axhspan(80, 100, facecolor="r", alpha=0.2)
    ax2.axhspan(0, 20, facecolor="g", alpha=0.2)
    ax2.axhline(80, linewidth=3, color="r", ls="--")
    ax2.axhline(20, linewidth=3, color="g", ls="--")
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")
    ax2.set_ylim([0, 100])

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.set_yticks([20, 80])
    ax3.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])
    ax2.legend([f"%K {df_ta.columns[0]}", f"%D {df_ta.columns[1]}"], loc="lower left")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)
    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "stoch",
        df_ta,
    )


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

    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} Fisher Transform")
    ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=1)
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Price")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax2 = axes[1]
    ax2.plot(
        df_ta.index,
        df_ta.iloc[:, 0].values,
        "b",
        lw=2,
        label="Fisher",
    )
    ax2.plot(
        df_ta.index,
        df_ta.iloc[:, 1].values,
        "fuchsia",
        lw=2,
        label="Signal",
    )
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.axhspan(2, plt.gca().get_ylim()[1], facecolor="r", alpha=0.2)
    ax2.axhspan(plt.gca().get_ylim()[0], -2, facecolor="g", alpha=0.2)
    ax2.axhline(2, linewidth=3, color="r", ls="--")
    ax2.axhline(-2, linewidth=3, color="g", ls="--")
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.axhspan(2, plt.gca().get_ylim()[1], facecolor="r", alpha=0.2)
    ax2.axhspan(plt.gca().get_ylim()[0], -2, facecolor="g", alpha=0.2)
    ax2.axhline(2, linewidth=3, color="r", ls="--")
    ax2.axhline(-2, linewidth=3, color="g", ls="--")
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")
    ax2.set_yticks([-2, 0, 2])
    ax2.set_yticklabels(["-2 STDEV", "0", "+2 STDEV"])

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.legend()
    plt.show()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "fisher",
        df_ta,
    )


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

    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} Centre of Gravity")
    ax.plot(values.index, values.values, "k", lw=1)
    ax.set_xlim(values.index[0], values.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax2 = axes[1]
    ax2.plot(df_ta.index, df_ta.values, "b", lw=2, label="CG")
    # shift cg 1 bar forward for signal
    signal = df_ta.values
    signal = np.roll(signal, 1)
    ax2.plot(df_ta.index, signal, "g", lw=1, label="Signal")
    ax2.set_xlim(values.index[0], values.index[-1])
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)
    plt.legend()
    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cg",
        df_ta,
    )
