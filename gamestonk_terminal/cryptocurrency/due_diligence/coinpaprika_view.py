"""CoinPaprika view"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import (
    export_data,
)
from gamestonk_terminal.cryptocurrency.due_diligence import coinpaprika_model
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    long_number_format_with_type_check,
)
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=C0302, too-many-lines

TWEETS_FILTERS = ["date", "user_name", "status", "retweet_count", "like_count"]

EVENTS_FILTERS = ["date", "date_to", "name", "description", "is_conference"]

EX_FILTERS = ["id", "name", "adjusted_volume_24h_share", "fiats"]

MARKET_FILTERS = [
    "pct_volume_share",
    "exchange",
    "pair",
    "trust_score",
    "volume",
    "price",
]

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

    df = coinpaprika_model.get_coin_twitter_timeline(coin_id)

    if df.empty:
        print(f"Couldn't find any tweets for coin {coin_id}", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)
    # Remove unicode chars (it breaks pretty tables)
    df["status"] = df["status"].apply(
        lambda text: "".join(i if ord(i) < 128 else "" for i in text)
    )
    if gtff.USE_TABULATE_DF:
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
    else:
        print(df.to_string, "\n")

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

    df = coinpaprika_model.get_coin_events_by_id(coin_id)

    if df.empty:
        print(f"Couldn't find any events for coin {coin_id}\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    df_data = df.copy()

    if links is True:
        df = df[["date", "name", "link"]]
    else:
        df.drop("link", axis=1, inplace=True)

    if gtff.USE_TABULATE_DF:
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
    else:
        print(df.to_string, "\n")

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

    df = coinpaprika_model.get_coin_exchanges_by_id(coin_id)

    if df.empty:
        print("No data found", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    if gtff.USE_TABULATE_DF:
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
    else:
        print(df.to_string, "\n")

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
    export: str = "",
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

    df = coinpaprika_model.get_coin_markets_by_id(coin_id, currency)

    if df.empty:
        print("There is no data \n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    df_data = df.copy()

    if links is True:
        df = df[["exchange", "pair", "trust_score", "market_url"]]
    else:
        df.drop("market_url", axis=1, inplace=True)

    if gtff.USE_TABULATE_DF:
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
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mkt",
        df_data,
    )


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

    df = coinpaprika_model.get_tickers_info_for_coin(coin_id, currency)

    if df.empty:
        print("No data found", "\n")
        return

    df = df.applymap(lambda x: long_number_format_with_type_check(x))

    if gtff.USE_TABULATE_DF:
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
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ps",
        df,
    )


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

    df = coinpaprika_model.basic_coin_info(coin_id)

    if df.empty:
        print("No data available\n")
        return

    if gtff.USE_TABULATE_DF:
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
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "basic",
        df,
    )
