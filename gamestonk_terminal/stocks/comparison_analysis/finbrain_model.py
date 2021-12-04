""" Comparison Analysis FinBrain Model """
__docformat__ = "numpy"

from typing import List
import pandas as pd
import requests


def get_sentiments(tickers: List[str]) -> pd.DataFrame:
    """Gets Sentiment analysis from several tickers provided by FinBrain's API

    Parameters
    ----------
    tickers : List[str]
        List of tickers to get sentiment

    Returns
    -------
    pd.DataFrame
        Contains sentiment analysis from several tickers
    """

    df_sentiment = pd.DataFrame()
    dates_sentiment = []
    tickers_to_remove = list()
    for ticker in tickers:
        result = requests.get(f"https://api.finbrain.tech/v0/sentiments/{ticker}")
        if result.status_code == 200:
            if "ticker" in result.json() and "sentimentAnalysis" in result.json():
                df_sentiment[ticker] = [
                    float(val)
                    for val in list(result.json()["sentimentAnalysis"].values())
                ]
                dates_sentiment = list(result.json()["sentimentAnalysis"].keys())
            else:
                print(f"Unexpected data format from FinBrain API for {ticker}")
                tickers_to_remove.append(ticker)

        else:
            print(f"Request error in retrieving {ticker} sentiment from FinBrain API")
            tickers_to_remove.append(ticker)

    for ticker in tickers_to_remove:
        tickers.remove(ticker)

    if not df_sentiment.empty:
        df_sentiment.index = dates_sentiment
        df_sentiment.sort_index(ascending=True, inplace=True)

    return df_sentiment
