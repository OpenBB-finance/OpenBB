"""Finnhub model"""
__docformat__ = "numpy"

from typing import List, Tuple
import requests
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.rich_config import console


def get_similar_companies(ticker: str) -> Tuple[List[str], str]:
    result = requests.get(
        f"https://finnhub.io/api/v1/stock/peers?symbol={ticker}&token={cfg.API_FINNHUB_KEY}"
    )

    if result.status_code == 200:
        similar = result.json()
        user = "Finnhub"

    else:
        console.print("Similar companies not found.")
        similar = [""]
        user = "Error"
    return similar, user
