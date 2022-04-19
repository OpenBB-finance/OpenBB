"""Stocks Trading Hours Model."""

from datetime import datetime
import logging

import pandas as pd
import pytz

from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.tradinghours.data.bursa import exchange_trading_hours

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
        df = df.append(pd.DataFrame([is_open], index=["open"], columns=df.columns.values))
        return df
    if symbol in bursa.index:
        df = pd.DataFrame(bursa.loc[symbol])
        is_open = check_if_open(bursa, symbol)
        df = df.append(pd.DataFrame([is_open], index=["open"], columns=df.columns.values))
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


def all_bursa():
    """Get all exchanges from dictionary

    Parameters
    __________

    Returns
    _______
    pd.DataFrame
        All exchanges
    """
    bursa = pd.DataFrame.from_dict(exchange_trading_hours, orient="index")
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
    if localDatetime.weekday() >= 5:
        return False
    if (
        (
            localDatetime.hour > exchange_df["market_open"].hour
            and localDatetime.hour < exchange_df["market_close"].hour
        )
        or (
            localDatetime.hour > exchange_df["market_open"].hour
            and localDatetime.hour == exchange_df["market_close"].hour
            and localDatetime.minute < exchange_df["market_close"].minute
        )
        or (
            localDatetime.hour == exchange_df["market_open"].hour
            and localDatetime.minute >= exchange_df["market_open"].minute
        )
    ):
        if (
            exchange_df["lunchbreak_start"] is not None
            and exchange_df["lunchbreak_end"] is not None
        ):
            if (
                (
                    localDatetime.hour > exchange_df["lunchbreak_start"].hour
                    and localDatetime.hour < exchange_df["lunchbreak_end"].hour
                )
                or (
                    localDatetime.hour > exchange_df["lunchbreak_start"].hour
                    and localDatetime.hour == exchange_df["lunchbreak_end"].hour
                    and localDatetime.minute < exchange_df["lunchbreak_end"].minute
                )
                or (
                    localDatetime.hour == exchange_df["lunchbreak_start"].hour
                    and localDatetime.minute >= exchange_df["lunchbreak_start"].minute
                )
            ):
                return False
        return True
    else:
        return False
