""" Comparison Analysis Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
from sklearn.preprocessing import MinMaxScaler

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
    print_rich_table,
)
from openbb_terminal.stocks.comparison_analysis import yahoo_finance_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
    "v": "Volume",
    "r": "Returns",
}


@log_start_end(log=logger)
def display_historical(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    candle_type: str = "a",
    normalize: bool = True,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical stock prices. [Source: Yahoo Finance]

    Parameters
    ----------
    similar: List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date: Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end_date: Optional[str], optional
        End date (e.g., 2023-01-01)
    candle_type: str, optional
        OHLCA column to use or R to use daily returns calculated from Adjusted Close, by default "a" for Adjusted Close
    normalize: bool, optional
        Boolean to normalize all stock prices using MinMax defaults True
    export: str, optional
        Format to export historical prices, by default ""
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_similar = yahoo_finance_model.get_historical(
        similar, start_date, end_date, candle_type
    )

    # This puts everything on 0-1 scale for visualizing
    if normalize:
        mm_scale = MinMaxScaler()
        df_similar = pd.DataFrame(
            mm_scale.fit_transform(df_similar),
            columns=df_similar.columns,
            index=df_similar.index,
        )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    companies_names = df_similar.columns.to_list()
    ax.plot(df_similar, label=companies_names)
    ax.set_title("Historical price of similar companies")
    ax.set_ylabel(f"{['','Normalized'][normalize]} Share Price {['($)',''][normalize]}")
    # ensures that the historical data starts from same datapoint
    ax.set_xlim([df_similar.index[0], df_similar.index[-1]])
    ax.legend()
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "historical", df_similar
    )


@log_start_end(log=logger)
def display_volume(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display stock volume. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end_date : Optional[str], optional
        End date (e.g., 2023-01-01). Defaults to today
    export : str, optional
        Format to export historical prices, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_similar = yahoo_finance_model.get_volume(similar, start_date, end_date)

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    df_similar = df_similar.div(1_000_000)
    companies_names = df_similar.columns.to_list()

    ax.plot(df_similar, label=companies_names)
    ax.set_title("Historical volume of similar companies")
    ax.set_ylabel("Volume [M]")
    # ensures that the historical data starts from same datapoint
    ax.set_xlim([df_similar.index[0], df_similar.index[-1]])

    ax.legend()
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "volume", df_similar
    )


@log_start_end(log=logger)
def display_correlation(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    candle_type: str = "a",
    display_full_matrix: bool = False,
    raw: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
    export: str = "",
):
    """
    Correlation heatmap based on historical price comparison
    between similar companies. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end_date : Optional[str], optional
        End date (e.g., 2023-01-01)
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close
    display_full_matrix : bool, optional
        Optionally display all values in the matrix, rather than masking off half, by default False
    raw: bool, optional
        Whether to display raw data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    export : str, optional
        Format to export correlation prices, by default ""
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")

    correlations, df_similar = yahoo_finance_model.get_correlation(
        similar, start_date, end_date, candle_type
    )

    mask = None
    if not display_full_matrix:
        mask = np.zeros((df_similar.shape[1], df_similar.shape[1]), dtype=bool)
        mask[np.triu_indices(len(mask))] = True

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    if raw:
        print_rich_table(
            correlations,
            headers=[x.title().upper() for x in correlations.columns],
            show_index=True,
        )

    sns.heatmap(
        correlations,
        cbar_kws={"ticks": [-1.0, -0.5, 0.0, 0.5, 1.0]},
        cmap="RdYlGn",
        linewidths=1,
        annot=True,
        annot_kws={"fontsize": 10},
        vmin=-1,
        vmax=1,
        mask=mask,
        ax=ax,
    )
    ax.set_title(f"Correlation Heatmap of similar companies from {start_date}")

    if not external_axes:
        theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "hcorr", df_similar)


@log_start_end(log=logger)
def display_sp500_comps_tsne(
    symbol: str,
    lr: int = 200,
    no_plot: bool = False,
    limit: int = 10,
    external_axes: Optional[List[plt.Axes]] = None,
) -> List[str]:
    """Runs TSNE on SP500 tickers (along with ticker if not in SP500).
    TSNE is a method of visualing higher dimensional data
    https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
    Note that the TSNE numbers are meaningless and will be arbitrary if run again.

    Parameters
    ----------
    symbol: str
        Ticker to get comparisons to
    lr: int
        Learning rate for TSNE
    no_plot: bool
        Flag to hold off on plotting
    limit: int
        Number of tickers to return
    external_axes : Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None

    Returns
    -------
    List[str]
        List of the 10 closest stocks due to TSNE
    """
    data = yahoo_finance_model.get_sp500_comps_tsne(symbol=symbol, lr=lr)

    top_n = data.iloc[1 : (limit + 1)]
    top_n_name = top_n.index.to_list()

    if not no_plot:
        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return []

        top_100 = data[(limit + 1) : 101]
        symbol_df = data[data.index == symbol]

        ax.scatter(
            top_n.X,
            top_n.Y,
            alpha=0.8,
            c=theme.up_color,
            label=f"Top {limit} closest tickers",
        )
        ax.scatter(
            top_100.X, top_100.Y, alpha=0.5, c="grey", label="Top 100 closest tickers"
        )

        for x, y, company in zip(top_n.X, top_n.Y, top_n.index):
            ax.annotate(company, (x, y), fontsize=9, alpha=0.9)

        for x, y, company in zip(top_100.X, top_100.Y, top_100.index):
            ax.annotate(company, (x, y), fontsize=9, alpha=0.75)

        ax.scatter(
            symbol_df.X,
            symbol_df.Y,
            s=50,
            c=theme.down_color,
        )
        ax.annotate(symbol, (symbol_df.X, symbol_df.Y), fontsize=9, alpha=1)
        ax.legend()

        ax.set_title(
            f"Top 100 closest stocks on S&P500 to {symbol} using TSNE algorithm",
            fontsize=11,
        )
        ax.set_xlabel("Dimension 1")
        ax.set_ylabel("Dimension 2")
        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    return top_n_name
