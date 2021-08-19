"""Rolling Statistics"""
__docformat__ = "numpy"

import argparse
from typing import List
import matplotlib.pyplot as plt
import pandas_ta as ta
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.helper_funcs import (
    check_positive,
    check_proportion_range,
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def spread(
    other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame
):
    """Standard Deviation & Variance

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
        prog="spread",
        description="""

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
            df_ta = ta.stdev(
                close=df_stock["Adj Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()
            df_ta_ = ta.variance(
                close=df_stock["Adj Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.stdev(
                close=df_stock["Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()
            df_ta_ = ta.variance(
                close=df_stock["Adj Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(3, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.set_title(f"{s_ticker} Spread")
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "fuchsia", lw=1)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "fuchsia", lw=1)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.yaxis.set_label_position("right")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax1 = axes[1]
        ax1.plot(df_ta.index, df_ta.values, "b", lw=1, label="stdev")
        ax1.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax1.set_ylabel("Stdev")
        ax1.yaxis.set_label_position("right")
        ax1.grid(b=True, which="major", color="#666666", linestyle="-")
        ax1.minorticks_on()
        ax1.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax2 = axes[2]
        ax2.plot(df_ta_.index, df_ta_.values, "g", lw=1, label="variance")
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.set_ylabel("Variance")
        ax2.yaxis.set_label_position("right")
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


def quantile(
    other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame
):
    """Overlay Median & Quantile

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Data interval
    df_stock: pd.DataFrame
        Dataframe of dates and prices
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="quantile",
        description="""
            The quantiles are values which divide the distribution such that
            there is a given proportion of observations below the quantile.
            For example, the median is a quantile. The median is the central
            value of the distribution, such that half the points are less than
            or equal to it and half are greater than or equal to it.

            By default, q is set at 0.5, which effectively is median. Change q to
            get the desired quantile (0<q<1).
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
    parser.add_argument(
        "-q",
        "--quantile",
        action="store",
        dest="f_quantile",
        type=check_proportion_range,
        default=0.5,
        help="quantile",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if s_interval == "1440min":
            plt.plot(df_stock.index, df_stock["Adj Close"].values, color="fuchsia")
        else:
            plt.plot(df_stock.index, df_stock["Close"].values, color="fuchsia")
        ax.set_title(f"{s_ticker} Median & Quantile")
        if s_interval == "1440min":
            df_ta_ = ta.median(
                close=df_stock["Adj Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()
            df_ta = ta.quantile(
                df_stock["Adj Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
                q=ns_parser.f_quantile,
            ).dropna()
        else:
            df_ta_ = ta.median(
                close=df_stock["Adj Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()
            df_ta = ta.quantile(
                df_stock["Close"],
                ns_parser.n_length,
                offset=ns_parser.n_offset,
                q=ns_parser.f_quantile,
            ).dropna()
        plt.plot(df_ta_.index, df_ta_.values, "g", lw=1, label="median")
        plt.plot(df_ta.index, df_ta.values, "b", lw=1, label="quantile")

        plt.title(f"Median & Quantile on {s_ticker}")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel(f"{s_ticker} Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.legend()
        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


def skew(other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame):
    """Skewness Indicator

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
        prog="skew",
        description="""
            Skewness is a measure of asymmetry or distortion of symmetric
            distribution. It measures the deviation of the given distribution
            of a random variable from a symmetric distribution, such as normal
            distribution. A normal distribution is without any skewness, as it is
            symmetrical on both sides. Hence, a curve is regarded as skewed if
            it is shifted towards the right or the left.
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
            df_ta = ta.skew(
                close=df_stock["Adj Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.skew(
                close=df_stock["Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.set_title(f"{s_ticker} Skewness Indicator")
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "fuchsia", lw=1)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "fuchsia", lw=1)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax2 = axes[1]
        ax2.plot(df_ta.index, df_ta.values, "b", lw=2, label="skew")

        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.minorticks_on()
        ax2.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.legend()
        plt.show()

        print("")

    except Exception as e:
        print(e, "\n")
