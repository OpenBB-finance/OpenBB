"""Binance model"""
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException
from tabulate import tabulate
from gamestonk_terminal.main_helper import parse_known_args_and_warn
from gamestonk_terminal.config_terminal import API_BINANCE_KEY, API_BINANCE_SECRET
from gamestonk_terminal.cryptocurrency.binance_view import plot_order_book, plot_candles


def check_valid_binance_str(symbol: str) -> str:
    """Check if symbol is in defined binance"""
    client = Client(API_BINANCE_KEY, API_BINANCE_SECRET)
    try:
        client.get_avg_price(symbol=symbol.upper())
        return symbol.upper()
    except BinanceAPIException as e:
        raise argparse.ArgumentTypeError(
            f"{symbol} is not a valid binance symbol"
        ) from e


# pylint: disable=inconsistent-return-statements
def select_binance_coin(other_args: List[str]):
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
        prog="select",
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
    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return None, None

        coin = ns_parser.coin + ns_parser.quote
        if check_valid_binance_str(coin):
            print(f"{ns_parser.coin.upper()} loaded vs {ns_parser.quote.upper()}")
            return ns_parser.coin.upper(), ns_parser.quote.upper()

    except Exception as e:
        print(e, "\n")
        return None, None


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
    limit_list = [5, 10, 20, 50, 100, 500, 1000, 5000]
    parser = argparse.ArgumentParser(
        prog="book", add_help=False, description="Get the order book for selected coin"
    )
    parser.add_argument(
        "-l",
        "--limit",
        dest="limit",
        help="Limit parameter.  Adjusts the weight",
        default=100,
        type=int,
        choices=limit_list,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        client = Client(API_BINANCE_KEY, API_BINANCE_SECRET)
        market_book = client.get_order_book(symbol=coin, limit=ns_parser.limit)
        bids = np.asarray(market_book["bids"], dtype=float)
        asks = np.asarray(market_book["asks"], dtype=float)
        bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
        asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
        plot_order_book(bids, asks, coin)

    except Exception as e:
        print(e, "\n")


def show_candles(coin: str, other_args: List[str]):
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
    client = Client(API_BINANCE_KEY, API_BINANCE_SECRET)

    interval_map = {
        "1day": client.KLINE_INTERVAL_1DAY,
        "3day": client.KLINE_INTERVAL_3DAY,
        "1hour": client.KLINE_INTERVAL_1HOUR,
        "2hour": client.KLINE_INTERVAL_2HOUR,
        "4hour": client.KLINE_INTERVAL_4HOUR,
        "6hour": client.KLINE_INTERVAL_6HOUR,
        "8hour": client.KLINE_INTERVAL_8HOUR,
        "12hour": client.KLINE_INTERVAL_12HOUR,
        "1week": client.KLINE_INTERVAL_1WEEK,
        "1min": client.KLINE_INTERVAL_1MINUTE,
        "3min": client.KLINE_INTERVAL_3MINUTE,
        "5min": client.KLINE_INTERVAL_5MINUTE,
        "15min": client.KLINE_INTERVAL_15MINUTE,
        "30min": client.KLINE_INTERVAL_30MINUTE,
        "1month": client.KLINE_INTERVAL_1MONTH,
    }
    interval_choices = list(interval_map.keys())

    parser = argparse.ArgumentParser(
        prog="candle",
        add_help=False,
        description="Program to plot candles for binance data",
    )
    parser.add_argument(
        "-i",
        "--interval",
        help="Interval to get data",
        choices=interval_choices,
        dest="interval",
        default="1day",
        type=str,
    )

    parser.add_argument(
        "-l", "--limit", dest="limit", default=100, help="Number to get", type=int
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        candles = client.get_klines(
            symbol=coin,
            interval=interval_map[ns_parser.interval],
            limit=ns_parser.limit,
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

        plot_candles(
            candles_df,
            f"{coin} from {candles_df.index[0].strftime('%Y/%m/%d')} to "
            f"{candles_df.index[-1].strftime('%Y/%m/%d')}",
        )

    except Exception as e:
        print(e, "\n")


def balance(coin: str):
    """
    Get account holdings for asset

    Parameters
    ----------
    coin: str
        Coin to get holdings of

    Returns
    -------

    """
    client = Client(API_BINANCE_KEY, API_BINANCE_SECRET)
    try:
        current_balance = client.get_asset_balance(asset=coin)
        if current_balance is None:
            print("Check loaded coin")
            return
        print("")
        amounts = [float(current_balance["free"]), float(current_balance["locked"])]
        total = np.sum(amounts)
        df = pd.DataFrame(amounts)
        df.columns = ["Amount"]
        df.index = ["Free", "Locked"]
        df["Percent"] = df.div(df.sum(axis=0), axis=1).round(3)
        print(f"You currently have {total} coins and the breakdown is:")
        print(tabulate(df, headers=df.columns, showindex=True, tablefmt="fancy_grid"))
        print("")
        return
    except Exception as e:
        print(e, "\n")
        return
