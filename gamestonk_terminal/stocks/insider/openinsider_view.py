import os
import textwrap
import itertools
from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style
from gamestonk_terminal.helper_funcs import (
    patch_pandas_text_adjustment,
    export_data,
)
from gamestonk_terminal.stocks.insider.openinsider_model import (
    get_open_insider_link,
    get_open_insider_data,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console

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


def print_insider_data(type_insider: str, limit: int = 10, export: str = ""):
    """Print insider data

    Parameters
    ----------
    type_insider: str
        Insider type of data
    limit: int
        Limit of data rows to display
    export: str
        Export data format
    """
    response = requests.get(f"http://openinsider.com/{d_open_insider[type_insider]}")
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "tinytable"})

    if not table:
        console.print("No insider information found", "\n")
        return

    table_rows = table.find_all("tr")

    res = []
    for tr in table_rows:
        td = tr.find_all("td")
        row = [tr.text.strip() for tr in td if tr.text.strip()]
        res.append(row)

    df = pd.DataFrame(res).dropna().head(n=limit)

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
            lambda x: "\n".join(textwrap.wrap(x, width=20)) if isinstance(x, str) else x
        )
    else:
        df["Insider Name"] = df["Insider Name"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=20)) if isinstance(x, str) else x
        )

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                tablefmt="fancy_grid",
                stralign="right",
                showindex=False,
            )
        )
    else:
        console.print(df.to_string())

    export_data(export, os.path.dirname(os.path.abspath(__file__)), type_insider, df)

    l_chars = [list(chars) for chars in df["X"].values]
    l_uchars = np.unique(list(itertools.chain(*l_chars)))

    for char in l_uchars:
        console.print(d_notes[char])
    console.print("")


def print_insider_filter(
    preset_loaded: str,
    ticker: str,
    limit: int = 10,
    links: bool = False,
    export: str = "",
):
    """Print insider filter based on loaded preset. [Source: OpenInsider]

    Parameters
    ----------
    preset_loaded : str
        Loaded preset filter
    ticker : str
        Stock ticker
    limit : int
        Limit of rows of data to display
    links : bool
        Flag to show hyperlinks
    export : str
        Format to export data
    """
    if ticker:
        link = f"http://openinsider.com/screener?s={ticker}"
    else:
        link = get_open_insider_link(preset_loaded)

    if not link:
        console.print("")
        return

    df_insider = get_open_insider_data(link, has_company_name=bool(not ticker))
    df_insider_orig = df_insider.copy()

    if df_insider.empty:
        console.print("No insider data found\n")
        return

    if links:
        df_insider = df_insider[["Ticker Link", "Insider Link", "Filing Link"]].head(
            limit
        )
    else:
        df_insider = df_insider.drop(
            columns=["Filing Link", "Ticker Link", "Insider Link"]
        ).head(limit)

    if gtff.USE_COLOR and not links:
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

    console.print("")
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_insider,
                headers=df_insider.columns,
                tablefmt="fancy_grid",
            )
        )
    else:
        console.print(df_insider.to_string(index=False))

    if export:
        if preset_loaded:
            cmd = "filter"
        if ticker:
            cmd = "lis"

        export_data(export, os.path.dirname(os.path.abspath(__file__)), cmd, df_insider)

    if not links:
        l_chars = [list(chars) for chars in df_insider_orig["X"].values]
        l_uchars = np.unique(list(itertools.chain(*l_chars)))
        console.print("")
        for char in l_uchars:
            console.print(d_notes[char])

        l_tradetype = df_insider_orig["Trade Type"].values
        l_utradetype = np.unique(l_tradetype)
        console.print("")
        for tradetype in l_utradetype:
            console.print(d_trade_types[tradetype])

    console.print("")
