import argparse
import textwrap
from typing import List
import itertools
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    patch_pandas_text_adjustment,
)
from gamestonk_terminal.insider.openinsider_model import (
    get_open_insider_link,
    get_open_insider_data,
)
from gamestonk_terminal import feature_flags as gtff

d_open_insider = {
    "lcb": "latest-cluster-buys",
    "lpsb": "latest-penny-stock-buys",
    "lit": "latest-insider-trading",
    "lip": "insider-purchases",
    "blip": "latest-insider-purchases-25k",
    "blop": "latest-officer-purchases-25k",
    "blcp": "latest-ceo-cfo-purchases-25k",
    "lis": "insider-sales",
    "blis": "latest-insider-sales-100k",
    "blos": "latest-officer-sales-100k",
    "blcs": "latest-ceo-cfo-sales-100k",
    "topt": "top-officer-purchases-of-the-day",
    "toppw": "top-officer-purchases-of-the-week",
    "toppm": "top-officer-purchases-of-the-month",
    "tipt": "top-insider-purchases-of-the-day",
    "tippw": "top-insider-purchases-of-the-week",
    "tippm": "top-insider-purchases-of-the-month",
    "tist": "top-insider-sales-of-the-day",
    "tispw": "top-insider-sales-of-the-week",
    "tispm": "top-insider-sales-of-the-month",
}

d_notes = {
    "A": "A: Amended filing",
    "D": "D: Derivative transaction in filing (usually option exercise)",
    "E": "E: Error detected in filing",
    "M": "M: Multiple transactions in filing; earliest reported transaction date and weighted average transaction price",
}

d_trade_types = {
    "S - Sale": f"{Fore.RED}S - Sale: Sale of securities on an exchange or to another person{Style.RESET_ALL}",
    "S - Sale+OE": f"{Fore.YELLOW}S - Sale+OE: Sale of securities "
    f"on an exchange or to another person (after option exercise){Style.RESET_ALL}",
    "F - Tax": f"{Fore.MAGENTA}F - Tax: Payment of exercise price or "
    f"tax liability using portion of securities received from the company{Style.RESET_ALL}",
    "P - Purchase": f"{Fore.GREEN}P - Purchase: Purchase of securities on "
    f"an exchange or from another person{Style.RESET_ALL}",
}


def red_highlight(values):
    """Red highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    ----------
    List[str]
        colored dataframes values
    """
    return [f"{Fore.RED}{val}{Style.RESET_ALL}" for val in values]


def yellow_highlight(values):
    """Yellow highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    ----------
    List[str]
        colored dataframes values
    """
    return [f"{Fore.YELLOW}{val}{Style.RESET_ALL}" for val in values]


def magenta_highlight(values):
    """Magenta highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    ----------
    List[str]
        colored dataframes values
    """
    return [f"{Fore.MAGENTA}{val}{Style.RESET_ALL}" for val in values]


def green_highlight(values):
    """Green highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    ----------
    List[str]
        colored dataframes values
    """
    return [f"{Fore.GREEN}{val}{Style.RESET_ALL}" for val in values]


def print_insider_data(other_args: List[str], type_insider: str):
    """Print insider data

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    type_insider: str
        Insider type of data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=type_insider,
        description=f"Print {d_open_insider[type_insider].replace('-', ' ')} [Source: OpenInsider]",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="num",
        type=check_positive,
        default=20,
        help="Number of datarows to display",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        response = requests.get(
            f"http://openinsider.com/{d_open_insider[type_insider]}"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "tinytable"})

        if not table:
            print("No insider information found", "\n")
            return

        table_rows = table.find_all("tr")

        res = []
        for tr in table_rows:
            td = tr.find_all("td")
            row = [tr.text.strip() for tr in td if tr.text.strip()]
            res.append(row)

        df = pd.DataFrame(res).dropna().head(n=ns_parser.num)

        df.columns = [
            "X",
            "Filing Date",
            "Trade Date",
            "Ticker",
            "Company Name",
            "Industry" if type_insider == "lcb" else "Insider Name",
            "Title",
            "Trade Type",
            "Price",
            "Qty",
            "Owned",
            "Diff Own",
            "Value",
        ]

        df["Filing Date"] = df["Filing Date"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=10)) if isinstance(x, str) else x
        )
        df["Company Name"] = df["Company Name"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=20)) if isinstance(x, str) else x
        )
        df["Title"] = df["Title"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=10)) if isinstance(x, str) else x
        )
        if type_insider == "lcb":
            df["Industry"] = df["Industry"].apply(
                lambda x: "\n".join(textwrap.wrap(x, width=20))
                if isinstance(x, str)
                else x
            )
        else:
            df["Insider Name"] = df["Insider Name"].apply(
                lambda x: "\n".join(textwrap.wrap(x, width=20))
                if isinstance(x, str)
                else x
            )

        print(
            tabulate(
                df,
                headers=df.columns,
                tablefmt="fancy_grid",
                stralign="right",
                showindex=False,
            )
        )
        l_chars = [list(chars) for chars in df["X"].values]
        l_uchars = np.unique(list(itertools.chain(*l_chars)))

        for char in l_uchars:
            print(d_notes[char])
        print("")

    except Exception as e:
        print(e, "\n")


def print_insider_filter(other_args: List[str], preset_loaded: str):
    """Print insider filter based on loaded preset

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    preset_loaded: str
        Loaded preset filter
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="filter",
        description="Print open insider filtered data using loaded preset, or selected ticker. [Source: OpenInsider]",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="num",
        type=check_positive,
        default=20,
        help="Number of datarows to display",
    )
    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="ticker",
        type=str,
        default="",
        help="Filter latest insiders from this ticker",
    )
    parser.add_argument(
        "-l",
        "--links",
        action="store_true",
        default=False,
        help="Flag to show hyperlinks",
        dest="links",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.ticker:
            link = f"http://openinsider.com/screener?s={ns_parser.ticker}"
        else:
            link = get_open_insider_link(preset_loaded)

        if not link:
            print("")
            return

        df_insider = get_open_insider_data(
            link, has_company_name=bool(not ns_parser.ticker)
        )
        df_insider_orig = df_insider.copy()

        if df_insider.empty:
            print("")
            return

        if ns_parser.links:
            df_insider = df_insider[
                ["Ticker Link", "Insider Link", "Filing Link"]
            ].head(ns_parser.num)
        else:
            df_insider = df_insider.drop(
                columns=["Filing Link", "Ticker Link", "Insider Link"]
            ).head(ns_parser.num)

        if gtff.USE_COLOR and not ns_parser.links:
            if not df_insider[df_insider["Trade Type"] == "S - Sale"].empty:
                df_insider[df_insider["Trade Type"] == "S - Sale"] = df_insider[
                    df_insider["Trade Type"] == "S - Sale"
                ].apply(red_highlight)
            if not df_insider[df_insider["Trade Type"] == "S - Sale+OE"].empty:
                df_insider[df_insider["Trade Type"] == "S - Sale+OE"] = df_insider[
                    df_insider["Trade Type"] == "S - Sale+OE"
                ].apply(yellow_highlight)
            if not df_insider[df_insider["Trade Type"] == "F - Tax"].empty:
                df_insider[df_insider["Trade Type"] == "F - Tax"] = df_insider[
                    df_insider["Trade Type"] == "F - Tax"
                ].apply(magenta_highlight)
            if not df_insider[df_insider["Trade Type"] == "P - Purchase"].empty:
                df_insider[df_insider["Trade Type"] == "P - Purchase"] = df_insider[
                    df_insider["Trade Type"] == "P - Purchase"
                ].apply(green_highlight)

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", 0)
            pd.set_option("display.max_rows", None)

            # needs to be done because table is too large :(
            df_insider = df_insider.drop(columns=["Filing Date", "Trade Type"])

        else:
            # needs to be done because table is too large :(
            df_insider = df_insider.drop(columns=["Filing Date"])

        print("")
        print(df_insider.to_string(index=False))

        if not ns_parser.links:
            l_chars = [list(chars) for chars in df_insider_orig["X"].values]
            l_uchars = np.unique(list(itertools.chain(*l_chars)))
            print("")
            for char in l_uchars:
                print(d_notes[char])

            l_tradetype = df_insider_orig["Trade Type"].values
            l_utradetype = np.unique(l_tradetype)
            print("")
            for tradetype in l_utradetype:
                print(d_trade_types[tradetype])

        print("")

    except Exception as e:
        print(e, "\n")
