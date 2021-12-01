"""Cryptocurrency helpers"""
__docformat__ = "numpy"

import os
import json
from typing import Tuple, Any, Optional, Union
import difflib
import pandas as pd
import numpy as np
from binance.client import Client
import matplotlib.pyplot as plt
from tabulate import tabulate
import mplfinance as mpf
from gamestonk_terminal.helper_funcs import (
    plot_autoscale,
    export_data,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.cryptocurrency.due_diligence import (
    pycoingecko_model,
    coinpaprika_model,
)
from gamestonk_terminal.cryptocurrency.discovery.pycoingecko_model import get_coin_list
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_list_of_coins,
)
from gamestonk_terminal.cryptocurrency.due_diligence.binance_model import (
    check_valid_binance_str,
    show_available_pairs_for_given_symbol,
    plot_candles,
)

from gamestonk_terminal.cryptocurrency.due_diligence import coinbase_model
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.feature_flags import USE_ION as ion
from gamestonk_terminal import feature_flags as gtff


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


def load_binance_map():
    return _load_coin_map("binance_gecko_map.json")


def load_coinbase_map():
    return _load_coin_map("coinbase_gecko_map.json")


def prepare_all_coins_df() -> pd.DataFrame:
    """Helper method which loads coins from all sources: CoinGecko, CoinPaprika, Binance
    and merge those coins on keys:

        CoinGecko - > name < - CoinPaprika
        CoinGecko - > id <- Binance

    Returns
    -------
    pd.DataFrame
        CoinGecko - id for coin in CoinGecko API: uniswap
        CoinPaprika - id for coin in CoinPaprika API: uni-uniswap
        Binance - symbol (baseAsset) for coin in Binance API: UNI
        Coinbase - symbol for coin in Coinbase Pro API e.g UNI
        Symbol: uni
    """

    gecko_coins_df = get_coin_list()
    paprika_coins_df = get_list_of_coins()

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

    return df_merged[["CoinGecko", "CoinPaprika", "Binance", "Coinbase", "Symbol"]]


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


def load(
    coin: str,
    source: str,
) -> Tuple[Union[Optional[str], pycoingecko_model.Coin], Optional[Any], Optional[Any]]:
    """Load cryptocurrency from given source. Available sources are: CoinGecko, CoinPaprika, Coinbase and Binance.

    Loading coin from Binance and CoinPaprika means validation if given coins exists in chosen source,
    if yes then id of the coin is returned as a string.
    In case of CoinGecko load will return Coin object, if provided coin exists. Coin object has access to different coin
    information.

    Parameters
    ----------
    coin: str
        Coin symbol or id which is checked if exists in chosen data source.
    source : str
        Source of the loaded data. CoinGecko, CoinPaprika, or Binance

    Returns
    -------
    Tuple[Union[str, pycoingecko_model.Coin], str, str]
        - str or Coin object for provided coin
        - str with source of the loaded data. CoinGecko, CoinPaprika, or Binance
        - str with
    """

    current_coin = ""  # type: Optional[Any]

    if source == "cg":
        coingecko = pycoingecko_model.Coin(coin)
        return coingecko, source, coingecko.symbol

    if source == "bin":
        parsed_coin = coin.upper()
        current_coin, pairs = show_available_pairs_for_given_symbol(parsed_coin)
        if len(pairs) > 0:
            print(f"Coin found : {current_coin}\n")
        else:
            print(f"Couldn't find coin with symbol {current_coin}\n")
        return current_coin, source, parsed_coin

    if source == "cp":
        paprika_coins = get_list_of_coins()
        paprika_coins_dict = dict(zip(paprika_coins.id, paprika_coins.symbol))
        current_coin, symbol = coinpaprika_model.validate_coin(coin, paprika_coins_dict)
        return current_coin, source, symbol

    if source == "cb":
        coinbase_coin = coin.upper()
        current_coin, pairs = coinbase_model.show_available_pairs_for_given_symbol(
            coinbase_coin
        )
        if len(pairs) > 0:
            print(f"Coin found : {current_coin}\n")
        else:
            print(f"Couldn't find coin with symbol {current_coin}\n")
        return current_coin, source, coin

    return current_coin, None, None


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
        print(
            "Couldn't execute find methods for CoinPaprika, Binance, Coinbase or CoinGecko\n"
        )
        df = pd.DataFrame()

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

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
            print("Couldn't find any coins")
        print("")

    try:
        df = df[skip : skip + top]
    except Exception as e:
        print(e)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )

    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "coins",
        df,
    )


def load_ta_data(
    coin: Union[str, pycoingecko_model.Coin], source: str, currency: str, **kwargs: Any
) -> Tuple[pd.DataFrame, str]:
    """Load data for Technical Analysis

    Parameters
    ----------
    coin: str
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

        assert isinstance(coin, str)
        pair = coin + currency

        if check_valid_binance_str(pair):
            print(f"{coin} loaded vs {currency.upper()}")

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
        df = coinpaprika_model.get_ohlc_historical(str(coin), currency.upper(), days)

        if df.empty:
            print("No data found", "\n")
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
        assert isinstance(coin, pycoingecko_model.Coin)
        df = coin.get_coin_market_chart(currency, days)
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
        assert isinstance(coin, str)
        coin, currency = coin.upper(), currency.upper()
        pair = f"{coin}-{currency}"

        if coinbase_model.check_validity_of_product(pair):
            print(f"{coin} loaded vs {currency}")

            df = coinbase_model.get_candles(
                product_id=pair,
                interval=interval or "24hour",
            ).head(limit)

            df_coin = df.set_index(pd.to_datetime(df["date"], unit="s")).drop(
                "date", axis=1
            )

            return df_coin[::-1], currency

    return pd.DataFrame(), currency


def plot_chart(
    coin: Union[str, pycoingecko_model.Coin], source: str, currency: str, **kwargs: Any
) -> None:
    """Load data for Technical Analysis

    Parameters
    ----------
    coin: str
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

        assert isinstance(coin, str)
        pair = coin + currency

        if check_valid_binance_str(pair):
            print(f"{coin} loaded vs {currency.upper()}")

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

            plot_candles(
                df_coin,
                f"{coin + currency} from {df_coin.index[0].strftime('%Y/%m/%d')} to "
                f"{df_coin.index[-1].strftime('%Y/%m/%d')}",
            )

    if source == "cp":
        df = coinpaprika_model.get_ohlc_historical(str(coin), currency.upper(), days)

        if df.empty:
            print("There is not data to plot chart\n")
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
        title = (
            f"\n{coin}/{currency} from {df.index[0].strftime('%Y/%m/%d')} to {df.index[-1].strftime('%Y/%m/%d')}",
        )
        df["Volume"] = df["Volume"] / 1_000_000
        mpf.plot(
            df,
            type="candle",
            volume=True,
            ylabel_lower="Volume [1M]",
            title=str(title[0]) if isinstance(title, tuple) else title,
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

    if source == "cg":
        assert isinstance(coin, pycoingecko_model.Coin)
        df = coin.get_coin_market_chart(currency, days)
        df = df["price"].resample("1D").ohlc().ffill()

        df.columns = [
            "Open",
            "High",
            "Low",
            "Close",
        ]

        title = (
            f"\n{coin.coin_symbol}/{currency} from {df.index[0].strftime('%Y/%m/%d')} "
            f"to {df.index[-1].strftime('%Y/%m/%d')}",
        )

        mpf.plot(
            df,
            type="candle",
            volume=False,
            title=str(title[0]) if isinstance(title, tuple) else title,
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

    if source == "cb":
        assert isinstance(coin, str)
        coin, currency = coin.upper(), currency.upper()
        pair = f"{coin}-{currency}"

        if coinbase_model.check_validity_of_product(pair):
            print(f"{coin} loaded vs {currency}")

            df = coinbase_model.get_candles(
                product_id=pair,
                interval=interval or "24hour",
            ).head(limit)
            df = df.astype(float).iloc[:, :6]
            df.sort_values(by="date", inplace=True, ascending=True)
            df = df.set_index(pd.to_datetime(df["date"], unit="s")).drop("date", axis=1)

            title = (
                f"\n{coin}/{currency} from {df.index[0].strftime('%Y/%m/%d')} to {df.index[-1].strftime('%Y/%m/%d')}",
            )
            df["Volume"] = df["Volume"] / 1_000
            mpf.plot(
                df,
                type="candle",
                volume=True,
                ylabel_lower="Volume [1K]",
                title=str(title[0]) if isinstance(title, tuple) else title,
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


def plot_order_book(bids: np.ndarray, asks: np.ndarray, coin: str) -> None:
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
