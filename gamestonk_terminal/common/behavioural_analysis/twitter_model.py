"""Twitter Model"""
__docformat__ = "numpy"

import logging
from typing import Optional

import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import clean_tweet, get_data
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

analyzer = SentimentIntensityAnalyzer()


@log_start_end(log=logger)
def load_analyze_tweets(
    ticker: str,
    count: int,
    start_time: Optional[str] = "",
    end_time: Optional[str] = "",
) -> pd.DataFrame:
    """Load tweets from twitter API and analyzes using VADER

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
    df_tweet: pd.DataFrame
        Dataframe of tweets and sentiment
    """
    params = {
        "query": rf"(\${ticker}) (lang:en)",
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
        console.print("Twitter API Key provided is incorrect\n")
        return pd.DataFrame()
    elif response.status_code == 400:
        console.print(
            """
            Status Code 400.
            This means you are requesting data from beyond the API's 7 day limit"""
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
