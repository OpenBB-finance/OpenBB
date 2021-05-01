"""Binance view functions"""
__docformat__ = "numpy"

import numpy as np
import matplotlib.pyplot as plt
from gamestonk_terminal.main_helper import plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.feature_flags import USE_ION as ion


def plot_order_book(bids: np.array, asks: np.array, coin: str):
    """
    Plots Bid/Ask
    Parameters
    ----------
    bids : np.array
        array of bids with columns: price, size, cumulative size
    asks : np.array
        array of asks with columns: price, size, cumulative size
    coin : str
        Coin being plotted

    Returns
    -------

    """

    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(bids[:, 0], bids[:, 2], "g", label="bids")
    ax.fill_between(bids[:, 0], bids[:, 2], color="g", alpha=0.4)
    ax.plot(asks[:, 0], asks[:, 2], "r", label="asks")
    ax.fill_between(asks[:, 0], asks[:, 2], color="r", alpha=0.4)
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    plt.legend(loc=0)
    plt.xlabel("Price")
    plt.ylabel("Size (Coins) ")
    plt.title(f"Order Book for {coin}")
    # if ion:
    #    plt.ion()
    plt.show()
    print("")
