""" Comparison Analysis FinBrain Model """
__docformat__ = "numpy"

import logging
from typing import List, Tuple

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def find_smallest_num_data_point(results_list: List[dict]) -> int:
    """Helper function to find the number for the smallest total number of data points
    out of all the tickers. This is necessary because if one ticker has more or less
    data points than another then it will throw an indexing error. The solution is to
    have each ticker have the same number of data points as to graph and view properly.
    We chose to set each ticker to the minimum of number data points out of all the
    tickers.

    Parameters
    ----------
    results_list : List[json]
        List of dicts storing ticker data

    Returns
    -------
    int
        Value of smallest total number of sentiment data points
    """
    small_list = list()
    for result_json in results_list:
        if (
            "ticker" in result_json
            and "sentimentAnalysis" in result_json
            and len(result_json["sentimentAnalysis"].values()) > 0
        ):
            small_list.append(len(result_json["sentimentAnalysis"].values()))
    return min(small_list)


@log_start_end(log=logger)
def get_sentiments(symbols: List[str]) -> pd.DataFrame:
    """Gets Sentiment analysis from several symbols provided by FinBrain's API.

    Parameters
    ----------
    symbols : List[str]
        List of tickers to get sentiment.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().

    Returns
    -------
    pd.DataFrame
        Contains sentiment analysis from several tickers
    """

    df_sentiment = pd.DataFrame()
    dates_sentiment = []
    symbols_to_remove = list()
    results_list = list()
    for ticker in symbols:
        result = request(f"https://api.finbrain.tech/v0/sentiments/{ticker}")
        # Check status code, if its correct then convert to dict using .json()
        if result.status_code == 200:
            result_json = result.json()
            results_list.append(result_json)
        else:
            console.print(
                f"Request error in retrieving {ticker} sentiment from FinBrain API"
            )
            symbols_to_remove.append(ticker)

    # Finds the smallest amount of data points from any of the tickers as to not run
    # into an indexing error when graphing
    smallest_num_data_point = find_smallest_num_data_point(results_list)

    num = 0
    for result_json in results_list:
        ticker = symbols[num]
        # Checks to see if sentiment data in results_json
        if (
            "ticker" in result_json
            and "sentimentAnalysis" in result_json
            and len(result_json["sentimentAnalysis"].values()) > 0
        ):
            # Storing sentiments and dates in list
            sentiments = list(result_json["sentimentAnalysis"].values())
            dates_sentiment = list(result_json["sentimentAnalysis"].keys())

            # If there are more sentiment data points for one ticker compared to the
            # smallest amount of data points, then remove that data points from that
            # ticker as to be able to graph properly
            if len(sentiments) > smallest_num_data_point:
                sentiments = sentiments[0:smallest_num_data_point]
                dates_sentiment = dates_sentiment[0:smallest_num_data_point]

            df_sentiment[ticker] = [float(val) for val in sentiments]

        # If sentiment data not in results_json remove it
        else:
            console.print(
                f"Unexpected data format or no data from FinBrain API for {ticker}"
            )
            symbols_to_remove.append(ticker)

        num = num + 1

    for ticker in symbols_to_remove:
        symbols.remove(ticker)

    if not df_sentiment.empty:
        df_sentiment.index = dates_sentiment
        df_sentiment.sort_index(ascending=True, inplace=True)

    return df_sentiment


@log_start_end(log=logger)
def get_sentiment_correlation(
    similar: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get correlation sentiments across similar companies. [Source: FinBrain].

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().

    Returns
    -------
    Tuple[pd.DataFrame,pd.DataFrame]
        Contains sentiment analysis from several tickers
    """
    df_sentiment = get_sentiments(similar)
    corrs = df_sentiment.corr()

    return corrs, df_sentiment
