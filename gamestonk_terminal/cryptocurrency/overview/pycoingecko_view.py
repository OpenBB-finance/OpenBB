"""CoinGecko view"""
__docformat__ = "numpy"

import os
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    long_number_format_with_type_check,
)
from rich.console import Console
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import (
    export_data,
    rich_table_from_df,
)
import gamestonk_terminal.cryptocurrency.overview.pycoingecko_model as gecko
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console

register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302

t_console = Console()


def display_holdings_overview(coin: str, export: str) -> None:
    """Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]

    Parameters
    ----------
    coin: str
        Cryptocurrency: ethereum or bitcoin
    export: str
        Export dataframe data to csv,json,xlsx
    """

    res = gecko.get_holdings_overview(coin)
    stats_string = res[0]
    df = res[1]

    if df.empty:
        console.print("\nZero companies holding this crypto\n")
    else:
        console.print(f"\n{stats_string}\n")
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
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cghold",
            df,
        )


def display_nft_market_status(export: str) -> None:
    """Shows overview data of nft markets "https://www.coingecko.com/en/nft" [Source: CoinGecko]

    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

    Parameters
    ----------
    export: str
        Export dataframe data to csv,json,xlsx
    """

    df = gecko.get_nft_data()
    if not df.empty:
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
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "nft",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_exchange_rates(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_exchange_rates().sort_values(by=sortby, ascending=descend)

    if not df.empty:
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
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "exrates",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_global_market_info(export: str) -> None:
    """Shows global statistics about crypto. [Source: CoinGecko]
        - market cap change
        - number of markets
        - icos
        - number of active crypto
        - market_cap_pct

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_global_info()

    if not df.empty:
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
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "global",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_global_defi_info(export: str) -> None:
    """Shows global statistics about Decentralized Finances. [Source: CoinGecko]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_global_defi_info()

    if not df.empty:
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
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "defi",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_stablecoins(top: int, export: str, sortby: str, descend: bool) -> None:
    """Shows stablecoins data [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_stable_coins(top)

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend).head(top)
        df = df.set_axis(
            [
                "Symbol",
                "Name",
                "Price ($)",
                "Market Cap ($)",
                "Market Cap Rank",
                "Change 24h (%)",
                "Change 7d (%)",
                "Volume ($)",
            ],
            axis=1,
            inplace=False,
        )
        total_market_cap = int(df["Market Cap ($)"].sum())
        df = df.applymap(lambda x: long_number_format_with_type_check(x))
        console.print(
            f"""
First {top} stablecoins have a total {long_number_format_with_type_check(total_market_cap)} dollards of market cap.
"""
        )
        if gtff.USE_TABULATE_DF:
            console.print(
                rich_table_from_df(
                    df.head(top),
                    headers=list(df.columns),
                    floatfmt=".2f",
                    show_index=False,
                ),
                "\n",
            )
        else:
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgstables",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


def display_categories(sortby: str, top: int, export: str) -> None:
    """Shows top cryptocurrency categories by market capitalization from https://www.coingecko.com/en/categories

    The cryptocurrency category ranking is based on market capitalization. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_top_crypto_categories(sortby)
    if not df.empty:
        if gtff.USE_TABULATE_DF:
            t_console.print(
                rich_table_from_df(
                    df.head(top),
                    headers=list(df.columns),
                    floatfmt=".2f",
                    show_index=False,
                ),
                "\n",
            )
        else:
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgcategories",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


def display_exchanges(
    sortby: str, descend: bool, top: int, links: bool, export: str
) -> None:
    """Shows list of top exchanges from CoinGecko. [Source: CoinGecko]

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

    df = gecko.get_exchanges()

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

        if links is True:
            df = df[["Rank", "Name", "Url"]]
        else:
            df.drop("Url", axis=1, inplace=True)

        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df.head(top),
                    headers=df.columns,
                    floatfmt=".1f",
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
            "exchanges",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_platforms(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows list of financial platforms. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_financial_platforms()

    if not df.empty:
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
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "platforms",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_products(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows list of financial products. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_finance_products()

    if not df.empty:
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
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "products",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_indexes(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows list of crypto indexes. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_indexes()
    if not df.empty:
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
            console.print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "indexes",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_derivatives(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows  list of crypto derivatives. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_derivatives()

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

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
            "derivatives",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")
