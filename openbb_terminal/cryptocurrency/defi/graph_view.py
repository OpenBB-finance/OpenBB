"""The Graph view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal import rich_config
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_very_long_number_formatter,
)
from openbb_terminal.cryptocurrency.defi import graph_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_uni_tokens(
    skip: int = 0,
    limit: int = 20,
    sortby: str = "index",
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing tokens trade-able on Uniswap DEX.
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    skip: int
        Number of records to skip
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = graph_model.get_uni_tokens(skip=skip)
    df_data = df.copy()

    # Converting these to float
    df["tradeVolumeUSD"] = df["tradeVolumeUSD"].astype(float)
    df["totalLiquidity"] = df["totalLiquidity"].astype(float)
    df["txCount"] = df["txCount"].astype(float)

    df = df.sort_values(by=sortby, ascending=ascend)

    if rich_config.USE_COLOR and not get_current_user().preferences.USE_INTERACTIVE_DF:
        df[["totalLiquidity", "tradeVolumeUSD"]] = df[
            ["totalLiquidity", "tradeVolumeUSD"]
        ].applymap(lambda x: lambda_very_long_number_formatter(x))

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="UniSwarp DEX Trade-able Tokens",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tokens",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_uni_stats(export: str = "", sheet_name: Optional[str] = None) -> None:
    """Prints table showing base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]
    [Source: https://thegraph.com/en/]

    Parameters
    ----------

    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = graph_model.get_uniswap_stats()
    df_data = df.copy()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Uniswap DEX Base Statistics",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stats",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_recently_added(
    limit: int = 20,
    days: int = 7,
    min_volume: int = 20,
    min_liquidity: int = 0,
    min_tx: int = 100,
    sortby: str = "created",
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing Lastly added pairs on Uniswap DEX.
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    limit: int
        Number of records to display
    days: int
        Number of days the pair has been active,
    min_volume: int
        Minimum trading volume,
    min_liquidity: int
        Minimum liquidity
    min_tx: int
        Minimum number of transactions
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = graph_model.get_uniswap_pool_recently_added(
        last_days=days,
        min_volume=min_volume,
        min_liquidity=min_liquidity,
        min_tx=min_tx,
    )
    df_data = df.copy()

    # Converting these to float
    df["volumeUSD"] = df["volumeUSD"].astype(float)
    df["txCount"] = df["txCount"].astype(float)
    df["totalSupply"] = df["totalSupply"].astype(float)

    df = df.sort_values(by=sortby, ascending=ascend)

    df[["volumeUSD", "totalSupply"]] = df[["volumeUSD", "totalSupply"]].applymap(
        lambda x: lambda_very_long_number_formatter(x)
    )

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Latest Added Pairs on Uniswap DEX",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pairs",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_uni_pools(
    limit: int = 20,
    sortby: str = "volumeUSD",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing uniswap pools by volume.
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://bit.ly/3ORagr1 then press ctrl-enter or execute the query).
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = graph_model.get_uni_pools_by_volume()

    # Converting these to float
    df["volumeUSD"] = df["volumeUSD"].astype(float)
    df["txCount"] = df["txCount"].astype(float)

    df = df.sort_values(by=sortby, ascending=ascend)

    df["volumeUSD"] = df["volumeUSD"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )
    df_data = df.copy()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Uniswap Pools",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pools",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_last_uni_swaps(
    limit: int = 10,
    sortby: str = "timestamp",
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing last swaps done on Uniswap
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2).
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = graph_model.get_last_uni_swaps(limit=limit, sortby=sortby, ascend=ascend)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Last Uniswap Swaps",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "swaps",
        df,
        sheet_name,
    )
