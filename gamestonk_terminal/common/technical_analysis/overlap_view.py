"""TA Overlap View"""
__docformat__ = "numpy"

import os
from typing import List

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from pandas.plotting import register_matplotlib_converters

import gamestonk_terminal.feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import overlap_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale

register_matplotlib_converters()


def view_ma(
    ma: str,
    s_ticker: str,
    s_interval: str,
    df_stock: pd.DataFrame,
    window_length: List[int],
    export: str,
):
    """Plots EMA technical indicator

    Parameters
    ----------
    ma: str
        Type of moving average.  Either "EMA" "ZLMA" or "SMA"
    s_ticker : str
        Ticker
    s_interval : str
        Interval of data
    df_stock : pd.DataFrame
        Dataframe of prices
    window_length : int
        Length of EMA window
    export : str
        Format to export data
    """
    if s_interval == "1440min":
        price_df = pd.DataFrame(
            df_stock["Adj Close"].values, columns=["Price"], index=df_stock.index
        )
    else:
        price_df = pd.DataFrame(
            df_stock["Close"].values, columns=["Price"], index=df_stock.index
        )

    l_legend = [s_ticker]
    for win in window_length:
        if ma == "EMA":
            df_ta = overlap_model.ema(s_interval, df_stock, win)
            price_df = price_df.join(df_ta)
            l_legend.append(f"EMA {win}")
        elif ma == "SMA":
            df_ta = overlap_model.sma(s_interval, df_stock, win)
            price_df = price_df.join(df_ta)
            l_legend.append(f"SMA {win}")
        elif ma == "ZLMA":
            df_ta = overlap_model.zlma(s_interval, df_stock, win)
            price_df = price_df.join(df_ta)
            l_legend.append(f"ZLMA {win}")

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            f"{ma}{window_length}",
            price_df,
        )
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.set_title(f"{window_length} Day {ma.upper()} on {s_ticker}")

    ax.plot(price_df.index, price_df["Price"], lw=3, c="k")

    ax.set_xlabel("Time")
    ax.set_ylabel(f"{s_ticker} Price($)")

    for idx in range(1, price_df.shape[1]):
        ax.plot(price_df.iloc[:, idx])

    ax.legend(l_legend)
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.show()
    print("")


def view_vwap(s_ticker: str, s_interval: str, df_stock: pd.DataFrame, export: str):
    """Plots EMA technical indicator

    Parameters
    ----------
    s_ticker : str
        Ticker
    s_interval : str
        Interval of data
    df_stock : pd.DataFrame
        Dataframe of prices
    export : str
        Format to export data
    """

    df_stock.index = df_stock.index.tz_localize(None)
    df_stock["Day"] = [idx.date() for idx in df_stock.index]

    day_df = df_stock[df_stock.Day == df_stock.Day[-1]]

    df_vwap = overlap_model.vwap(day_df)

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "vwap",
            df_vwap,
        )
    mc = mpf.make_marketcolors(
        up="green", down="red", edge="black", wick="black", volume="in", ohlc="i"
    )

    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=True)
    apdict = mpf.make_addplot(df_vwap, color="k")

    mpf.plot(
        day_df,
        style=s,
        type="candle",
        addplot=apdict,
        volume=True,
        title=f"\n{s_ticker} {s_interval} VWAP",
    )

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    print("")
