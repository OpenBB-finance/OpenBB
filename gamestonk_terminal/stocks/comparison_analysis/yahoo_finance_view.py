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

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.comparison_analysis import yahoo_finance_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
    "v": "Volume",
}


@log_start_end(log=logger)
def display_historical(
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    candle_type: str = "a",
    normalize: bool = True,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical stock prices. [Source: Yahoo Finance]

    Parameters
    ----------
    similar_tickers : List[str]
        List of similar tickers
    start : str, optional
        Start date of comparison, by default 1 year ago
    candle_type : str, optional
        OHLCA column to use, by default "a" for Adjusted Close
    normalize : bool, optional
        Boolean to normalize all stock prices using MinMax defaults True
    export : str, optional
        Format to export historical prices, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    df_similar = yahoo_finance_model.get_historical(similar_tickers, start, candle_type)
    df_similar = df_similar[similar_tickers]

    if np.any(df_similar.isna()):
        nan_tickers = df_similar.columns[df_similar.isna().sum() >= 1].to_list()
        console.print(
            f"NaN values found in: {', '.join(nan_tickers)}.  Replacing with zeros."
        )
        df_similar = df_similar.fillna(0)

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
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    # breakpoint()
    companies_names = df_similar.columns.to_list()
    ax.plot(df_similar, label=companies_names)
    ax.set_title("Historical price of similar companies")
    ax.set_ylabel(f"{['','Normalized'][normalize]} Share Price {['($)',''][normalize]}")
    # ensures that the historical data starts from same datapoint
    ax.set_xlim([df_similar.index[0], df_similar.index[-1]])
    ax.legend(loc="best")
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "historical", df_similar
    )
    console.print("")


@log_start_end(log=logger)
def display_volume(
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display volume stock prices. [Source: Yahoo Finance]

    Parameters
    ----------
    similar_tickers : List[str]
        List of similar tickers
    start : str, optional
        Start date of comparison, by default 1 year ago
    export : str, optional
        Format to export historical prices, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_similar = yahoo_finance_model.get_historical(similar_tickers, start, "v")
    df_similar = df_similar[similar_tickers]

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

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
    console.print("")


@log_start_end(log=logger)
def display_correlation(
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    candle_type: str = "a",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """
    Correlation heatmap based on historical price comparison
    between similar companies. [Source: Yahoo Finance]

    Parameters
    ----------
    similar_tickers : List[str]
        List of similar tickers
    start : str, optional
        Start date of comparison, by default 1 year ago
    candle_type : str, optional
        OHLCA column to use, by default "a" for Adjusted Close
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    df_similar = yahoo_finance_model.get_historical(similar_tickers, start, candle_type)
    df_similar = df_similar[similar_tickers]

    if np.any(df_similar.isna()):
        nan_tickers = df_similar.columns[df_similar.isna().sum() >= 1].to_list()
        console.print(
            f"NaN values found in: {', '.join(nan_tickers)}.  Backfilling data"
        )
        df_similar = df_similar.fillna(method="bfill")

    df_similar = df_similar.dropna(axis=1, how="all")

    mask = np.zeros((df_similar.shape[1], df_similar.shape[1]), dtype=bool)
    mask[np.triu_indices(len(mask))] = True

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    sns.heatmap(
        df_similar.corr(),
        cbar_kws={"ticks": [-1.0, -0.5, 0.0, 0.5, 1.0]},
        cmap="RdYlGn",
        linewidths=1,
        annot=True,
        vmin=-1,
        vmax=1,
        mask=mask,
        ax=ax,
    )
    ax.set_title(f"Correlation Heatmap of similar companies from {start}")

    if not external_axes:
        theme.visualize_output()

    console.print("")
