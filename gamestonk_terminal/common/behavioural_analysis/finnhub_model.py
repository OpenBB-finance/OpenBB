"""Finnhub Model"""
__docformat__ = "numpy"

from typing import Dict
import requests
from gamestonk_terminal import config_terminal as cfg


def get_sentiment_stats(ticker: str) -> Dict:
    """Get sentiment stats [Source: finnhub]

    Parameters
    ----------
    ticker : str
        Ticker to get sentiment stats

    Returns
    -------
    Dict
        Get sentiment stats
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={cfg.API_FINNHUB_KEY}"
    )
    if response.status_code == 200:
        return response.json()

    return {}
