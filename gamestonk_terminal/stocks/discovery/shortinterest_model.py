""" Short Interest View """
__docformat__ = "numpy"

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame

from gamestonk_terminal.helper_funcs import get_user_agent


def get_low_float() -> DataFrame:
    """Returns low float DataFrame

    Returns
    -------
    DataFrame
        Low float DataFrame with the following columns:
        Ticker, Company, Exchange, ShortInt, Float, Outstd, Industry
    """
    url_high_short_interested_stocks = "https://www.lowfloat.com"

    text_soup_low_float_stocks = BeautifulSoup(
        requests.get(
            url_high_short_interested_stocks, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    a_low_float_header = list()
    for low_float_header in text_soup_low_float_stocks.findAll(
        "td", {"class": "tblhdr"}
    ):
        a_low_float_header.append(low_float_header.text.strip("\n").split("\n")[0])
    df_low_float = pd.DataFrame(columns=a_low_float_header)
    df_low_float.loc[0] = ["", "", "", "", "", "", ""]

    stock_list_tr = text_soup_low_float_stocks.find_all("tr")

    low_float_data = list()
    for a_stock in stock_list_tr:
        a_stock_txt = a_stock.text

        if a_stock_txt == "":
            continue

        low_float_data = a_stock_txt.split("\n")

        if len(low_float_data) == 8:
            df_low_float.loc[len(df_low_float.index)] = low_float_data[:-1]

        low_float_data = list()

    return df_low_float


def get_today_hot_penny_stocks() -> DataFrame:
    """Returns today hot penny stocks

    Returns
    -------
    DataFrame
        Today hot penny stocks DataFrame with the following columns:
        Ticker, Price, Change, $ Volume, Volume, # Trades
    """
    url_penny_stock_stocks = "https://www.pennystockflow.com"

    text_soup_penny_stock_stocks = BeautifulSoup(
        requests.get(
            url_penny_stock_stocks, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    a_penny_stock_header = list()
    for penny_stock_header in text_soup_penny_stock_stocks.findAll(
        "td", {"class": "tblhdr"}
    ):
        a_penny_stock_header.append(penny_stock_header.text)

    df_penny = pd.DataFrame(columns=a_penny_stock_header)

    first_penny = list()
    for idx, penny_stock_header in enumerate(text_soup_penny_stock_stocks.findAll("a")):
        if idx == 0:
            continue
        if idx > 1:
            break
        first_penny.append(penny_stock_header.text)

    for idx, first_penny_stock in enumerate(
        text_soup_penny_stock_stocks.findAll("td", {"align": "right"})
    ):
        first_penny.append(first_penny_stock.text)
        if idx > 3:
            break

    df_penny.loc[0] = first_penny

    a_penny_stock = list()
    penny_idx = 1
    for idx, penny_stock in enumerate(
        text_soup_penny_stock_stocks.findAll("td", {"class": "tdi"})
    ):
        a_penny_stock.append(penny_stock.text)

        if (idx + 1) % 6 == 0:
            df_penny.loc[penny_idx] = a_penny_stock
            penny_idx += 1
            a_penny_stock = list()

    return df_penny
