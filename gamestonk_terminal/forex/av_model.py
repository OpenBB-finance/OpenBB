"""AlphaVantage FX Model"""

import argparse
from typing import Dict
import os
import pandas as pd
import requests
from gamestonk_terminal import config_terminal as cfg


def check_valid_forex_currency(fx_symbol: str) -> str:
    """Check if given symbol is supported on alphavantage

    Parameters
    ----------
    fx_symbol : str
        Symbol to check

    Returns
    -------
    str
        Currency symbol

    Raises
    ------
    argparse.ArgumentTypeError
        Symbol not valid on alphavantage
    """
    path = os.path.join(os.path.dirname(__file__), "av_forex_currencies.csv")
    if fx_symbol.upper() in list(pd.read_csv(path)["currency code"]):
        return fx_symbol.upper()

    raise argparse.ArgumentTypeError(
        f"{fx_symbol.upper()} not found in alphavantage supported currency codes. "
    )


def get_quote(to_symbol: str, from_symbol: str) -> Dict:
    """Get current exchange rate quote from alpha vantage

    Parameters
    ----------
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol

    Returns
    -------
    Dict
        Dictionary of exchange rate
    """
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_symbol}&\
        to_currency={to_symbol}&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    r = requests.get(url)
    if r.status_code != 200:
        return {}
    return r.json()


def load():
    pass
