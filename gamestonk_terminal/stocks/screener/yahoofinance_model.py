""" Yahoo Finance Model """
__docformat__ = "numpy"

import pandas as pd
import requests


def get_most_shorted() -> pd.DataFrame:
    """Get Yahoo Finance most shorted stock screener
    Returns
    -------
    pd.DataFrame
        Most Shorted Stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/most_shorted_stocks"

    data = pd.read_html(requests.get(url).text)[0]
    data = data.iloc[:, :-1]
    return data


def get_undervalued() -> pd.DataFrame:
    """Get Yahoo Finance undervalued growth stocks
    Returns
    -------
    pd.DataFrame
        Undervalued stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks"

    data = pd.read_html(requests.get(url).text)[0]
    data = data.iloc[:, :-1]
    return data
