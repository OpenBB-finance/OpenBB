"""Twitter view"""
__docformat__ = "numpy"
import argparse
from typing import List, Optional
from datetime import datetime, timedelta
import requests
import dateutil
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
)

analyzer = SentimentIntensityAnalyzer()

def load_analyze_tweets(s_ticker: str, count: int, start_time:Optional[str]="", end_time:Optional[str]="") -> DataFrame:
    """
    Load tweets from twitter API and analyzes using VADER
    Parameters
    ----------
    s_ticker: str
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
        "query": f"(\${s_ticker}) (lang:en)",
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


    sentiments = []
    pos = []
    neg = []
    neu = []
    for s_tweet in df_tweets["text"].to_list():
        tweet = clean_tweet(s_tweet, s_ticker)
        """ 
        VADER stores predictions as a dict with "pos", "neu", "neg", "compound"
        The compound will be the one of interest, as it is 
        a 'normalized, weighted composite score' is accurate
        """

        sentiments.append(analyzer.polarity_scores(tweet)["compound"])
        pos.append(analyzer.polarity_scores(tweet)["pos"])
        neg.append(analyzer.polarity_scores(tweet)["neg"])
        neu.append( analyzer.polarity_scores(tweet)["neu"] )
    # Add sentiments to tweets dataframe
    df_tweets["sentiment"] = sentiments
    df_tweets["positive"] = pos
    df_tweets["negative"] = neg
    df_tweets["neutral"] = neu

    return df_tweets


def inference(other_args:List[str], s_ticker:str):
    """
    Infer sentiment from past n tweets
    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    s_ticker: str
        Stock ticker

    """
    parser = argparse.ArgumentParser(
        add_help=False,
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
        type=int,
        default=100,
        choices=range(10, 101),
        help="num of latest tweets to infer from.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_tweets = load_analyze_tweets(s_ticker, ns_parser.n_num)

        # Parse tweets
        dt_from = dateutil.parser.parse(df_tweets["created_at"].values[-1])
        dt_to = dateutil.parser.parse(df_tweets["created_at"].values[0])
        print(f"From: {dt_from.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"To:   {dt_to.strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"{len(df_tweets)} tweets were analyzed.")
        dt_delta = dt_to - dt_from
        n_freq = dt_delta.total_seconds() / len(df_tweets)
        print(f"Frequency of approx 1 tweet every {round(n_freq)} seconds.")

        pos = df_tweets["positive"]
        neg = df_tweets["negative"]

        percent_pos = len(np.where(pos>neg)[0])/len(df_tweets)
        percent_neg = len(np.where(pos < neg)[0]) / len(df_tweets)
        total_sent = np.round(np.sum(df_tweets["sentiment"]),2)
        mean_sent = np.round(np.mean(df_tweets["sentiment"]),2)
        print(f"The summed compound sentiment of {s_ticker} is: {total_sent}")
        print(f"The average compound sentiment of {s_ticker} is: {mean_sent}")
        print(f"Of the last {len(df_tweets)} tweets, {100*percent_pos:.2f} % had a higher positive sentiment")
        print(f"Of the last {len(df_tweets)} tweets, {100*percent_neg:.2f} % had a higher negative sentiment")
        print("")

    except Exception as e:
        print(e, "\n")


def sentiment(other_args:List[str], s_ticker:str):
    """
    Plot sentiments from ticker
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    s_ticker: str
        Stock to get sentiment for

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="sen",
        description="""
            Plot in-depth sentiment predicted from tweets from last days
            that contain pre-defined ticker. T[Source: Twitter]
        """,
    )

    # in reality this argument could be 100, but after testing it takes too long
    # to compute which may not be acceptable
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_tweets",
        type=int,
        default=10,
        choices=range(10, 61),
        help="num of tweets to extract per hour.",
    )
    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days_past",
        type=int,
        default=7,
        choices=range(1, 8),
        help="num of days in the past to extract tweets.",
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

        df_tweets = pd.DataFrame(columns = ["created_at", "text", "sentiment","positive","negative","neutral"])
        while True:
            # Iterate until we haven't passed the old number of days
            if dt_recent < dt_old:
                break
            # Update past datetime
            dt_past = dt_recent - timedelta(minutes=60)
            if dt_past.day < dt_recent.day:
                print(
                    f"From {dt_past.date()} retrieving {ns_parser.n_tweets*24} tweets ({ns_parser.n_tweets} tweets/hour)"
                )
            temp = load_analyze_tweets(s_ticker, ns_parser.n_tweets, start_time = dt_past.strftime(dtformat),
                                 end_time = dt_recent.strftime(dtformat) )
            df_tweets = pd.concat([df_tweets,temp] )

            # Update recent datetime
            dt_recent = dt_past

        # Sort tweets per date
        df_tweets.sort_index(ascending=False, inplace=True)
        pos = df_tweets["positive"]
        neg = df_tweets["negative"]
        compound = df_tweets["sentiment"]
        df_tweets["cumulative_compound"] = df_tweets["sentiment"].cumsum()
        df_tweets["prob_sen"] = 1

        total_sentiment = np.sum(compound)

        # df_tweets.to_csv(r'notebooks/tweets.csv', index=False)
        df_tweets.reset_index(inplace=True)

        # Plotting
        plt.subplot(211)
        plt.title(f"Twitter's {s_ticker} total compound sentiment over time is {total_sentiment}")
        plt.plot(
            df_tweets.index, df_tweets["cumulative_compound"].values, lw=3, c="cyan"
        )
        plt.xlim(df_tweets.index[0], df_tweets.index[-1])
        plt.grid(
            b=True, which="major", color="#666666", linestyle="-", lw=1.5, alpha=0.5
        )
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        plt.ylabel("sentiment")
        l_xticks = list()
        l_xlabels = list()
        l_xticks.append(0)
        l_xlabels.append(df_tweets["created_at"].values[0].split(" ")[0])
        n_day = datetime.strptime(
            df_tweets["created_at"].values[0], "%Y-%m-%d %H:%M:%S"
        ).day
        n_idx = 0
        for n_next_idx, dt_created in enumerate(df_tweets["created_at"]):
            if datetime.strptime(dt_created, "%Y-%m-%d %H:%M:%S").day > n_day:
                l_xticks.append(n_next_idx)
                l_xlabels.append(
                    df_tweets["created_at"].values[n_next_idx].split(" ")[0]
                )
                l_val_days = (
                    df_tweets["sentiment"].values[n_idx:n_next_idx]
                    - df_tweets["sentiment"].values[n_idx]
                )
                plt.plot(range(n_idx, n_next_idx), l_val_days, lw=3, c="tab:blue")
                n_day_avg = np.mean(l_val_days)
                if n_day_avg > 0:
                    plt.hlines(
                        n_day_avg,
                        n_idx,
                        n_next_idx,
                        linewidth=2.5,
                        linestyle="--",
                        color="green",
                        lw=3,
                    )
                else:
                    plt.hlines(
                        n_day_avg,
                        n_idx,
                        n_next_idx,
                        linewidth=2.5,
                        linestyle="--",
                        color="red",
                        lw=3,
                    )
                n_idx = n_next_idx
                n_day += 1
        l_val_days = (
            df_tweets["sentiment"].values[n_idx:]
            - df_tweets["sentiment"].values[n_idx]
        )
        plt.plot(range(n_idx, len(df_tweets)), l_val_days, lw=3, c="tab:blue")
        n_day_avg = np.mean(l_val_days)
        if n_day_avg > 0:
            plt.hlines(
                n_day_avg,
                n_idx,
                len(df_tweets),
                linewidth=2.5,
                linestyle="--",
                color="green",
                lw=3,
            )
        else:
            plt.hlines(
                n_day_avg,
                n_idx,
                len(df_tweets),
                linewidth=2.5,
                linestyle="--",
                color="red",
                lw=3,
            )
        l_xticks.append(len(df_tweets))
        # (unused?) datetime.strptime(dt_created, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
        l_xlabels.append(
            datetime.strftime(
                datetime.strptime(
                    df_tweets["created_at"].values[len(df_tweets) - 1],
                    "%Y-%m-%d %H:%M:%S",
                )
                + timedelta(days=1),
                "%Y-%m-%d",
            )
        )
        plt.xticks(l_xticks, l_xlabels)
        plt.axhspan(plt.gca().get_ylim()[0], 0, facecolor="r", alpha=0.1)
        plt.axhspan(0, plt.gca().get_ylim()[1], facecolor="g", alpha=0.1)

        plt.subplot(212)
        plt.bar(
            df_tweets[df_tweets["prob_sen"] > 0].index,
            df_tweets[df_tweets["prob_sen"] > 0]["prob_sen"].values,
            color="green",
        )
        plt.bar(
            df_tweets[df_tweets["prob_sen"] < 0].index,
            df_tweets[df_tweets["prob_sen"] < 0]["prob_sen"].values,
            color="red",
        )
        for l_x in l_xticks[1:]:
            plt.vlines(l_x, -1, 1, linewidth=2, linestyle="--", color="k", lw=3)
        plt.xlim(df_tweets.index[0], df_tweets.index[-1])
        plt.xticks(l_xticks, l_xlabels)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.ylabel("Sentiment")
        plt.xlabel("Time")
        plt.show()

    except Exception as e:
        print(e)
        print("")
