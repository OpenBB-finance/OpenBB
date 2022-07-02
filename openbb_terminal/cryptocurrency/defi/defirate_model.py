"""DeFi Rate model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def _scrape_defirate(url: str, current: bool = True) -> Tag:
    """Helper method that scrapes table object from defirate.com
    [Source: https://defirate.com/]

    Parameters
    ----------
    url: str
        Defirate url
    current: bool
        Flag that indicates if you want to scrape current data or last 30 days average.

    Returns
    -------
    bs4.element.Tag
        Table with scraped data
    """

    current_or_average_map = {
        True: "table-container",
        False: "table-container table-hidden",
    }

    div_class = current_or_average_map[current]
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="lxml")
    table = soup.find("div", class_=div_class).find("table")
    return table


@log_start_end(log=logger)
def get_funding_rates(current: bool = True) -> pd.DataFrame:
    """Funding rates are transfer payments made between long and short positions on perpetual swap futures markets.
    They’re designed to keep contract prices consistent with the underlying asset.
    [Source: https://defirate.com/]

    Parameters
    ----------
    current: bool
        If true displays current funding rate values. If false displays last 30 day average of funding rates.

    -------
    pd.DataFrame
        Dataframe with funding rates.
    """

    url = "https://defirate.com/funding/"
    table = _scrape_defirate(url, current)
    items = []
    first_row = table.find("thead").text.strip().split()
    headers = [r for r in first_row if r != "Trade"]
    headers.insert(0, "Symbol")
    for i in table.find_all("td"):
        items.append(i.text.strip())
    fundings = [items[i : i + 5] for i in range(0, len(items), 5)]  # noqa: E203
    return pd.DataFrame(columns=headers, data=fundings)


@log_start_end(log=logger)
def get_lending_rates(current: bool = True) -> pd.DataFrame:
    """Decentralized Finance lending – or DeFi lending for short – allows users to supply cryptocurrencies
    in exchange for earning an annualized return.
    [Source: https://defirate.com]

    Parameters
    ----------
    current: bool
        If true displays current lending rates values. If false displays last 30 day average of lending rates.

    Returns
    -------
    pd.DataFrame
        Dataframe with lending rates.
    """

    url = "https://defirate.com/loans/?exchange_table_type=lend"
    table = _scrape_defirate(url, current)
    items = []
    first_row = table.find("thead").text.strip().split()

    headers = [r for r in first_row if r not in ["Lend", ""]]
    headers.insert(0, "Symbol")
    for i in table.find_all("td"):
        items.append(i.text.strip())
    lendings = [items[i : i + 12] for i in range(0, len(items), 12)]  # noqa: E203
    return pd.DataFrame(columns=headers, data=lendings)


@log_start_end(log=logger)
def get_borrow_rates(current: bool = True) -> pd.DataFrame:
    """One aspect of Decentralized Finance (DeFi) is the ability to take out a loan on top cryptocurrencies at any time
    in an entirely permissionless fashion.By using smart contracts, borrowers are able to lock collateral to protect
    against defaults while seamlesslyadding to or closing their loans at any time.
    [Source: https://defirate.com]

    Parameters
    ----------
    current: bool
        If true displays current borrow rates values. If false displays last 30 day average of borrow rates.

    Returns
    -------
    pd.DataFrame
        Dataframe with borrow rates
    """

    url = "https://defirate.com/loans/?exchange_table_type=borrow"
    table = _scrape_defirate(url, current)
    items = []
    first_row = (
        table.find("thead").text.strip().replace("Compound v2", "Compound_v2").split()
    )

    headers = [r for r in first_row if r not in ["Borrow", ""]]
    headers.insert(0, "Symbol")
    for i in table.find_all("td"):
        items.append(i.text.strip())
    borrowings = [items[i : i + 8] for i in range(0, len(items), 8)]  # noqa: E203
    return pd.DataFrame(columns=headers, data=borrowings)
