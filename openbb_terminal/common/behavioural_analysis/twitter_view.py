"""Twitter view."""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser as dparse

import openbb_terminal.config_plot as cfg_plot
from openbb_terminal.common.behavioural_analysis import twitter_model
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    get_closing_price,
    is_valid_axes_count,
    plot_autoscale,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_inference(
    symbol: str, limit: int = 100, export: str = "", sheet_name: Optional[str] = None
):
    """Prints Inference sentiment from past n tweets.

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of tweets to analyze
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export tweet dataframe
    """
    df_tweets = twitter_model.load_analyze_tweets(symbol, limit)

    if (isinstance(df_tweets, pd.DataFrame) and df_tweets.empty) or (
        not isinstance(df_tweets, pd.DataFrame) and not df_tweets
    ):
        return

    # Parse tweets
    dt_from = dparse.parse(df_tweets["created_at"].values[-1])
    dt_to = dparse.parse(df_tweets["created_at"].values[0])
    console.print(f"From: {dt_from.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"To:   {dt_to.strftime('%Y-%m-%d %H:%M:%S')}")

    console.print(f"{len(df_tweets)} tweets were analyzed.")
    dt_delta = dt_to - dt_from
    n_freq = dt_delta.total_seconds() / len(df_tweets)
    console.print(f"Frequency of approx 1 tweet every {round(n_freq)} seconds.")

    pos = df_tweets["positive"]
    neg = df_tweets["negative"]

    percent_pos = len(np.where(pos > neg)[0]) / len(df_tweets)
    percent_neg = len(np.where(pos < neg)[0]) / len(df_tweets)
    total_sent = np.round(np.sum(df_tweets["sentiment"]), 2)
    mean_sent = np.round(np.mean(df_tweets["sentiment"]), 2)
    console.print(f"The summed compound sentiment of {symbol} is: {total_sent}")
    console.print(f"The average compound sentiment of {symbol} is: {mean_sent}")
    console.print(
        f"Of the last {len(df_tweets)} tweets, {100*percent_pos:.2f} % had a higher positive sentiment"
    )
    console.print(
        f"Of the last {len(df_tweets)} tweets, {100*percent_neg:.2f} % had a higher negative sentiment"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "infer",
        df_tweets,
        sheet_name,
    )


@log_start_end(log=logger)
def display_sentiment(
    symbol: str,
    n_tweets: int = 15,
    n_days_past: int = 2,
    compare: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots sentiments from symbol

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to get sentiment for
    n_tweets: int
        Number of tweets to get per hour
    n_days_past: int
        Number of days to extract tweets for
    compare: bool
        Show corresponding change in stock price
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export tweet dataframe
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_tweets = twitter_model.get_sentiment(symbol, n_tweets, n_days_past)

    if df_tweets.empty:
        return

    ax1, ax2, ax3 = None, None, None

    if compare:
        # This plot has 3 axes
        if external_axes is None:
            _, axes = plt.subplots(
                3, 1, sharex=False, figsize=plot_autoscale(), dpi=cfg_plot.PLOT_DPI
            )
            ax1, ax2, ax3 = axes
        elif is_valid_axes_count(external_axes, 3):
            (ax1, ax2, ax3) = external_axes
        else:
            return
    else:
        # This plot has 2 axes
        if external_axes is None:
            _, axes = plt.subplots(
                2, 1, sharex=True, figsize=plot_autoscale(), dpi=cfg_plot.PLOT_DPI
            )
            ax1, ax2 = axes
        elif is_valid_axes_count(external_axes, 2):
            (ax1, ax2) = external_axes
        else:
            return

    ax1.plot(
        pd.to_datetime(df_tweets["created_at"]),
        df_tweets["cumulative_compound"].values,
    )
    ax1.set_ylabel("\nCumulative\nVADER Sentiment")
    for _, day_df in df_tweets.groupby(by="Day"):
        day_df["time"] = pd.to_datetime(day_df["created_at"])
        day_df = day_df.sort_values(by="time")
        ax1.plot(
            day_df["time"],
            day_df["sentiment"].cumsum(),
            label=pd.to_datetime(day_df["date"]).iloc[0].strftime("%Y-%m-%d"),
        )
        ax2.bar(
            df_tweets["date"],
            df_tweets["positive"],
            color=theme.up_color,
            width=theme.volume_bar_width / 100,
        )
    ax2.bar(
        df_tweets["date"],
        -1 * df_tweets["negative"],
        color=theme.down_color,
        width=theme.volume_bar_width / 100,
    )
    ax1.set_title(
        f"Twitter's {symbol} total compound sentiment over time is {round(np.sum(df_tweets['sentiment']), 2)}"
    )

    theme.style_primary_axis(ax1)

    ax2.set_ylabel("VADER Polarity Scores")
    theme.style_primary_axis(ax2)

    if compare:
        # get stock end price for each corresponding day if compare == True
        closing_price_df = get_closing_price(symbol, n_days_past)
        if ax3:
            ax3.plot(
                closing_price_df["Date"],
                closing_price_df["Close"],
                label=pd.to_datetime(closing_price_df["Date"])
                .iloc[0]
                .strftime("%Y-%m-%d"),
            )

            ax3.set_ylabel("Stock Price")
            theme.style_primary_axis(ax3)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sentiment",
        df_tweets,
        sheet_name,
    )
