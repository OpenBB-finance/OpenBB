""" SEC View """
__docformat__ = "numpy"

import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.dark_pool_shorts import sec_model

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def fails_to_deliver(
    symbol: str,
    data: Optional[pd.DataFrame] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 0,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display fails-to-deliver data for a given ticker. [Source: SEC]

    Parameters
    ----------
    symbol: str
        Stock ticker
    data: pd.DataFrame
        Stock data
    start_date: Optional[str]
        Start of data, in YYYY-MM-DD format
    end_date: Optional[str]
        End of data, in YYYY-MM-DD format
    limit : int
        Number of latest fails-to-deliver being printed
    raw: bool
        Print raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None

    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if data is None:
        data = stocks_helper.load(
            symbol=symbol, start_date=start_date, end_date=end_date
        )

    ftds_data = sec_model.get_fails_to_deliver(symbol, start_date, end_date, limit)

    # This plot has 2 axes
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax2 = ax1.twinx()
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    ax1.bar(
        ftds_data["SETTLEMENT DATE"],
        ftds_data["QUANTITY (FAILS)"] / 1000,
        label="Fail Quantity",
    )
    ax1.set_ylabel("Shares [K]")
    ax1.set_title(f"Fails-to-deliver Data for {symbol}")
    ax1.legend(loc="lower right")

    if limit > 0:
        data_ftd = data[data.index > (datetime.now() - timedelta(days=limit + 31))]
    else:
        data_ftd = data[data.index > start_date]
        data_ftd = data_ftd[data_ftd.index < end_date]

    ax2.plot(data_ftd.index, data_ftd["Adj Close"], color="orange", label="Share Price")
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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ftd",
        ftds_data.reset_index(),
        sheet_name,
    )
