"""Ccxt model"""
__docformat__ = "numpy"

import ccxt
import pandas as pd


def get_exchanges():
    return ccxt.exchanges


def get_orderbook(exchange_id: str, coin: str, vs: str):
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    ob = exchange.fetch_order_book(f"{coin.upper()}/{vs.upper()}")
    return ob


def get_trades(exchange_id: str, coin: str, vs: str):
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    trades = exchange.fetch_trades(f"{coin.upper()}/{vs.upper()}")
    df = pd.DataFrame(trades, columns=["datetime", "price", "amount", "cost", "side"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df
