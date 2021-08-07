"""Stockanalysis.com/etf Model"""
__docformat__ = "numpy"

import argparse
from typing import List
import webbrowser
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)


def get_all_names_symbols() -> (List[str], List[str]):
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


def limit_number_of_holdings(num: str) -> int:
    if int(num) > 200:
        raise argparse.ArgumentTypeError("Asking for too many holdings")
    return int(num)


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

    vars = [0, 2, 4, 6, 8, 10, 12, 18, 20, 22, 26, 28, 30, 32]
    vals = [idx + 1 for idx in vars]
    columns = [texts[idx] for idx in vars]
    data = [texts[idx] for idx in vals]
    df = pd.DataFrame(data, index=columns, columns=[etf_symbol.upper()])
    return df


def etf_holdings(other_args: List[str]):
    """Look at ETF holdings

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="holdings",
        description="Look at ETF holdings",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        dest="name",
        help="ETF to get holdings for",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=limit_number_of_holdings,
        dest="limit",
        help="Number of holdings to get",
        default=20,
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        r1 = requests.get(f"https://stockanalysis.com/etf/{ns_parser.name}/holdings")
        s1 = (
            bs(r1.text, "html.parser")
            .find("table", {"class": "fullholdings"})
            .find("tbody")
        )
        tick, percent, shares = [], [], []
        for idx, entry in enumerate(s1.findAll("tr"), 1):
            tick.append(entry.findAll("td")[1].text)
            percent.append(entry.findAll("td")[3].text)
            shares.append(entry.findAll("td")[4].text)
            if idx >= ns_parser.limit:
                break

        df = pd.DataFrame(data=[tick, percent, shares]).T
        print(
            tabulate(
                df, headers=["Ticker", "% of ETF", "Shares"], tablefmt="fancy_grid"
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


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
