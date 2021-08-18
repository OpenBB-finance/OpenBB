"""Volatility Technical Indicators View"""
__docformat__ = "numpy"

import os

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import volatility_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale

register_matplotlib_converters()


def view_bbands(
    ticker: str,
    s_interval: str,
    df_stock: pd.DataFrame,
    length: int,
    n_std: float,
    mamode: str,
    export: str,
):
    """Show bollinger bands

    Parameters
    ----------
    ticker : str
        Ticker
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    export : str
        Format of export file
    """
    df_ta = volatility_model.bbands(s_interval, df_stock, length, n_std, mamode)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    if s_interval == "1440min":
        ax.plot(df_stock.index, df_stock["Adj Close"].values, color="k", lw=3)
    else:
        ax.plot(df_stock.index, df_stock["Close"].values, color="k", lw=3)
    ax.plot(df_ta.index, df_ta.iloc[:, 0].values, "r", lw=2)
    ax.plot(df_ta.index, df_ta.iloc[:, 1].values, "b", lw=1.5, ls="--")
    ax.plot(df_ta.index, df_ta.iloc[:, 2].values, "g", lw=2)
    ax.set_title(f"{ticker} Bollinger Bands")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_xlabel("Time")
    ax.set_ylabel("Share Price ($)")

    ax.legend([ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
    ax.fill_between(
        df_ta.index,
        df_ta.iloc[:, 0].values,
        df_ta.iloc[:, 2].values,
        alpha=0.1,
        color="b",
    )
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "bbands",
        df_ta,
    )
