"""Alpaca View"""
__docformat__ = "numpy"

import os
import matplotlib.pyplot as plt
from tabulate import tabulate
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data

from gamestonk_terminal.portfolio.brokers.alpaca import alpaca_model


def view_holdings(export: str = ""):
    """Display holdings on Alpaca

    Parameters
    ----------
    export : str, optional
        Format to export
    """
    holdings = alpaca_model.get_holdings()

    if gtff.USE_TABULATE_DF:
        print(tabulate(holdings, headers=holdings.columns, tablefmt="fancy_grid"), "\n")
    else:
        print(holdings.to_string(), "\n")

    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "alpaca_hold",
        holdings,
    )


def view_history(period: str = "1M", timeframe: str = "1D", export: str = ""):
    """Display historical account value

    Parameters
    ----------
    period : str, optional
        Lookback period, by default "1M"
    timeframe : str, optional
        Resolution to look at, by default "1D"
    export : str, optional
        Format to export data
    """
    history = alpaca_model.get_account_history(period, timeframe)
    fig, ax = plt.subplots()
    ax.plot(history.index, history.equity)
    ax.set_xlim(history.index[0], history.index[-1])
    ax.set_ylabel("Equity")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    if gtff.USE_ION:
        plt.ion()
    plt.gcf().autofmt_xdate()
    fig.tight_layout()

    plt.show()
    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "alpaca_history",
        history,
    )
    print("")
