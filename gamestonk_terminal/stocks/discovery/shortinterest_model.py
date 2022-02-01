""" Short Interest View """
__docformat__ = "numpy"

import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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

    a_low_float_header = []
    for low_float_header in text_soup_low_float_stocks.findAll(
        "td", {"class": "tblhdr"}
    ):
        a_low_float_header.append(low_float_header.text.strip("\n").split("\n")[0])
    df_low_float = pd.DataFrame(columns=a_low_float_header)
    df_low_float.loc[0] = ["", "", "", "", "", "", ""]

    stock_list_tr = text_soup_low_float_stocks.find_all("tr")

    low_float_data = []
    for a_stock in stock_list_tr:
        a_stock_txt = a_stock.text

        if a_stock_txt == "":
            continue

        low_float_data = a_stock_txt.split("\n")

        if len(low_float_data) == 8:
            df_low_float.loc[len(df_low_float.index)] = low_float_data[:-1]

        low_float_data = []

    return df_low_float


@log_start_end(log=logger)
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
            url_penny_stock_stocks,
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )

    a_penny_stock_header = list()
    for penny_stock_header in text_soup_penny_stock_stocks.findAll(
        "td", {"class": "tblhdr"}
    ):
        a_penny_stock_header.append(penny_stock_header.text)

    l_stocks = list()
    for penny_stock in text_soup_penny_stock_stocks.find_all("a", href=True):
        if penny_stock.text:
            l_stocks.append(penny_stock.text)

    a_penny_stock = list()
    penny_idx = 0
    d_stocks = {}
    for penny_stock in text_soup_penny_stock_stocks.findAll("td", {"align": "right"}):
        a_penny_stock.append(penny_stock.text)

        if len(a_penny_stock) == 5:
            d_stocks[l_stocks[penny_idx]] = a_penny_stock
            penny_idx += 1
            a_penny_stock = list()

    df_penny = pd.DataFrame.from_dict(d_stocks).T
    df_penny.columns = a_penny_stock_header[1:]

    return df_penny
