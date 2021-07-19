"""FinBrain View Module"""
__docformat__ = "numpy"

import argparse
from typing import List
import requests
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
from colorama import Fore, Style

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff


register_matplotlib_converters()


def sentiment_coloring(val: float, last_val: float) -> str:
    if float(val) > last_val:
        color = Fore.GREEN
    else:
        color = Fore.RED
    return f"{color}{val}{Style.RESET_ALL}"


def get_sentiment(ticker: str) -> pd.DataFrame:
    """Gets Sentiment analysis provided by FinBrain's API

    Parameters
    ----------
    ticker : str
        Ticker to get the sentiment analysis from

    Returns
    -------
    DataFrame()
        Empty if there was an issue with data retrieval
    """
    result = requests.get(f"https://api.finbrain.tech/v0/sentiments/{ticker}")
    sentiment = pd.DataFrame()
    if result.status_code == 200:
        if "sentimentAnalysis" in result.json():
            sentiment = pd.DataFrame.from_dict(
                result.json()["sentimentAnalysis"], orient="index"
            )
            sentiment.index = pd.to_datetime(sentiment.index).to_pydatetime()
            sentiment.index.name = "date"
            sentiment.columns = ["Sentiment Analysis"]
        else:
            print("Unexpected data format from FinBrain API")
    else:
        print("Request error in retrieving sentiment from FinBrain API")

    return sentiment


def plot_sentiment(sentiment: pd.DataFrame, ticker: str):
    """Plot Sentiment analysis provided by FinBrain's API

    Parameters
    ----------
    sentiment : pd.DataFrame
        Dataframe with sentiment data to plot
    ticker : str
        Ticker to get the sentiment analysis from
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
    for index, row in sentiment.iterrows():
        if float(row["Sentiment Analysis"]) >= 0:
            plt.scatter(index, float(row["Sentiment Analysis"]), s=100, c="green")
        else:
            plt.scatter(index, float(row["Sentiment Analysis"]), s=100, c="red")
    plt.axhline(y=0, color="k", linestyle="--", lw=2)
    plt.xlabel("Time")
    plt.ylabel("Sentiment")
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    start_date = sentiment.index[-1].strftime("%Y/%m/%d")
    plt.title(f"FinBrain's Sentiment Analysis for {ticker.upper()} since {start_date}")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.gcf().autofmt_xdate()
    plt.ylim([-1.1, 1.1])
    senValues = np.array(pd.to_numeric(sentiment["Sentiment Analysis"].values))
    senNone = np.array(0 * len(sentiment))
    plt.fill_between(
        sentiment.index,
        pd.to_numeric(sentiment["Sentiment Analysis"].values),
        0,
        where=(senValues < senNone),
        alpha=0.30,
        color="red",
        interpolate=True,
    )
    plt.fill_between(
        sentiment.index,
        pd.to_numeric(sentiment["Sentiment Analysis"].values),
        0,
        where=(senValues >= senNone),
        alpha=0.30,
        color="green",
        interpolate=True,
    )
    if gtff.USE_ION:
        plt.ion()
    plt.show()


def sentiment_analysis(other_args: List[str], ticker: str):
    """Sentiment analysis from FinBrain

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker to get the sentiment analysis from
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="finbrain",
        description="""FinBrain collects the news headlines from 15+ major financial news
                    sources on a daily basis and analyzes them to generate sentiment scores
                    for more than 4500 US stocks.FinBrain Technologies develops deep learning
                    algorithms for financial analysis and prediction, which currently serves
                    traders from more than 150 countries all around the world.
                    [Source:  https://finbrain.tech]""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_sentiment = get_sentiment(ticker)

        if not df_sentiment.empty:
            plot_sentiment(df_sentiment, ticker)

        df_sentiment.sort_index(ascending=True, inplace=True)

        if gtff.USE_COLOR:
            print(
                df_sentiment["Sentiment Analysis"]
                .apply(sentiment_coloring, last_val=0)
                .to_string()
            )
        else:
            print(df_sentiment.to_string())
        print("")

    except Exception as e:
        print(e, "\n")
        print("")
