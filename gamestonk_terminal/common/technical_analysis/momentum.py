"""Momentum Technical Analysis"""
__docformat__ = "numpy"

import argparse
from typing import List

import matplotlib.pyplot as plt
import pandas_ta as ta
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def cci(other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame):
    """Commodity channel index

    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="cci",
        description="""
            The CCI is designed to detect beginning and ending market trends.
            The range of 100 to -100 is the normal trading range. CCI values outside of this
            range indicate overbought or oversold conditions. You can also look for price
            divergence in the CCI. If the price is making new highs, and the CCI is not,
            then a price correction is likely.
        """,
    )

    parser.add_argument(
        "-l",
        "--length",
        action="store",
        dest="n_length",
        type=check_positive,
        default=14,
        help="length",
    )
    parser.add_argument(
        "-s",
        "--scalar",
        action="store",
        dest="n_scalar",
        type=check_positive,
        default=0.015,
        help="scalar",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="n_offset",
        type=check_positive,
        default=0,
        help="offset",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Daily
        if s_interval == "1440min":
            df_ta = ta.cci(
                high=df_stock["High"],
                low=df_stock["Low"],
                close=df_stock["Adj Close"],
                length=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.cci(
                high=df_stock["High"],
                low=df_stock["Low"],
                close=df_stock["Close"],
                length=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.set_title(f"{s_ticker} CCI")
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax2 = axes[1]
        ax2.plot(df_ta.index, df_ta.values, "b", lw=2)
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.axhspan(100, plt.gca().get_ylim()[1], facecolor="r", alpha=0.2)
        ax2.axhspan(plt.gca().get_ylim()[0], -100, facecolor="g", alpha=0.2)
        ax2.axhline(100, linewidth=3, color="r", ls="--")
        ax2.axhline(-100, linewidth=3, color="g", ls="--")
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.minorticks_on()
        ax2.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

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

    except Exception as e:
        print(e, "\n")


def macd(other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame):
    """Moving average convergence divergence

    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="macd",
        description="""
            The Moving Average Convergence Divergence (MACD) is the difference
            between two Exponential Moving Averages. The Signal line is an Exponential Moving
            Average of the MACD. \n \n The MACD signals trend changes and indicates the start
            of new trend direction. High values indicate overbought conditions, low values
            indicate oversold conditions. Divergence with the price indicates an end to the
            current trend, especially if the MACD is at extreme high or low values. When the MACD
            line crosses above the signal line a buy signal is generated. When the MACD crosses
            below the signal line a sell signal is generated. To confirm the signal, the MACD
            should be above zero for a buy, and below zero for a sell.
        """,
    )

    parser.add_argument(
        "-f",
        "--fast",
        action="store",
        dest="n_fast",
        type=check_positive,
        default=12,
        help="The short period.",
    )
    parser.add_argument(
        "-s",
        "--slow",
        action="store",
        dest="n_slow",
        type=check_positive,
        default=26,
        help="The long period.",
    )
    parser.add_argument(
        "--signal",
        action="store",
        dest="n_signal",
        type=check_positive,
        default=9,
        help="The signal period.",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="n_offset",
        type=check_positive,
        default=0,
        help="How many periods to offset the result.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Daily
        if s_interval == "1440min":
            df_ta = ta.macd(
                df_stock["Adj Close"],
                fast=ns_parser.n_fast,
                slow=ns_parser.n_slow,
                signal=ns_parser.n_signal,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.macd(
                df_stock["Close"],
                fast=ns_parser.n_fast,
                slow=ns_parser.n_slow,
                signal=ns_parser.n_signal,
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.set_title(f"{s_ticker} MACD")
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.minorticks_on()
        ax2.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


def rsi(other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame):
    """Relative strength index

    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="rsi",
        description="""
            The Relative Strength Index (RSI) calculates a ratio of the
            recent upward price movements to the absolute price movement. The RSI ranges
            from 0 to 100. The RSI is interpreted as an overbought/oversold indicator when
            the value is over 70/below 30. You can also look for divergence with price. If
            the price is making new highs/lows, and the RSI is not, it indicates a reversal.
        """,
    )

    parser.add_argument(
        "-l",
        "--length",
        action="store",
        dest="n_length",
        type=check_positive,
        default=14,
        help="length",
    )
    parser.add_argument(
        "-s",
        "--scalar",
        action="store",
        dest="n_scalar",
        type=check_positive,
        default=100,
        help="scalar",
    )
    parser.add_argument(
        "-d",
        "--drift",
        action="store",
        dest="n_drift",
        type=check_positive,
        default=1,
        help="drift",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="n_offset",
        type=check_positive,
        default=0,
        help="offset",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Daily
        if s_interval == "1440min":
            df_ta = ta.rsi(
                df_stock["Adj Close"],
                length=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                drift=ns_parser.n_drift,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.rsi(
                df_stock["Close"],
                length=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                drift=ns_parser.n_drift,
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
        ax.set_title(f" {s_ticker} RSI{ns_parser.n_length} ")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax2 = axes[1]
        ax2.plot(df_ta.index, df_ta.values, "b", lw=2)
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.axhspan(70, 100, facecolor="r", alpha=0.2)
        ax2.axhspan(0, 30, facecolor="g", alpha=0.2)
        ax2.axhline(70, linewidth=3, color="r", ls="--")
        ax2.axhline(30, linewidth=3, color="g", ls="--")
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.minorticks_on()
        ax2.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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

    except Exception as e:
        print(e, "\n")


def stoch(
    other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame
):
    """Stochastic oscillator

    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="stoch",
        description="""
            The Stochastic Oscillator measures where the close is in relation
            to the recent trading range. The values range from zero to 100. %D values over 75
            indicate an overbought condition; values under 25 indicate an oversold condition.
            When the Fast %D crosses above the Slow %D, it is a buy signal; when it crosses
            below, it is a sell signal. The Raw %K is generally considered too erratic to use
            for crossover signals.
        """,
    )

    parser.add_argument(
        "-k",
        "--fastkperiod",
        action="store",
        dest="n_fastkperiod",
        type=check_positive,
        default=14,
        help="The time period of the fastk moving average",
    )
    parser.add_argument(
        "-d",
        "--slowdperiod",
        action="store",
        dest="n_slowdperiod",
        type=check_positive,
        default=3,
        help="The time period of the slowd moving average",
    )
    parser.add_argument(
        "--slowkperiod",
        action="store",
        dest="n_slowkperiod",
        type=check_positive,
        default=3,
        help="The time period of the slowk moving average",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="n_offset",
        type=check_positive,
        default=0,
        help="offset",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Daily
        if s_interval == "1440min":
            df_ta = ta.stoch(
                high=df_stock["High"],
                low=df_stock["Low"],
                close=df_stock["Adj Close"],
                k=ns_parser.n_fastkperiod,
                d=ns_parser.n_slowdperiod,
                smooth_k=ns_parser.n_slowkperiod,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.stoch(
                high=df_stock["High"],
                low=df_stock["Low"],
                close=df_stock["Close"],
                k=ns_parser.n_fastkperiod,
                d=ns_parser.n_slowdperiod,
                smooth_k=ns_parser.n_slowkperiod,
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
        ax.set_title(f"Stochastic Relative Strength Index (STOCH RSI) on {s_ticker}")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_xticklabels([])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        ax2 = axes[1]
        ax2.plot(df_ta.index, df_ta.iloc[:, 0].values, "k", lw=2)
        ax2.plot(df_ta.index, df_ta.iloc[:, 1].values, "b", lw=2, ls="--")
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])

        ax2.axhspan(80, 100, facecolor="r", alpha=0.2)
        ax2.axhspan(0, 20, facecolor="g", alpha=0.2)
        ax2.axhline(80, linewidth=3, color="r", ls="--")
        ax2.axhline(20, linewidth=3, color="g", ls="--")

        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.minorticks_on()
        ax2.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax2.set_ylim([0, 100])

        ax3 = ax2.twinx()
        ax3.set_ylim(ax2.get_ylim())
        ax3.set_yticks([20, 80])
        ax3.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])
        ax2.legend(
            [f"%K {df_ta.columns[0]}", f"%D {df_ta.columns[1]}"], loc="lower left"
        )

        if gtff.USE_ION:
            plt.ion()

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)
        plt.show()

        print("")

    except Exception as e:
        print(e, "\n")


def fisher(
    other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame
):
    """Fisher Transform

    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="fisher",
        description="""
            The Fisher Transform is a technical indicator created by John F. Ehlers
            that converts prices into a Gaussian normal distribution.1 The indicator
            highlights when prices have   moved to an extreme, based on recent prices.
            This may help in spotting turning points in the price of an asset. It also
            helps show the trend and isolate the price waves within a trend.
        """,
    )

    parser.add_argument(
        "-l",
        "--length",
        action="store",
        dest="n_length",
        type=check_positive,
        default=14,
        help="length",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="n_offset",
        type=check_positive,
        default=0,
        help="offset",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Daily
        if s_interval == "1440min":
            df_ta = ta.fisher(
                high=df_stock["High"],
                low=df_stock["Low"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.fisher(
                high=df_stock["High"],
                low=df_stock["Low"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.set_title(f"{s_ticker} Fisher Transform")
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=1)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "k", lw=1)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax2 = axes[1]
        ax2.plot(
            df_ta.index,
            df_ta["FISHERT_14_1"].values,
            "b",
            lw=2,
            label="Fisher",
        )
        ax2.plot(
            df_ta.index,
            df_ta["FISHERTs_14_1"].values,
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
        ax2.minorticks_on()
        ax2.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.axhspan(2, plt.gca().get_ylim()[1], facecolor="r", alpha=0.2)
        ax2.axhspan(plt.gca().get_ylim()[0], -2, facecolor="g", alpha=0.2)
        ax2.axhline(2, linewidth=3, color="r", ls="--")
        ax2.axhline(-2, linewidth=3, color="g", ls="--")
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.minorticks_on()
        ax2.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        ax2.set_yticks([-2, 0, 2])
        ax2.set_yticklabels(["-2 STDEV", "0", "+2 STDEV"])

        if gtff.USE_ION:
            plt.ion()

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.legend()
        plt.show()

        print("")

    except Exception as e:
        print(e, "\n")
