""" Short Interest View """
__docformat__ = "numpy"

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame

from gamestonk_terminal.helper_funcs import get_user_agent


def get_high_short_interest() -> DataFrame:
    """Returns a high short interest DataFrame

    Returns
    -------
    DataFrame
        High short interest Dataframe with the following columns:
        Ticker, Company, Exchange, ShortInt, Float, Outstd, Industry
    """
    url_high_short_interested_stocks = "https://www.highshortinterest.com"

    text_soup_high_short_interested_stocks = BeautifulSoup(
        requests.get(
            url_high_short_interested_stocks, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    a_high_short_interest_header = []
    for high_short_interest_header in text_soup_high_short_interested_stocks.findAll(
        "td", {"class": "tblhdr"}
    ):
        a_high_short_interest_header.append(
            high_short_interest_header.text.strip("\n").split("\n")[0]
        )
    df_high_short_interest = pd.DataFrame(columns=a_high_short_interest_header)
    df_high_short_interest.loc[0] = ["", "", "", "", "", "", ""]

    stock_list_tr = text_soup_high_short_interested_stocks.find_all("tr")

    shorted_stock_data = []
    for a_stock in stock_list_tr:
        a_stock_txt = a_stock.text

        if a_stock_txt == "":
            continue

        shorted_stock_data = a_stock_txt.split("\n")

        if len(shorted_stock_data) == 8:
            df_high_short_interest.loc[
                len(df_high_short_interest.index)
            ] = shorted_stock_data[:-1]

        shorted_stock_data = []

    return df_high_short_interest
