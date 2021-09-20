"""Ally Model"""
__docformat__ = "numpy"

import ally
import pandas as pd


def get_holdings() -> pd.DataFrame:
    """Get holdings from Ally account in pandas df

    Returns
    -------
    pd.DataFrame
        Dataframe of positions
    """
    a = ally.Ally()
    return ally_positions_to_df(a.holdings(dataframe=True))


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


def get_history() -> pd.DataFrame:
    """Gets transaction history for the account."

    Returns
    -------
    pd.DataFrame
        Dataframe of transaction history
    """
    a = ally.Ally()
    return a.history(dataframe=True)


def get_balances() -> pd.DataFrame:
    """Gets balance details for the account."

    Returns
    -------
    pd.DataFrame
        Dataframe of transaction history
    """
    a = ally.Ally()
    return a.balances(dataframe=True)
