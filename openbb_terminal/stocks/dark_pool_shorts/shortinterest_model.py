""" Short Interest View """
__docformat__ = "numpy"

import logging

import pandas as pd
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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
        request(
            url_high_short_interested_stocks, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    a_high_short_interest_header = [
        high_short_interest_header.text.strip("\n").split("\n")[0]
        for high_short_interest_header in text_soup_high_short_interested_stocks.findAll(
            "td", {"class": "tblhdr"}
        )
    ]

    if not a_high_short_interest_header:
        return pd.DataFrame()

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
