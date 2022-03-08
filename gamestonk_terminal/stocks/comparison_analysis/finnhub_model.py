"""Finnhub model"""
__docformat__ = "numpy"

import logging
from typing import List, Tuple

import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_similar_companies(ticker: str) -> Tuple[List[str], str]:
    response = requests.get(
        f"https://finnhub.io/api/v1/stock/peers?symbol={ticker}&token={cfg.API_FINNHUB_KEY}"
    )

    similar = []
    user = "Error"

    if response.status_code == 200:
        similar = response.json()
        user = "Finnhub"

        if not similar:
            console.print("Similar companies not found.")
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return similar, user
