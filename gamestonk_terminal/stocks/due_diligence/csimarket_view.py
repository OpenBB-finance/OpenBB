"""Stockgrid DD View"""
__docformat__ = "numpy"

import argparse
from typing import List
from bs4 import BeautifulSoup
import requests
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)


def suppliers(ticker: str, other_args: List[str]):
    """Print suppliers from ticker provided

    Parameters
    ----------
    ticker: str
        Ticker to select suppliers from
    other_args : List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(
        prog="supplier",
        add_help=False,
        description="List of suppliers from ticker provided. [Source: CSIMarket]",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        url_supply_chain = f"https://csimarket.com/stocks/competitionNO3.php?supply&code={ticker.upper()}"
        text_supplier_chain = BeautifulSoup(requests.get(url_supply_chain).text, "lxml")

        l_supplier = list()
        for supplier in text_supplier_chain.findAll(
            "td", {"class": "plavat svjetlirub dae al"}
        ):
            l_supplier.append(supplier.text)

        if l_supplier:
            print("List of Suppliers: " + ", ".join(l_supplier) + "\n")
        else:
            print("No suppliers found.\n")

    except Exception as e:
        print(e, "\n")


def customers(ticker: str, other_args: List[str]):
    """Print customers from ticker provided

    Parameters
    ----------
    ticker: str
        Ticker to select customers from
    other_args : List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(
        prog="customer",
        add_help=False,
        description="List of customers from ticker provided. [Source: CSIMarket]",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        url_customer_chain = (
            f"https://csimarket.com/stocks/custexNO.php?markets&code={ticker.upper()}"
        )
        text_customer_chain = BeautifulSoup(
            requests.get(url_customer_chain).text, "lxml"
        )

        l_customer = list()
        for customer in text_customer_chain.findAll(
            "td", {"class": "plava svjetlirub"}
        ):
            l_customer.append(customer.text)

        if l_customer:
            print("List of Customers: " + ", ".join(l_customer) + "\n")
        else:
            print("No customers found.\n")

    except Exception as e:
        print(e, "\n")
