"""Ccxt model"""
__docformat__ = "numpy"

import ccxt


def get_exchanges():
    return ccxt.exchanges


def get_orderbook(exchange_id: str):
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    ob = exchange.fetch_order_book("BTC/USDT")
    return ob

