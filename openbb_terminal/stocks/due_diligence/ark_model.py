"""Ark Model"""
__docformat__ = "numpy"

import json
import logging

import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_ark_trades_by_ticker(symbol: str) -> pd.DataFrame:
    """Gets a dataframe of ARK trades for ticker

    Parameters
    ----------
    symbol : str
        Ticker to get trades for

    Returns
    -------
    pd.DataFrame
        DataFrame of trades
    """
    url = f"https://cathiesark.com/ark-combined-holdings-of-{symbol}"
    r = request(url, headers={"User-Agent": get_user_agent()})
    # Error in request
    if r.status_code != 200:
        return pd.DataFrame()

    parsed_script = BeautifulSoup(r.text, "lxml").find(
        "script", {"id": "__NEXT_DATA__"}
    )
    parsed_json = json.loads(parsed_script.string)
    # Return empty dataframe if there is no "trades" data

    if "trades" not in parsed_json["props"]["pageProps"]:
        return pd.DataFrame()

    df_orders = pd.json_normalize(parsed_json["props"]["pageProps"]["trades"])

    # If trades found in dictionary, but the output is empty
    if df_orders.empty:
        return pd.DataFrame()

    df_orders = df_orders.drop(columns=["hidden", "everything.profile.customThumbnail"])
    df_orders["date"] = df_orders["date"].apply(lambda x: x.strip("Z"))

    df_orders.rename(columns={"date": "Date"}, inplace=True)

    # Get yfinance price to merge.  Use Close which assumes purchased throughout day
    prices = yf.download(
        symbol,
        end=df_orders.Date.iloc[0],
        start=df_orders.Date.iloc[-1],
        progress=False,
        ignore_tz=True,
    )["Close"]

    df_orders.set_index("Date", inplace=True)
    df_orders.index = pd.DatetimeIndex(df_orders.index)
    df_orders = df_orders.join(prices)
    df_orders["Total"] = df_orders["Close"] * df_orders["shares"]
    return df_orders.sort_index(ascending=False)
