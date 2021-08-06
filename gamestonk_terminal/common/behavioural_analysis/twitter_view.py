"""Twitter view"""
__docformat__ = "numpy"
import argparse
from typing import List, Optional
from datetime import datetime, timedelta
import requests
from dateutil import parser as dparse
import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    get_data,
    clean_tweet,
    parse_known_args_and_warn,
    plot_autoscale,
    check_int_range,
)
import gamestonk_terminal.config_plot as cfg_plot
from gamestonk_terminal import feature_flags as gtff

analyzer = SentimentIntensityAnalyzer()


def load_analyze_tweets(
    ticker: str,
    count: int,
    start_time: Optional[str] = "",
    end_time: Optional[str] = "",
) -> DataFrame:
    """
    Load tweets from twitter API and analyzes using VADER
    Parameters
    ----------
    ticker: str
        Ticker to search twitter for
    count: int
        Number of tweets to analyze
    start : Optional[str]
        If given, the start time to get tweets from
    end : Optional[str]
        If given, the end time to get tweets from

    Returns
    -------
    de_tweet: pd.DataFrame
        Dataframe of tweets and sentiment
    """
    params = {
        "query": fr"(\${ticker}) (lang:en)",
        "max_results": str(count),
        "tweet.fields": "created_at,lang",
    }

    if start_time:
        # Assign from and to datetime parameters for the API
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time

    # Request Twitter API
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/recent",
        params=params,  # type: ignore
        headers={"authorization": "Bearer " + cfg.API_TWITTER_BEARER_TOKEN},
    )

    # Create dataframe
    df_tweets = pd.DataFrame()

    # Check that the API response was successful
    if response.status_code == 200:
        for tweet in response.json()["data"]:
            row = get_data(tweet)
            df_tweets = df_tweets.append(row, ignore_index=True)
    elif response.status_code == 401:
        print("Twitter API Key provided is incorrect\n")
        return pd.DataFrame()
    elif response.status_code == 400:
        print(
            "Status Code 400.  This means you are requesting data from beyond the API's 7 day limit"
        )
        return pd.DataFrame()

    sentiments = []
    pos = []
    neg = []
    neu = []

    for s_tweet in df_tweets["text"].to_list():
        tweet = clean_tweet(s_tweet, ticker)
        sentiments.append(analyzer.polarity_scores(tweet)["compound"])
        pos.append(analyzer.polarity_scores(tweet)["pos"])
        neg.append(analyzer.polarity_scores(tweet)["neg"])
        neu.append(analyzer.polarity_scores(tweet)["neu"])
    # Add sentiments to tweets dataframe
    df_tweets["sentiment"] = sentiments
    df_tweets["positive"] = pos
    df_tweets["negative"] = neg
    df_tweets["neutral"] = neu

    return df_tweets


def inference(other_args: List[str], ticker: str):
    """Infer sentiment from past n tweets

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    ticker: str
        Stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="infer",
        description="""
            Print quick sentiment inference from last tweets that contain the ticker.
            This model splits the text into character-level tokens and uses vader sentiment analysis.
            [Source: Twitter]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_int_range(10, 100),
        default=100,
        help="num of latest tweets to infer from.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_tweets = load_analyze_tweets(ticker, ns_parser.n_num)

        if df_tweets.empty:
            return

        # Parse tweets
        dt_from = dparse.parse(df_tweets["created_at"].values[-1])
        dt_to = dparse.parse(df_tweets["created_at"].values[0])
        print(f"From: {dt_from.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"To:   {dt_to.strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"{len(df_tweets)} tweets were analyzed.")
        dt_delta = dt_to - dt_from
        n_freq = dt_delta.total_seconds() / len(df_tweets)
        print(f"Frequency of approx 1 tweet every {round(n_freq)} seconds.")

        pos = df_tweets["positive"]
        neg = df_tweets["negative"]

        percent_pos = len(np.where(pos > neg)[0]) / len(df_tweets)
        percent_neg = len(np.where(pos < neg)[0]) / len(df_tweets)
        total_sent = np.round(np.sum(df_tweets["sentiment"]), 2)
        mean_sent = np.round(np.mean(df_tweets["sentiment"]), 2)
        print(f"The summed compound sentiment of {ticker} is: {total_sent}")
        print(f"The average compound sentiment of {ticker} is: {mean_sent}")
        print(
            f"Of the last {len(df_tweets)} tweets, {100*percent_pos:.2f} % had a higher positive sentiment"
        )
        print(
            f"Of the last {len(df_tweets)} tweets, {100*percent_neg:.2f} % had a higher negative sentiment"
        )
        print("")

    except Exception as e:
        print(e, "\n")


def sentiment(other_args: List[str], ticker: str):
    """Plot sentiments from ticker

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    ticker: str
        Stock to get sentiment for
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="sen",
        description="""
            Plot in-depth sentiment predicted from tweets from last days
            that contain pre-defined ticker. [Source: Twitter]
        """,
    )
    # in reality this argument could be 100, but after testing it takes too long
    # to compute which may not be acceptable
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_tweets",
        type=check_int_range(10, 62),
        default=15,
        help="number of tweets to extract per hour.",
    )
    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days_past",
        type=check_int_range(1, 6),
        default=6,
        help="number of days in the past to extract tweets.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Date format string required by twitter
        dtformat = "%Y-%m-%dT%H:%M:%SZ"

        # Algorithm to extract
        dt_recent = datetime.now() - timedelta(seconds=20)
        dt_old = dt_recent - timedelta(days=ns_parser.n_days_past)
        print(
            f"From {dt_recent.date()} retrieving {ns_parser.n_tweets*24} tweets ({ns_parser.n_tweets} tweets/hour)"
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

            temp = load_analyze_tweets(
                ticker,
                ns_parser.n_tweets,
                start_time=dt_past.strftime(dtformat),
                end_time=dt_recent.strftime(dtformat),
            )

            if temp.empty:
                return

            df_tweets = pd.concat([df_tweets, temp])

            if dt_past.day < dt_recent.day:
                print(
                    f"From {dt_past.date()} retrieving {ns_parser.n_tweets*24} tweets ({ns_parser.n_tweets} tweets/hour)"
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
        df_tweets["Day"] = pd.to_datetime(df_tweets["created_at"]).apply(
            lambda x: x.day
        )
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
            xlabels.append(
                day_df["time"].apply(lambda x: x.strftime("%m-%d")).values[0]
            )

            ax[1].bar(
                df_tweets["date"], df_tweets["positive"], color="green", width=0.02
            )
        ax[1].bar(
            df_tweets["date"], -1 * df_tweets["negative"], color="red", width=0.02
        )
        ax[0].grid(
            b=True, which="major", color="#666666", linestyle="-", lw=1.5, alpha=0.5
        )
        ax[0].minorticks_on()
        ax[0].grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax[0].set_xticks(xlocations)
        ax[0].set_xticklabels(xlabels)

        ax[1].grid(
            b=True, which="major", color="#666666", linestyle="-", lw=1.5, alpha=0.5
        )
        ax[1].minorticks_on()
        ax[1].grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax[1].set_ylabel("VADER Polarity Scores")
        ax[1].set_xticks(xlocations)
        ax[1].set_xticklabels(xlabels)
        plt.suptitle(
            f"Twitter's {ticker} total compound sentiment over time is {np.sum(df_tweets['sentiment'])}"
        )
        if gtff.USE_ION:
            plt.ion()
        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
