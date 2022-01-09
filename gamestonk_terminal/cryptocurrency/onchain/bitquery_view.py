"""The BitQuery view"""
__docformat__ = "numpy"

import os
from tabulate import tabulate

from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    very_long_number_formatter,
    prettify_column_names,
)
from gamestonk_terminal.cryptocurrency.onchain import bitquery_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console


def display_dex_trades(
    trade_amount_currency: str = "USD",
    kind: str = "dex",
    top: int = 20,
    days: int = 90,
    sortby: str = "tradeAmount",
    descend: bool = False,
    export: str = "",
) -> None:
    """Trades on Decentralized Exchanges aggregated by DEX or Month [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    kind: str
        Aggregate trades by dex or time
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    days:  int
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    if kind == "time":
        df = bitquery_model.get_dex_trades_monthly(trade_amount_currency, days)
        df = df.sort_values(by="date", ascending=descend)
    else:
        df = bitquery_model.get_dex_trades_by_exchange(trade_amount_currency, days)
        df = df.sort_values(by=sortby, ascending=descend)

    df_data = df.copy()

    df[["tradeAmount", "trades"]] = df[["tradeAmount", "trades"]].applymap(
        lambda x: very_long_number_formatter(x)
    )

    df.columns = prettify_column_names(df.columns)

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
        "lt",
        df_data,
    )


def display_daily_volume_for_given_pair(
    token: str = "WBTC",
    vs: str = "USDT",
    top: int = 20,
    sortby: str = "date",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display daily volume for given pair
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    token: str
        ERC20 token symbol or address
    vs: str
        Quote currency.
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    Returns
    -------
    pd.DataFrame
        Token volume on different decentralized exchanges
    """

    df = bitquery_model.get_daily_dex_volume_for_given_pair(
        token=token,
        vs=vs,
        limit=top,
    )

    if df.empty:
        return
    df = df.sort_values(by=sortby, ascending=descend)

    df_data = df.copy()

    df[["tradeAmount", "trades"]] = df[["tradeAmount", "trades"]].applymap(
        lambda x: very_long_number_formatter(x)
    )
    df.columns = prettify_column_names(df.columns)

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
        "dvcp",
        df_data,
    )


def display_dex_volume_for_token(
    token: str = "WBTC",
    trade_amount_currency: str = "USD",
    top: int = 10,
    sortby: str = "tradeAmount",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    token: str
        ERC20 token symbol or address
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    Returns
    -------
    pd.DataFrame
        Token volume on different decentralized exchanges
    """

    df = bitquery_model.get_token_volume_on_dexes(
        token=token,
        trade_amount_currency=trade_amount_currency,
    ).sort_values(by=sortby, ascending=descend)

    df_data = df.copy()
    df[["tradeAmount", "trades"]] = df[["tradeAmount", "trades"]].applymap(
        lambda x: very_long_number_formatter(x)
    )

    df.columns = prettify_column_names(df.columns)

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
        "tv",
        df_data,
    )


def display_ethereum_unique_senders(
    interval: str = "days",
    limit: int = 10,
    sortby: str = "date",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display number of unique ethereum addresses which made a transaction in given time interval
     [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    interval: str
        Time interval in which ethereum address made transaction. month, week or day
    limit: int
        Number of records to display. It's calculated base on provided interval.
        If interval is month then calculation is made in the way: limit * 30 = time period,
        in case if interval is set to week, then time period is calculated as limit * 7.
        For better user experience maximum time period in days is equal to 90.
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    Returns
    -------
    pd.DataFrame
        Number of unique ethereum addresses which made a transaction in given time interval
    """

    df = bitquery_model.get_ethereum_unique_senders(interval, limit).sort_values(
        by=sortby, ascending=descend
    )

    df[["uniqueSenders", "transactions", "maximumGasPrice"]] = df[
        ["uniqueSenders", "transactions", "maximumGasPrice"]
    ].applymap(lambda x: very_long_number_formatter(x))

    df_data = df.copy()
    df.columns = prettify_column_names(df.columns)

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
        "ueat",
        df_data,
    )


def display_most_traded_pairs(
    exchange="Uniswap",
    days: int = 10,
    top: int = 10,
    sortby: str = "tradeAmount",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display most traded crypto pairs on given decentralized exchange in chosen time period.
     [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    exchange:
        Decentralized exchange name
    days:
        Number of days taken into calculation account.
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    Returns
    -------
    pd.DataFrame
        Most traded crypto pairs on given decentralized exchange in chosen time period.
    """

    df = bitquery_model.get_most_traded_pairs(
        exchange=exchange, limit=days
    ).sort_values(by=sortby, ascending=descend)
    df_data = df.copy()
    df[["tradeAmount", "trades"]] = df[["tradeAmount", "trades"]].applymap(
        lambda x: very_long_number_formatter(x)
    )
    df.columns = prettify_column_names(df.columns)

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
        "ttcp",
        df_data,
    )


def display_spread_for_crypto_pair(
    token="ETH",
    vs="USDC",
    days: int = 10,
    sortby: str = "date",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display an average bid and ask prices, average spread for given crypto pair for chosen time period.
       [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    days:  int
        Last n days to query data
    token: str
        ERC20 token symbol
    vs: str
        Quoted currency.
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    pd.DataFrame
        Average bid and ask prices, spread for given crypto pair for chosen time period
    """

    df = bitquery_model.get_spread_for_crypto_pair(
        token=token, vs=vs, limit=days
    ).sort_values(by=sortby, ascending=descend)

    df.columns = prettify_column_names(df.columns)

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
        "baas",
        df,
    )
