"""Cryptocurrency helpers"""
__docformat__ = "numpy"

import argparse
from typing import List, Tuple, Any, Optional, Union
import difflib
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, check_positive
from gamestonk_terminal.cryptocurrency.due_diligence import (
    pycoingecko_model,
    coinpaprika_view,
    binance_view,
)
from gamestonk_terminal.cryptocurrency.discovery.pycoingecko_model import (
    get_coin_list,
    create_mapping_matrix_for_binance,
    load_binance_map,
)
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_list_of_coins,
)


def prepare_all_coins_df():
    """Helper method which loads coins from all sources: CoinGecko, CoinPaprika, Binance and
    merge those coins on keys:
        CoinGecko - > name < - CoinPaprika
        CoinGecko - > id <- Binance

    Returns
    -------
    pd.DataFrame
        CoinGecko - id for coin in CoinGecko API: uniswap
        CoinPaprika - id for coin in CoinPaprika API: uni-uniswap
        Binance - symbol (baseAsset) for coin in Binance API: UNI
        Symbol: uni

    """
    gecko_coins_df = get_coin_list()
    paprika_coins_df = get_list_of_coins()
    binance_coins_df = load_binance_map().rename(columns={"symbol": "Binance"})
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

    return df_merged[["CoinGecko", "CoinPaprika", "Binance", "Symbol"]]


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
    coin: str, other_args: List[str]
) -> Tuple[Union[Optional[str], pycoingecko_model.Coin], Any]:
    """Load cryptocurrency from given source. Available sources are: CoinGecko, CoinPaprika and Binance.

    Loading coin from Binance and CoinPaprika means validation if given coins exists in chosen source,
    if yes then id of the coin is returned as a string.
    In case of CoinGecko load will return Coin object, if provided coin exists. Coin object has access to different coin
    information.

    Parameters
    ----------
    coin: str
        Coin symbol or id which is checked if exists in chosen data source.
    other_args: List[str]
        Arguments to pass to argparse

    Returns
    -------
    Tuple[Union[str, pycoingecko_model.Coin], Any]
        - str or Coin object for provided coin
        - str with source of the loaded data. CoinGecko, CoinPaprika, or Binance

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="load",
        description="Load crypto currency to perform analysis on. "
        "Available data sources are CoinGecko, CoinPaprika, and Binance"
        "By default main source used for analysis is CoinGecko (cg). To change it use --source flag",
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Coin to get",
        dest="coin",
        type=str,
        required="-h" not in other_args,
    )

    parser.add_argument(
        "-s",
        "--source",
        help="Source of data",
        dest="source",
        choices=("cp", "cg", "bin"),
        default="cg",
        required=False,
    )

    try:
        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return coin, None

        source = ns_parser.source
        current_coin = ""  # type: Optional[Any]

        for arg in ["--source", source]:
            if arg in other_args:
                other_args.remove(arg)

        if source == "cg":
            current_coin = pycoingecko_model.Coin(ns_parser.coin)
            return current_coin, source

        if source == "bin":
            current_coin = binance_view.load(other_args=other_args)
            return current_coin, source

        if source == "cp":
            current_coin = coinpaprika_view.load(other_args=other_args)
            return current_coin, source

        return current_coin, None

    except KeyError:
        print(f"Could not find coin: {ns_parser.coin}", "\n")
        return coin, None
    except SystemExit:
        print("")
        return coin, None
    except Exception as e:
        print(e, "\n")
        return coin, None


def find(other_args: List[str]):
    """Find similar coin by coin name,symbol or id.

    If you don't remember exact name or id of the Coin at CoinGecko or CoinPaprika
    you can use this command to display coins with similar name, symbol or id to your search query.
    Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.
      -c, --coin stands for coin - you provide here your search query
      -k, --key it's a searching key. You can search by symbol, id or name of coin
      -t, --top it displays top N number of records.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="find",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Find similar coin by coin name,symbol or id. If you don't remember exact name or id of the Coin at CoinGecko,
        Binance or CoinPaprika you can use this command to display coins with similar name, symbol or id
        to your search query.
        Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
        It will search for coin that has similar name to polka and display top 25 matches.
        -c, --coin stands for coin - you provide here your search query
        -k, --key it's a searching key. You can search by symbol, id or name of coin
        -t, --top it displays top N number of records.""",
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Symbol Name or Id of Coin",
        dest="coin",
        required="-h" not in other_args,
        type=str,
    )
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Specify by which column you would like to search: symbol, name, id",
        type=str,
        choices=["id", "symbol", "name"],
        default="symbol",
    )
    parser.add_argument(
        "-t",
        "--top",
        default=10,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )

    parser.add_argument(
        "--source",
        dest="source",
        choices=["cp", "cg", "bin"],
        default="cg",
        help="Source of data.",
        type=str,
    )

    try:

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.source == "cg":
            coins_df = get_coin_list()
            coins_list = coins_df[ns_parser.key].to_list()
            sim = difflib.get_close_matches(ns_parser.coin, coins_list, ns_parser.top)
            df = pd.Series(sim).to_frame().reset_index()
            df.columns = ["index", ns_parser.key]
            coins_df.drop("index", axis=1, inplace=True)
            df = df.merge(coins_df, on=ns_parser.key)
            print(
                tabulate(
                    df,
                    headers=df.columns,
                    floatfmt=".1f",
                    showindex=False,
                    tablefmt="fancy_grid",
                )
            )
        elif ns_parser.source == "cp":
            coins_df = get_list_of_coins()
            coins_list = coins_df[ns_parser.key].to_list()

            keys = {"name": "title", "symbol": "upper", "id": "lower"}

            key = keys.get(ns_parser.key)
            coin = getattr(ns_parser.coin, str(key))()

            sim = difflib.get_close_matches(coin, coins_list, ns_parser.top)
            df = pd.Series(sim).to_frame().reset_index()
            df.columns = ["index", ns_parser.key]
            df = df.merge(coins_df, on=ns_parser.key)
            print(
                tabulate(
                    df,
                    headers=df.columns,
                    floatfmt=".1f",
                    showindex=False,
                    tablefmt="fancy_grid",
                )
            )
        elif ns_parser.source == "bin":

            # TODO: Fix it in future. Determine if user looks for symbol like ETH or ethereum
            if len(ns_parser.coin) > 4:
                ns_parser.key = "id"

            coins_df_gecko = get_coin_list()
            coins_bin = create_mapping_matrix_for_binance()
            coins_df_bin = pd.Series(coins_bin).reset_index()
            coins_df_bin.columns = ["symbol", "id"]
            coins = pd.merge(
                coins_df_bin, coins_df_gecko[["id", "name"]], how="left", on="id"
            )
            coins_list = coins[ns_parser.key].to_list()

            sim = difflib.get_close_matches(ns_parser.coin, coins_list, ns_parser.top)
            df = pd.Series(sim).to_frame().reset_index()
            df.columns = ["index", ns_parser.key]
            df = df.merge(coins, on=ns_parser.key)
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
            print("Couldn't execute find methods for CoinPaprika, Binance or CoinGecko")
        print("")

    except Exception as e:
        print(e, "\n")


def all_coins(other_args: List[str]):
    """Find similar coin by coin name,symbol or id.

    If you don't remember exact name or id of the Coin at CoinGecko or CoinPaprika
    you can use this command to display coins with similar name, symbol or id to your search query.
    Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.
      -c, --coin stands for coin - you provide here your search query
      -t, --top it displays top N number of records.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="coins",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows list of coins available on CoinGecko, CoinPaprika and Binance.
        If you provide name of coin then in result you will see ids of coins with best match for all mentioned services.
        If you provide ALL keyword in your search query, then all coins will be displayed. To move over the coins you
        can use pagination mechanism with skip, top params. E.g. coins ALL --skip 100 --limit 30 then all coins
        from 100 to 130 will be displayed. By default skip = 0, limit = 10.
        If you won't provide source of the data everything will be displayed (CoinGecko, CoinPaprika, Binance).
        If you want to search only in given source then use --source flag. E.g. if you want to find coin with name
        uniswap on CoinPaprika then use: coins uniswap --source cp --limit 10
        """,
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Coin you search for",
        dest="coin",
        required="-h" not in other_args,
        type=str,
    )
    parser.add_argument(
        "-s",
        "--skip",
        default=0,
        dest="skip",
        help="Skip n of records",
        type=check_positive,
    )

    parser.add_argument(
        "-l",
        "--limit",
        default=10,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )

    parser.add_argument(
        "--source",
        dest="source",
        required=False,
        help="Source of data.",
        type=str,
    )

    limit, cutoff = 30, 0.75
    coins_func_map = {
        "cg": get_coin_list,
        "cp": get_list_of_coins,
        "bin": load_binance_map,
    }

    try:

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if "ALL" in other_args:
            coins_func = coins_func_map.get(ns_parser.source)
            if coins_func:
                df = coins_func()
            else:
                df = prepare_all_coins_df()

        elif not ns_parser.source or ns_parser.source not in ["cg", "cp", "bin"]:
            df = prepare_all_coins_df()
            cg_coins_list = df["CoinGecko"].to_list()
            sim = difflib.get_close_matches(
                ns_parser.coin.lower(), cg_coins_list, limit, cutoff
            )
            df_matched = pd.Series(sim).to_frame().reset_index()
            df_matched.columns = ["index", "CoinGecko"]
            df = df.merge(df_matched, on="CoinGecko")
            df.drop("index", axis=1, inplace=True)

        else:

            if ns_parser.source == "cg":
                coins_df = get_coin_list().drop("index", axis=1)
                df = _create_closest_match_df(
                    ns_parser.coin.lower(), coins_df, limit, cutoff
                )
                df = df[["index", "id", "name"]]

            elif ns_parser.source == "cp":
                coins_df = get_list_of_coins()
                df = _create_closest_match_df(
                    ns_parser.coin.lower(), coins_df, limit, cutoff
                )
                df = df[["index", "id", "name"]]

            elif ns_parser.source == "bin":
                coins_df_gecko = get_coin_list()
                coins_df_bin = load_binance_map()
                coins_df_bin.columns = ["symbol", "id"]
                coins_df = pd.merge(
                    coins_df_bin, coins_df_gecko[["id", "name"]], how="left", on="id"
                )
                df = _create_closest_match_df(
                    ns_parser.coin.lower(), coins_df, limit, cutoff
                )
                df = df[["index", "symbol", "name"]]
                df.columns = ["index", "id", "name"]

            else:
                df = pd.DataFrame(columns=["index", "id", "symbol"])
                print("Couldn't find any coins")
            print("")

        try:
            df = df[ns_parser.skip : ns_parser.skip + ns_parser.top]
        except Exception as e:
            print(e)

        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )

    except Exception as e:
        print(e, "\n")
