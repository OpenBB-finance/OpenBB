"""CoinGecko view"""
__docformat__ = "numpy"

import os
from pandas.plotting import register_matplotlib_converters
from tabulate import tabulate
from gamestonk_terminal.cryptocurrency.discovery import pycoingecko_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302


def display_gainers(
    period: str, top: int, sortby: str, descend: bool, links: bool, export: str
) -> None:
    """Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]

    Parameters
    ----------
    period: str
        Time period by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
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

    if sortby == "Change":
        sortby = f"%Change_{period}"

    df = pycoingecko_model.get_gainers_or_losers(period=period, typ="gainers")
    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

        df_data = df.copy()

        if not links:
            df.drop("Url", axis=1, inplace=True)

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
            print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "gainers",
            df_data,
        )
    else:
        print("")
        print("Unable to retrieve data from CoinGecko.")
        print("")


def display_losers(
    period: str, top: int, sortby: str, descend: bool, links: bool, export: str
) -> None:
    """Shows Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]

    Parameters
    ----------
    period: str
        Time period by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
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

    if sortby == "Change":
        sortby = f"%Change_{period}"

    df = pycoingecko_model.get_gainers_or_losers(period=period, typ="losers")
    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

        df_data = df.copy()

        if not links:
            df.drop("Url", axis=1, inplace=True)

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
            print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "losers",
            df_data,
        )
    else:
        print("")
        print("Unable to retrieve data from CoinGecko.")
        print("")


def display_discover(
    category: str, top: int, sortby: str, descend: bool, links: bool, export: str
) -> None:
    """Discover coins by different categories. [Source: CoinGecko]
        - Most voted coins
        - Most popular coins
        - Recently added coins
        - Most positive sentiment coins

    Parameters
    ----------
    category: str
        one from list: [trending, most_voted, positive_sentiment, most_visited]
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

    df = pycoingecko_model.get_discovered_coins(category=category)
    if not df.empty:
        df.index = df.index + 1
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Rank"}, inplace=True)

        df = df.sort_values(by=sortby, ascending=descend)

        df_data = df.copy()

        if not links:
            df.drop("Url", axis=1, inplace=True)

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
            print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            category,
            df_data,
        )
    else:
        print("")
        print("Unable to retrieve data from CoinGecko.")
        print("")


def display_recently_added(
    top: int, sortby: str, descend: bool, links: bool, export: str
) -> None:
    """Shows recently added coins from "https://www.coingecko.com/en/coins/recently_added" [Source: CoinGecko]

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

    df = pycoingecko_model.get_recently_added_coins().sort_values(
        by=sortby, ascending=descend
    )

    df_data = df.copy()

    if links is True:
        df = df[["Rank", "Symbol", "Added", "Url"]]
    else:
        df.drop("Url", axis=1, inplace=True)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(top),
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
        "recently",
        df_data,
    )


def display_top_defi_coins(
    top: int, sortby: str, descend: bool, links: bool, export: str
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

    df = pycoingecko_model.get_top_defi_coins().sort_values(
        by=sortby, ascending=descend
    )

    df_data = df.copy()

    if links is True:
        df = df[["Rank", "Name", "Symbol", "Url"]]
    else:
        df.drop("Url", axis=1, inplace=True)

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
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "defi",
        df_data,
    )


def display_top_dex(top: int, sortby: str, descend: bool, export: str) -> None:
    """Shows Top Decentralized Exchanges on CoinGecko by Trading Volume from "https://www.coingecko.com/en/dex"
    [Source: CoinGecko]

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

    df = pycoingecko_model.get_top_dexes().sort_values(by=sortby, ascending=descend)

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
        "dex",
        df,
    )


def display_top_volume_coins(top: int, sortby: str, descend: bool, export: str) -> None:
    """Shows Top 100 Coins by Trading Volume from "https://www.coingecko.com/en/yield-farming" [Source: CoinGecko]

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

    df = pycoingecko_model.get_top_volume_coins()

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
            print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "volume",
            df,
        )
    else:
        print("")
        print("Unable to retrieve data from CoinGecko.")
        print("")


def display_top_nft(
    top: int, sortby: str, descend: bool, links: bool, export: str
) -> None:
    """Shows Top 100 NFT Coins by Market Capitalization from "https://www.coingecko.com/en/nft"
    Top 100 NFT Coins by Market Capitalization
    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
    [Source: CoinGecko]

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

    df = pycoingecko_model.get_top_nfts().sort_values(by=sortby, ascending=descend)

    if not df.empty:
        df_data = df.copy()

        if links is True:
            df = df[["Rank", "Name", "Symbol", "Url"]]
        else:
            df.drop("Url", axis=1, inplace=True)

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
            print(df.to_string, "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "nft",
            df_data,
        )
    else:
        print("")
        print("Unable to retrieve data from CoinGecko.")
        print("")


def display_yieldfarms(top: int, sortby: str, descend: bool, export: str) -> None:
    """Shows Top Yield Farming Pools by Value Locked from "https://www.coingecko.com/en/yield-farming"
    [Source: CoinGecko]

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

    df = pycoingecko_model.get_yield_farms()

    if not df.empty:
        df_data = df.copy()

        df = df.sort_values(by=sortby, ascending=descend)

        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df.head(top),
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
            "yfarms",
            df_data,
        )
    else:
        print("")
        print("Unable to retrieve data from CoinGecko.")
        print("")
