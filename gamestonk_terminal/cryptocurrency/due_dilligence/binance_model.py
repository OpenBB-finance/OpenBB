"""Binance model"""
__docformat__ = "numpy"

import argparse

from typing import Tuple, Union
from collections import defaultdict
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.feature_flags import USE_ION as ion


def _get_all_binance_pairs() -> list:
    """Helper methods that returns all available pairs on Binance in format
    ["EOSETH", "ETHBTC", ....]

    Returns
    -------
    list:
        ["EOSETH", "ETHBTC", ....]

    """
    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
    pairs = client.get_all_tickers()
    symbols = [p["symbol"] for p in pairs]
    return symbols


def _get_binance_available_pairs() -> dict:
    """Helper methods that for every coin available on Binance add all quote assets.

    Returns
    -------
    dict:
        {'ETH' : ['BTC', 'USDT' ...], 'UNI' : ['ETH', 'BTC','BUSD', ...]

    """
    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
    ex_info = client.get_exchange_info()["symbols"]
    trading_pairs = [p for p in ex_info if p["status"] == "TRADING"]

    results = defaultdict(list)
    for pair in trading_pairs:
        results[pair["baseAsset"]].append(pair["quoteAsset"])
    return results


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


def show_available_pairs_for_given_symbol(
    symbol: str = "ETH",
) -> Tuple[Union[str, None], list]:
    """Return all available quoted assets for given symbol.

    Parameters
    ----------
    symbol:
        Uppercase symbol of coin e.g BTC, ETH, UNI, LUNA, DOT ...

    Returns
    -------
    str:
        Coin symbol
    list:
        Quoted assets for given symbol: ["BTC", "USDT" , "BUSD"]
    """

    symbol_upper = symbol.upper()
    pairs = _get_binance_available_pairs()
    for k, v in pairs.items():
        if k == symbol_upper:
            return k, v
    print(f"Couldn't find anything for symbol {symbol_upper}")
    return None, []


def plot_order_book(bids: np.array, asks: np.array, coin: str):
    """
    Plots Bid/Ask
    Parameters
    ----------
    bids : np.array
        array of bids with columns: price, size, cumulative size
    asks : np.array
        array of asks with columns: price, size, cumulative size
    coin : str
        Coin being plotted

    Returns
    -------

    """
    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(bids[:, 0], bids[:, 2], "g", label="bids")
    ax.fill_between(bids[:, 0], bids[:, 2], color="g", alpha=0.4)
    ax.plot(asks[:, 0], asks[:, 2], "r", label="asks")
    ax.fill_between(asks[:, 0], asks[:, 2], color="r", alpha=0.4)
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    plt.legend(loc=0)
    plt.xlabel("Price")
    plt.ylabel("Size (Coins) ")
    plt.title(f"Order Book for {coin}")
    if ion:
        plt.ion()
    plt.show()
    print("")


def plot_candles(candles_df: pd.DataFrame, title: str):
    """
    Plot candle chart from dataframe
    Parameters
    ----------
    candles_df: pd.DataFrame
        Dataframe containing time and OHLVC
    title: str
        title of graph

    Returns
    -------

    """
    mpf.plot(
        candles_df,
        type="candle",
        volume=True,
        title=f"\n{title}",
        xrotation=20,
        style="binance",
        figratio=(10, 7),
        figscale=1.10,
        figsize=(plot_autoscale()),
        update_width_config=dict(
            candle_linewidth=1.0, candle_width=0.8, volume_linewidth=1.0
        ),
    )
    if ion:
        plt.ion()
    plt.show()
    print("")
