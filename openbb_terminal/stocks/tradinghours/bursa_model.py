"""Exhcange Open Hours Model."""

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
    bursa = pd.DataFrame.from_dict(exchange_trading_hours, orient="index")

    if symbol in bursa["short_name"].values:
        return pd.DataFrame(bursa.loc[bursa["short_name"] == symbol]).transpose()
    if symbol in bursa.index:
        return pd.DataFrame(bursa.loc[symbol])
    else:
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
    bursa = pd.DataFrame.from_dict(exchange_trading_hours, orient="index")
    is_open = []
    for exchange in bursa.index:
        open = check_if_open(bursa, exchange)
        is_open.append(open)
    bursa["open"] = is_open
    open = bursa.loc[bursa["open"] == True]
    return open[["name", "short_name"]]


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
    bursa = pd.DataFrame.from_dict(exchange_trading_hours, orient="index")
    is_open = []
    for exchange in bursa.index:
        open = check_if_open(bursa, exchange)
        is_open.append(open)
    bursa["open"] = is_open
    open = bursa.loc[bursa["open"] == False]
    return open[["name", "short_name"]]


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
    bursa = pd.DataFrame.from_dict(exchange_trading_hours, orient="index")
    is_open = []
    for exchange in bursa.index:
        open = check_if_open(bursa, exchange)
        is_open.append(open)
    bursa["open"] = is_open
    return bursa[["name", "short_name", "open"]]


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
    tz = bursa.loc[exchange]["timezone"]
    utcmoment_naive = datetime.utcnow()
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
    localDatetime = utcmoment.astimezone(pytz.timezone(tz))
    if (
        (
            localDatetime.hour > bursa.loc[exchange]["market_open"].hour
            and localDatetime.hour < bursa.loc[exchange]["market_close"].hour
        )
        or (
            localDatetime.hour > bursa.loc[exchange]["market_open"].hour
            and localDatetime.hour == bursa.loc[exchange]["market_close"].hour
            and localDatetime.minute < bursa.loc[exchange]["market_close"].minute
        )
        or (
            localDatetime.hour == bursa.loc[exchange]["market_open"].hour
            and localDatetime.minute >= bursa.loc[exchange]["market_open"].minute
        )
    ):
        if (
            bursa.loc[exchange]["lunchbreak_start"] is not None
            and bursa.loc[exchange]["lunchbreak_end"] is not None
        ):
            if (
                (
                    localDatetime.hour > bursa.loc[exchange]["lunchbreak_start"].hour
                    and localDatetime.hour < bursa.loc[exchange]["lunchbreak_end"].hour
                )
                or (
                    localDatetime.hour > bursa.loc[exchange]["lunchbreak_start"].hour
                    and localDatetime.hour == bursa.loc[exchange]["lunchbreak_end"].hour
                    and localDatetime.minute
                    < bursa.loc[exchange]["lunchbreak_end"].minute
                )
                or (
                    localDatetime.hour == bursa.loc[exchange]["lunchbreak_start"].hour
                    and localDatetime.minute
                    >= bursa.loc[exchange]["lunchbreak_start"].minute
                )
            ):
                return False
        return True
    else:
        return False
