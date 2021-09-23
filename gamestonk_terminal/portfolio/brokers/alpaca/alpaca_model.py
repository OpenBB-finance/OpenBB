"""Alpaca Model"""
__docformat__ = "numpy"

from typing import List
import alpaca_trade_api as alp_api
import pandas as pd


def get_holdings() -> pd.DataFrame:
    """Get holdings from alpaca api

    Returns
    -------
    pd.DataFrame
        Dataframe of positions
    """
    api = alp_api.REST()
    positions = api.list_positions()
    return positions_to_df(positions)


def get_account_history(period: str = "1M", timeframe: str = "1D") -> pd.DataFrame:
    """Get historcial account value from alpaca api

    Parameters
    ----------
    period : str, optional
        Lookback period, by default "1M"
    timeframe : str, optional
        Time resolution, by default "1D"

    Returns
    -------
    pd.DataFrame
        Dataframe containing historical account value
    """
    api = alp_api.REST()
    return api.get_portfolio_history(period=period, timeframe=timeframe).df


def positions_to_df(positions: List[alp_api.entity.Asset]) -> pd.DataFrame:
    """Generate a df from alpaca api assests

    Parameters
    ----------
    positions : List[alp_api.entity.Asset]
        List of alpaca trade assets

    Returns
    -------
    pd.DataFrame
        Processed dataframe
    """

    df = pd.DataFrame(columns=["Symbol", "MarketValue", "Quantity", "CostBasis"])
    sym = []
    mv = []
    qty = []
    cb = []

    for pos in positions:
        sym.append(pos.symbol)
        mv.append(float(pos.market_value))
        qty.append(float(pos.qty))
        cb.append(float(pos.cost_basis))

    df["Symbol"] = sym
    df["MarketValue"] = mv
    df["Quantity"] = qty
    df["CostBasis"] = cb
    df["Broker"] = "alp"

    return df
