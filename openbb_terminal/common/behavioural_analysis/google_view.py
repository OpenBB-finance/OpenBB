"""Google View."""
__docformat__ = "numpy"

import logging
import os
from typing import List

import pandas as pd

from openbb_terminal.common.behavioural_analysis import google_model
from openbb_terminal.config_terminal import theme
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_mentions(
    symbol: str,
    start_date: str = "",
    export: str = "",
    external_axes: bool = False,
):
    """Plots weekly bars of stock's interest over time. other users watchlist. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol
    start_date : str
        Start date as YYYY-MM-DD string
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df_interest = google_model.get_mentions(symbol)

    if df_interest.empty:
        return

    fig = OpenBBFigure(
        title=f"Interest over time on {symbol}",
        xaxis_title="Date",
        yaxis_title="Interest [%]",
    )
    if start_date:
        df_interest = df_interest[start_date:]  # type: ignore

    fig.add_bar(
        x=df_interest.index[:-1],
        y=df_interest[symbol].values[:-1],
        name=symbol,
        showlegend=False,
    )
    fig.add_bar(
        x=[df_interest.index[-1]],
        y=[df_interest[symbol].values[-1]],
        name=symbol,
        showlegend=False,
    )
    fig.update_layout(xaxis=dict(type="date"))

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "mentions", df_interest
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def display_correlation_interest(
    symbol: str,
    data: pd.DataFrame,
    words: List[str],
    export: str = "",
    external_axes: bool = False,
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
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    fig = OpenBBFigure.create_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            f"{symbol.upper()} stock price and interest over time on {','.join(words)}",
            "Interest",
        ),
    )
    fig.add_scatter(
        x=data.index,
        y=data["Adj Close"].values,
        name="Stock Price",
        row=1,
        col=1,
    )
    for word in words:
        df_interest = google_model.get_mentions(word)
        fig.add_scatter(
            x=df_interest.index,
            y=df_interest[word],
            name=word,
            row=2,
            col=1,
        )
    fig.update_layout(xaxis=dict(type="date"))

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "interest", df_interest
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def display_regions(
    symbol: str, limit: int = 5, export: str = "", external_axes: bool = False
):
    """Plots bars of regions based on stock's interest. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol
    limit: int
        Number of regions to show
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_interest_region = google_model.get_regions(symbol)

    if df_interest_region.empty:
        return

    df_interest_region = df_interest_region.head(limit)
    df = df_interest_region.sort_values([symbol], ascending=True)

    fig = OpenBBFigure(
        title=f"Regions with highest interest in {symbol}",
        yaxis_title="Region",
        xaxis_title="Interest [%]",
    )
    fig.add_bar(
        x=df[symbol],
        y=df.index,
        orientation="h",
        name=symbol,
        showlegend=False,
        marker_color=theme.get_colors(reverse=True),
    )
    fig.update_layout(yaxis=dict(type="category"))

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "regions", df)

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def display_queries(symbol: str, limit: int = 5, export: str = ""):
    """Prints table showing top related queries with this stock's query. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol
    limit: int
        Number of regions to show
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
    )


@log_start_end(log=logger)
def display_rise(symbol: str, limit: int = 10, export: str = ""):
    """Prints top rising related queries with this stock's query. [Source: Google].

    Parameters
    ----------
    symbol : str
        Ticker symbol
    limit: int
        Number of queries to show
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
        export, os.path.dirname(os.path.abspath(__file__)), "rise", df_related_queries
    )
