""" SEC View """
__docformat__ = "numpy"

import logging
import os
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.dark_pool_shorts import sec_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def fails_to_deliver(
    ticker: str,
    stock: pd.DataFrame,
    start: datetime,
    end: datetime,
    num: int,
    raw: bool,
    export: str = "",
):
    """Display fails-to-deliver data for a given ticker. [Source: SEC]

    Parameters
    ----------
    ticker : str
        Stock ticker
    stock : pd.DataFrame
        Stock data
    start : datetime
        Start of data
    end : datetime
        End of data
    num : int
        Number of latest fails-to-deliver being printed
    raw : bool
        Print raw data
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    ftds_data = sec_model.get_fails_to_deliver(ticker, start, end, num)

    plt.bar(
        ftds_data["SETTLEMENT DATE"],
        ftds_data["QUANTITY (FAILS)"] / 1000,
    )
    plt.ylabel("Shares [K]")
    plt.title(f"Fails-to-deliver Data for {ticker}")
    plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gcf().autofmt_xdate()
    plt.xlabel("Days")

    _ = plt.gca().twinx()

    if num > 0:
        stock_ftd = stock[stock.index > (datetime.now() - timedelta(days=num + 31))]
    else:
        stock_ftd = stock[stock.index > start]
        stock_ftd = stock_ftd[stock_ftd.index < end]
    plt.plot(stock_ftd.index, stock_ftd["Adj Close"], color="tab:orange")
    plt.ylabel("Share Price [$]")

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    console.print("")

    if raw:
        print_rich_table(
            ftds_data,
            headers=list(ftds_data.columns),
            show_index=False,
            title="Fails-To-Deliver Data",
        )
        console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ftd",
        ftds_data.reset_index(),
    )
