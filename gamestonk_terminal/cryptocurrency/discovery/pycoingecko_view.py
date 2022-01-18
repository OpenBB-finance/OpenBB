"""CoinGecko view"""
__docformat__ = "numpy"

import os
from pandas.plotting import register_matplotlib_converters
from rich.console import Console

from tabulate import tabulate
from gamestonk_terminal.cryptocurrency.discovery import pycoingecko_model
from gamestonk_terminal.helper_funcs import export_data, rich_table_from_df
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console

register_matplotlib_converters()

t_console = Console()

# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302


def display_coins(category: str, top: int, export: str) -> None:
    """Shows top coins [Source: CoinGecko]

    Parameters
    ----------
    category: str

    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = pycoingecko_model.get_coins(top=top, category=category)
    print(df)
    if not df.empty:
        df = df[
            [
                "symbol",
                "name",
                "market_cap",
                "market_cap_rank",
                "price_change_percentage_7d_in_currency",
                "price_change_percentage_24h_in_currency",
                "total_volume",
            ]
        ]
        if gtff.USE_TABULATE_DF:
            t_console.print(
                rich_table_from_df(
                    df.head(top),
                    headers=list(df.columns),
                    floatfmt=".4f",
                    show_index=False,
                ),
                "\n",
            )
        else:
            t_console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgtop",
            df,
        )
    else:
        t_console.print("\nUnable to retrieve data from CoinGecko.\n")


def display_gainers(period: str, top: int, export: str) -> None:
    """Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]

    Parameters
    ----------
    period: str
        Time period by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = pycoingecko_model.get_gainers_or_losers(top=top, period=period, typ="gainers")
    if not df.empty:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df.head(top),
                    headers=df.columns,
                    floatfmt=".4f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
                "\n",
            )
        else:
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "gainers",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_losers(period: str, top: int, export: str) -> None:
    """Shows Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]

    Parameters
    ----------
    period: str
        Time period by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = pycoingecko_model.get_gainers_or_losers(top=top, period=period, typ="losers")
    if not df.empty:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df.head(top),
                    headers=df.columns,
                    floatfmt=".4f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
                "\n",
            )
        else:
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "losers",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_trending(export: str) -> None:
    """Display trending coins [Source: CoinGecko]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = pycoingecko_model.get_trending_coins()
    if not df.empty:
        if gtff.USE_TABULATE_DF:
            t_console.print(
                rich_table_from_df(
                    df,
                    headers=list(df.columns),
                    floatfmt=".4f",
                    show_index=False,
                    title="Trending coins on CoinGecko",
                ),
                "\n",
            )
        else:
            t_console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgtrending",
            df,
        )
    else:
        t_console.print("\nUnable to retrieve data from CoinGecko.\n")


def display_top_defi_coins(
    top: int,
    export: str
    # top: int, sortby: str, descend: bool, links: bool, export: str
) -> None:
    """Shows Top 100 DeFi Coins by Market Capitalization from "https://www.coingecko.com/en/defi"
    DeFi or Decentralized Finance refers to financial services that are built
    on top of distributed networks with no central intermediaries. [Source: CoinGecko]

    Parameters
    ----------
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

    res = pycoingecko_model.get_top_defi_coins(top)
    stats_str = res[0]
    df = res[1]
    if df.empty:
        console.print("No available data\n")
    else:
        console.print("\n", stats_str, "\n")
        if gtff.USE_TABULATE_DF:
            console.print(
                rich_table_from_df(
                    df.head(top),
                    headers=list(df.columns),
                    floatfmt=".4f",
                    show_index=False,
                ),
                "\n",
            )
        else:
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "defi",
            df,
        )


def display_top_volume_coins(top: int, export: str) -> None:
    """Shows Top 100 Coins by Trading Volume from "https://www.coingecko.com/en/yield-farming" [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = pycoingecko_model.get_top_volume_coins(top)

    if not df.empty:
        # df = df.sort_values(by=sortby, ascending=descend)
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df.head(top),
                    headers=df.columns,
                    floatfmt=".4f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
                "\n",
            )
        else:
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "volume",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")
