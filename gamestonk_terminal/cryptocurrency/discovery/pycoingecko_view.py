"""CoinGecko view"""
__docformat__ = "numpy"

import os
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    very_long_number_formatter,
)
from gamestonk_terminal.cryptocurrency.discovery import pycoingecko_model
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console

register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302

COINS_COLUMNS = [
    "Symbol",
    "Name",
    "Volume [$]",
    "Market Cap [$]",
    "Market Cap Rank",
    "7D Change [%]",
    "24H Change [%]",
]


def display_coins(category: str, top: int, sortby: str, export: str) -> None:
    """Display top coins [Source: CoinGecko]

    Parameters
    ----------
    category: str
        Coingecko category. If no category is passed it will search for all coins. (E.g., smart-contract-platform)
    top: int
        Number of records to display
    sortby: str
        Key to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = pycoingecko_model.get_coins(top=top, category=category)
    if not df.empty:
        df = df[
            [
                "symbol",
                "name",
                "total_volume",
                "market_cap",
                "market_cap_rank",
                "price_change_percentage_7d_in_currency",
                "price_change_percentage_24h_in_currency",
            ]
        ]
        df = df.set_axis(
            COINS_COLUMNS,
            axis=1,
            inplace=False,
        )
        if sortby in COINS_COLUMNS:
            df = df.sort_values(by=sortby, ascending=False)
        for col in ["Volume [$]", "Market Cap [$]"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: very_long_number_formatter(x))
        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgtop",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


def display_gainers(period: str, top: int, sortby: str, export: str) -> None:
    """Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]

    Parameters
    ----------
    period: str
        Time period by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    top: int
        Number of records to display
    sortby: str
        Key to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = pycoingecko_model.get_gainers_or_losers(top=top, period=period, typ="gainers")
    if not df.empty:
        if sortby in COINS_COLUMNS:
            df = df.sort_values(by=sortby, ascending=False)
        for col in ["Volume [$]", "Market Cap [$]"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: very_long_number_formatter(x))
        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "gainers",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


def display_losers(period: str, top: int, export: str, sortby: str) -> None:
    """Shows Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]

    Parameters
    ----------
    period: str
        Time period by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    top: int
        Number of records to display
    sortby: str
        Key to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = pycoingecko_model.get_gainers_or_losers(top=top, period=period, typ="losers")
    if not df.empty:
        if sortby in COINS_COLUMNS:
            df = df.sort_values(by=sortby, ascending=False)
        for col in ["Volume [$]", "Market Cap [$]"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: very_long_number_formatter(x))
        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
        )
        console.print()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cglosers",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


def display_trending(export: str) -> None:
    """Display trending coins [Source: CoinGecko]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = pycoingecko_model.get_trending_coins()
    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            floatfmt=".4f",
            show_index=False,
            title="Trending coins on CoinGecko",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgtrending",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")
