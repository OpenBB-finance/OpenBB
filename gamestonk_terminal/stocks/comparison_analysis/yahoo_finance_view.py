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
}


def display_historical(
    ticker: str,
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    candle_type: str = "a",
    normalize: bool = True,
    export: str = "",
):
    """Display historical stock prices

    Parameters
    ----------
    ticker : str
        Base ticker
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
    ordered_tickers = [ticker, *similar_tickers]
    df_similar = yahoo_finance_model.get_historical(
        ticker, similar_tickers, start, candle_type
    )
    # To plot with ticker first
    df_similar = df_similar[ordered_tickers]

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
    ax.set_title(f"Similar companies to {ticker}")
    ax.plot(df_similar.index, df_similar[ticker].values)
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


def display_correlation(
    ticker: str,
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    candle_type: str = "a",
):
    """
    Correlation heatmap based on historical price comparison
    between similar companies. [Source: Yahoo Finance]

    Parameters
    ----------
    ticker : str
        Base ticker
    similar_tickers : List[str]
        List of similar tickers
    start : str, optional
        Start date of comparison, by default 1 year ago
    candle_type : str, optional
        OHLCA column to use, by default "a" for Adjusted Close
    """
    ordered_tickers = [ticker, *similar_tickers]
    df_similar = yahoo_finance_model.get_historical(
        ticker, similar_tickers, start, candle_type
    )
    # To plot with ticker first
    df_similar = df_similar[ordered_tickers]

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
    plt.title("Correlation Heatmap")
    plt.show()
    print("")
