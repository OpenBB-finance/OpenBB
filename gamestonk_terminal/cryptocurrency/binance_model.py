"""Binance model"""
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException
from gamestonk_terminal.main_helper import parse_known_args_and_warn
from gamestonk_terminal.config_terminal import BINANCE_API_KEY, BINANCE_SECRET_KEY
from gamestonk_terminal.cryptocurrency.binance_view import plot_order_book, plot_candles


def check_valid_binance_str(symbol: str):
    """Check if symbol is in defined binance"""
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    try:
        client.get_avg_price(symbol=symbol.upper())
        return symbol.upper()
    except BinanceAPIException:
        raise argparse.ArgumentTypeError(f"{symbol} is not a valid binance symbol")


def add_binance_coin(other_args:List[str]):
    """
    Define current_coin from binance
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    Returns
    -------
    coin: str
        Coin that is defined on binance
    """
    parser = argparse.ArgumentParser(
        prog="add_coin",
        add_help=False,
        description="Define the coin to be used from binance",
    )
    parser.add_argument(
        "-c", "--coin", help="Coin to get", dest="coin", type=str, default="BTC"
    )
    parser.add_argument(
        "-q",
        "--quote",
        help="Quote currency (what to view coin vs)",
        dest="quote",
        type=str,
        default="USDT",
    )
    parser.add_argument(
        "-s",
        "--symbol",
        help="binance symbol (overrides other arguments)",
        dest="symbol",
        default=None,
        type=check_valid_binance_str,
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return None

        if ns_parser.symbol:
            return ns_parser.symbol

        coin = ns_parser.coin + ns_parser.quote
        return check_valid_binance_str(coin)

    except Exception as e:
        print(e)
        print("")
        return None


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
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    try:
        candles = client.get_klines(
            symbol=coin, interval=Client.KLINE_INTERVAL_30MINUTE
        )

        # Response
        # 1499040000000, // Open time
        # "0.01634790", // Open
        # "0.80000000", // High
        # "0.01575800", // Low
        # "0.01577100", // Close
        # "148976.11427815", // Volume
        # 1499644799999, // Close time
        # "2434.19055334", // Quote asset volume
        # 308, // Number of trades
        # "1756.87402397", // Taker buy base asset volume
        # "28.46694368", // Taker buy quote asset volume
        # "17928899.62484339" // Ignore.

        candles_df = pd.DataFrame(candles).astype(float).iloc[:, :7]

        candles_df.columns = [
            "Time0",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Time1",
        ]
        candles_df.index = pd.to_datetime(
            (candles_df["Time0"] + candles_df["Time1"]) / 2, unit="ms"
        )

        plot_candles(candles_df, "")

    except Exception as e:
        print(e)
        print("")


def balance(coin: str, other_args: List[str]):
    """
    Get account holdings for asset
    Parameters
    ----------
    coin: str
        Coin to get holdings of
    other_args : List[str]
        Argparse arguments

    Returns
    -------

    """
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    try:
        client.get_asset_balance(asset=coin)
    except Exception as e:
        print(e)
        print("")
