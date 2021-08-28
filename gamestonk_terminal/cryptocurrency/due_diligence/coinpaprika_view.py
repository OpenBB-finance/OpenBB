"""CoinPaprika view"""
__docformat__ = "numpy"

import argparse
import os
from typing import List, Tuple
from tabulate import tabulate
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    plot_autoscale,
    export_data,
)
from gamestonk_terminal.feature_flags import USE_ION as ion
import gamestonk_terminal.cryptocurrency.due_diligence.coinpaprika_model as paprika
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_list_of_coins,
)
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    long_number_format_with_type_check,
)

register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=C0302, too-many-lines

CURRENCIES = [
    "BTC",
    "ETH",
    "USD",
    "EUR",
    "PLN",
    "KRW",
    "GBP",
    "CAD",
    "JPY",
    "RUB",
    "TRY",
    "NZD",
    "AUD",
    "CHF",
    "UAH",
    "HKD",
    "SGD",
    "NGN",
    "PHP",
    "MXN",
    "BRL",
    "THB",
    "CLP",
    "CNY",
    "CZK",
    "DKK",
    "HUF",
    "IDR",
    "ILS",
    "INR",
    "MYR",
    "NOK",
    "PKR",
    "SEK",
    "TWD",
    "ZAR",
    "VND",
    "BOB",
    "COP",
    "PEN",
    "ARS",
    "ISK",
]


def coins(other_args: List[str]):
    """Shows list of all available coins on CoinPaprika

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="coins",
        description="""Shows list of all available coins on CoinPaprika.
        You can display top N number of coins with --top N flag,
        You can search by starting letters with -l/--letter flag like `coins -l M`
        And you can also specify by which column you are searching for coin with --key
        Displays columns like:
            rank, id, name, type""",
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
        "-t",
        "--top",
        default=30,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )
    parser.add_argument("-l", "--letter", dest="letter", help="First letters", type=str)
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Search in column symbol, name, id",
        type=str,
        choices=["id", "symbol", "name"],
        default="symbol",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = get_list_of_coins()

        letter = ns_parser.letter
        if letter and isinstance(letter, str):
            df = df[
                df[ns_parser.key].str.match(f"^({letter.lower()}|{letter.upper()})")
            ]

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
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def display_twitter(
    coin_id: str, top: int, sortby: str, descend: bool, export: str
) -> None:
    """Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

    Parameters
    ----------
    coin_id: str
        Identifier of coin for CoinPaprika API
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = paprika.get_coin_twitter_timeline(coin_id)

    if df.empty:
        print(f"Couldn't find any tweets for coin {coin_id}", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)
    # Remove unicode chars (it breaks pretty tables)
    df["status"] = df["status"].apply(
        lambda text: "".join(i if ord(i) < 128 else "" for i in text)
    )
    print(
        tabulate(
            df.head(top),
            headers=df.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "twitter",
        df,
    )


def display_events(
    coin_id: str, top: int, sortby: str, descend: bool, links: bool, export: str
) -> None:
    """Get all events for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    coin_id: str
        Identifier of coin for CoinPaprika API
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = paprika.get_coin_events_by_id(coin_id)

    if df.empty:
        print(f"Couldn't find any events for coin {coin_id}\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    df_data = df.copy()

    if links is True:
        df = df[["date", "name", "link"]]
    else:
        df.drop("link", axis=1, inplace=True)

    print(
        tabulate(
            df.head(top),
            headers=df.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "events",
        df_data,
    )


def display_exchanges(
    coin_id: str, top: int, sortby: str, descend: bool, export: str
) -> None:
    """Get all exchanges for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    coin_id: str
        Identifier of coin for CoinPaprika API
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = paprika.get_coin_exchanges_by_id(coin_id)

    if df.empty:
        print("No data found", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    print(
        tabulate(
            df.head(top),
            headers=df.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ex",
        df,
    )


def display_markets(
    coin_id: str,
    currency: str,
    top: int,
    sortby: str,
    descend: bool,
    links: bool,
    export: str,
) -> None:
    """Get all markets for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    coin_id: str
        Identifier of coin for CoinPaprika API
    currency: str
        Quoted currency
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    if sortby in ["volume", "price"]:
        sortby = f"{str(currency).lower()}_{sortby}"

    df = paprika.get_coin_markets_by_id(coin_id, currency)

    if df.empty:
        print("There is no data \n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    df_data = df.copy()

    if links is True:
        df = df[["exchange", "pair", "trust_score", "market_url"]]
    else:
        df.drop("market_url", axis=1, inplace=True)

    print(
        tabulate(
            df.head(top),
            headers=df.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mkt",
        df_data,
    )


def plot_chart(coin_id: str, other_args: List[str]):
    """Plots chart for loaded cryptocurrency [Source: CoinPaprika]

    Parameters
    ----------
    coin_id: str
        Identifier of coin for CoinPaprika API
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="chart",
        description="""Display chart for loaded coin. You can specify currency vs which you want
                        to show chart and also number of days to get data for.
                        By default currency: usd and days: 90.
                        E.g. if you loaded in previous step Ethereum and you want to see it's price vs bitcoin
                        in last 90 days range use `chart --vs btc --days 90`
                        Available quoted currencies are only btc and usd""",
    )
    parser.add_argument(
        "--vs",
        default="usd",
        dest="vs",
        help="Currency to display vs coin",
        choices=["usd", "btc", "BTC", "USD"],
    )
    parser.add_argument(
        "-d",
        "--days",
        default=30,
        dest="days",
        type=check_positive,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = paprika.get_ohlc_historical(coin_id, ns_parser.vs.upper(), ns_parser.days)

        if df.empty:
            print("There is not data to plot chart\n")
            return

        df.drop(["time_close", "market_cap"], axis=1, inplace=True)
        df.columns = [
            "Time0",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
        df = df.set_index(pd.to_datetime(df["Time0"])).drop("Time0", axis=1)
        title = (
            f"\n{coin_id}/{ns_parser.vs} from {df.index[0].strftime('%Y/%m/%d')} to {df.index[-1].strftime('%Y/%m/%d')}",
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
    except SystemExit:
        print("")

    except Exception as e:
        print(e, "\n")


def display_price_supply(coin_id: str, currency: str, export: str) -> None:
    """Get ticker information for single coin [Source: CoinPaprika]

    Parameters
    ----------
    coin_id: str
        Identifier of coin for CoinPaprika API
    currency: str
        Quoted currency
    export: str
        Export dataframe data to csv,json,xlsx

    """

    df = paprika.get_tickers_info_for_coin(coin_id, currency)

    if df.empty:
        print("No data found", "\n")
        return

    df = df.applymap(lambda x: long_number_format_with_type_check(x))
    print(
        tabulate(
            df,
            headers=df.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ps",
        df,
    )


def load(other_args: List[str]):
    """Select coin from CoinPaprika [Source: CoinPaprika]

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    Returns
    -------
    coin: str
        Coin that is defined on binance
    df_coin : pd.DataFrame
        Dataframe of prices for selected coin
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="load",
        description="Define the coin to be used from CoinPaprika and get data",
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Coin to get",
        dest="coin",
        type=str,
        required="-h" not in other_args,
    )

    try:

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        COINS = get_list_of_coins()
        COINS_DCT = dict(zip(COINS.id, COINS.symbol))
        coin_id, _ = paprika.validate_coin(ns_parser.coin, COINS_DCT)

        if coin_id:
            return coin_id

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def load_ta_data(coin_id: str, other_args: List[str]) -> Tuple[pd.DataFrame, str]:
    """Load data for Technical Analysis

    Parameters
    ----------
    coin_id: Identifier of coin for CoinPaprika
        Cryptocurrency
    other_args : List[str]
        argparse arguments

    Returns
    ----------
    Tuple[pd.DataFrame, str]
        dataframe with prices
        quoted currency

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ta",
        description="""Loads data for technical analysis. You can specify currency vs which you want
                        to show chart and also number of days to get data for.
                        By default currency: usd and days: 30.
                        E.g. if you loaded in previous step Ethereum and you want to see it's price vs btc
                        in last 90 days range use `ta --vs btc --days 90`""",
    )
    parser.add_argument(
        "--vs",
        default="usd",
        dest="vs",
        help="Currency to display vs coin",
        choices=["usd", "btc", "BTC", "USD"],
        type=str,
    )
    parser.add_argument(
        "-d",
        "--days",
        default=30,
        dest="days",
        help="Number of days to get data for",
        type=check_positive,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return pd.DataFrame(), ""

        df = paprika.get_ohlc_historical(coin_id, ns_parser.vs.upper(), ns_parser.days)

        if df.empty:
            print("No data found", "\n")
            return pd.DataFrame(), ""

        df.drop(["time_close", "market_cap"], axis=1, inplace=True)
        df.columns = [
            "Time0",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
        df = df.set_index(pd.to_datetime(df["Time0"])).drop("Time0", axis=1)
        return df, ns_parser.vs

    except SystemExit:
        print("")
        return pd.DataFrame(), ""

    except Exception as e:
        print(e, "\n")
        return pd.DataFrame(), ""


def display_basic(coin_id: str, export: str) -> None:
    """Get basic information for coin. Like:
        name, symbol, rank, type, description, platform, proof_type, contract, tags, parent.  [Source: CoinPaprika]

    Parameters
    ----------
    coin_id: str
        Identifier of coin for CoinPaprika API
    export: str
        Export dataframe data to csv,json,xlsx

    """

    df = paprika.basic_coin_info(coin_id)

    if df.empty:
        print("No data available\n")
        return

    print(
        tabulate(
            df,
            headers=df.columns,
            floatfmt=".0f",
            showindex=False,
            tablefmt="fancy_grid",
        ),
        "\n",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "basic",
        df,
    )
