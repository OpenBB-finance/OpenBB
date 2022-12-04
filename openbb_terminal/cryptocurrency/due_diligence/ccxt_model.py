"""Ccxt model"""
__docformat__ = "numpy"

from typing import Any, Dict, List

import ccxt
import pandas as pd

from openbb_terminal.cryptocurrency.dataframe_helpers import prettify_column_names


def get_exchanges() -> List[str]:
    """Helper method to get all the exchanges supported by ccxt
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------

    Returns
    -------
    List[str]
        list of all the exchanges supported by ccxt
    """
    return ccxt.exchanges


def get_binance_currencies() -> List[str]:
    """Helper method to get all the currenices supported by ccxt
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------

    Returns
    -------
    List[str]
        list of all the currenices supported by ccxt
    """

    # Refactor this eventually to allow for any entered exchange -
    # right now only works on default binace for "ob" and "trades"

    # Commented out for now, since binance started blocking requests
    # exchange = ccxt.binance({"fetchCurrencies": True})
    # exchange.load_markets()
    # currencies = exchange.quoteCurrencies
    # return [c["code"] for c in currencies.values()]
    return [
        "AUD",
        "BIDR",
        "BKRW",
        "BNB",
        "BRL",
        "BTC",
        "BUSD",
        "BVND",
        "DAI",
        "DOGE",
        "DOT",
        "ETH",
        "EUR",
        "GBP",
        "IDRT",
        "NGN",
        "PAX",
        "PLN",
        "RUB",
        "TRX",
        "TRY",
        "TUSD",
        "UAH",
        "USDC",
        "USDP",
        "USDS",
        "USDT",
        "UST",
        "VAI",
        "XRP",
        "ZAR",
    ]


def get_orderbook(exchange: str, symbol: str, to_symbol: str) -> Dict[str, Any]:
    """Returns orderbook for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange : str
        exchange id
    symbol : str
        coin symbol
    to_symbol : str
        currency to compare coin against

    Returns
    -------
    Dict[str, Any]
        With bids and asks
    """
    exchange_class = getattr(ccxt, exchange)
    exchange_cls = exchange_class()
    ob = exchange_cls.fetch_order_book(f"{symbol.upper()}/{to_symbol.upper()}")
    return ob


def get_trades(exchange_id: str, symbol: str, to_symbol: str) -> pd.DataFrame:
    """Returns trades for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange_id : str
        exchange id
    symbol : str
        coin symbol
    to_symbol : str
        currency to compare coin against

    Returns
    -------
    pd.DataFrame
        trades for a coin in a given exchange
    """
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    trades = exchange.fetch_trades(f"{symbol.upper()}/{to_symbol.upper()}")
    df = pd.DataFrame(trades, columns=["datetime", "price", "amount", "cost", "side"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.rename(columns={"datetime": "date"}, inplace=True)
    df.columns = prettify_column_names(df.columns)
    return df
