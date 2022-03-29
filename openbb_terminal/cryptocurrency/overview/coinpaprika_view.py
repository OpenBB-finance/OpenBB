"""CoinPaprika view"""
__docformat__ = "numpy"

import logging
import os

from pandas.plotting import register_matplotlib_converters

import openbb_terminal.cryptocurrency.overview.coinpaprika_model as paprika
from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_long_number_format_with_type_check,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

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

# see https://github.com/GamestonkTerminal/GamestonkTerminal/pull/562#issuecomment-887842888
# EXCHANGES = paprika.get_list_of_exchanges()


@log_start_end(log=logger)
def display_global_market(export: str) -> None:
    """Return data frame with most important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated [Source: CoinPaprika]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = paprika.get_global_market()
    df_data = df.copy()
    df["Value"] = df["Value"].apply(
        lambda x: lambda_long_number_format_with_type_check(x)
    )

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Global Crypto Statistics"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "global",
        df_data,
    )


@log_start_end(log=logger)
def display_all_coins_market_info(
    currency: str, sortby: str, descend: bool, top: int, export: str
) -> None:
    """Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]

    Parameters
    ----------
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

    df = paprika.get_coins_market_info(quotes=currency).sort_values(
        by=sortby, ascending=descend
    )

    df_data = df.copy()

    if df.empty:
        console.print("No data found", "\n")
        return

    cols = [col for col in df.columns if col != "rank"]
    df[cols] = df[cols].applymap(lambda x: lambda_long_number_format_with_type_check(x))

    console.print(f"\nDisplaying data vs {currency}")

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Basic Market Information",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "markets",
        df_data,
    )


@log_start_end(log=logger)
def display_all_coins_info(
    currency: str, sortby: str, descend: bool, top: int, export: str
) -> None:
    """Displays basic coin information for all coins from CoinPaprika API. [Source: CoinPaprika]

    Parameters
    ----------
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

    df = paprika.get_coins_info(quotes=currency).sort_values(
        by=sortby, ascending=descend
    )

    df_data = df.copy()

    if df.empty:
        console.print("Not data found", "\n")
        return

    cols = [col for col in df.columns if col != "rank"]
    df[cols] = df[cols].applymap(lambda x: lambda_long_number_format_with_type_check(x))

    console.print(f"\nDisplaying data vs {currency}")

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Basic Coin Information",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        df_data,
    )


@log_start_end(log=logger)
def display_all_exchanges(
    currency: str, sortby: str, descend: bool, top: int, export: str
) -> None:
    """List exchanges from CoinPaprika API. [Source: CoinPaprika]

    Parameters
    ----------
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

    df = paprika.get_list_of_exchanges(quotes=currency).sort_values(
        by=sortby, ascending=descend
    )

    df_data = df.copy()

    if df.empty:
        console.print("No data found", "\n")
        return

    cols = [col for col in df.columns if col != "rank"]
    df[cols] = df[cols].applymap(lambda x: lambda_long_number_format_with_type_check(x))
    console.print(f"\nDisplaying data vs {currency}")

    print_rich_table(
        df.head(top), headers=list(df.columns), show_index=False, title="List Exchanges"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "exchanges",
        df_data,
    )


@log_start_end(log=logger)
def display_exchange_markets(
    exchange: str, sortby: str, descend: bool, top: int, links: bool, export: str
) -> None:
    """Get all markets for given exchange [Source: CoinPaprika]

    Parameters
    ----------
    exchange: str
        Exchange identifier e.g Binance
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

    df = paprika.get_exchanges_market(exchange_id=exchange)

    df_data = df.copy()

    if df.empty:
        console.print("No data found", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    if links is True:
        df = df[["exchange_id", "pair", "trust_score", "market_url"]]
    else:
        df.drop("market_url", axis=1, inplace=True)

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Exchange Markets",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "exmarkets",
        df_data,
    )


@log_start_end(log=logger)
def display_all_platforms(export: str) -> None:
    """List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama. [Source: CoinPaprika]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = paprika.get_all_contract_platforms()

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Smart Contract Platforms"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "platforms",
        df,
    )


@log_start_end(log=logger)
def display_contracts(
    platform: str, sortby: str, descend: bool, top: int, export: str
) -> None:
    """Gets all contract addresses for given platform. [Source: CoinPaprika]

    Parameters
    ----------
    platform: str
        Blockchain platform like eth-ethereum
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = paprika.get_contract_platform(platform)

    if df.empty:
        console.print(f"Nothing found for platform: {platform}", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Contract Addresses",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "contracts",
        df,
    )
