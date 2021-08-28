"""Binance view"""
__docformat__ = "numpy"

import argparse

import os
from typing import List, Tuple, Union
from binance.client import Client
from tabulate import tabulate
import numpy as np
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    export_data,
)
from gamestonk_terminal.cryptocurrency.due_diligence.binance_model import (
    check_valid_binance_str,
    show_available_pairs_for_given_symbol,
    plot_candles,
    plot_order_book,
)
import gamestonk_terminal.config_terminal as cfg


def display_order_book(coin: str, limit: int, currency: str, export: str) -> None:
    """Get order book for currency. [Source: Binance]

    Parameters
    ----------

    coin: str
        Cryptocurrency
    limit: int
        Limit parameter. Adjusts the weight
    currency: str
        Quote currency (what to view coin vs)
    export: str
        Export dataframe data to csv,json,xlsx


    """

    pair = coin + currency

    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
    market_book = client.get_order_book(symbol=pair, limit=limit)
    bids = np.asarray(market_book["bids"], dtype=float)
    asks = np.asarray(market_book["asks"], dtype=float)
    bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
    asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
    plot_order_book(bids, asks, coin)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        pd.DataFrame(market_book),
    )


def display_balance(coin: str, currency: str, export: str) -> None:
    """Get account holdings for asset. [Source: Binance]

    Parameters
    ----------
    coin: str
        Cryptocurrency
    currency: str
        Quote currency (what to view coin vs)
    export: str
        Export dataframe data to csv,json,xlsx

    """

    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)

    pair = coin + currency
    current_balance = client.get_asset_balance(asset=pair)
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
    print(
        tabulate(df, headers=df.columns, showindex=True, tablefmt="fancy_grid"),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        df,
    )


def load(other_args: List[str]) -> Union[str, None]:
    """Define current_coin from binance. [Source: Binance]

    Parameters
    ----------
    other_args : List[str]
        Argparse arguments

    Returns
    -------
    str
        Coin that is defined on binance

    """
    parser = argparse.ArgumentParser(
        prog="load",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Define the coin to be used from binance and get data",
    )
    parser.add_argument(
        "-c", "--coin", help="Coin to get", dest="coin", type=str, default="BTC"
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return None

        parsed_coin = ns_parser.coin.upper()

        coin, pairs = show_available_pairs_for_given_symbol(parsed_coin)
        if len(pairs) > 0:
            print(f"Coin found : {coin}\n")
            return coin

        print(f"Couldn't find coin with symbol {coin}\n")
        return None

    except Exception as e:
        print(e, "\n")
        return None


def display_chart(coin: str, other_args: List[str]) -> Tuple[str, str, pd.DataFrame]:
    """Define current_coin from binance. [Source: Binance]

    Parameters
    ----------
    coin: str
        Coin that is defined on binance
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

    _, quotes = show_available_pairs_for_given_symbol(coin)

    parser = argparse.ArgumentParser(
        prog="chart",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Chart",
    )

    parser.add_argument(
        "--vs",
        help="Quote currency (what to view coin vs)",
        dest="vs",
        type=str,
        default="USDT",
        choices=quotes,
    )

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
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return "", "", pd.DataFrame()

        pair = coin + ns_parser.vs

        if check_valid_binance_str(pair):
            print(f"{coin} loaded vs {ns_parser.vs.upper()}")

            candles = client.get_klines(
                symbol=pair,
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

            plot_candles(
                df_coin,
                f"{coin + ns_parser.vs} from {df_coin.index[0].strftime('%Y/%m/%d')} to "
                f"{df_coin.index[-1].strftime('%Y/%m/%d')}",
            )

            return coin.upper(), ns_parser.vs.upper(), df_coin
        return coin.upper(), ns_parser.vs.upper(), pd.DataFrame()

    except Exception as e:
        print(e, "\n")
        return "", "", pd.DataFrame()


def ta(coin: str, other_args: List[str]) -> Tuple[pd.DataFrame, str]:
    """Define current_coin from binance. [Source: Binance]

    Parameters
    ----------
    coin: str
        Coin that is defined on binance
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

    _, quotes = show_available_pairs_for_given_symbol(coin)

    parser = argparse.ArgumentParser(
        prog="ta",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Chart",
    )

    parser.add_argument(
        "--vs",
        help="Quote currency (what to view coin vs)",
        dest="vs",
        type=str,
        default="USDT",
        choices=quotes,
    )

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
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return pd.DataFrame(), ""

        pair = coin + ns_parser.vs

        if check_valid_binance_str(pair):
            print(f"{coin} loaded vs {ns_parser.vs.upper()}")

            candles = client.get_klines(
                symbol=pair,
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

            return df_coin, ns_parser.vs
        return pd.DataFrame(), ns_parser.vs

    except Exception as e:
        print(e, "\n")
        return pd.DataFrame(), ""
