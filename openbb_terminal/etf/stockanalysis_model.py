"""Stockanalysis.com/etf Model"""
__docformat__ = "numpy"

import logging
import pathlib
from typing import List, Tuple

import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)

csv_path = pathlib.Path(__file__).parent / "etfs.csv"


@log_start_end(log=logger)
def get_all_names_symbols() -> Tuple[List[str], List[str]]:
    """Gets all etf names and symbols

    Returns
    -------
    Tuple[List[str], List[str]]
        List of all available etf symbols, List of all available etf names
    """

    etf_symbols = []
    etf_names = []

    # 11/25 I am hard coding the etf lists because of stockanalysis changing the format of their website
    data = pd.read_csv(csv_path)
    etf_symbols = data.s.to_list()
    etf_names = data.n.to_list()
    return etf_symbols, etf_names


@log_start_end(log=logger)
def get_etf_overview(symbol: str) -> pd.DataFrame:
    """Get overview data for selected etf

    Parameters
    ----------
    etf_symbol : str
        Etf symbol to get overview for

    Returns
    -------
    df : pd.DataFrame
        Dataframe of stock overview data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.etf.overview("SPY")
    """
    r = request(
        f"https://stockanalysis.com/etf/{symbol}",
        headers={"User-Agent": get_user_agent()},
    )
    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.findAll("table")
    texts = []
    for tab in tables[:2]:
        entries = tab.findAll("td")
        for ent in entries:
            texts.append(ent.get_text())

    var_cols = [0, 2, 4, 6, 8, 10, 12, 18, 20, 22, 26, 28, 30, 32]
    vals = [idx + 1 for idx in var_cols]
    columns = [texts[idx] for idx in var_cols]
    data = [texts[idx] for idx in vals]
    df = pd.DataFrame(data, index=columns, columns=[symbol.upper()])
    return df


@log_start_end(log=logger)
def get_etf_holdings(symbol: str) -> pd.DataFrame:
    """Get ETF holdings

    Parameters
    ----------
    symbol: str
        Symbol to get holdings for

    Returns
    -------
    df: pd.DataFrame
        Dataframe of holdings

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.etf.holdings("SPY")
    """

    link = f"https://stockanalysis.com/etf/{symbol}/holdings/"
    r = request(link, headers={"User-Agent": get_user_agent()})
    try:
        df = pd.read_html(r.content)[0]
        df["Symbol"] = df["Symbol"].fillna("N/A")
        df = df.set_index("Symbol")
        df = df[["Name", "% Weight", "Shares"]]
        df = df.rename(columns={"% Weight": "% Of Etf"})
    except ValueError:
        df = pd.DataFrame()
    return df


@log_start_end(log=logger)
def compare_etfs(symbols: List[str]) -> pd.DataFrame:
    """Compare selected ETFs

    Parameters
    ----------
    symbols : List[str]
        ETF symbols to compare

    Returns
    -------
    df_compare : pd.DataFrame
        Dataframe of etf comparisons

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> compare_etfs = openbb.etf.compare(["SPY", "QQQ", "IWM"])
    """

    df_compare = pd.DataFrame()
    for symbol in symbols:
        df_compare = pd.concat([df_compare, get_etf_overview(symbol)], axis=1)

    return df_compare


@log_start_end(log=logger)
def get_etfs_by_name(name_to_search: str) -> pd.DataFrame:
    """Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]

    Parameters
    ----------
    name_to_search: str
        ETF name to match

    Returns
    -------
    df: pd.Dataframe
        Dataframe with symbols and names
    """
    all_symbols, all_names = get_all_names_symbols()

    filtered_symbols = list()
    filtered_names = list()
    for symbol, name in zip(all_symbols, all_names):
        if name_to_search.lower() in name.lower():
            filtered_symbols.append(symbol)
            filtered_names.append(name)

    df = pd.DataFrame(
        list(zip(filtered_symbols, filtered_names)), columns=["Symbol", "Name"]
    )

    return df
