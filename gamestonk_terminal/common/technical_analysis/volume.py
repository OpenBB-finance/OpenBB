"""Volume Technical Analysis"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import timedelta

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


def ad(other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame):
    """Accumulation Dictribution Line

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock data interval
    df_stock: pd.DataFrame
        Dataframe of stock prices
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ad",
        description="""
            The Accumulation/Distribution Line is similar to the On Balance
            Volume (OBV), which sums the volume times +1/-1 based on whether the close is
            higher than the previous close. The Accumulation/Distribution indicator, however
            multiplies the volume by the close location value (CLV). The CLV is based on the
            movement of the issue within a single bar and can be +1, -1 or zero. \n \n
            The Accumulation/Distribution Line is interpreted by looking for a divergence in
            the direction of the indicator relative to price. If the Accumulation/Distribution
            Line is trending upward it indicates that the price may follow. Also, if the
            Accumulation/Distribution Line becomes flat while the price is still rising (or falling)
            then it signals an impending flattening of the price.
        """,
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
        "--open",
        action="store_true",
        default=False,
        dest="b_use_open",
        help="uses open value of stock",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        bar_colors = [
            "r" if x[1].Open < x[1].Close else "g" for x in df_stock.iterrows()
        ]

        if s_interval == "1440min":
            bar_width = timedelta(days=1)
        else:
            bar_width = timedelta(minutes=int(s_interval.split("m")[0]))

        if ns_parser.b_use_open:
            df_ta = ta.ad(
                high=df_stock["High"],
                low=df_stock["Low"],
                close=df_stock["Adj Close"],
                volume=df_stock["Volume"],
                offset=ns_parser.n_offset,
                open_=df_stock["Open"],
            ).dropna()
        # Do not use open stock values
        else:
            # Note this should always be Close not Adj Close
            df_ta = ta.ad(
                high=df_stock["High"],
                low=df_stock["Low"],
                close=df_stock["Close"],
                volume=df_stock["Volume"],
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(
            3,
            1,
            gridspec_kw={"height_ratios": [2, 1, 1]},
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax = axes[0]
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
        ax.set_title(f"{s_ticker} AD")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        ax2 = axes[1]
        ax2.set_ylabel("Volume")
        if s_interval == "1440min":
            ax2.bar(
                df_stock.index,
                df_stock["Volume"].values,
                color=bar_colors,
                alpha=0.8,
                width=0.3,
            )
        else:
            ax2.bar(
                df_stock.index,
                df_stock["Volume"].values,
                color=bar_colors,
                alpha=0.8,
                width=bar_width,
            )
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])

        ax3 = axes[2]
        ax3.plot(df_ta.index, df_ta.values, "b", lw=1)
        ax3.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax3.axhline(0, linewidth=2, color="k", ls="--")
        ax3.set_ylabel("A/D")
        ax3.set_xlabel("Time")
        ax3.grid(b=True, which="major", color="#666666", linestyle="-")
        ax3.minorticks_on()
        ax3.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


def obv(other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame):
    """On Balance Volume

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock data interval
    df_stock: pd.DataFrame
        Dataframe of stock prices
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="obv",
        description="""
            The On Balance Volume (OBV) is a cumulative total of the up and
            down volume. When the close is higher than the previous close, the volume is added
            to the running total, and when the close is lower than the previous close, the volume
            is subtracted from the running total. \n \n To interpret the OBV, look for the OBV
            to move with the price or precede price moves. If the price moves before the OBV,
            then it is a non-confirmed move. A series of rising peaks, or falling troughs, in the
            OBV indicates a strong trend. If the OBV is flat, then the market is not trending.
        """,
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

        bar_colors = [
            "r" if x[1].Open < x[1].Close else "g" for x in df_stock.iterrows()
        ]

        if s_interval == "1440min":
            bar_width = timedelta(days=1)
        else:
            bar_width = timedelta(minutes=int(s_interval.split("m")[0]))

        # Daily
        if s_interval == "1440min":
            df_ta = ta.obv(
                close=df_stock["Adj Close"],
                volume=df_stock["Volume"],
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.obv(
                close=df_stock["Close"],
                volume=df_stock["Volume"],
                offset=ns_parser.n_offset,
            ).dropna()

        fig, axes = plt.subplots(
            3,
            1,
            gridspec_kw={"height_ratios": [2, 1, 1]},
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax = axes[0]
        if s_interval == "1440min":
            ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        else:
            ax.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)

        ax.set_title(f"{s_ticker} OBV")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax2 = axes[1]
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])

        if s_interval == "1440min":
            ax2.bar(
                df_stock.index,
                df_stock["Volume"].values,
                color=bar_colors,
                alpha=0.8,
                width=bar_width,
            )
        else:
            ax2.bar(
                df_stock.index,
                df_stock["Volume"].values,
                color=bar_colors,
                alpha=0.8,
                width=bar_width,
            )
        ax3 = axes[2]
        ax3.plot(df_ta.index, df_ta.values, "b", lw=1)
        ax3.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax3.set_xlabel("Time")
        ax3.grid(b=True, which="major", color="#666666", linestyle="-")
        ax3.minorticks_on()
        ax3.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
