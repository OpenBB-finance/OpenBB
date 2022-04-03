"""FinBrain View Module"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.common.behavioural_analysis import finbrain_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal import rich_config


logger = logging.getLogger(__name__)


def lambda_sentiment_coloring(val: float, last_val: float) -> str:
    if float(val) > last_val:
        return f"[green]{val}[/green]"
    return f"[red]{val}[/red]"


@log_start_end(log=logger)
def plot_sentiment(
    sentiment: pd.DataFrame, ticker: str, external_axes: Optional[List[plt.Axes]] = None
) -> None:
    """Plot Sentiment analysis provided by FinBrain's API

    Parameters
    ----------
    sentiment : pd.DataFrame
        Dataframe with sentiment data to plot
    ticker : str
        Ticker to get the sentiment analysis from
    """
    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    for index, row in sentiment.iterrows():
        if float(row["Sentiment Analysis"]) >= 0:
            ax.scatter(
                index, float(row["Sentiment Analysis"]), s=100, color=theme.up_color
            )
        else:
            ax.scatter(
                index, float(row["Sentiment Analysis"]), s=100, color=theme.down_color
            )
    ax.axhline(y=0, linestyle="--")
    ax.set_xlabel("Time")
    ax.set_ylabel("Sentiment")
    start_date = sentiment.index[-1].strftime("%Y/%m/%d")
    ax.set_title(
        f"FinBrain's Sentiment Analysis for {ticker.upper()} since {start_date}"
    )
    ax.set_ylim([-1.1, 1.1])
    senValues = np.array(pd.to_numeric(sentiment["Sentiment Analysis"].values))
    senNone = np.array(0 * len(sentiment))
    ax.fill_between(
        sentiment.index,
        pd.to_numeric(sentiment["Sentiment Analysis"].values),
        0,
        where=(senValues < senNone),
        alpha=0.30,
        color=theme.down_color,
        interpolate=True,
    )
    ax.fill_between(
        sentiment.index,
        pd.to_numeric(sentiment["Sentiment Analysis"].values),
        0,
        where=(senValues >= senNone),
        alpha=0.30,
        color=theme.up_color,
        interpolate=True,
    )
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_sentiment_analysis(
    ticker: str, export: str = "", external_axes: Optional[List[plt.Axes]] = None
):
    """Sentiment analysis from FinBrain

    Parameters
    ----------
    ticker : str
        Ticker to get the sentiment analysis from
    export : str
        Format to export data
    """
    df_sentiment = finbrain_model.get_sentiment(ticker)
    if df_sentiment.empty:
        console.print("No sentiment data found.\n")
        return

    plot_sentiment(sentiment=df_sentiment, ticker=ticker, external_axes=external_axes)

    df_sentiment.sort_index(ascending=True, inplace=True)

    if rich_config.USE_COLOR:
        color_df = df_sentiment["Sentiment Analysis"].apply(
            lambda_sentiment_coloring, last_val=0
        )
        color_df = pd.DataFrame(
            data=color_df.values,
            index=pd.to_datetime(df_sentiment.index).strftime("%Y-%m-%d"),
        )
        print_rich_table(
            color_df,
            headers=["Sentiment"],
            title="FinBrain Ticker Sentiment",
            show_index=True,
        )
    else:
        print_rich_table(
            pd.DataFrame(
                data=df_sentiment.values,
                index=pd.to_datetime(df_sentiment.index).strftime("%Y-%m-%d"),
            ),
            headers=["Sentiment"],
            title="FinBrain Ticker Sentiment",
            show_index=True,
        )

    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "headlines", df_sentiment
    )
