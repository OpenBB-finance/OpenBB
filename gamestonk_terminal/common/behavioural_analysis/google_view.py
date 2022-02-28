"""Google View."""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import matplotlib.pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.common.behavioural_analysis import google_model
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

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
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

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
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

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
