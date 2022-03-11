""" EconDB View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import pandas as pd
from matplotlib import pyplot as plt
import financedatabase as fd

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy.yfinance_model import get_index, INDICES
from gamestonk_terminal.helper_funcs import (
    plot_autoscale,
    print_rich_table,
    export_data,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def show_indices(
    indices: list,
    interval: str = "1d",
    start_date: int = None,
    end_date: int = None,
    column: str = "Adj Close",
    raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
    export: str = "",
):
    """Load (and show) the selected indices over time [Source: Yahoo Finance]

    Parameters
    ----------
    indices: list
        A list of indices you wish to load (and plot).
    interval: str
        Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        Intraday data cannot extend last 60 days
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : str
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    raw : bool
        Whether to display the raw output.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file

    Returns
    ----------
    Plots the Series.
    """
    indices_data: pd.DataFrame = pd.DataFrame()

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    for index in indices:
        indices_data[index] = get_index(index, interval, start_date, end_date, column)

        if index in INDICES:
            label = INDICES[index]["name"]
        else:
            label = index

        if not indices_data[index].empty:
            ax.plot(indices_data[index], label=label)

    ax.set_title("Indices")
    ax.legend()

    if raw:
        print_rich_table(
            indices_data.fillna("-").iloc[-10:],
            headers=list(indices_data.columns),
            show_index=True,
            title=f"Indices [column: {column}]",
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "index_data",
            indices_data,
        )

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def search_indices(keyword: list, limit: int = 10):
    """Load (and show) the selected indices over time [Source: Yahoo Finance]

    Parameters
    ----------
    keyword: list
        The keyword you wish to search for. This can include spaces.
    limit: int
        The amount of views you want to show, by default this is set to 10.

    Returns
    ----------
    Shows a rich table with the available options.
    """
    keyword_adjusted = " ".join(keyword)

    indices = fd.select_indices()

    queried_indices = pd.DataFrame.from_dict(
        fd.search_products(indices, keyword_adjusted, "short_name"), orient="index"
    )

    print_rich_table(
        queried_indices.iloc[:limit],
        show_index=True,
        index_name="ticker",
        headers=queried_indices.columns,
        title=f"Queried Indices with keyword {keyword_adjusted}",
    )
