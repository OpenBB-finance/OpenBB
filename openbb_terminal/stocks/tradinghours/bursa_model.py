"""Stocks Trading Hours Model."""

from datetime import datetime

import logging
import os

import pandas as pd
import pytz

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


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
        df = df.append(
            pd.DataFrame([is_open], index=["open"], columns=df.columns.values)
        )
        return df
    if symbol in bursa.index:
        df = pd.DataFrame(bursa.loc[symbol])
        is_open = check_if_open(bursa, symbol)
        df = df.append(
            pd.DataFrame([is_open], index=["open"], columns=df.columns.values)
        )
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


def check_if_open(bursa, exchange):
    """Check if market open helper function

    Parameters
    __________
    bursa
        pd.DataFrame of all exchanges
    exchange
        bursa pd.DataFrame index value for exchande

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
    localDatetime = utcmoment.astimezone(pytz.timezone(tz))
    market_open = datetime.strptime(exchange_df["market_open"], "%H:%M:%S")
    market_close = datetime.strptime(exchange_df["market_close"], "%H:%M:%S")
    try:
        lunchbreak_start = datetime.strptime(
            exchange_df["lunchbreak_start"], "%H:%M:%S"
        )
        lunchbreak_end = datetime.strptime(exchange_df["lunchbreak_end"], "%H:%M:%S")
    except Exception:
        lunchbreak_end = None
        lunchbreak_start = None

    if localDatetime.weekday() >= 5:
        result = False
    elif (
        localDatetime.hour > market_open.hour and localDatetime.hour < market_close.hour
    ):
        if lunchbreak_start is not None and lunchbreak_end is not None:
            if (
                localDatetime.hour > lunchbreak_start.hour
                and localDatetime.hour < lunchbreak_end.hour
            ):
                result = False
            elif (
                localDatetime.hour > lunchbreak_start.hour
                and localDatetime.hour == lunchbreak_end.hour
                and localDatetime.minute < lunchbreak_end.minute
            ):
                result = False
            elif (
                localDatetime.hour == lunchbreak_start.hour
                and localDatetime.minute >= lunchbreak_start.minute
            ):
                result = False
        else:
            result = True
    elif (
        localDatetime.hour > market_open.hour
        and localDatetime.hour == market_close.hour
        and localDatetime.minute < market_close.minute
    ):
        if lunchbreak_start is not None and lunchbreak_end is not None:
            if (
                localDatetime.hour > lunchbreak_start.hour
                and localDatetime.hour < lunchbreak_end.hour
            ):
                result = False
            elif (
                localDatetime.hour > lunchbreak_start.hour
                and localDatetime.hour == lunchbreak_end.hour
                and localDatetime.minute < lunchbreak_end.minute
            ):
                result = False
            elif (
                localDatetime.hour == lunchbreak_start.hour
                and localDatetime.minute >= lunchbreak_start.minute
            ):
                result = False
            else:
                result = True
        else:
            result = True
    elif (
        localDatetime.hour == market_open.hour
        and localDatetime.minute >= market_open.minute
    ):
        if lunchbreak_start is not None and lunchbreak_end is not None:
            if (
                localDatetime.hour > lunchbreak_start.hour
                and localDatetime.hour < lunchbreak_end.hour
            ):
                result = False
            elif (
                localDatetime.hour > lunchbreak_start.hour
                and localDatetime.hour == lunchbreak_end.hour
                and localDatetime.minute < lunchbreak_end.minute
            ):
                result = False
            elif (
                localDatetime.hour == lunchbreak_start.hour
                and localDatetime.minute >= lunchbreak_start.minute
            ):
                result = False
            else:
                result = True
        else:
            result = True
    else:
        result = False

    return result
