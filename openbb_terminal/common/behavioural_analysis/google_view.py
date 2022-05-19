"""Google View."""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List
import pandas as pd

import matplotlib.pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.common.behavioural_analysis import google_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_mentions(
    ticker: str,
    start: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]

    Parameters
    ----------
    ticker : str
        Ticker
    start : str
        Start date as YYYY-MM-DD string
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_interest = google_model.get_mentions(ticker)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.set_title(f"Interest over time on {ticker}")
    if start:
        df_interest = df_interest[start:]  # type: ignore
        ax.bar(df_interest.index, df_interest[ticker], width=2)
        ax.bar(
            df_interest.index[-1],
            df_interest[ticker].values[-1],
            width=theme.volume_bar_width,
        )
    else:
        ax.bar(df_interest.index, df_interest[ticker], width=1)
        ax.bar(
            df_interest.index[-1],
            df_interest[ticker].values[-1],
            width=theme.volume_bar_width,
        )
    ax.set_ylabel("Interest [%]")
    ax.set_xlim(df_interest.index[0], df_interest.index[-1])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "mentions", df_interest
    )


@log_start_end(log=logger)
def display_correlation_interest(
    ticker: str,
    df_data: pd.DataFrame,
    words: List[str],
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot interest over time of words/sentences versus stock price. [Source: Google]

    Parameters
    ----------
    ticker : str
        Ticker to check price
    df_data : pd.DataFrame
        Data dataframe
    words : List[str]
        Words to check for interest for
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
        f"{ticker.upper()} stock price and interest over time on {','.join(words)}"
    )
    ax[0].plot(
        df_data.index,
        df_data["Adj Close"].values,
        c="#FCED00",
    )
    ax[0].set_ylabel("Stock Price")
    ax[0].set_xlim(df_data.index[0], df_data.index[-1])

    colors = theme.get_colors()[1:]
    for idx, word in enumerate(words):
        df_interest = google_model.get_mentions(word)
        ax[1].plot(df_interest.index, df_interest[word], "-", color=colors[idx])

    ax[1].set_ylabel("Interest [%]")
    ax[1].set_xlim(df_data.index[0], df_data.index[-1])
    ax[1].legend(words)
    theme.style_primary_axis(ax[0])
    theme.style_primary_axis(ax[1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "interest", df_interest
    )


@log_start_end(log=logger)
def display_regions(
    ticker: str,
    num: int = 5,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot bars of regions based on stock's interest. [Source: Google]

    Parameters
    ----------
    ticker : str
        Ticker
    num: int
        Number of regions to show
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_interest_region = google_model.get_regions(ticker)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    if df_interest_region.empty:
        console.print("No region data found.")
        console.print("")
        return

    df_interest_region = df_interest_region.sort_values([ticker], ascending=False).head(
        num
    )
    df = df_interest_region.sort_values([ticker], ascending=True)

    ax.set_title(f"Top's regions interest on {ticker}")
    ax.barh(
        y=df.index, width=df[ticker], color=theme.get_colors(reverse=True), zorder=3
    )
    ax.set_xlabel("Interest [%]")
    ax.set_ylabel("Region")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "regions", df)


@log_start_end(log=logger)
def display_queries(ticker: str, num: int = 5, export: str = ""):
    """Print top related queries with this stock's query. [Source: Google]

    Parameters
    ----------
    ticker : str
        Ticker
    num: int
        Number of regions to show
    export: str
        Format to export data
    """

    df_related_queries = google_model.get_queries(ticker)
    df = df_related_queries.copy()
    df_related_queries = df_related_queries[ticker]["top"].head(num)
    df_related_queries["value"] = df_related_queries["value"].apply(
        lambda x: str(x) + "%"
    )
    print_rich_table(
        df_related_queries,
        headers=list(df_related_queries.columns),
        title=f"Top {ticker}'s related queries",
    )
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "queries", df)


@log_start_end(log=logger)
def display_rise(ticker: str, num: int, export: str = ""):
    """Print top rising related queries with this stock's query. [Source: Google]

    Parameters
    ----------
    ticker : str
        Ticker
    num: int
        Number of regions to show
    export: str
        Format to export data
    """
    df_related_queries = google_model.get_rise(ticker)
    df = df_related_queries.copy()
    df_related_queries = df_related_queries.head(num)

    print_rich_table(
        df_related_queries,
        headers=list(df_related_queries.columns),
        title=f"Top rising {ticker}'s related queries",
    )
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "rise", df)
