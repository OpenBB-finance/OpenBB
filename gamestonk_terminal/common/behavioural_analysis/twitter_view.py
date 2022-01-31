"""Twitter view"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser as dparse

import gamestonk_terminal.config_plot as cfg_plot
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.behavioural_analysis import twitter_model
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

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
def display_sentiment(ticker: str, n_tweets: int, n_days_past: int, export: str = ""):
    """Plot sentiments from ticker

    Parameters
    ----------
    ticker: str
        Stock to get sentiment for
    n_tweets: int
        Number of tweets to get per hour
    n_days_past: int
        Number of days to extract tweets for
    export: str
        Format to export tweet dataframe
    """
    # Date format string required by twitter
    dtformat = "%Y-%m-%dT%H:%M:%SZ"

    # Algorithm to extract
    dt_recent = datetime.now() - timedelta(seconds=20)
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
            start_time=dt_past.strftime(dtformat),
            end_time=dt_recent.strftime(dtformat),
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
    _, ax = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=cfg_plot.PLOT_DPI)
    ax[0].plot(
        pd.to_datetime(df_tweets["created_at"]),
        df_tweets["cumulative_compound"].values,
        lw=3,
        c="cyan",
    )
    ax[0].set_ylabel("Cumulative VADER Sentiment")
    xlocations = []
    xlabels = []
    for _, day_df in df_tweets.groupby(by="Day"):
        day_df["time"] = pd.to_datetime(day_df["created_at"])
        day_df = day_df.sort_values(by="time")
        ax[0].plot(day_df["time"], day_df["sentiment"].cumsum(), c="tab:blue")
        xlocations.append(day_df.time.values[0])
        xlabels.append(day_df["time"].apply(lambda x: x.strftime("%m-%d")).values[0])

        ax[1].bar(df_tweets["date"], df_tweets["positive"], color="green", width=0.02)
    ax[1].bar(df_tweets["date"], -1 * df_tweets["negative"], color="red", width=0.02)
    ax[0].grid(b=True, which="major", color="#666666", linestyle="-", lw=1.5, alpha=0.5)
    ax[0].minorticks_on()
    ax[0].grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax[0].set_xticks(xlocations)
    ax[0].set_xticklabels(xlabels)

    ax[1].grid(b=True, which="major", color="#666666", linestyle="-", lw=1.5, alpha=0.5)
    ax[1].minorticks_on()
    ax[1].grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax[1].set_ylabel("VADER Polarity Scores")
    ax[1].set_xticks(xlocations)
    ax[1].set_xticklabels(xlabels)
    plt.suptitle(
        f"Twitter's {ticker} total compound sentiment over time is {round(np.sum(df_tweets['sentiment']), 2)}"
    )
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "sentiment", df_tweets
    )
