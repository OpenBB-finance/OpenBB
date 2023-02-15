import difflib

import pandas as pd

from openbb_terminal.rich_config import console

# TODO: Find better algorithm then difflib.get_close_matches to find most similar coins


def find(
    query: str,
    source: str = "CoinGecko",
    key: str = "symbol",
    limit: int = 10,
) -> pd.DataFrame:
    """Find similar coin by coin name,symbol or id.

    If you don't know exact name or id of the Coin at CoinGecko CoinPaprika, Binance or Coinbase
    you use this command to display coins with similar name, symbol or id to your search query.
    Example: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.

    Parameters
    ----------
    query: str
        Cryptocurrency
    source: str
        Data source of coins.  CoinGecko or CoinPaprika or Binance or Coinbase
    key: str
        Searching key (symbol, id, name)
    limit: int
        Number of records to display

    Returns
    -------
    pd.DataFrame
        DataFrame with 'limit' similar coins

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.crypto.find("polka", "CoinGecko", "name", 25)
    """

    df = pd.DataFrame()

    if source == "CoinGecko":
        df = _find_CoinGecko(key=key, query=query, limit=limit)

    elif source == "CoinPaprika":
        df = _find_CoinPaprika(key=key, query=query, limit=limit)

    elif source == "Binance":
        df = _find_Binance(key=key, query=query, limit=limit)

    elif source == "Coinbase":
        df = _find_Coinbase(key=key, query=query, limit=limit)

    else:
        console.print(
            "Couldn't execute find methods for CoinPaprika, Binance, Coinbase or CoinGecko\n"
        )

    return df


def _find_CoinGecko(key: str, query: str, limit: int) -> pd.DataFrame:
    # pylint: disable=C0415
    from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import get_coin_list

    coins_df = get_coin_list()
    coins_list = coins_df[key].to_list()
    if key in ["symbol", "id"]:
        query = query.lower()

    sim = difflib.get_close_matches(query, coins_list, limit)
    df = pd.Series(sim).to_frame().reset_index()
    df.columns = ["index", key]
    coins_df.drop("index", axis=1, inplace=True)
    df = df.merge(coins_df, on=key)

    return df


def _find_CoinPaprika(key: str, query: str, limit: int) -> pd.DataFrame:
    # pylint: disable=C0415
    from openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model import (
        get_coin_list,
    )

    coins_df = get_coin_list()
    coins_list = coins_df[key].to_list()
    keys = {"name": "title", "symbol": "upper", "id": "lower"}

    func_key = keys[key]
    query = getattr(query, str(func_key))()

    sim = difflib.get_close_matches(query, coins_list, limit)
    df = pd.Series(sim).to_frame().reset_index()
    df.columns = ["index", key]
    df = df.merge(coins_df, on=key)

    return df


def _find_Binance(key: str, query: str, limit: int) -> pd.DataFrame:
    # pylint: disable=C0415
    from openbb_terminal.cryptocurrency.cryptocurrency_helpers import load_binance_map
    from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import get_coin_list

    # TODO: Fix it in future. Determine if user looks for symbol like ETH or ethereum
    if len(query) > 5:
        key = "id"

    coins_df_gecko = get_coin_list()
    coins_df_bin = load_binance_map()
    coins = pd.merge(coins_df_bin, coins_df_gecko[["id", "name"]], how="left", on="id")
    coins_list = coins[key].to_list()

    sim = difflib.get_close_matches(query, coins_list, limit)
    df = pd.Series(sim).to_frame().reset_index()
    df.columns = ["index", key]
    df = df.merge(coins, on=key)

    return df


def _find_Coinbase(key: str, query: str, limit: int) -> pd.DataFrame:
    # pylint: disable=C0415
    from openbb_terminal.cryptocurrency.cryptocurrency_helpers import load_coinbase_map
    from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import get_coin_list

    if len(query) > 5:
        key = "id"

    coins_df_gecko = get_coin_list()
    coins_df_bin = load_coinbase_map()
    coins = pd.merge(coins_df_bin, coins_df_gecko[["id", "name"]], how="left", on="id")
    coins_list = coins[key].to_list()

    sim = difflib.get_close_matches(query, coins_list, limit)
    df = pd.Series(sim).to_frame().reset_index()
    df.columns = ["index", key]
    df = df.merge(coins, on=key)

    return df
