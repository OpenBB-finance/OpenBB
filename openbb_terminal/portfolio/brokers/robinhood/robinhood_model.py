"""Robinhood Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from robin_stocks import robinhood

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

dt_format = "%Y-%m-%dT%H:%M:%SZ"


@log_start_end(log=logger)
def login():
    """Robinhood login"""
    current_user = get_current_user()
    robinhood.login(
        current_user.credentials.RH_USERNAME, current_user.credentials.RH_PASSWORD
    )
    console.print("")


@log_start_end(log=logger)
def logoff():
    """Robinhood logoff"""
    robinhood.logout()


@log_start_end(log=logger)
def get_holdings() -> pd.DataFrame:
    """Return Robinhood holdings

    Returns
    -------
    pd.DataFrame
        Robinhood holdings
    """
    holds = robinhood.account.build_holdings()
    return rh_positions_to_df(holds)


@log_start_end(log=logger)
def rh_positions_to_df(holds: dict) -> pd.DataFrame:
    """Process robinhood holdings to dataframe

    Parameters
    ----------
    holds : dict
        Dictionary from robin_stocks

    Returns
    -------
    pd.DataFrame
        Processed dataframe of holdings
    """
    df = pd.DataFrame(columns=["Symbol", "MarketValue", "Quantity", "CostBasis"])
    sym = []
    mv = []
    qty = []
    cb = []
    for stonk, data in holds.items():
        sym.append(stonk)
        qty.append(float(data["quantity"]))
        mv.append(float(data["equity"]))
        cb.append(float(data["quantity"]) * float(data["average_buy_price"]))
    df["Symbol"] = sym
    df["MarketValue"] = mv
    df["Quantity"] = qty
    df["CostBasis"] = cb
    return df


@log_start_end(log=logger)
def get_historical(interval: str = "day", window: str = "3month") -> pd.DataFrame:
    """Get historical portfolio in candle form

    Parameters
    ----------
    interval : str, optional
        Interval for robinhood (candle width), by default "day"
    window : str, optional
        Lookback to get portfolio history, by default "3month"

    Returns
    -------
    pd.DataFrame
        Historical portfolio with OHLC variables
    """
    rhhist = robinhood.account.get_historical_portfolio(interval, window)
    rhhist_eq = rhhist["equity_historicals"]
    open_eq = []
    close_eq = []
    time = []

    for h in rhhist_eq:
        time.append(datetime.strptime(h["begins_at"], dt_format) - timedelta(hours=4))
        close_eq.append(float(h["adjusted_close_equity"]))
        open_eq.append(float(h["adjusted_open_equity"]))

    close_eq_array = np.asarray(close_eq)
    open_eq_array = np.asarray(open_eq)
    high = np.maximum(open_eq_array, close_eq_array)
    low = np.minimum(open_eq_array, close_eq_array)

    df = pd.DataFrame(index=time)
    df["High"] = high
    df["Low"] = low
    df["Open"] = open_eq_array
    df["Close"] = close_eq_array

    return df
