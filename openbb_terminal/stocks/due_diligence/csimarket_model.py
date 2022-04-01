"""CSIMarket Model"""
__docformat__ = "numpy"

import logging

import requests
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_suppliers(ticker: str) -> str:
    """Get suppliers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    ticker: str
        Ticker to select suppliers from

    Returns
    -------
    str
        Suppliers for ticker provided
    """
    # TODO: This link has a lot more data that we can display
    # TODO: We could at least sort the tickers based on market cap
    url_supply_chain = (
        f"https://csimarket.com/stocks/competitionNO3.php?supply&code={ticker.upper()}"
    )
    text_supplier_chain = BeautifulSoup(requests.get(url_supply_chain).text, "lxml")

    l_supplier = list()
    for supplier in text_supplier_chain.findAll(
        "td", {"class": "svjetlirub11 block al"}
    ):
        l_supplier.append(supplier.text.replace("\n", "").strip())

    if l_supplier:
        return f"List of Suppliers: {', '.join(l_supplier)}\n"
    return "No suppliers found.\n"


@log_start_end(log=logger)
def get_customers(ticker: str) -> str:
    """Print customers from ticker provided

    Parameters
    ----------
    ticker: str
        Ticker to select customers from

    Returns
    -------
    str
        Customers for ticker provided
    """
    # TODO: This link has a lot more data that we can display
    # TODO: We could at least sort the tickers based on market cap
    url_customer_chain = (
        f"https://csimarket.com/stocks/custexNO.php?markets&code={ticker.upper()}"
    )
    text_customer_chain = BeautifulSoup(requests.get(url_customer_chain).text, "lxml")

    l_customer = list()
    for customer in text_customer_chain.findAll("td", {"class": "plava svjetlirub"}):
        l_customer.append(customer.text)

    if l_customer:
        return f"List of Customers: {', '.join(l_customer)}\n"
    return "No customers found.\n"
