"""Google View."""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.common.behavioural_analysis import google_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_mentions(
    symbol: str,
    start_date: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots weekly bars of stock's interest over time. other users watchlist. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol
    start_date : str
        Start date as YYYY-MM-DD string
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_interest = google_model.get_mentions(symbol)

    if df_interest.empty:
        return

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.set_title(f"Interest over time on {symbol}")
    if start_date:
        df_interest = df_interest[start_date:]  # type: ignore
        ax.bar(df_interest.index, df_interest[symbol], width=2)
        ax.bar(
            df_interest.index[-1],
            df_interest[symbol].values[-1],
            width=theme.volume_bar_width,
        )
    else:
        ax.bar(df_interest.index, df_interest[symbol], width=1)
        ax.bar(
            df_interest.index[-1],
            df_interest[symbol].values[-1],
            width=theme.volume_bar_width,
        )
    ax.set_ylabel("Interest [%]")
    ax.set_xlim(df_interest.index[0], df_interest.index[-1])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mentions",
        df_interest,
        sheet_name,
    )


@log_start_end(log=logger)
def display_correlation_interest(
    symbol: str,
    data: pd.DataFrame,
    words: List[str],
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots interest over time of words/sentences versus stock price. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol to check price
    data : pd.DataFrame
        Data dataframe
    words : List[str]
        Words to check for interest for
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
            nrows=2,
            ncols=1,
            sharex=True,
            gridspec_kw={"height_ratios": [1, 2]},
        )
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return
    ax[0].set_title(
        f"{symbol.upper()} stock price and interest over time on {','.join(words)}"
    )
    ax[0].plot(
        data.index,
        data["Adj Close"].values,
        c="#FCED00",
    )
    ax[0].set_ylabel("Stock Price")
    ax[0].set_xlim(data.index[0], data.index[-1])

    colors = theme.get_colors()[1:]
    for idx, word in enumerate(words):
        df_interest = google_model.get_mentions(word)
        if df_interest.empty:
            continue
        ax[1].plot(df_interest.index, df_interest[word], "-", color=colors[idx])

    ax[1].set_ylabel("Interest [%]")
    ax[1].set_xlim(data.index[0], data.index[-1])
    ax[1].legend(words)
    theme.style_primary_axis(ax[0])
    theme.style_primary_axis(ax[1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "interest",
        df_interest,
        sheet_name,
    )


@log_start_end(log=logger)
def display_regions(
    symbol: str,
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots bars of regions based on stock's interest. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol
    limit: int
        Number of regions to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_interest_region = google_model.get_regions(symbol)

    if df_interest_region.empty:
        return

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    df_interest_region = df_interest_region.head(limit)
    df = df_interest_region.sort_values([symbol], ascending=True)

    ax.set_title(f"Regions with highest interest in {symbol}")
    ax.barh(
        y=df.index, width=df[symbol], color=theme.get_colors(reverse=True), zorder=3
    )
    ax.set_xlabel("Interest [%]")
    ax.set_ylabel("Region")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "regions",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_queries(
    symbol: str, limit: int = 5, export: str = "", sheet_name: Optional[str] = None
):
    """Prints table showing top related queries with this stock's query. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol
    limit: int
        Number of regions to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
        {"csv","json","xlsx","png","jpg","pdf","svg"}
    """
    # Retrieve a dict with top and rising queries
    df = google_model.get_queries(symbol, limit)

    if df.empty:
        return

    print_rich_table(
        df,
        headers=list(df.columns),
        title=f"Top {symbol}'s related queries",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "queries",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_rise(
    symbol: str, limit: int = 10, export: str = "", sheet_name: Optional[str] = None
):
    """Prints top rising related queries with this stock's query. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol
    limit: int
        Number of queries to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_related_queries = google_model.get_rise(symbol, limit)

    if df_related_queries.empty:
        return

    print_rich_table(
        df_related_queries,
        headers=list(df_related_queries.columns),
        title=f"Top rising {symbol}'s related queries",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rise",
        df_related_queries,
        sheet_name,
    )
