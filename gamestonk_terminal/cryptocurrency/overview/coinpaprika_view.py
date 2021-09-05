"""CoinPaprika view"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import export_data
import gamestonk_terminal.cryptocurrency.overview.coinpaprika_model as paprika
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    long_number_format_with_type_check,
)
from gamestonk_terminal import feature_flags as gtff

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
    df["Value"] = df["Value"].apply(lambda x: long_number_format_with_type_check(x))

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
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "global",
        df_data,
    )


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
        print("No data found", "\n")
        return

    cols = [col for col in df.columns if col != "rank"]
    df[cols] = df[cols].applymap(lambda x: long_number_format_with_type_check(x))

    print(f"\nDisplaying data vs {currency}")

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(top),
                headers=df.columns,
                floatfmt=".3f",
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
        "markets",
        df_data,
    )


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
        print("Not data found", "\n")
        return

    cols = [col for col in df.columns if col != "rank"]
    df[cols] = df[cols].applymap(lambda x: long_number_format_with_type_check(x))

    print(f"\nDisplaying data vs {currency}")

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(top),
                headers=df.columns,
                floatfmt=".3f",
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
        "info",
        df_data,
    )


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
        print("No data found", "\n")
        return

    cols = [col for col in df.columns if col != "rank"]
    df[cols] = df[cols].applymap(lambda x: long_number_format_with_type_check(x))
    print(f"\nDisplaying data vs {currency}")

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
        "exchanges",
        df_data,
    )


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
        print("No data found", "\n")
        return

    df = df.sort_values(by=sortby, ascending=descend)

    if links is True:
        df = df[["exchange_id", "pair", "trust_score", "market_url"]]
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
        "exmarkets",
        df_data,
    )


def display_all_platforms(export: str) -> None:
    """List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama. [Source: CoinPaprika]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = paprika.get_all_contract_platforms()

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
        "platforms",
        df,
    )


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
        print(f"Nothing found for platform: {platform}", "\n")
        return

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
        "contracts",
        df,
    )
