""" EconDB View """
__docformat__ = "numpy"
# pylint:disable=too-many-arguments

import logging
import os
from typing import Optional, List

import pandas as pd
from matplotlib import pyplot as plt
import financedatabase as fd

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy.yfinance_model import get_index, INDICES
from openbb_terminal.helper_funcs import (
    plot_autoscale,
    print_rich_table,
    export_data,
    reindex_dates,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def show_indices(
    indices: list,
    interval: str = "1d",
    start_date: int = None,
    end_date: int = None,
    column: str = "Adj Close",
    returns: bool = False,
    store: bool = False,
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
    column : str
        Which column to load in, by default this is the Adjusted Close.
    returns: bool
        Flag to show cumulative returns on index
    store : bool
        Whether to prevent plotting the data.
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

    for index in indices:
        indices_data[index] = get_index(index, interval, start_date, end_date, column)

    if returns:
        indices_data = indices_data.pct_change().dropna()
        indices_data = indices_data + 1
        indices_data = indices_data.cumprod()

    if not store:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes[0]

        for index in indices:
            if index.lower() in INDICES:
                label = INDICES[index.lower()]["name"]
            else:
                label = index

            if not indices_data[index].empty:

                if returns:
                    indices_data.index.name = "date"
                    data_to_percent = 100 * (indices_data[index].values - 1)
                    plot_data = reindex_dates(indices_data)
                    ax.plot(plot_data.index, data_to_percent, label=label)
                else:
                    ax.plot(indices_data.index, indices_data[index], label=label)

        ax.set_title("Indices")
        if returns:
            ax.set_ylabel("Performance (%)")
        ax.legend(
            bbox_to_anchor=(0, 0.40, 1, -0.52),
            loc="upper right",
            mode="expand",
            borderaxespad=0,
            prop={"size": 9},
            ncol=2,
        )

        if returns:
            theme.style_primary_axis(
                ax,
                data_index=plot_data.index.to_list(),
                tick_labels=plot_data["date"].to_list(),
            )
            ax.set_xlim(plot_data.index[0], plot_data.index[-1])
        else:
            theme.style_primary_axis(ax)
        if external_axes is None:
            theme.visualize_output()

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

    return indices_data


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
