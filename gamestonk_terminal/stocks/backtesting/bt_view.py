"""bt view module"""
__docformat__ = "numpy"

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.stocks.backtesting import bt_model

register_matplotlib_converters()

np.seterr(divide="ignore")


def display_simple_ema(
    ticker: str,
    df_stock: pd.DataFrame,
    ema_length: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    export: str = "",
):
    """Strategy where stock is bought when Price > EMA(l)

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.Dataframe
        Dataframe of prices
    ema_length : int
        Length of ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    export : bool
        Format to export backtest results
    """
    res = bt_model.ema_strategy(ticker, df_stock, ema_length, spy_bt, no_bench)
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    res.plot(title=f"Equity for EMA({ema_length})", ax=ax)
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.set_xlim([df_stock.index[0], df_stock.index[-1]])
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    print(res.display(), "\n")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "simple_ema", res.stats
    )


def display_ema_cross(
    ticker: str,
    df_stock: pd.DataFrame,
    short_ema: int,
    long_ema: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
    export: str = "",
):
    """Strategy where we go long/short when EMA(short) is greater than/less than EMA(short)

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.Dataframe
        Dataframe of prices
    short_ema : int
        Length of short ema window
    long_ema : int
        Length of long ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Boolean to allow for selling of the stock at cross
    export : str
        Format to export data
    """
    res = bt_model.ema_cross_strategy(
        ticker, df_stock, short_ema, long_ema, spy_bt, no_bench, shortable
    )
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    res.plot(title=f"EMA Cross for EMA({short_ema})/EMA({long_ema})", ax=ax)
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.set_xlim([df_stock.index[0], df_stock.index[-1]])
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    print(res.display(), "\n")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "ema_cross", res.stats
    )


# pylint:disable=too-many-arguments
def display_rsi_strategy(
    ticker: str,
    df_stock: pd.DataFrame,
    periods: int,
    low_rsi: int,
    high_rsi: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
    export: str = "",
):
    """Strategy that buys when the stock is less than a threshold and shorts when it exceeds a threshold.

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.Dataframe
        Dataframe of prices
    periods : int
        Number of periods for RSI calculation
    low_rsi : int
        Low RSI value to buy
    hirh_rsi : int
        High RSI value to sell
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Boolean to allow for selling of the stock at cross
    export : str
        Format to export backtest results
    """
    res = bt_model.rsi_strategy(
        ticker, df_stock, periods, low_rsi, high_rsi, spy_bt, no_bench, shortable
    )
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    res.plot(title=f"RSI Strategy between ({low_rsi}, {high_rsi})", ax=ax)
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.set_xlim([df_stock.index[0], df_stock.index[-1]])
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    print(res.display(), "\n")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "rsi_corss", res.stats
    )
