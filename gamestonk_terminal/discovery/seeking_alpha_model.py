""" Seeking Alpha Model """
__docformat__ = "numpy"

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame

from gamestonk_terminal.helper_funcs import get_user_agent


def get_earnings_html(url_next_earnings: str) -> str:
    """Wraps HTTP requests.get for testibility

    Parameters
    ----------
    url_next_earnings : str
        Next earnings URL

    Returns
    -------
    str
        HTML page of next earnings
    """
    earnings_html = requests.get(
        url_next_earnings, headers={"User-Agent": get_user_agent()}
    ).text

    return earnings_html


def get_next_earnings(pages: int) -> DataFrame:
    """Returns a DataFrame with upcoming earnings

    Parameters
    ----------
    pages : int
        Number of pages

    Returns
    -------
    DataFrame
        Upcoming earnings DataFrame
    """

    earnings = list()
    url_next_earnings = "https://seekingalpha.com/earnings/earnings-calendar"

    for idx in range(0, pages):
        text_soup_earnings = BeautifulSoup(
            get_earnings_html(url_next_earnings),
            "lxml",
        )

        for stock_rows in text_soup_earnings.findAll("tr", {"data-exchange": "NASDAQ"}):
            stocks = list()
            for a_stock in stock_rows.contents[:3]:
                stocks.append(a_stock.text)
            earnings.append(stocks)

        url_next_earnings = (
            f"https://seekingalpha.com/earnings/earnings-calendar/{idx+1}"
        )

    df_earnings = pd.DataFrame(earnings, columns=["Ticker", "Name", "Date"])
    df_earnings["Date"] = pd.to_datetime(df_earnings["Date"])
    df_earnings = df_earnings.set_index("Date")

    return df_earnings
