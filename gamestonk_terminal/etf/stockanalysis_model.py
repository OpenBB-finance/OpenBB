"""Stockanalysis.com/etf Model"""
__docformat__ = "numpy"

from typing import List, Tuple
import json

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from gamestonk_terminal.helper_funcs import get_user_agent


def get_all_names_symbols() -> Tuple[List[str], List[str]]:
    """Gets all etf names and symbols

    Returns
    -------
    etf_symbols: List[str]:
        List of all available etf symbols
    etf_names: List[str]
        List of all available etf names
    """
    r = requests.get(
        "https://stockanalysis.com/etf/", headers={"User-Agent": get_user_agent()}
    )
    soup2 = bs(r.text, "html.parser")
    script = soup2.find("script", {"id": "__NEXT_DATA__"})
    etfs = pd.DataFrame(json.loads(script.text)["props"]["pageProps"]["stocks"])
    etf_symbols = etfs.s.to_list()
    etf_names = etfs.n.to_list()
    return etf_symbols, etf_names


def get_etf_overview(etf_symbol: str) -> pd.DataFrame:
    """Get overview data for selected etf

    Parameters
    ----------
    etf_symbol : str
        Etf symbol to get overview for

    Returns
    ----------
    df : pd.DataFrame
        Dataframe of stock overview data
    """
    r = requests.get(
        f"https://stockanalysis.com/etf/{etf_symbol}",
        headers={"User-Agent": get_user_agent()},
    )
    soup = bs(r.text, "html.parser")  # %%
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
    df = pd.DataFrame(data, index=columns, columns=[etf_symbol.upper()])
    return df


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
    """

    link = f"https://stockanalysis.com/etf/{symbol}/holdings/"
    r = requests.get(link, headers={"User-Agent": get_user_agent()})
    soup = bs(r.text, "html.parser")
    soup = soup.find("table")
    tds = soup.findAll("td")
    tickers = []
    for i in tds[1::5]:
        tickers.append(i.text)
    percents = []
    for i in tds[3::5]:
        percents.append(i.text)
    shares = []
    for i in tds[4::5]:
        shares.append(i.text)
    df = pd.DataFrame(index=tickers)
    df["% Of Etf"] = percents
    df["Shares"] = shares
    return df


def compare_etfs(symbols: List[str]) -> pd.DataFrame:
    """Compare selected ETFs

    Parameters
    ----------
    symbols : List[str]
        ETF symbols to compare

    Returns
    ----------
    df_compare : pd.DataFrame
        Dataframe of etf comparisons
    """

    df_compare = pd.DataFrame()
    for symbol in symbols:
        df_compare = pd.concat([df_compare, get_etf_overview(symbol)], axis=1)

    return df_compare


def search_etfs(to_search) -> List[str]:
    """Search for an etf string in list of ETFs

    Parameters
    ----------
    to_search: str
        String to match

    Returns
    -------
    matching_etfs: List[str]
        List of matching ETF names
    """
    all_symbols, all_names = get_all_names_symbols()
    matching_etfs = [
        all_symbols[idx] + " - " + etf
        for idx, etf in enumerate(all_names)
        if to_search.lower() in etf.lower()
    ]
    return matching_etfs
