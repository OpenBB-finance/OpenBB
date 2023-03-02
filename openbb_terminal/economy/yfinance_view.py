""" EconDB View """
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,unused-argument

import logging
import os
from typing import Optional, Tuple, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy.yfinance_model import (
    INDICES,
    get_indices,
    get_search_indices,
)
from openbb_terminal.helper_funcs import export_data, print_rich_table, reindex_dates

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def show_indices(
    indices: list,
    interval: str = "1d",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    column: str = "Adj Close",
    returns: bool = False,
    raw: bool = False,
    external_axes: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, OpenBBFigure]]:
    """Load (and show) the selected indices over time [Source: Yahoo Finance]
    Parameters
    ----------
    indices: list
        A list of indices you wish to load (and plot).
        Available indices can be accessed through economy.available_indices().
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
    raw : bool
        Whether to display the raw output.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    Returns
    -------
    Plots the Series.
    """

    indices_data = get_indices(indices, interval, start_date, end_date, column, returns)

    fig = OpenBBFigure(title="Indices", yaxis=dict(side="right"))

    for index in indices:
        label = INDICES[index.lower()]["name"] if index.lower() in INDICES else index

        if not indices_data[index].empty:
            if returns:
                indices_data.index.name = "date"
                data_to_percent = 100 * (indices_data[index].values - 1)
                plot_data = reindex_dates(indices_data)
                fig.add_scatter(
                    x=plot_data["date"].to_list(),
                    y=data_to_percent,
                    mode="lines",
                    name=label,
                )
                fig.update_layout(
                    yaxis_title="Percentage (%)",
                    xaxis_range=[plot_data.index[0], plot_data.index[-1]],
                )
            else:
                fig.add_scatter(
                    x=indices_data.index,
                    y=indices_data[index],
                    mode="lines",
                    name=label,
                )

            fig.show(external=external_axes)

    if raw:
        print_rich_table(
            indices_data.fillna("-").iloc[-10:],
            headers=list(indices_data.columns),
            show_index=True,
            title=f"Indices [column: {column}]",
            export=bool(export),
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "index_data",
            indices_data,
            sheet_name,
            fig,
        )

    if (output := indices_data) is not None and external_axes:
        output = (indices_data, fig.show(external_axes=external_axes))

    return output


@log_start_end(log=logger)
def search_indices(query: list, limit: int = 10):
    """Load (and show) the selected indices over time [Source: Yahoo Finance]
    Parameters
    ----------
    query: list
        The keyword you wish to search for. This can include spaces.
    limit: int
        The amount of views you want to show, by default this is set to 10.
    Returns
    -------
    Shows a rich table with the available options.
    """

    keyword_adjusted, queried_indices = get_search_indices(query, limit)

    print_rich_table(
        queried_indices,
        show_index=True,
        index_name="ticker",
        headers=queried_indices.columns,
        title=f"Queried Indices with keyword {keyword_adjusted}",
    )
