"""bt view module"""
__docformat__ = "numpy"

from typing import Union
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import bt

from gamestonk_terminal.stocks.backtesting import bt_model
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()

np.seterr(divide="ignore")


def plot_bt(res: bt.backtest.Result, plot_title: str):
    """
    Plot the bt result
    Parameters
    ----------
    res: bt.backtest.Result
        Result after a bt backtest is run
    plot_title: str
        Title of plot

    """
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    res.plot(title=plot_title, ax=ax)
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()


def display_simple_ema(
    ticker: str,
    start_date: Union[str, datetime],
    ema_length: int,
    spy_bt: bool = True,
    no_bench: bool = False,
):
    """Strategy where stock is bought when Price > EMA(l)

    Parameters
    ----------
    ticker : str
        Stock to test
    start : Union[str, datetime]
        Backtest start date.  Can be either string or datetime
    other_args : List[str]
        List of argparse arguments
    """
    res = bt_model.ema_strategy(ticker, start_date, ema_length, spy_bt, no_bench)
    plot_bt(res, f"Equity for EMA({ema_length})")
    print(res.display(), "\n")


def display_ema_cross(
    ticker: str,
    start_date: Union[str, datetime],
    short_ema: int,
    long_ema: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
):
    """Strategy where we go long/short when EMA(short) is greater than/less than EMA(short)

    Parameters
    ----------
    ticker : str
        Stock ticker
    start_date : Union[str, datetime]
        Start date of backtest
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
    """
    res = bt_model.ema_cross_strategy(
        ticker, start_date, short_ema, long_ema, spy_bt, no_bench, shortable
    )
    plot_bt(res, f"EMA Cross for EMA({short_ema})/EMA({long_ema})")
    print(res.display(), "\n")


def display_rsi_strat(
    ticker: str,
    start_date: Union[str, datetime],
    periods: int,
    low_rsi: int,
    high_rsi: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
):
    """Strategy that buys when the stock is less than a threshold and shorts when it exceeds a threshold.

    Parameters
    ----------
    ticker : str
        Stock ticker
    start_date : Union[str, datetime]
        Start date of backtest
    periods : int
        Number of periods for RSI calculati
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
    """
    res = bt_model.rsi_strategy(
        ticker, start_date, periods, low_rsi, high_rsi, spy_bt, no_bench, shortable
    )
    plot_bt(res, f"RSI Strategy between ({low_rsi}, {high_rsi})")
    print(res.display(), "\n")
