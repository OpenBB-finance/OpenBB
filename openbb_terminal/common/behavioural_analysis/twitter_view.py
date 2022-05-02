"""Twitter view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser as dparse

import openbb_terminal.config_plot as cfg_plot
from openbb_terminal.config_terminal import theme
from openbb_terminal.common.behavioural_analysis import twitter_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale, get_closing_price
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_inference(ticker: str, num: int, export: str = ""):
    """Infer sentiment from past n tweets

    Parameters
    ----------
    ticker: str
        Stock ticker
    num: int
        Number of tweets to analyze
    export: str
        Format to export tweet dataframe
    """
    df_tweets = twitter_model.load_analyze_tweets(ticker, num)

    if df_tweets.empty:
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
    console.print(f"The summed compound sentiment of {ticker} is: {total_sent}")
    console.print(f"The average compound sentiment of {ticker} is: {mean_sent}")
    console.print(
        f"Of the last {len(df_tweets)} tweets, {100*percent_pos:.2f} % had a higher positive sentiment"
    )
    console.print(
        f"Of the last {len(df_tweets)} tweets, {100*percent_neg:.2f} % had a higher negative sentiment"
    )
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "infer", df_tweets)


@log_start_end(log=logger)
def display_sentiment(
    ticker: str,
    n_tweets: int,
    n_days_past: int,
    compare: bool,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot sentiments from ticker

    Parameters
    ----------
    ticker: str
        Stock to get sentiment for
    n_tweets: int
        Number of tweets to get per hour
    n_days_past: int
        Number of days to extract tweets for
    compare: bool
        Show corresponding change in stock price
    export: str
        Format to export tweet dataframe
    """
    # Date format string required by twitter
    dt_format = "%Y-%m-%dT%H:%M:%SZ"

    # Algorithm to extract
    dt_recent = datetime.utcnow() - timedelta(seconds=20)
    dt_old = dt_recent - timedelta(days=n_days_past)
    console.print(
        f"From {dt_recent.date()} retrieving {n_tweets*24} tweets ({n_tweets} tweets/hour)"
    )

    df_tweets = pd.DataFrame(
        columns=[
            "created_at",
            "text",
            "sentiment",
            "positive",
            "negative",
            "neutral",
        ]
    )
    while True:
        # Iterate until we haven't passed the old number of days
        if dt_recent < dt_old:
            break
        # Update past datetime
        dt_past = dt_recent - timedelta(minutes=60)

        temp = twitter_model.load_analyze_tweets(
            ticker,
            n_tweets,
            start_time=dt_past.strftime(dt_format),
            end_time=dt_recent.strftime(dt_format),
        )

        if temp.empty:
            return

        df_tweets = pd.concat([df_tweets, temp])

        if dt_past.day < dt_recent.day:
            console.print(
                f"From {dt_past.date()} retrieving {n_tweets*24} tweets ({n_tweets} tweets/hour)"
            )

        # Update recent datetime
        dt_recent = dt_past

    # Sort tweets per date
    df_tweets.sort_index(ascending=False, inplace=True)
    df_tweets["cumulative_compound"] = df_tweets["sentiment"].cumsum()
    df_tweets["prob_sen"] = 1

    # df_tweets.to_csv(r'notebooks/tweets.csv', index=False)
    df_tweets.reset_index(inplace=True)
    df_tweets["Month"] = pd.to_datetime(df_tweets["created_at"]).apply(
        lambda x: x.month
    )
    df_tweets["Day"] = pd.to_datetime(df_tweets["created_at"]).apply(lambda x: x.day)
    df_tweets["date"] = pd.to_datetime(df_tweets["created_at"])
    df_tweets = df_tweets.sort_values(by="date")
    df_tweets["cumulative_compound"] = df_tweets["sentiment"].cumsum()

    ax1, ax2, ax3 = None, None, None

    if compare:
        # This plot has 3 axis
        if external_axes is None:
            _, axes = plt.subplots(
                3, 1, sharex=False, figsize=plot_autoscale(), dpi=cfg_plot.PLOT_DPI
            )
            ax1, ax2, ax3 = axes
        else:
            if len(external_axes) != 3:
                logger.error("Expected list of three axis item.")
                console.print("[red]Expected list of three axis item./n[/red]")
                return
            (ax1, ax2, ax3) = external_axes
    else:
        # This plot has 2 axis
        if external_axes is None:
            _, axes = plt.subplots(
                2, 1, sharex=True, figsize=plot_autoscale(), dpi=cfg_plot.PLOT_DPI
            )
            ax1, ax2 = axes
        else:
            if len(external_axes) != 2:
                logger.error("Expected list of one axis item.")
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax1, ax2) = external_axes

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
        f"Twitter's {ticker} total compound sentiment over time is {round(np.sum(df_tweets['sentiment']), 2)}"
    )

    theme.style_primary_axis(ax1)

    ax2.set_ylabel("VADER Polarity Scores")
    theme.style_primary_axis(ax2)

    if compare:
        # get stock end price for each corresponding day if compare == True
        closing_price_df = get_closing_price(ticker, n_days_past)
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
        export, os.path.dirname(os.path.abspath(__file__)), "sentiment", df_tweets
    )
