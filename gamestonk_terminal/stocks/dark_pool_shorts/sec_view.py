""" SEC View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional
from datetime import datetime, timedelta

import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    print_rich_table,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
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
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None

    """
    ftds_data = sec_model.get_fails_to_deliver(ticker, start, end, num)

    # This plot has 2 axis
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax2 = ax1.twinx()
    else:
        if len(external_axes) != 2:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax1, ax2) = external_axes

    ax1.bar(
        ftds_data["SETTLEMENT DATE"],
        ftds_data["QUANTITY (FAILS)"] / 1000,
        label="Fail Quantity",
    )
    ax1.set_ylabel("Shares [K]")
    ax1.set_title(f"Fails-to-deliver Data for {ticker}")
    ax1.legend(loc="upper left")

    if num > 0:
        stock_ftd = stock[stock.index > (datetime.now() - timedelta(days=num + 31))]
    else:
        stock_ftd = stock[stock.index > start]
        stock_ftd = stock_ftd[stock_ftd.index < end]

    ax2.plot(
        stock_ftd.index, stock_ftd["Adj Close"], color="orange", label="Share Price"
    )
    ax2.set_ylabel("Share Price [$]")
    ax2.legend(loc="upper right")

    theme.style_twin_axes(ax1, ax2)

    if not external_axes:
        theme.visualize_output()

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
