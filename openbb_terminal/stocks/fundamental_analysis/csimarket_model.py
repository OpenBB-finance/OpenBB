"""CSIMarket Model"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


def clean_table(df: pd.DataFrame) -> pd.DataFrame:
    """Clean up the table from CSIMarket

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe to clean

    Returns
    -------
    df: pd.DataFrame
        Cleaned dataframe
    """
    if df.empty:
        return df
    if "TICKER" in df.columns:
        df = df.set_index("TICKER")
    df.columns = [x.title() for x in df.columns]
    if "Company Name.1" in df.columns:
        df = df.drop("Company Name.1", axis=1)
    if "SUBTOTAL" in df.index:
        df = df.drop("SUBTOTAL", axis=0)
    if "Revenue" in df.columns:
        df = df.sort_values("Revenue", ascending=False)
    df = df[df.index.notnull()]
    return df


@log_start_end(log=logger)
def get_suppliers(symbol: str) -> pd.DataFrame:
    """Get suppliers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    symbol: str
        Ticker to select suppliers from

    Returns
    -------
    pd.DataFrame
        A dataframe of suppliers
    """
    url = f"https://csimarket.com/stocks/competition2.php?supply&code={symbol.upper()}"
    dfs = pd.read_html(url, header=0)
    df = dfs[10]
    df = clean_table(df)
    return df


@log_start_end(log=logger)
def get_customers(symbol: str) -> pd.DataFrame:
    """Print customers from ticker provided

    Parameters
    ----------
    symbol: str
        Ticker to select customers from

    Returns
    -------
    pd.DataFrame
        A dataframe of suppliers
    """
    url = f"https://csimarket.com/stocks/custexNO.php?markets&code={symbol.upper()}"
    dfs = pd.read_html(url, header=0)
    df = dfs[9]
    df = clean_table(df)

    return df
