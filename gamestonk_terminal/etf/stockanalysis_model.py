"""Stockanalysis.com/etf Model"""
__docformat__ = "numpy"

import argparse
from typing import List
import webbrowser
import requests
from bs4 import BeautifulSoup as bs
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


def open_web():
    """Opens webbrowser to the website page"""
    webbrowser.open("https://stockanalysis.com/etf/")


def name_search(other_args: List[str]):
    """

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
