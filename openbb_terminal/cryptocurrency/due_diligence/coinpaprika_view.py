"""CoinPaprika view"""
__docformat__ = "numpy"

import logging
import os

from pandas.plotting import register_matplotlib_converters

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_long_number_format_with_type_check,
)
from openbb_terminal.cryptocurrency.due_diligence import coinpaprika_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.cryptocurrency import cryptocurrency_helpers

logger = logging.getLogger(__name__)

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


@log_start_end(log=logger)
def display_twitter(
    symbol: str = "BTC",
    top: int = 10,
    sortby: str = "date",
    descend: bool = False,
    export: str = "",
) -> None:
    """Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    # get coinpaprika id using crypto symbol
    cp_id = cryptocurrency_helpers.get_coinpaprika_id(symbol)

    df = coinpaprika_model.get_coin_twitter_timeline(cp_id)

    if df.empty:
        console.print(f"Couldn't find any tweets for coin {symbol}", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)
    # Remove unicode chars (it breaks pretty tables)
    df["status"] = df["status"].apply(
        lambda text: "".join(i if ord(i) < 128 else "" for i in text)
    )
    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Twitter Timeline",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "twitter",
        df,
    )


@log_start_end(log=logger)
def display_events(
    symbol: str = "BTC",
    top: int = 10,
    sortby: str = "date",
    descend: bool = False,
    links: bool = False,
    export: str = "",
) -> None:
    """Get all events for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
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
    # get coinpaprika id using crypto symbol
    cp_id = cryptocurrency_helpers.get_coinpaprika_id(symbol)

    df = coinpaprika_model.get_coin_events_by_id(cp_id)

    if df.empty:
        console.print(f"Couldn't find any events for coin {symbol}\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    df_data = df.copy()

    if links is True:
        df = df[["date", "name", "link"]]
    else:
        df.drop("link", axis=1, inplace=True)

    print_rich_table(
        df.head(top), headers=list(df.columns), show_index=False, title="All Events"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "events",
        df_data,
    )


@log_start_end(log=logger)
def display_exchanges(
    symbol: str = "btc",
    top: int = 10,
    sortby: str = "adjusted_volume_24h_share",
    descend: bool = False,
    export: str = "",
) -> None:
    """Get all exchanges for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    # get coinpaprika id using crypto symbol
    cp_id = cryptocurrency_helpers.get_coinpaprika_id(symbol)

    df = coinpaprika_model.get_coin_exchanges_by_id(cp_id)

    if df.empty:
        console.print("No data found", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    print_rich_table(
        df.head(top), headers=list(df.columns), show_index=False, title="All Exchanges"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ex",
        df,
    )


@log_start_end(log=logger)
def display_markets(
    symbol: str = "BTC",
    currency: str = "USD",
    top: int = 20,
    sortby: str = "pct_volume_share",
    descend: bool = False,
    links: bool = False,
    export: str = "",
) -> None:
    """Get all markets for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
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

    # get coinpaprika id using crypto symbol
    cp_id = cryptocurrency_helpers.get_coinpaprika_id(symbol)

    df = coinpaprika_model.get_coin_markets_by_id(cp_id, currency)

    if df.empty:
        console.print("There is no data \n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    df_data = df.copy()

    if links is True:
        df = df[["exchange", "pair", "trust_score", "market_url"]]
    else:
        df.drop("market_url", axis=1, inplace=True)

    print_rich_table(
        df.head(top), headers=list(df.columns), show_index=False, title="All Markets"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mkt",
        df_data,
    )


@log_start_end(log=logger)
def display_price_supply(
    symbol: str = "BTC",
    currency: str = "USD",
    export: str = "",
) -> None:
    """Get ticker information for single coin [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    currency: str
        Quoted currency
    export: str
        Export dataframe data to csv,json,xlsx

    """
    # get coinpaprika id using crypto symbol
    cp_id = cryptocurrency_helpers.get_coinpaprika_id(symbol)

    df = coinpaprika_model.get_tickers_info_for_coin(cp_id, currency)

    if df.empty:
        console.print("No data found", "\n")
        return

    df = df.applymap(lambda x: lambda_long_number_format_with_type_check(x))

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Coin Information"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ps",
        df,
    )


@log_start_end(log=logger)
def display_basic(
    symbol: str = "BTC",
    export: str = "",
) -> None:
    """Get basic information for coin. Like:
        name, symbol, rank, type, description, platform, proof_type, contract, tags, parent.  [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    export: str
        Export dataframe data to csv,json,xlsx
    """
    # get coinpaprika id using crypto symbol
    cp_id = cryptocurrency_helpers.get_coinpaprika_id(symbol)

    df = coinpaprika_model.basic_coin_info(cp_id)

    if df.empty:
        console.print("No data available\n")
        return

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Basic Coin Information"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "basic",
        df,
    )
