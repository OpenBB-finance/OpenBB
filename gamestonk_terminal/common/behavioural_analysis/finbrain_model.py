"""FinBrain Model"""
__docformat__ = "numpy"

import pandas as pd
import requests


def get_sentiment(ticker: str) -> pd.DataFrame:
    """Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]

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
    return sentiment
