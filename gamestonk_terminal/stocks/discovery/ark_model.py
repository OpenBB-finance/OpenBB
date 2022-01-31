""" ARK Model """
__docformat__ = "numpy"

import json
import logging
from datetime import timedelta

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_ark_orders() -> DataFrame:
    """Returns ARK orders in a Dataframe

    Returns
    -------
    DataFrame
        ARK orders data frame with the following columns:
        ticker, date, shares, weight, fund, direction
    """
    url_orders = "https://cathiesark.com/ark-funds-combined/trades"

    raw_page = requests.get(url_orders, headers={"User-Agent": get_user_agent()}).text

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

    return df_orders


@log_start_end(log=logger)
def add_order_total(df_orders: DataFrame) -> DataFrame:
    """Takes an ARK orders dataframe and pulls data from Yahoo Finance to add
    volume, open, close, high, low, and total columns

    Parameters
    ----------
    df_orders : DataFrame
        ARK orders data frame with the following columns:
        ticker, date, shares, weight, fund, direction

    Returns
    -------
    DataFrame
        ARK orders data frame with the following columns:
        ticker, date, shares, volume, open, close, high, low, total, weight, fund, direction
    """
    start_date = df_orders["date"].iloc[-1] - timedelta(days=1)

    tickers = " ".join(df_orders["ticker"].unique())

    console.print("")

    prices = yf.download(tickers, start=start_date, progress=False)

    for i, candle in enumerate(["Volume", "Open", "Close", "High", "Low", "Total"]):
        df_orders.insert(i + 3, candle.lower(), 0)

    pd.options.mode.chained_assignment = None
    for i, _ in df_orders.iterrows():
        if np.isnan(
            prices["Open"][df_orders.loc[i, "ticker"]][
                df_orders.loc[i, "date"].strftime("%Y-%m-%d")
            ]
        ):
            for candle in ["Volume", "Open", "Close", "High", "Low", "Total"]:
                df_orders.loc[i, candle.lower()] = 0
            continue

        for candle in ["Volume", "Open", "Close", "High", "Low"]:
            df_orders.loc[i, candle.lower()] = prices[candle][
                df_orders.loc[i, "ticker"]
            ][df_orders.loc[i, "date"].strftime("%Y-%m-%d")]

        df_orders.loc[i, "total"] = (
            df_orders.loc[i, "close"] * df_orders.loc[i, "shares"]
        )

    pd.options.mode.chained_assignment = "warn"

    return df_orders
