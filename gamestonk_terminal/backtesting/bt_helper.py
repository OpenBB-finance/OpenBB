"""Helper functions for backtesting"""
__docformat__ = "numpy"


from datetime import datetime
from typing import Union
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
import bt
import yfinance as yf
import pandas as pd
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def get_data(ticker: str, start_date: Union[str, datetime]):
    """
    Function to replace bt.get,  Gets Adjusted close of ticker
    Parameters
    ----------
    ticker: str
        Ticker to get data for
    start_date:
        Start date

    Returns
    -------
    prices: pd.DataFrame
        Dataframe of Adj Close with columns = [ticker]
    """
    prices = yf.download(ticker, start=start_date, progress=False)
    prices = pd.DataFrame(prices["Adj Close"])
    prices.columns = [ticker]
    return prices


def buy_and_hold(ticker: str, start_date: Union[str, datetime], name: str):
    """
    Generates a backtest object for the given ticker
    Parameters
    ----------
    ticker: str
        Stock to test
    start: Union[str, datetime]
        Backtest start date.  Can be either string or datetime
    name:
        Name of the backtest (for labeling purposes)

    Returns
    -------
    bt.Backtest object for buy and hold strategy
    """
    # prices = bt.get(ticker, start=start)
    prices = get_data(ticker, start_date)
    bt_strategy = bt.Strategy(
        name,
        [
            bt.algos.RunOnce(),
            bt.algos.SelectAll(),
            bt.algos.WeighEqually(),
            bt.algos.Rebalance(),
        ],
    )
    return bt.Backtest(bt_strategy, prices)


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
    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    res.plot(title=plot_title, ax=ax)
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

    if gtff.USE_ION:
        plt.ion()
    plt.show()
