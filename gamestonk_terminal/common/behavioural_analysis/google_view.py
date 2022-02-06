"""Google View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime

import matplotlib.pyplot as plt

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff
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
def display_mentions(ticker: str, start: datetime, export: str = ""):
    """Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]

    Parameters
    ----------
    ticker : str
        Ticker
    start : datetime
        Start date
    export: str
        Format to export data
    """
    df_interest = google_model.get_mentions(ticker)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    ax.set_title(f"Interest over time on {ticker}")
    if start:
        df_interest = df_interest[start:]  # type: ignore
        ax.bar(df_interest.index, df_interest[ticker], width=2)
        ax.bar(
            df_interest.index[-1],
            df_interest[ticker].values[-1],
            color="tab:orange",
            width=2,
        )
    else:
        ax.bar(df_interest.index, df_interest[ticker], width=1)
        ax.bar(
            df_interest.index[-1],
            df_interest[ticker].values[-1],
            color="tab:orange",
            width=1,
        )

    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.set_ylabel("Interest [%]")
    ax.set_xlabel("Time")

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout()
    plt.show()
    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "mentions", df_interest
    )


@log_start_end(log=logger)
def display_regions(ticker: str, num: int = 5, export: str = ""):
    """Plot bars of regions based on stock's interest. [Source: Google]

    Parameters
    ----------
    ticker : str
        Ticker
    num: int
        Number of regions to show
    export: str
        Format to export data
    """
    df_interest_region = google_model.get_regions(ticker)
    if not df_interest_region.empty:
        df_interest_region = df_interest_region.sort_values(
            [ticker], ascending=False
        ).head(num)
        df = df_interest_region.copy()
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
        ax.set_title(f"Top's regions interest on {ticker}")
        ax.bar(df_interest_region.index, df_interest_region[ticker], width=0.8)
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.set_ylabel("Interest [%]")
        ax.set_xlabel("Region")
        if gtff.USE_ION:
            plt.ion()
        fig.tight_layout()
        plt.show()
    else:
        console.print("No region data found.")
    console.print("")
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
