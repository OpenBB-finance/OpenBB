""" ARK Model """
__docformat__ = "numpy"

import json
import logging
from datetime import timedelta

import numpy as np
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_ark_orders(
    buys_only: bool = False,
    sells_only: bool = False,
    fund: str = "",
) -> DataFrame:
    """Returns ARK orders in a Dataframe

    Parameters
    ----------
    buys_only: bool
        Flag to filter on buys only
    sells_only: bool
        Flag to sort on sells only
    fund: str
        Optional filter by fund

    Returns
    -------
    DataFrame
        ARK orders data frame with the following columns -
        (ticker, date, shares, weight, fund, direction)
    """
    url_orders = "https://cathiesark.com/ark-funds-combined/trades"

    raw_page = request(url_orders, headers={"User-Agent": get_user_agent()}).text

    parsed_script = BeautifulSoup(raw_page, "lxml").find(
        "script", {"id": "__NEXT_DATA__"}
    )

    parsed_json = json.loads(parsed_script.string)

    df_orders = pd.json_normalize(parsed_json["props"]["pageProps"]["arkTrades"])

    if df_orders.empty:
        return pd.DataFrame()

    df_orders.drop(
        [
            "hidden",
            "images.thumbnail",
            "cusip",
            "estimated_price",
            "updated_at",
            "created_at",
            "region",
            "country",
            "isADR",
            "companyName",
            "clinicalTrialsSearchHandle",
            "wasSPACBuy",
            "currencyMultiplier",
            "useRapidAPI",
            "description",
            "quandlTicker",
            "customThumbnail",
            "custom_thumbnail",
            "id",
        ],
        axis=1,
        inplace=True,
    )

    df_orders["date"] = pd.to_datetime(df_orders["date"], format="%Y-%m-%d").dt.date

    if df_orders.empty:
        console.print("The ARK orders aren't available at the moment.\n")
        return pd.DataFrame()
    if fund:
        df_orders = df_orders[df_orders.fund == fund]
    if buys_only:
        df_orders = df_orders[df_orders.direction == "Buy"]
    if sells_only:
        df_orders = df_orders[df_orders.direction == "Sell"]

    return df_orders


@log_start_end(log=logger)
def add_order_total(data: DataFrame) -> DataFrame:
    """Takes an ARK orders dataframe and pulls data from Yahoo Finance to add
    volume, open, close, high, low, and total columns

    Parameters
    ----------
    data: DataFrame
        ARK orders data frame with the following columns -
        (ticker, date, shares, weight, fund, direction)

    Returns
    -------
    DataFrame
        ARK orders data frame with the following columns -
        (ticker, date, shares, volume, open, close, high, low, total, weight, fund, direction)
    """
    start_date = data["date"].iloc[-1] - timedelta(days=1)

    tickers = " ".join(data["ticker"].unique())

    prices = yf.download(tickers, start=start_date, progress=False)

    if prices.empty:
        return pd.DataFrame()
    for i, candle in enumerate(["Volume", "Open", "Close", "High", "Low", "Total"]):
        data.insert(i + 3, candle.lower(), 0)

    pd.options.mode.chained_assignment = None
    for i, _ in data.iterrows():
        if np.isnan(
            prices["Open"][data.loc[i, "ticker"]][
                data.loc[i, "date"].strftime("%Y-%m-%d")
            ]
        ):
            for candle in ["Volume", "Open", "Close", "High", "Low", "Total"]:
                data.loc[i, candle.lower()] = 0
            continue

        for candle in ["Volume", "Open", "Close", "High", "Low"]:
            data.loc[i, candle.lower()] = prices[candle][data.loc[i, "ticker"]][
                data.loc[i, "date"].strftime("%Y-%m-%d")
            ]

        data.loc[i, "total"] = data.loc[i, "close"] * data.loc[i, "shares"]

    pd.options.mode.chained_assignment = "warn"

    return data
