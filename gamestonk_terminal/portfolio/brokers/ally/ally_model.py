"""Ally Model"""
__docformat__ = "numpy"

import logging

import ally
import pandas as pd

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_holdings() -> pd.DataFrame:
    """Get holdings from Ally account in pandas df

    Returns
    -------
    pd.DataFrame
        Dataframe of positions
    """
    a = ally.Ally()
    return ally_positions_to_df(a.holdings(dataframe=True))


@log_start_end(log=logger)
def ally_positions_to_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean up ally holdings dataframe

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe of holdings

    Returns
    -------
    pd.DataFrame
        Processed holdings
    """
    names = {
        "costbasis": "CostBasis",
        "marketvalue": "MarketValue",
        "sym": "Symbol",
        "qty": "Quantity",
    }
    df = df.loc[:, ["qty", "costbasis", "marketvalue", "sym"]]
    df[["qty", "costbasis", "marketvalue"]] = df[
        ["qty", "costbasis", "marketvalue"]
    ].astype(float)
    df = df.rename(columns=names)
    df["PnL"] = df["MarketValue"] - df["CostBasis"]
    return df


@log_start_end(log=logger)
def get_history() -> pd.DataFrame:
    """Gets transaction history for the account."

    Returns
    -------
    pd.DataFrame
        Dataframe of transaction history
    """
    a = ally.Ally()
    return a.history(dataframe=True)


@log_start_end(log=logger)
def get_balances() -> pd.DataFrame:
    """Gets balance details for the account."

    Returns
    -------
    pd.DataFrame
        Dataframe of transaction history
    """
    a = ally.Ally()
    return a.balances(dataframe=True)


@log_start_end(log=logger)
def get_stock_quote(ticker: str) -> pd.DataFrame:
    """Gets quote for stock ticker

    Parameters
    ----------
    ticker : str
        Ticker to get.  Can be in form of 'tick1,tick2...'
    Returns
    -------
    pd.DataFrame
        Dataframe of ticker quote
    """
    a = ally.Ally()
    return a.quote(
        ticker,
        fields=["last", "bid", "ask", "opn", "dollar_value", "chg", "vl"],
        dataframe=True,
    )


@log_start_end(log=logger)
def get_top_movers(list_type: str, exchange: str) -> pd.DataFrame:
    """
    Gets top lists from ally Invest API.  Documentation for parameters below:
    https://www.ally.com/api/invest/documentation/market-toplists-get/

    Parameters
    ----------
    list_type : str
        Which list to get data for
    exchange : str
        Which exchange to look at

    Returns
    -------
    pd.DataFrame
        DataFrame of top movers
    """
    a = ally.Ally()
    return a.toplists(list_type, exchange, dataframe=True)
