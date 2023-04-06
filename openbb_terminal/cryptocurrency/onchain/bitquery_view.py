"""The BitQuery view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_very_long_number_formatter,
    prettify_column_names,
)
from openbb_terminal.cryptocurrency.onchain import bitquery_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_BITQUERY_KEY"])
def display_dex_trades(
    trade_amount_currency: str = "USD",
    kind: str = "dex",
    limit: int = 20,
    days: int = 90,
    sortby: str = "tradeAmount",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing Trades on Decentralized Exchanges aggregated by DEX or Month
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    kind: str
        Aggregate trades by dex or time
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    days:  int
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    if kind == "time":
        df = bitquery_model.get_dex_trades_monthly(trade_amount_currency, days, ascend)
    else:
        df = bitquery_model.get_dex_trades_by_exchange(
            trade_amount_currency, days, sortby, ascend
        )

    if not df.empty:
        df_data = df.copy()

        column_names = ["tradeAmount", "trades"]
        column_names = prettify_column_names(column_names)

        df[column_names] = df[column_names].applymap(
            lambda x: lambda_very_long_number_formatter(x)
        )

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Trades on Decentralized Exchanges",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "lt",
            df_data,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_BITQUERY_KEY"])
def display_daily_volume_for_given_pair(
    symbol: str = "WBTC",
    to_symbol: str = "USDT",
    limit: int = 20,
    sortby: str = "date",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing daily volume for given pair
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    symbol: str
        ERC20 token symbol or address
    to_symbol: str
        Quote currency.
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    pd.DataFrame
        Token volume on different decentralized exchanges
    """

    df = bitquery_model.get_daily_dex_volume_for_given_pair(
        symbol=symbol,
        to_symbol=to_symbol,
        limit=limit,
        sortby=sortby,
        ascend=ascend,
    )

    if df.empty:
        return

    df_data = df.copy()

    df[["Trade amount", "Trades"]] = df[["Trade amount", "Trades"]].applymap(
        lambda x: lambda_very_long_number_formatter(x)
    )
    # The -d command takes the place of what would normally be -l. This means
    # we want to print out all of the data from each --day. If there is
    # more exchange data per day then we will have more than -d amount of
    # rows. If we do not change this value then only -d amount of rows will
    # be printed out, not -d amount of days which is what we want. So we set
    # this to an arbitrary amount to cover the potential for more than
    # one row per day

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Daily Volume for Pair",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dvcp",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_BITQUERY_KEY"])
def display_dex_volume_for_token(
    symbol: str = "WBTC",
    trade_amount_currency: str = "USD",
    limit: int = 10,
    sortby: str = "tradeAmount",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing token volume on different Decentralized Exchanges.
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    symbol: str
        ERC20 token symbol or address
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    pd.DataFrame
        Token volume on different decentralized exchanges
    """

    df = bitquery_model.get_token_volume_on_dexes(
        symbol=symbol,
        trade_amount_currency=trade_amount_currency,
        sortby=sortby,
        ascend=ascend,
    )
    if not df.empty:
        df_data = df.copy()

        column_names = ["tradeAmount", "trades"]
        column_names = prettify_column_names(column_names)

        df[column_names] = df[column_names].applymap(
            lambda x: lambda_very_long_number_formatter(x)
        )

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Token Volume on Exchanges",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "tv",
            df_data,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_BITQUERY_KEY"])
def display_ethereum_unique_senders(
    interval: str = "days",
    limit: int = 10,
    sortby: str = "date",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing number of unique ethereum addresses which made a transaction in given time interval
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
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    pd.DataFrame
        Number of unique ethereum addresses which made a transaction in given time interval
    """

    df = bitquery_model.get_ethereum_unique_senders(interval, limit, sortby, ascend)
    if not df.empty:
        column_names = ["uniqueSenders", "transactions", "maximumGasPrice"]
        column_names = prettify_column_names(column_names)

        df[column_names] = df[column_names].applymap(
            lambda x: lambda_very_long_number_formatter(x)
        )

        df_data = df.copy()

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Unique Ethereum Addresses",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "ueat",
            df_data,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_BITQUERY_KEY"])
def display_most_traded_pairs(
    exchange: str = "Uniswap",
    days: int = 10,
    limit: int = 10,
    sortby: str = "tradeAmount",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing most traded crypto pairs on given decentralized exchange in chosen time period.
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    exchange: str
        Decentralized exchange name
    days: int
        Number of days taken into calculation account.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    pd.DataFrame
        Most traded crypto pairs on given decentralized exchange in chosen time period.
    """

    df = bitquery_model.get_most_traded_pairs(
        exchange=exchange, limit=days, sortby=sortby, ascend=ascend
    )
    if not df.empty:
        df_data = df.copy()

        column_names = ["tradeAmount", "trades"]
        column_names = prettify_column_names(column_names)

        df[column_names] = df[column_names].applymap(
            lambda x: lambda_very_long_number_formatter(x)
        )

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Most Traded Crypto Pairs",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "ttcp",
            df_data,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_BITQUERY_KEY"])
def display_spread_for_crypto_pair(
    symbol: str = "WETH",
    to_symbol: str = "USDT",
    limit: int = 10,
    sortby: str = "date",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing an average bid and ask prices, average spread for given crypto pair for chosen
    time period. [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    symbol: str
        ERC20 token symbol
    to_symbol: str
        Quoted currency.
    limit:  int
        Last n days to query data
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    pd.DataFrame
        Average bid and ask prices, spread for given crypto pair for chosen time period
    """

    df = bitquery_model.get_spread_for_crypto_pair(
        symbol=symbol, to_symbol=to_symbol, limit=limit, sortby=sortby, ascend=ascend
    )
    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Average Spread for Given Crypto",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "baas",
            df,
            sheet_name,
        )
