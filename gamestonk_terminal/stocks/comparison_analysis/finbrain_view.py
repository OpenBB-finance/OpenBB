""" Comparison Analysis FinBrain API """
__docformat__ = "numpy"

import argparse
from typing import List
import requests
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
import seaborn as sns

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff


register_matplotlib_converters()


def sentiment_compare(other_args: List[str], ticker: str, similar: List[str]):
    """Plot sentiments across similar companies

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Main ticker to compare income
    similar : List[str]
        Similar companies to compare income with
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="sentiment_compare",
        description="""
            FinBrain's sentiment comparison across similar tickers.
            FinBrain collects the news headlines from 15+ major financial news
            sources on a daily basis and analyzes them to generate sentiment scores
            for more than 4500 US stocks.FinBrain Technologies develops deep learning
            algorithms for financial analysis and prediction, which currently serves
            traders from more than 150 countries all around the world.
            [Source: https://finbrain.tech]
        """,
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=similar,
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=[],
        help="apart from loaded similar companies also compare with.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        l_similar = ns_parser.l_similar
        l_similar += ns_parser.l_also

        # Add main ticker to similar list of companies
        l_similar = [ticker] + l_similar

        df_sentiment = get_sentiments(l_similar)

        if not df_sentiment.empty:
            plot_sentiments(df_sentiment, l_similar)
        print("")

    except Exception as e:
        print(e, "\n")


def sentiment_correlation(other_args: List[str], ticker: str, similar: List[str]):
    """Plot correlation sentiments across similar companies

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Main ticker to compare income
    similar : List[str]
        Similar companies to compare income with
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="sentiment_compare",
        description="""
            FinBrain's sentiment correlation across similar tickers.
            FinBrain collects the news headlines from 15+ major financial news
            sources on a daily basis and analyzes them to generate sentiment scores
            for more than 4500 US stocks.FinBrain Technologies develops deep learning
            algorithms for financial analysis and prediction, which currently serves
            traders from more than 150 countries all around the world.
            [Source: https://finbrain.tech]
        """,
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=similar,
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=[],
        help="apart from loaded similar companies also compare with.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        l_similar = ns_parser.l_similar
        l_similar += ns_parser.l_also

        # Add main ticker to similar list of companies
        l_similar = [ticker] + l_similar

        df_sentiment = get_sentiments(l_similar)

        if not df_sentiment.empty:
            plot_correlation(df_sentiment, l_similar)
        print("")

    except Exception as e:
        print(e, "\n")


def get_sentiments(similar: List[str]) -> pd.DataFrame:
    """Gets Sentiment analysis from several tickers provided by FinBrain's API

    Parameters
    ----------
    similar : List[str]
        Similar tickers to get the sentiment analysis from

    Returns
    -------
    DataFrame()
        Contains sentiment analysis from several tickers
    """

    df_sentiment = pd.DataFrame()
    dates_sentiment = list()
    for ticker in similar:
        result = requests.get(f"https://api.finbrain.tech/v0/sentiments/{ticker}")
        if result.status_code == 200:
            if "sentimentAnalysis" in result.json():
                df_sentiment[ticker] = [
                    float(val)
                    for val in list(result.json()["sentimentAnalysis"].values())
                ]
                dates_sentiment = list(result.json()["sentimentAnalysis"].keys())
            else:
                print(f"Unexpected data format from FinBrain API for {ticker}")
                similar.remove(ticker)

        else:
            print(f"Request error in retrieving {ticker} sentiment from FinBrain API")
            similar.remove(ticker)

    if not df_sentiment.empty:
        df_sentiment.index = dates_sentiment
        df_sentiment.sort_index(ascending=True, inplace=True)

    return df_sentiment


def plot_sentiments(df_sentiment: pd.DataFrame, similar: List[str]):
    """Plot Sentiment analysis comparison between similar companies

    Parameters
    ----------
    df_sentiment : pd.DataFrame
        Dataframe with sentiment analysis from several similar companies
    similar : List[str]
        List of similar companies
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    for idx, ticker in enumerate(similar):
        offset = 2 * idx
        plt.axhline(y=offset, color="k", linestyle="--", lw=2)
        plt.axhline(y=offset + 1, color="k", linestyle="--", lw=1)

        senValues = np.array(pd.to_numeric(df_sentiment[ticker].values))
        senNone = np.array(0 * len(df_sentiment))
        plt.fill_between(
            df_sentiment.index,
            pd.to_numeric(df_sentiment[ticker].values) + offset,
            offset,
            where=(senValues < senNone),
            alpha=0.60,
            color="red",
            interpolate=True,
        )

        plt.fill_between(
            df_sentiment.index,
            pd.to_numeric(df_sentiment[ticker].values) + offset,
            offset,
            where=(senValues >= senNone),
            alpha=0.60,
            color="green",
            interpolate=True,
        )

    plt.xlabel("Time")
    plt.ylabel("Sentiment")
    plt.axhline(y=-1, color="k", linestyle="--", lw=1)
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    plt.yticks(np.arange(len(similar)) * 2, similar)
    plt.title(f"FinBrain's Sentiment Analysis since {df_sentiment.index[0]}")
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.gcf().autofmt_xdate()

    if gtff.USE_ION:
        plt.ion()
    plt.show()


def plot_correlation(df_sentiment: pd.DataFrame, similar: List[str]):
    """Plot Sentiment correlation between similar companies

    Parameters
    ----------
    df_sentiment : pd.DataFrame
        Dataframe with sentiment analysis from several similar companies
    similar : List[str]
        List of similar companies
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    mask = np.zeros((len(similar), len(similar)), dtype=bool)
    mask[np.triu_indices(len(mask))] = True

    sns.heatmap(
        df_sentiment.corr(),
        cbar_kws={"ticks": [-1.0, -0.5, 0.0, 0.5, 1.0]},
        cmap="RdYlGn",
        linewidths=1,
        annot=True,
        vmin=-1,
        vmax=1,
        mask=mask,
    )

    if gtff.USE_ION:
        plt.ion()
    plt.show()
