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

# Run this when called to get all available etfs and names
r = requests.get("https://stockanalysis.com/etf/")
soup = bs(r.text, "html.parser").findAll("ul", {"class": "no-spacing"})
all_links = soup[0].findAll("li")
etf_symbols = []
etf_names = []
for link in all_links:
    etf_symbols.append(link.text.split("-")[0].strip(" "))
    etf_names.append(link.text.split("-")[1].strip(" "))


def limit_number_of_holdings(num: int) -> int:
    if num > 200:
        raise argparse.ArgumentTypeError("Asking for too many holdings")
    return num


def open_web():
    """Opens webbrowser to the website page"""
    webbrowser.open("https://stockanalysis.com/etf/")


def name_search(other_args: List[str]):
    """
    Search all available etfs for matching input
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    """

    parser = argparse.ArgumentParser(prog="search", add_help=False)
    parser.add_argument(
        "-n", "--name", type=str, dest="name", help="Name to search for", required=True
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return ""

        matching_etfs = [
            etf_symbols[idx] + " - " + etf
            for idx, etf in enumerate(etf_names)
            if ns_parser.name.lower() in etf.lower()
        ]
        print(*matching_etfs, sep="\n")
        print("")
        return ""

    except SystemExit:
        print("")
        return ""

    except Exception as e:
        print(e, "\n")
        return ""


def etf_overview(other_args: List[str]):
    """
    Get overview data for selected etf
    Parameters
    ----------
    other_args : List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(prog="overview", add_help=False)
    parser.add_argument(
        "-n", "--name", type=str, dest="name", help="Symbol to look for", required=True
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return ""

        if ns_parser.name not in etf_symbols:
            print("ETF symbol not available")
            return ""
        r1 = requests.get(f"https://stockanalysis.com/etf/{ns_parser.name}")
        soup1 = bs(r1.text, "html.parser").find("div", {"class": "info"}).findAll("td")
        column = []
        value = []
        column.append("Last Price")
        value.append(
            bs(r1.text, "html.parser")
            .find("div", {"class": "quote"})
            .find("td", {"id": "qLast"})
            .text
        )
        for row in soup1[:-4:2]:
            column.append(row.text)
        for row in soup1[1:-4:2]:
            value.append(row.text)
        df = pd.DataFrame(value, index=column, columns=[ns_parser.name.upper()])
        print(tabulate(df, headers=df.columns, tablefmt="fancy_grid"))
        return ""
    except Exception as e:
        print(e, "\n")
        return ""


def etf_holdings(other_args: List[str]):
    """
    Look at ETF holdings
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(prog="holdings", add_help=False)
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
            return ""
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
        return ""

    except Exception as e:
        print(e, "\n")
        return ""


def compare_etfs(other_args: List[str]):
    """
    Compare selected ETFs
    Parameters
    ----------
    other_args : List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(prog="compare", add_help=False)
    parser.add_argument(
        "-n",
        "--names",
        type=str,
        dest="names",
        help="Symbols to compare",
        required=True,
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return ""
        to_compare = [name.upper() for name in ns_parser.names.split(",")]
        df = pd.DataFrame(columns=to_compare)
        for etf in to_compare:
            if etf in etf_symbols:
                r1 = requests.get(f"https://stockanalysis.com/etf/{etf}")
                soup1 = (
                    bs(r1.text, "html.parser")
                    .find("div", {"class": "info"})
                    .findAll("td")
                )
                column = []
                value = []
                column.append("Last Price")
                value.append(
                    bs(r1.text, "html.parser")
                    .find("div", {"class": "quote"})
                    .find("td", {"id": "qLast"})
                    .text
                )
                for row in soup1[:-4:2]:
                    column.append(row.text)
                for row in soup1[1:-4:2]:
                    value.append(row.text)
                df[etf] = value
            else:
                print(f"{etf} not found")
        df.index = column
        print(tabulate(df, headers=df.columns, tablefmt="fancy_grid"))
        return ""
    except Exception as e:
        print(e, "\n")
        return ""
