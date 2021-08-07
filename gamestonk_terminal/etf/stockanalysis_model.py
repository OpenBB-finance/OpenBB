"""Stockanalysis.com/etf Model"""
__docformat__ = "numpy"

from typing import List, Tuple
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs


def get_all_names_symbols() -> Tuple[List[str], List[str]]:
    """Gets all etf names and symbols

    Returns
    -------
    etf_symbols: List[str]:
        List of all available etf symbols
    etf_names: List[str]
        List of all available etf names
    """

    etf_symbols = []
    etf_names = []
    data = requests.get(
        "https://stockanalysis.com/_next/data/VDLj2l5sT7aRmdOwKVFT4/etf.json"
    ).json()
    for entry in data["pageProps"]["stocks"]:
        etf_symbols.append(entry["s"])
        etf_names.append(entry["n"])
    return etf_symbols, etf_names


def get_etf_overview(etf_symbol: str):
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
    r = requests.get(f"https://stockanalysis.com/etf/{etf_symbol}")
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


def get_etf_holdings(symbol: str):
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

    data = requests.get(
        f"https://stockanalysis.com/_next/data/VDLj2l5sT7aRmdOwKVFT4/etf/{symbol}/holdings.json"
    ).json()
    tickers = []
    assets = []
    shares = []
    for entry in data["pageProps"]["data"]["list"]:
        tickers.append(entry["symbol"].strip("$"))
        assets.append(entry["assets"])
        shares.append(entry["shares"])

    df = pd.DataFrame(data=[tickers, assets, shares]).T
    df.columns = ["Ticker", "% Holdings", "Shares"]
    return df


def compare_etfs(symbols: List[str]):
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
