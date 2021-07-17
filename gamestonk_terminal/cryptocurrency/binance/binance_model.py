"""Binance model"""
__docformat__ = "numpy"

import argparse

from typing import List, Tuple
import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import check_positive
from gamestonk_terminal.main_helper import parse_known_args_and_warn
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.cryptocurrency.binance.binance_view import (
    plot_order_book,
    plot_candles,
)


def check_valid_binance_str(symbol: str) -> str:
    """Check if symbol is in defined binance"""
    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
    try:
        client.get_avg_price(symbol=symbol.upper())
        return symbol.upper()
    except BinanceAPIException as e:
        raise argparse.ArgumentTypeError(
            f"{symbol} is not a valid binance symbol"
        ) from e


def select_binance_coin(other_args: List[str]) -> Tuple[str, str, pd.DataFrame]:
    """Define current_coin from binance

    Parameters
    ----------
    other_args : List[str]
        Argparse arguments

    Returns
    -------
    str
        Coin that is defined on binance
    str
        Base pair of coin
    pd.DataFrame
        Dataframe of prices for selected coin
    """
    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
    parser = argparse.ArgumentParser(
        prog="load",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Define the coin to be used from binance and get data",
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
    parser.add_argument(
        "-i",
        "--interval",
        help="Interval to get data",
        choices=list(interval_map.keys()),
        dest="interval",
        default="1day",
        type=str,
    )
    parser.add_argument(
        "-l",
        "--limit",
        dest="limit",
        default=100,
        help="Number to get",
        type=check_positive,
    )
    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return "", "", pd.DataFrame()

        coin = ns_parser.coin + ns_parser.quote

        if check_valid_binance_str(coin):
            print(f"{ns_parser.coin.upper()} loaded vs {ns_parser.quote.upper()}")

            candles = client.get_klines(
                symbol=coin.upper(),
                interval=interval_map[ns_parser.interval],
                limit=ns_parser.limit,
            )
            candles_df = pd.DataFrame(candles).astype(float).iloc[:, :6]

            candles_df.columns = [
                "Time0",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
            df_coin = candles_df.set_index(
                pd.to_datetime(candles_df["Time0"], unit="ms")
            ).drop("Time0", axis=1)

            return ns_parser.coin.upper(), ns_parser.quote.upper(), df_coin
        return "", "", pd.DataFrame

    except Exception as e:
        print(e, "\n")
        return "", "", pd.DataFrame


def order_book(other_args: List[str], coin: str, currency: str):
    """Get order book for currency

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    coin: str
        Coin to get symbol of
    currency : str
        Currency against which to check symbol
    """
    limit_list = [5, 10, 20, 50, 100, 500, 1000, 5000]
    parser = argparse.ArgumentParser(
        prog="book",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Get the order book for selected coin",
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
        if not coin or not currency:
            print("Coin needs to be selected prior to this command\n")
            return

        coin += currency

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
        market_book = client.get_order_book(symbol=coin, limit=ns_parser.limit)
        bids = np.asarray(market_book["bids"], dtype=float)
        asks = np.asarray(market_book["asks"], dtype=float)
        bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
        asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
        plot_order_book(bids, asks, coin)

    except Exception as e:
        print(e, "\n")


def show_candles(candles_df: pd.DataFrame, coin: str, currency: str):
    """Show candles

    Parameters
    ----------
    candles_df: pd.DataFrame
        Dataframe of prices
    coin: str
        Coin loaded
    currency : str
        Currency loaded
    """
    plot_candles(
        candles_df,
        f"{coin+currency} from {candles_df.index[0].strftime('%Y/%m/%d')} to "
        f"{candles_df.index[-1].strftime('%Y/%m/%d')}",
    )


def balance(coin: str):
    """Get account holdings for asset

    Parameters
    ----------
    coin: str
        Coin to get holdings of
    """
    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
    try:
        current_balance = client.get_asset_balance(asset=coin)
        if current_balance is None:
            print("Check loaded coin")
            return

        print("")
        amounts = [float(current_balance["free"]), float(current_balance["locked"])]
        total = np.sum(amounts)
        df = pd.DataFrame(amounts).apply(lambda x: str(float(x)))
        df.columns = ["Amount"]
        df.index = ["Free", "Locked"]
        df["Percent"] = df.div(df.sum(axis=0), axis=1).round(3)
        print(f"You currently have {total} coins and the breakdown is:")
        print(tabulate(df, headers=df.columns, showindex=True, tablefmt="fancy_grid"))
        print("")

    except Exception as e:
        print(e, "\n")
