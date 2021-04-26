"""Helper functions for backtesting"""
__docformat__ = "numpy"


from datetime import datetime
from typing import Union
import matplotlib
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
import bt
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI, backend
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()

if backend is not None:
    print(f"Setting matplotlib backend to {backend}")
    matplotlib.use(backend)

if matplotlib.get_backend() in ["Agg", "MacOSX"]:
    print(
        "You may encounter errors due to your MatplotLib backend. "
        " Please configure in config_plot.py."
    )


def buy_and_hold(ticker: str, start: Union[str, datetime], name: str):
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
    prices = bt.get(ticker, start=start)
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
    matplotlib.use("TkAgg")
    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    res.plot(title=plot_title, ax=ax)
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

    if gtff.USE_ION:
        plt.ion()
    plt.show()
