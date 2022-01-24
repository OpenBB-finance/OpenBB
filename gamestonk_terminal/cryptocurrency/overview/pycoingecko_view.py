"""CoinGecko view"""
__docformat__ = "numpy"

import os
import textwrap
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
import gamestonk_terminal.cryptocurrency.overview.pycoingecko_model as gecko
from gamestonk_terminal.rich_config import console

register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302


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
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title=f"{stats_string}"
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "hold",
            df,
        )


def display_nft_of_the_day(export: str) -> None:
    """Shows NFT of the day "https://www.coingecko.com/en/nft" [Source: CoinGecko]

    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

    Parameters
    ----------
    export: str
        Export dataframe data to csv,json,xlsx
    """

    df = gecko.get_nft_of_the_day()

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="NFT of the Day"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "nftday",
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

    df = gecko.get_nft_market_status()
    if not df.empty:
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="NFT Market Overview"
        )
        console.print("")

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
        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Exchange Rates",
        )
        console.print("")

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
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Global Crypto Statistics",
        )
        console.print("")

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
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Global DEFI Statistics",
        )
        console.print("")

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


def display_stablecoins(
    sortby: str, descend: bool, top: int, links: bool, export: str
) -> None:
    """Shows stablecoins data from "https://www.coingecko.com/en/stablecoins". [Source: CoinGecko]

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

    df = gecko.get_stable_coins()

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)
        df_data = df.copy()

        if links is True:
            df = df[["Rank", "Name", "Symbol", "Url"]]
        else:
            df.drop("Url", axis=1, inplace=True)

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Stablecoin Data",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "stables",
            df_data,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_news(
    sortby: str, descend: bool, top: int, links: bool, export: str
) -> None:
    """Shows latest crypto news. [Source: CoinGecko]

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

    df = gecko.get_news(n=top)

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)
        df_data = df.copy()

        df["Title"] = df["Title"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=65)) if isinstance(x, str) else x
        )

        if not links:
            df.drop("Url", axis=1, inplace=True)
        else:
            df = df[["Index", "Url"]]

        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Latest Crypto News"
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "news",
            df_data,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


def display_categories(
    sortby: str, descend: bool, top: int, links: bool, export: str
) -> None:
    """Shows top cryptocurrency categories by market capitalization from https://www.coingecko.com/en/categories

    The cryptocurrency category ranking is based on market capitalization. [Source: CoinGecko]

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

    df = gecko.get_top_crypto_categories()

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)
        df_data = df.copy()

        if not links:
            df.drop("Url", axis=1, inplace=True)
        else:
            df = df[["Rank", "Name", "Url"]]

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Top Crypto Categories by Market Cap",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "categories",
            df_data,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


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

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Top CoinGecko Exchanges",
        )
        console.print("")

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

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Financial Platforms",
        )
        console.print("")

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

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Financial Products",
        )
        console.print("")

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

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Crypto Indexes",
        )
        console.print("")

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

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Crypto Derivatives",
        )
        console.print("")

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
