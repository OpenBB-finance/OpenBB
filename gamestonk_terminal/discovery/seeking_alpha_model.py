""" Seeking Alpha Model """
__docformat__ = "numpy"

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame

from gamestonk_terminal.helper_funcs import get_user_agent


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
    for idx in range(0, pages):
        if idx == 0:
            url_next_earnings = "https://seekingalpha.com/earnings/earnings-calendar"
        else:
            url_next_earnings = (
                f"https://seekingalpha.com/earnings/earnings-calendar/{idx+1}"
            )
        text_soup_earnings = BeautifulSoup(
            requests.get(
                url_next_earnings, headers={"User-Agent": get_user_agent()}
            ).text,
            "lxml",
        )

        for stock_rows in text_soup_earnings.findAll("tr", {"data-exchange": "NASDAQ"}):
            stocks = list()
            for a_stock in stock_rows.contents[:3]:
                stocks.append(a_stock.text)
            earnings.append(stocks)

    df_earnings = pd.DataFrame(earnings, columns=["Ticker", "Name", "Date"])
    df_earnings["Date"] = pd.to_datetime(df_earnings["Date"])
    df_earnings = df_earnings.set_index("Date")

    return df_earnings
