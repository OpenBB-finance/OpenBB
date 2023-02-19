""" Stocksera View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.ticker
import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    lambda_long_number_format,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import stocksera_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_cost_to_borrow(
    symbol: str,
    data: pd.DataFrame,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot the cost to borrow of a stock. [Source: Stocksera]

    Parameters
    ----------
    symbol : str
        ticker to get cost to borrow from
    data: pd.DataFrame
        Cost to borrow dataframe
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """

    # This plot has 2 axes
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax2 = ax1.twinx()
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    if data.empty:
        return

    ax1.bar(
        data.index,
        data["Available"],
        0.3,
        color=theme.up_color,
    )

    ax1.set_title(f"Cost to Borrow of {symbol}")

    ax1.legend(labels=["Number Shares"], loc="best")
    ax1.yaxis.set_major_formatter(matplotlib.ticker.EngFormatter())

    ax2.set_ylabel("Fees %")
    ax2.plot(data.index, data["Fees"].values)
    ax2.tick_params(axis="y", which="major")

    theme.style_twin_axes(ax1, ax2)

    ax1.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(6))

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
@check_api_key(["API_STOCKSERA_KEY"])
def cost_to_borrow(
    symbol: str,
    limit: int = 100,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]
    Parameters
    ----------
    symbol : str
        ticker to get cost to borrow from
    limit: int
        Number of historical cost to borrow data to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    # Note: if you send an empty string stocksera will search every ticker
    if not symbol:
        console.print("[red]No symbol provided[/red]\n")
        return
    df_cost_to_borrow = stocksera_model.get_cost_to_borrow(symbol)

    df_cost_to_borrow = df_cost_to_borrow.head(limit)[::-1]

    pd.options.mode.chained_assignment = None

    plot_cost_to_borrow(symbol, df_cost_to_borrow, external_axes)

    if raw:
        df_cost_to_borrow["Available"] = df_cost_to_borrow["Available"].apply(
            lambda x: lambda_long_number_format(x)
        )
        print_rich_table(
            df_cost_to_borrow,
            headers=list(df_cost_to_borrow.columns),
            show_index=True,
            title=f"Cost to Borrow of {symbol}",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stocksera",
        df_cost_to_borrow,
        sheet_name,
    )
