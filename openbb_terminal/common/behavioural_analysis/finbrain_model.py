"""FinBrain Model"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_sentiment(symbol: str) -> pd.DataFrame:
    """Gets Sentiment analysis provided by FinBrain's API [Source: finbrain].

    Parameters
    ----------
    symbol : str
        Ticker symbol to get the sentiment analysis from

    Returns
    -------
    pd.DataFrame
        Empty if there was an issue with data retrieval
    """
    result = request(f"https://api.finbrain.tech/v0/sentiments/{symbol}")
    sentiment = pd.DataFrame()
    if result.status_code == 200:
        result_json = result.json()
        if "sentimentAnalysis" in result_json:
            sentiment = pd.DataFrame.from_dict(
                result_json["sentimentAnalysis"], orient="index"
            )
            sentiment.index = pd.to_datetime(sentiment.index).to_pydatetime()
            sentiment.index.name = "date"
            sentiment.columns = ["Sentiment Analysis"]
            sentiment.sort_index(ascending=True, inplace=True)

    return sentiment
