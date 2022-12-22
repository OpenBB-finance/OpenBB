"""Stocks Trading Hours Model."""

import logging
import os
from datetime import datetime

import pandas as pd
import pytz

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)
# pylint: disable=no-member

# pylint: disable=no-member


@log_start_end(log=logger)
def get_bursa(symbol: str) -> pd.DataFrame:
    """Get current exchange open hours.

    Parameters
    ----------
    symbol : str
        Exchange symbol

    Returns
    -------
    pd.DataFrame
        Exchange info
    """
    bursa = all_bursa()

    symbol = symbol.upper()
    if symbol in bursa["short_name"].values:
        df = pd.DataFrame(bursa.loc[bursa["short_name"] == symbol]).transpose()
        is_open = check_if_open(bursa, symbol)
        df_is_open = pd.DataFrame([is_open], index=["open"], columns=df.columns.values)
        df = pd.concat([df, df_is_open], axis=0)
        return df
    if symbol in bursa.index:
        df = pd.DataFrame(bursa.loc[symbol])
        is_open = check_if_open(bursa, symbol)
        df_is_open = pd.DataFrame([is_open], index=["open"], columns=df.columns.values)
        df = pd.concat([df, df_is_open], axis=0)
        return df
    return pd.DataFrame()


@log_start_end(log=logger)
def get_open() -> pd.DataFrame:
    """Get open exchanges.

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        Currently open exchanges
    """
    bursa = all_bursa()
    is_open_list = []
    for exchange in bursa.index:
        is_open = check_if_open(bursa, exchange)
        is_open_list.append(is_open)
    bursa["open"] = is_open_list
    bursa = bursa.loc[bursa["open"]]
    return bursa[["name", "short_name"]]


@log_start_end(log=logger)
def get_closed() -> pd.DataFrame:
    """Get closed exchanges.

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        Currently closed exchanges
    """
    bursa = all_bursa()
    is_open_list = []
    for exchange in bursa.index:
        is_open = check_if_open(bursa, exchange)
        is_open_list.append(is_open)
    bursa["open"] = is_open_list
    bursa = bursa.loc[~bursa["open"]]
    return bursa[["name", "short_name"]]


@log_start_end(log=logger)
def get_all() -> pd.DataFrame:
    """Get all exchanges.

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        All available exchanges
    """
    bursa = all_bursa()
    is_open_list = []
    for exchange in bursa.index:
        is_open = check_if_open(bursa, exchange)
        is_open_list.append(is_open)
    bursa["open"] = is_open_list
    return bursa[["name", "short_name", "open"]]


@log_start_end(log=logger)
def get_all_exchange_short_names() -> pd.DataFrame:
    """Get all exchanges short names.

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        All available exchanges short names
    """
    bursa = all_bursa()
    is_open_list = []
    for exchange in bursa.index:
        is_open = check_if_open(bursa, exchange)
        is_open_list.append(is_open)
    bursa["open"] = is_open_list
    return bursa[["short_name"]]


@log_start_end(log=logger)
def all_bursa():
    """Get all exchanges from dictionary

    Parameters
    __________

    Returns
    _______
    pd.DataFrame
        All exchanges
    """
    path = os.path.join(os.path.dirname(__file__), "data/bursa_open_hours.json")
    bursa = pd.read_json(path)  # , orient="index")
    return bursa


def check_if_open(bursa: pd.DataFrame, exchange: str) -> bool:
    """Check if market open helper function

    Parameters
    __________
    bursa : pd.DataFrame
        pd.DataFrame of all exchanges
    exchange : str
        bursa pd.DataFrame index value for exchange

    Returns
    _______
    bool
        If market is open
    """
    exchange = exchange.upper()
    if exchange in bursa.index.values:
        tz = bursa.loc[exchange]["timezone"]
        exchange_df = bursa.loc[exchange]
    elif exchange in bursa["short_name"].values:
        tz = bursa.loc[bursa["short_name"] == exchange]["timezone"].values[0]
        exchange_df = bursa.loc[bursa["short_name"] == exchange]
        exchange_df = exchange_df.iloc[0].transpose()
    utcmoment_naive = datetime.utcnow()
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
    local_datetime = utcmoment.astimezone(pytz.timezone(tz))
    market_open = datetime.strptime(exchange_df["market_open"], "%H:%M:%S")
    market_close = datetime.strptime(exchange_df["market_close"], "%H:%M:%S")
    after_market_open = local_datetime.time() >= market_open.time()
    before_market_close = local_datetime.time() <= market_close.time()
    try:
        lunchbreak_start = datetime.strptime(
            exchange_df["lunchbreak_start"], "%H:%M:%S"
        )
        lunchbreak_end = datetime.strptime(exchange_df["lunchbreak_end"], "%H:%M:%S")

        after_lunch_start = local_datetime.time() >= lunchbreak_start.time()
        before_lunch_end = local_datetime.time() <= lunchbreak_end.time()
    except Exception:
        after_lunch_start = False
        before_lunch_end = False

    if local_datetime.weekday() >= 5:
        result = False
    else:
        result = (
            after_market_open
            and before_market_close
            and not (after_lunch_start and before_lunch_end)
        )

    return result
