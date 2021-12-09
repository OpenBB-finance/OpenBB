""" Comparison Analysis Yahoo Finance View """
__docformat__ = "numpy"

import os
from datetime import datetime, timedelta
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
from sklearn.preprocessing import MinMaxScaler

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.stocks.comparison_analysis import yahoo_finance_model


register_matplotlib_converters()

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
    "v": "Volume",
}


def display_historical(
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    candle_type: str = "a",
    normalize: bool = True,
    export: str = "",
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
    """
    df_similar = yahoo_finance_model.get_historical(similar_tickers, start, candle_type)
    df_similar = df_similar[similar_tickers]

    if np.any(df_similar.isna()):
        nan_tickers = df_similar.columns[df_similar.isna().sum() >= 1].to_list()
        print(f"NaN values found in: {', '.join(nan_tickers)}.  Replacing with zeros.")
        df_similar = df_similar.fillna(0)
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    # This puts everything on 0-1 scale for visualizing
    if normalize:
        mm_scale = MinMaxScaler()
        df_similar = pd.DataFrame(
            mm_scale.fit_transform(df_similar),
            columns=df_similar.columns,
            index=df_similar.index,
        )
    df_similar.plot(ax=ax)
    ax.set_title("Historical price of similar companies")
    ax.set_xlabel("Time")
    ax.set_ylabel(f"{['','Normalized'][normalize]} Share Price {['($)',''][normalize]}")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    # ensures that the historical data starts from same datapoint
    ax.set_xlim([df_similar.index[0], df_similar.index[-1]])
    plt.gcf().autofmt_xdate()
    fig.tight_layout()
    plt.show()
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "historical", df_similar
    )
    print("")


def display_volume(
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    export: str = "",
):
    """Display volume stock prices. [Source: Yahoo Finance]

    Parameters
    ----------
    similar_tickers : List[str]
        List of similar tickers
    start : str, optional
        Start date of comparison, by default 1 year ago
    normalize : bool, optional
        Boolean to normalize all stock prices using MinMax defaults True
    export : str, optional
        Format to export historical prices, by default ""
    """
    df_similar = yahoo_finance_model.get_historical(similar_tickers, start, "v")
    df_similar = df_similar[similar_tickers]

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    df_similar = df_similar.div(1_000_000)

    df_similar.plot(ax=ax)
    ax.set_title("Historical volume of similar companies")
    # ax.plot(df_similar.index, df_similar[ticker].values/1_000_000)
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume [M]")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    # ensures that the historical data starts from same datapoint
    ax.set_xlim([df_similar.index[0], df_similar.index[-1]])
    plt.gcf().autofmt_xdate()
    fig.tight_layout()
    plt.show()
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "volume", df_similar
    )
    print("")


def display_correlation(
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    candle_type: str = "a",
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
    """
    df_similar = yahoo_finance_model.get_historical(similar_tickers, start, candle_type)
    df_similar = df_similar[similar_tickers]

    if np.any(df_similar.isna()):
        nan_tickers = df_similar.columns[df_similar.isna().sum() >= 1].to_list()
        print(f"NaN values found in: {', '.join(nan_tickers)}.  Backfilling data")
        df_similar = df_similar.fillna(method="bfill")
    mask = np.zeros((df_similar.shape[1], df_similar.shape[1]), dtype=bool)
    mask[np.triu_indices(len(mask))] = True

    sns.heatmap(
        df_similar.corr(),
        cbar_kws={"ticks": [-1.0, -0.5, 0.0, 0.5, 1.0]},
        cmap="RdYlGn",
        linewidths=1,
        annot=True,
        vmin=-1,
        vmax=1,
        mask=mask,
    )
    plt.title("Correlation Heatmap of similar companies")
    plt.show()
    print("")
