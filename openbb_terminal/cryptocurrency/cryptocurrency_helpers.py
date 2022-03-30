"""Cryptocurrency helpers"""
__docformat__ = "numpy"
# pylint: disable=C0301,R0911,C0302

import os
import json
from datetime import datetime, timedelta
from typing import Tuple, Any, Optional, List
import difflib
import logging

import pandas as pd
import numpy as np
from binance.client import Client
import matplotlib.pyplot as plt
import yfinance as yf
import mplfinance as mpf
from pycoingecko import CoinGeckoAPI

from openbb_terminal.helper_funcs import (
    plot_autoscale,
    export_data,
    print_rich_table,
)
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.cryptocurrency.due_diligence import (
    pycoingecko_model,
    coinpaprika_model,
)
from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import get_coin_list
from openbb_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_list_of_coins,
)
from openbb_terminal.cryptocurrency.due_diligence.binance_model import (
    check_valid_binance_str,
    show_available_pairs_for_given_symbol,
)

from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.due_diligence import coinbase_model
import openbb_terminal.config_terminal as cfg
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

INTERVALS = ["1H", "3H", "6H", "1D"]

SOURCES_INTERVALS = {
    "bin": [
        "1day",
        "3day",
        "1hour",
        "2hour",
        "4hour",
        "6hour",
        "8hour",
        "12hour",
        "1week",
        "1min",
        "3min",
        "5min",
        "15min",
        "30min",
        "1month",
    ],
    "cb": [
        "1min",
        "5min",
        "15min",
        "1hour",
        "6hour",
        "24hour",
        "1day",
    ],
    "yf": [
        "1min",
        "2min",
        "5min",
        "15min",
        "30min",
        "60min",
        "90min",
        "1hour",
        "1day",
        "5day",
        "1week",
        "1month",
        "3month",
    ],
}


YF_CURRENCY = [
    "CAD",
    "CNY",
    "ETH",
    "EUR",
    "GBP",
    "INR",
    "JPY",
    "KRW",
    "RUB",
    "USD",
    "AUD",
    "BTC",
]


def load_cg_coin_data(
    coin: str, currency: str = "USD", days: int = 365, sampling: str = "1D"
) -> pd.DataFrame:
    """Load cryptocurrency data from CoinGecko
    Timestamps from CoinGecko are not uniform, so the sampling is included to provide ohlc bars.
    Note that for days > 90, daily data is returned as prices only.  Less than 90 days returns hourly data
    which can be consolidated into OHLC

    Parameters
    ----------
    coin : str
        Cryptocurrency to load
    currency : str, optional
        Conversion unit, by default "USD"
    days : int, optional
        Number of days to get, by default 365
    sampling : str, optional
        Time period to resample in the format in the format #U where U can be H (hour) or D(day), by default "1D"

    Returns
    -------
    pd.DataFrame
        DataFrame of OHLC
    """
    prices = CoinGeckoAPI().get_coin_market_chart_by_id(coin, currency, days)
    df = pd.DataFrame(data=prices["prices"], columns=["time", "price"])
    df["time"] = pd.to_datetime(df.time, unit="ms")
    df = df.set_index("time")
    if days > 90:
        sampling = "1D"
    df = df.resample(sampling).ohlc()
    df.columns = ["Open", "High", "Low", "Close"]
    return df


def _load_coin_map(file_name: str) -> pd.DataFrame:
    if file_name.split(".")[1] != "json":
        raise TypeError("Please load json file")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "data", file_name)
    with open(path, encoding="utf8") as f:
        coins = json.load(f)

    coins_df = pd.Series(coins).reset_index()
    coins_df.columns = ["symbol", "id"]
    return coins_df


def read_data_file(file_name: str):
    if file_name.split(".")[1] != "json":
        raise TypeError("Please load json file")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "data", file_name)
    with open(path, encoding="utf8") as f:
        return json.load(f)


def load_coins_list(file_name: str, return_raw: bool = False) -> pd.DataFrame:
    if file_name.split(".")[1] != "json":
        raise TypeError("Please load json file")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "data", file_name)
    with open(path, encoding="utf8") as f:
        coins = json.load(f)
    if return_raw:
        return coins
    return pd.DataFrame(coins)


def load_binance_map():
    return _load_coin_map("binance_gecko_map.json")


def load_coinbase_map():
    return _load_coin_map("coinbase_gecko_map.json")


def prepare_all_coins_df() -> pd.DataFrame:
    """Helper method which loads coins from all sources: CoinGecko, CoinPaprika,
    Binance, Yahoo Finance and merge those coins on keys:

        CoinGecko - > name < - CoinPaprika
        CoinGecko - > id <- Binance

    Returns
    -------
    pd.DataFrame
        CoinGecko - id for coin in CoinGecko API: uniswap
        CoinPaprika - id for coin in CoinPaprika API: uni-uniswap
        Binance - symbol (baseAsset) for coin in Binance API: UNI
        Coinbase - symbol for coin in Coinbase Pro API e.g UNI
        Yahoo Finance - symbol for coin in Yahoo Finance e.g. UNI1-USD

        Symbol: uni
    """

    gecko_coins_df = load_coins_list("coingecko_coins.json")

    paprika_coins_df = load_coins_list("coinpaprika_coins.json")
    paprika_coins_df = paprika_coins_df[paprika_coins_df["is_active"]]
    paprika_coins_df = paprika_coins_df[["rank", "id", "name", "symbol", "type"]]
    yahoofinance_coins_df = load_coins_list("yahoofinance_coins.json")

    # TODO: Think about scheduled job, that once a day will update data

    binance_coins_df = load_binance_map().rename(columns={"symbol": "Binance"})
    coinbase_coins_df = load_coinbase_map().rename(columns={"symbol": "Coinbase"})
    gecko_paprika_coins_df = pd.merge(
        gecko_coins_df, paprika_coins_df, on="name", how="left"
    )
    df_merged = pd.merge(
        left=gecko_paprika_coins_df,
        right=binance_coins_df,
        left_on="id_x",
        right_on="id",
        how="left",
    )
    df_merged.rename(
        columns={
            "id_x": "CoinGecko",
            "symbol_x": "Symbol",
            "id_y": "CoinPaprika",
        },
        inplace=True,
    )

    df_merged = pd.merge(
        left=df_merged,
        right=coinbase_coins_df,
        left_on="CoinGecko",
        right_on="id",
        how="left",
    )

    yahoofinance_coins_df.rename(
        columns={
            "symbol": "Symbol",
        },
        inplace=True,
    )

    df_merged = pd.merge(
        left=df_merged,
        right=yahoofinance_coins_df[["Symbol", "id"]],
        on="Symbol",
        how="left",
    )

    df_merged.rename(
        columns={
            "id": "YahooFinance",
        },
        inplace=True,
    )

    return df_merged[
        ["CoinGecko", "CoinPaprika", "Binance", "Coinbase", "YahooFinance", "Symbol"]
    ]


def _create_closest_match_df(
    coin: str, coins: pd.DataFrame, limit: int, cutoff: float
) -> pd.DataFrame:
    """Helper method. Creates a DataFrame with best matches for given coin found in given list of coins.
    Based on difflib.get_close_matches func.

    Parameters
    ----------
    coin: str
        coin you search for
    coins: list
        list of coins in which you want to find similarities
    limit: int
        limit of matches
    cutoff: float
        float between <0, 1>. Show only coins matches with score higher then cutoff.

    Returns
    -------
    pd.DataFrame
        index, id, name, symbol - > depends on source of data.
    """

    coins_list = coins["id"].to_list()
    sim = difflib.get_close_matches(coin, coins_list, limit, cutoff)
    df = pd.Series(sim).to_frame().reset_index()
    df.columns = ["index", "id"]
    return df.merge(coins, on="id")


# pylint: disable=R0912
# TODO: verify vs, interval, days, depending on source
def load(
    coin: str,
    source: str = "cp",
    days: int = 60,
    vs: str = "usd",
    interval: str = "1day",
    should_load_ta_data: bool = False,
):
    """Load cryptocurrency from given source. Available sources are: CoinGecko, CoinPaprika,
    Coinbase, Binance and Yahoo Finance

    Loading coin from Binance and CoinPaprika means validation if given coins exists in chosen source,
    if yes then id of the coin is returned as a string.
    In case of CoinGecko load will return Coin object, if provided coin exists. Coin object has access to different coin
    information.

    Parameters
    ----------
    coin: str
        Coin symbol or id which is checked if exists in chosen data source.
    source : str
        Source of the loaded data. CoinGecko, CoinPaprika, Yahoo Finance or Binance

    Returns
    -------
    Tuple[Union[str, pycoingecko_model.Coin], str, str]
        - str or Coin object for provided coin
        - str with source of the loaded data. CoinGecko, CoinPaprika, Yahoo Finance or Binance
        - str with symbol
        - Dataframe with coin map to different sources
    """
    if source in ("cg", "cp"):
        if vs not in ("USD", "BTC", "usd", "btc"):
            console.print("You can only compare with usd or btc (e.g., --vs usd)\n")
            return None, None, None, None, None, None
        if interval != "1day":
            console.print(
                "Only daily data is supported for coingecko and coinpaprika (e.g., -i 1day)\n"
            )
            return None, None, None, None, None, None

    current_coin = ""  # type: Optional[Any]

    coins_map_df = prepare_all_coins_df().set_index("Symbol").dropna(thresh=2)

    if source == "cg":
        coingecko = pycoingecko_model.Coin(coin.lower(), True)

        if not coingecko.symbol:
            return None, None, None, None, None, None

        coin_map_df = coins_map_df.loc[coingecko.symbol]
        coin_map_df = (
            coin_map_df.iloc[0]
            if isinstance(coin_map_df, pd.DataFrame)
            else coin_map_df
        )  # TODO: improve to choose the row that matches better;
        # if it is dataframe, it means that found more than 1 coin
        if should_load_ta_data:
            df_prices, currency = load_ta_data(
                coin_map_df=coin_map_df,
                source=source,
                currency=vs,
                days=days,
                limit=0,
                interval=interval,
            )
            return (
                str(coingecko),
                source,
                coingecko.symbol,
                coin_map_df,
                df_prices,
                currency,
            )
        return (
            str(coingecko),
            source,
            coingecko.symbol,
            coin_map_df,
            None,
            None,
        )
    if source == "cp":
        paprika_coins = get_list_of_coins()
        paprika_coins_dict = dict(zip(paprika_coins.id, paprika_coins.symbol))
        current_coin, symbol = coinpaprika_model.validate_coin(coin, paprika_coins_dict)

        if not symbol:
            return None, None, None, None, None, None

        coin_map_df = coins_map_df.loc[symbol.lower() if symbol is not None else symbol]
        coin_map_df = (
            coin_map_df.iloc[0]
            if isinstance(coin_map_df, pd.DataFrame)
            else coin_map_df
        )

        if should_load_ta_data:
            df_prices, currency = load_ta_data(
                coin_map_df=coin_map_df,
                source=source,
                currency=vs,
                days=days,
                limit=0,
                interval=interval,
            )

            return (current_coin, source, symbol, coin_map_df, df_prices, currency)
        return (current_coin, source, symbol, coin_map_df, None, None)
    if source == "bin":
        if vs == "usd":
            vs = "USDT"
        if interval not in SOURCES_INTERVALS["bin"]:
            console.print(
                "Interval not available on binance. Run command again with one supported (e.g., -i 1day):\n",
                SOURCES_INTERVALS["bin"],
            )
            return None, None, None, None, None, None

        # TODO: convert bitcoin to btc before searching pairs
        parsed_coin = coin.upper()
        current_coin, pairs = show_available_pairs_for_given_symbol(parsed_coin)
        if len(pairs) > 0:
            if vs not in pairs:
                console.print(
                    "vs specified not supported by binance. Run command again with one supported (e.g., --vs USDT):\n",
                    pairs,
                )
                return None, None, None, None, None, None
            coin_map_df = coins_map_df.loc[parsed_coin.lower()]
            coin_map_df = (
                coin_map_df.iloc[0]
                if isinstance(coin_map_df, pd.DataFrame)
                else coin_map_df
            )
            # console.print(f"Coin found : {current_coin}\n")
            if should_load_ta_data:
                df_prices, currency = load_ta_data(
                    coin_map_df=coin_map_df,
                    source=source,
                    currency=vs,
                    days=0,
                    limit=days,
                    interval=interval,
                )
                return (
                    current_coin,
                    source,
                    parsed_coin,
                    coin_map_df,
                    df_prices,
                    currency,
                )
            return (current_coin, source, parsed_coin, coin_map_df, None, None)
        return None, None, None, None, None, None

    if source == "cb":
        if vs == "usd":
            vs = "USDT"
        if interval not in SOURCES_INTERVALS["cb"]:
            console.print(
                "Interval not available on coinbase. Run command again with one supported (e.g., -i 1day):\n",
                SOURCES_INTERVALS["cb"],
            )
            return None, None, None, None, None, None

        # TODO: convert bitcoin to btc before searching pairs
        coinbase_coin = coin.upper()
        current_coin, pairs = coinbase_model.show_available_pairs_for_given_symbol(
            coinbase_coin
        )
        if vs not in pairs:
            console.print(
                "vs specified not supported by coinbase. Run command again with one supported (e.g., --vs USDT):\n",
                pairs,
            )
            return None, None, None, None, None, None
        if len(pairs) > 0:
            # console.print(f"Coin found : {current_coin}\n")

            coin_map_df = coins_map_df.loc[coin]
            coin_map_df = (
                coin_map_df.iloc[0]
                if isinstance(coin_map_df, pd.DataFrame)
                else coin_map_df
            )
            if should_load_ta_data:
                df_prices, currency = load_ta_data(
                    coin_map_df=coin_map_df,
                    source=source,
                    currency=vs,
                    days=0,
                    limit=days,
                    interval=interval,
                )
                return (current_coin, source, coin, coin_map_df, df_prices, currency)
            return (current_coin, source, coin, coin_map_df, None, None)
        console.print(f"Couldn't find coin with symbol {current_coin}\n")
        return None, None, None, None, None, None

    if source == "yf":

        if vs.upper() not in YF_CURRENCY:
            console.print(
                "vs specified not supported by Yahoo Finance. Run command again with one supported (e.g., --vs USD):\n",
                YF_CURRENCY,
            )
            return None, None, None, None, None, None

        if interval not in SOURCES_INTERVALS["yf"]:
            console.print(
                "Interval not available on YahooFinance. Run command again with one supported (e.g., -i 1day):\n",
                SOURCES_INTERVALS["yf"],
            )
            return None, None, None, None, None, None

        # Search coin using crypto symbol
        coin_map_df_1 = coins_map_df.loc[coins_map_df.index == coin]
        # Search coin using yfinance id
        coin_map_df_2 = coins_map_df.loc[
            coins_map_df.YahooFinance == f"{coin.upper()}-{vs.upper()}"
        ]
        # Search coin using crypto full name
        coin_map_df_3 = coins_map_df.loc[coins_map_df.CoinGecko == coin]

        for _df in [coin_map_df_1, coin_map_df_2, coin_map_df_3]:
            if not _df.empty:
                coin_map_df = _df
                break

        if coin_map_df.empty:
            console.print(
                f"Cannot find {coin} against {vs} on Yahoo finance. Try another source or currency.\n"
            )
            return None, None, None, None, None, None

        if (coin_map_df["YahooFinance"]).isna().all():
            console.print(f"Cannot find {coin} Yahoo finance. Try another source.\n")
            return None, None, None, None, None, None

        # Filter for the currency
        coin_map_df = coin_map_df[
            coin_map_df["YahooFinance"].str.upper().str.contains(vs.upper())
        ]

        coin_map_df = (
            coin_map_df.iloc[0]
            if isinstance(coin_map_df, pd.DataFrame)
            else coin_map_df
        )

        if should_load_ta_data:
            df_prices, currency = load_ta_data(
                coin_map_df=coin_map_df,
                source=source,
                currency=vs,
                days=days,
                limit=0,
                interval=interval,
            )

            return (
                coin_map_df["YahooFinance"],
                source,
                coin,
                coin_map_df,
                df_prices,
                currency,
            )

        return (
            coin_map_df["YahooFinance"],
            source,
            coin,
            coin_map_df,
            None,
            None,
        )

    return None, None, None, None, None, None


FIND_KEYS = ["id", "symbol", "name"]

# TODO: Find better algorithm then difflib.get_close_matches to find most similar coins


def find(source: str, coin: str, key: str, top: int, export: str) -> None:
    """Find similar coin by coin name,symbol or id.

    If you don't remember exact name or id of the Coin at CoinGecko CoinPaprika, Binance or Coinbase
    you can use this command to display coins with similar name, symbol or id to your search query.
    Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.

        -c, --coin stands for coin - you provide here your search query
        -k, --key it's a searching key. You can search by symbol, id or name of coin
        -t, --top it displays top N number of records.

    Parameters
    ----------
    top: int
        Number of records to display
    coin: str
        Cryptocurrency
    key: str
        Searching key (symbol, id, name)
    source: str
        Data source of coins.  CoinGecko (cg) or CoinPaprika (cp) or Binance (bin), Coinbase (cb)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    if source == "cg":
        coins_df = get_coin_list()
        coins_list = coins_df[key].to_list()
        if key in ["symbol", "id"]:
            coin = coin.lower()
        sim = difflib.get_close_matches(coin, coins_list, top)
        df = pd.Series(sim).to_frame().reset_index()
        df.columns = ["index", key]
        coins_df.drop("index", axis=1, inplace=True)
        df = df.merge(coins_df, on=key)

    elif source == "cp":
        coins_df = get_list_of_coins()
        coins_list = coins_df[key].to_list()
        keys = {"name": "title", "symbol": "upper", "id": "lower"}

        func_key = keys[key]
        coin = getattr(coin, str(func_key))()

        sim = difflib.get_close_matches(coin, coins_list, top)
        df = pd.Series(sim).to_frame().reset_index()
        df.columns = ["index", key]
        df = df.merge(coins_df, on=key)

    elif source == "bin":

        # TODO: Fix it in future. Determine if user looks for symbol like ETH or ethereum
        if len(coin) > 5:
            key = "id"

        coins_df_gecko = get_coin_list()
        coins_df_bin = load_binance_map()
        coins = pd.merge(
            coins_df_bin, coins_df_gecko[["id", "name"]], how="left", on="id"
        )
        coins_list = coins[key].to_list()

        sim = difflib.get_close_matches(coin, coins_list, top)
        df = pd.Series(sim).to_frame().reset_index()
        df.columns = ["index", key]
        df = df.merge(coins, on=key)

    elif source == "cb":
        if len(coin) > 5:
            key = "id"

        coins_df_gecko = get_coin_list()
        coins_df_bin = load_coinbase_map()
        coins = pd.merge(
            coins_df_bin, coins_df_gecko[["id", "name"]], how="left", on="id"
        )
        coins_list = coins[key].to_list()

        sim = difflib.get_close_matches(coin, coins_list, top)
        df = pd.Series(sim).to_frame().reset_index()
        df.columns = ["index", key]
        df = df.merge(coins, on=key)

    else:
        console.print(
            "Couldn't execute find methods for CoinPaprika, Binance, Coinbase or CoinGecko\n"
        )
        df = pd.DataFrame()

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Similar Coins"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "find",
        df,
    )


def display_all_coins(
    source: str, coin: str, top: int, skip: int, show_all: bool, export: str
) -> None:
    """Find similar coin by coin name,symbol or id.

    If you don't remember exact name or id of the Coin at CoinGecko, CoinPaprika, Coinbase, Binance
    you can use this command to display coins with similar name, symbol or id to your search query.
    Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.

        -c, --coin stands for coin - you provide here your search query
        -t, --top it displays top N number of records.

    Parameters
    ----------
    top: int
        Number of records to display
    coin: str
        Cryptocurrency
    source: str
        Data source of coins.  CoinGecko (cg) or CoinPaprika (cp) or Binance (bin), Coinbase (cb)
    skip: int
        Skip N number of records
    show_all: bool
        Flag to show all sources of data
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    sources = ["cg", "cp", "bin", "cb"]
    limit, cutoff = 30, 0.75
    coins_func_map = {
        "cg": get_coin_list,
        "cp": get_list_of_coins,
        "bin": load_binance_map,
        "cb": load_coinbase_map,
    }

    if show_all:
        coins_func = coins_func_map.get(source)
        if coins_func:
            df = coins_func()
        else:
            df = prepare_all_coins_df()

    elif not source or source not in sources:
        df = prepare_all_coins_df()
        cg_coins_list = df["CoinGecko"].to_list()
        sim = difflib.get_close_matches(coin.lower(), cg_coins_list, limit, cutoff)
        df_matched = pd.Series(sim).to_frame().reset_index()
        df_matched.columns = ["index", "CoinGecko"]
        df = df.merge(df_matched, on="CoinGecko")
        df.drop("index", axis=1, inplace=True)

    else:

        if source == "cg":
            coins_df = get_coin_list().drop("index", axis=1)
            df = _create_closest_match_df(coin.lower(), coins_df, limit, cutoff)
            df = df[["index", "id", "name"]]

        elif source == "cp":
            coins_df = get_list_of_coins()
            df = _create_closest_match_df(coin.lower(), coins_df, limit, cutoff)
            df = df[["index", "id", "name"]]

        elif source == "bin":
            coins_df_gecko = get_coin_list()
            coins_df_bin = load_binance_map()
            coins_df_bin.columns = ["symbol", "id"]
            coins_df = pd.merge(
                coins_df_bin, coins_df_gecko[["id", "name"]], how="left", on="id"
            )
            df = _create_closest_match_df(coin.lower(), coins_df, limit, cutoff)
            df = df[["index", "symbol", "name"]]
            df.columns = ["index", "id", "name"]

        elif source == "cb":
            coins_df_gecko = get_coin_list()
            coins_df_cb = load_coinbase_map()
            coins_df_cb.columns = ["symbol", "id"]
            coins_df = pd.merge(
                coins_df_cb, coins_df_gecko[["id", "name"]], how="left", on="id"
            )
            df = _create_closest_match_df(coin.lower(), coins_df, limit, cutoff)
            df = df[["index", "symbol", "name"]]
            df.columns = ["index", "id", "name"]

        else:
            df = pd.DataFrame(columns=["index", "id", "symbol"])
            console.print("Couldn't find any coins")
        console.print("")

    try:
        df = df[skip : skip + top]  # noqa
    except Exception as e:
        logger.exception(str(e))
        console.print(e)

    print_rich_table(
        df.fillna("N/A"),
        headers=list(df.columns),
        show_index=False,
        title="Similar Coins",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "coins",
        df,
    )


def load_ta_data(
    coin_map_df: pd.DataFrame, source: str, currency: str, **kwargs: Any
) -> Tuple[pd.DataFrame, str]:
    """Load data for Technical Analysis

    Parameters
    ----------
    coin_map_df: pd.DataFrame
        Cryptocurrency
    source: str
        Source of data: CoinGecko, Binance, CoinPaprika, Yahoo Finance
    currency: str
        Quotes currency
    kwargs:
        days: int
            Days limit for coingecko, coinpaprika
        limit: int
            Limit for binance quotes
        interval: str
            Time interval for Binance
    Returns
    ----------
    Tuple[pd.DataFrame, str]
        df with prices
        quoted currency
    """

    limit = kwargs.get("limit", 100)
    interval = kwargs.get("interval", "1day")
    days = kwargs.get("days", 30)

    if source == "bin":
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

        symbol_binance = coin_map_df["Binance"]

        pair = symbol_binance + currency.upper()

        if check_valid_binance_str(pair):
            # console.print(f"{symbol_binance} loaded vs {currency.upper()}")

            candles = client.get_klines(
                symbol=pair,
                interval=interval_map[interval],
                limit=limit,
            )
            candles_df = pd.DataFrame(candles).astype(float).iloc[:, :6]
            candles_df.columns = [
                "date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
            df_coin = candles_df.set_index(
                pd.to_datetime(candles_df["date"], unit="ms")
            ).drop("date", axis=1)

            return df_coin, currency
        return pd.DataFrame(), currency

    if source == "cp":
        symbol_coinpaprika = coin_map_df["CoinPaprika"]
        df = coinpaprika_model.get_ohlc_historical(
            symbol_coinpaprika, currency.upper(), days
        )

        if df.empty:
            console.print("No data found", "\n")
            return pd.DataFrame(), ""

        df.drop(["time_close", "market_cap"], axis=1, inplace=True)
        df.columns = [
            "date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
        df = df.set_index(pd.to_datetime(df["date"])).drop("date", axis=1)
        return df, currency

    if source == "cg":
        coin_id = coin_map_df["CoinGecko"]
        # coin = pycoingecko_model.Coin(symbol_coingecko)
        df = pycoingecko_model.get_coin_market_chart(coin_id, currency, days)
        df = df["price"].resample("1D").ohlc().ffill()
        df.columns = [
            "Open",
            "High",
            "Low",
            "Close",
        ]
        df.index.name = "date"
        return df, currency

    if source == "cb":
        symbol_coinbase = coin_map_df["Coinbase"]
        coin, currency = symbol_coinbase.upper(), currency.upper()
        pair = f"{coin}-{currency}"

        if coinbase_model.check_validity_of_product(pair):
            # console.print(f"{coin} loaded vs {currency}")

            df = coinbase_model.get_candles(
                product_id=pair,
                interval=interval or "24hour",
            ).head(limit)

            df_coin = df.set_index(pd.to_datetime(df["date"], unit="s")).drop(
                "date", axis=1
            )

            return df_coin[::-1], currency

    if source == "yf":

        interval_map = {
            "1min": "1m",
            "2min": "2m",
            "5min": "5m",
            "15min": "15m",
            "30min": "30m",
            "60min": "60m",
            "90min": "90m",
            "1hour": "1h",
            "1day": "1d",
            "5day": "5d",
            "1week": "1wk",
            "1month": "1mo",
            "3month": "3mo",
        }

        symbol_yf = coin_map_df["YahooFinance"]

        df_coin = yf.download(
            symbol_yf,
            end=datetime.now(),
            start=datetime.now() - timedelta(days=days),
            progress=False,
            interval=interval_map[interval],
        ).sort_index(ascending=False)

        df_coin.index.names = ["date"]

        if df_coin.empty:
            console.print(f"Could not download data for {symbol_yf} from Yahoo Finance")
            return pd.DataFrame(), currency

        return df_coin[::-1], currency

    return pd.DataFrame(), currency


def plot_chart(
    coin_map_df: pd.DataFrame, source: str, currency: str, **kwargs: Any
) -> None:
    """Load data for Technical Analysis

    Parameters
    ----------
    coin_map_df: pd.DataFrame
        Cryptocurrency
    source: str
        Source of data: CoinGecko, Binance, CoinPaprika
    currency: str
        Quotes currency
    kwargs:
        days: int
            Days limit for coingecko, coinpaprika
        limit: int
            Limit for binance quotes
        interval: str
            Time interval for Binance
    Returns
    ----------
    Tuple[pd.DataFrame, str]
        dataframe with prices
        quoted currency
    """

    limit = kwargs.get("limit", 100)
    interval = kwargs.get("interval", "1day")
    days = kwargs.get("days", 30)

    if source == "bin":
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

        symbol_binance = coin_map_df["Binance"]

        pair = symbol_binance + currency

        if check_valid_binance_str(pair):
            # console.print(f"{symbol_binance} loaded vs {currency.upper()}")

            candles = client.get_klines(
                symbol=pair,
                interval=interval_map[interval],
                limit=limit,
            )
            candles_df = pd.DataFrame(candles).astype(float).iloc[:, :6]
            candles_df.columns = [
                "date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
            df_coin = candles_df.set_index(
                pd.to_datetime(candles_df["date"], unit="ms")
            ).drop("date", axis=1)

            title = f"{symbol_binance + currency} from {df_coin.index[0].strftime('%Y/%m/%d')} to {df_coin.index[-1].strftime('%Y/%m/%d')}"  # noqa: E501

            plot_candles(
                candles_df=df_coin,
                title=title,
                volume=True,
            )

    if source == "cp":
        symbol_coinpaprika = coin_map_df["CoinPaprika"]
        df = coinpaprika_model.get_ohlc_historical(
            str(symbol_coinpaprika), currency.upper(), days
        )

        if df.empty:
            console.print("There is not data to plot chart\n")
            return

        df.drop(["time_close", "market_cap"], axis=1, inplace=True)
        df.columns = [
            "date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
        df = df.set_index(pd.to_datetime(df["date"])).drop("date", axis=1)

        title = f"{symbol_coinpaprika}/{currency} from {df.index[0].strftime('%Y/%m/%d')} to {df.index[-1].strftime('%Y/%m/%d')}"  # noqa: E501

        df["Volume"] = df["Volume"] / 1_000_000

        plot_candles(
            candles_df=df,
            title=title,
            volume=True,
            ylabel="Volume [1M]",
        )

        console.print("")

    if source == "cg":
        symbol_coingecko = coin_map_df["CoinGecko"]
        coin = pycoingecko_model.Coin(symbol_coingecko)
        df = coin.get_coin_market_chart(currency, days)
        df = df["price"].resample("1D").ohlc().ffill()

        df.columns = [
            "Open",
            "High",
            "Low",
            "Close",
        ]

        title = f"{symbol_coingecko}/{currency} from {df.index[0].strftime('%Y/%m/%d')} to {df.index[-1].strftime('%Y/%m/%d')}"  # noqa: E501

        plot_candles(
            candles_df=df,
            title=title,
            volume=False,
            ylabel="Volume [1M]",
        )

        console.print("")

    if source == "cb":
        symbol_coinbase = coin_map_df["Coinbase"]
        coin, currency = symbol_coinbase.upper(), currency.upper()
        pair = f"{coin}-{currency}"

        if coinbase_model.check_validity_of_product(pair):

            df = coinbase_model.get_candles(
                product_id=pair,
                interval=interval or "24hour",
            ).head(limit)
            df = df.astype(float).iloc[:, :6]
            df.sort_values(by="date", inplace=True, ascending=True)
            df = df.set_index(pd.to_datetime(df["date"], unit="s")).drop("date", axis=1)

            title = f"{coin}/{currency} from {df.index[0].strftime('%Y/%m/%d')} to {df.index[-1].strftime('%Y/%m/%d')}"  # noqa: E501

            df["Volume"] = df["Volume"] / 1_000

            plot_candles(
                candles_df=df,
                title=title,
                volume=True,
                ylabel="Volume [1K]",
            )

            console.print("")

    if source == "yf":
        symbol_yf = coin_map_df["YahooFinance"]

        df = yf.download(
            symbol_yf,
            end=datetime.now(),
            start=datetime.now() - timedelta(days=days),
            progress=False,
            interval=interval,
        )[
            [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
        ].copy()
        # Because the label has Volume [1M]
        df.Volume = df.Volume / 1_000_000
        df.index.name = "date"

        title = f"{symbol_yf.replace('-', '/')} from {df.index[0].strftime('%Y/%m/%d')} to {df.index[-1].strftime('%Y/%m/%d')}"  # noqa: E501

        plot_candles(
            candles_df=df,
            title=title,
            volume=True,
            ylabel="Volume [1M]",
        )

        console.print()


def plot_candles(
    candles_df: pd.DataFrame,
    volume: bool,
    ylabel: str = "",
    title: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plot candle chart from dataframe. [Source: Binance]

    Parameters
    ----------
    candles_df: pd.DataFrame
        Dataframe containing time and OHLCV
    title: str
        title of graph
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "volume": volume,
        "xrotation": theme.xticks_rotation,
        "ylabel_lower": ylabel,
        "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "warn_too_much_data": 10000,
    }

    # This plot has 2 axes
    if external_axes is None:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        fig, _ = mpf.plot(candles_df, **candle_chart_kwargs)
        fig.suptitle(
            f"\n{title}",
            horizontalalignment="left",
            verticalalignment="top",
            x=0.05,
            y=1,
        )
        theme.visualize_output(force_tight_layout=False)
    else:
        nr_external_axes = 2 if volume else 1

        if len(external_axes) != nr_external_axes:
            logger.error("Expected list of %s axis items.", str(nr_external_axes))
            console.print(
                f"[red]Expected list of {nr_external_axes} axis items./n[/red]"
            )
            return

        if volume:
            (ax, volume) = external_axes
            candle_chart_kwargs["volume"] = volume
        else:
            ax = external_axes[0]

        candle_chart_kwargs["ax"] = ax

        mpf.plot(candles_df, **candle_chart_kwargs)


def plot_order_book(
    bids: np.ndarray,
    asks: np.ndarray,
    coin: str,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """
    Plots Bid/Ask. Can be used for Coinbase and Binance

    Parameters
    ----------
    bids : np.array
        array of bids with columns: price, size, cumulative size
    asks : np.array
        array of asks with columns: price, size, cumulative size
    coin : str
        Coin being plotted
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(bids[:, 0], bids[:, 2], color=theme.up_color, label="bids")
    ax.fill_between(bids[:, 0], bids[:, 2], color=theme.up_color, alpha=0.4)

    ax.plot(asks[:, 0], asks[:, 2], color=theme.down_color, label="asks")
    ax.fill_between(asks[:, 0], asks[:, 2], color=theme.down_color, alpha=0.4)

    ax.legend()
    ax.set_xlabel("Price")
    ax.set_ylabel("Size (Coins)")
    ax.set_title(f"Order Book for {coin}")

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output(force_tight_layout=False)
