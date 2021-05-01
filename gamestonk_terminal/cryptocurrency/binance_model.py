"""Binance model"""
__docformat__ = "numpy"

import argparse
from typing import List
import matplotlib.pyplot as plt
import numpy as np
from binance.client import Client
from gamestonk_terminal.main_helper import parse_known_args_and_warn
from gamestonk_terminal.config_terminal import BINANCE_API_KEY, BINANCE_SECRET_KEY
from gamestonk_terminal.cryptocurrency.binance_view import plot_order_book


def order_book(coin: str, other_args: List[str]):
    """
    Get order book for currency
    Parameters
    ----------
    coin: str
        Coin to get order book for
    other_args: List[str]
        Argparse arguments

    Returns
    -------

    """
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    order_book = client.get_order_book(symbol=coin)
    bids = np.asarray(order_book["bids"], dtype=float)
    asks = np.asarray(order_book["asks"], dtype=float)
    bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
    asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
    plot_order_book(bids, asks, coin)


def recent_trades(coin: str, other_args: List[str]):
    """
    Get recent trades for currency
    Parameters
    ----------
    coin: str
        Coin to get recent trades for
    other_args: List[str]
        Argparse arguments

    Returns
    -------

    """

    pass


def candles(coin: str, other_args: List[str]):
    """
    Get klines/candles for coin
    Parameters
    ----------
    coin: str
        Coin to get symbol of
    other_args: List[str]
        Argparse arguments

    Returns
    -------

    """
    pass


def balance(coin: str, other_args: List[str]):
    """
    Get accont holdings for asset
    Parameters
    ----------
    coin: str
        Coin to get holdings of
    other_args : List[str]
        Argparse arguments

    Returns
    -------

    """
    pass
