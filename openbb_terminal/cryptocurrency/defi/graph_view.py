"""The Graph view"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_very_long_number_formatter,
)
from openbb_terminal.cryptocurrency.defi import graph_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_uni_tokens(
    skip: int = 0,
    limit: int = 20,
    sortby: str = "index",
    descend: bool = True,
    export: str = "",
) -> None:
    """Displays tokens trade-able on Uniswap DEX.
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    skip: int
        Number of records to skip
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = graph_model.get_uni_tokens(skip=skip)
    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend)

    df[["totalLiquidity", "tradeVolumeUSD"]] = df[
        ["totalLiquidity", "tradeVolumeUSD"]
    ].applymap(lambda x: lambda_very_long_number_formatter(x))

    print_rich_table(
        df.head(limit),
        headers=list(df.columns),
        show_index=False,
        title="UniSwarp DEX Trade-able Tokens",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tokens",
        df_data,
    )


@log_start_end(log=logger)
def display_uni_stats(export: str = "") -> None:
    """Displays base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]
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
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stats",
        df_data,
    )


@log_start_end(log=logger)
def display_recently_added(
    top: int = 20,
    days: int = 7,
    min_volume: int = 20,
    min_liquidity: int = 0,
    min_tx: int = 100,
    sortby: str = "created",
    descend: bool = False,
    export: str = "",
) -> None:
    """Displays Lastly added pairs on Uniswap DEX.
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    top: int
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
    descend: bool
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

    df = df.sort_values(by=sortby, ascending=descend)

    df[["volumeUSD", "totalSupply"]] = df[["volumeUSD", "totalSupply"]].applymap(
        lambda x: lambda_very_long_number_formatter(x)
    )

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Latest Added Pairs on Uniswap DEX",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pairs",
        df_data,
    )


@log_start_end(log=logger)
def display_uni_pools(
    top: int = 20, sortby: str = "volumeUSD", descend: bool = False, export: str = ""
) -> None:
    """Displays uniswap pools by volume.
    [Source: https://thegraph.com/en/]

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
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = graph_model.get_uni_pools_by_volume().sort_values(by=sortby, ascending=descend)
    df["volumeUSD"] = df["volumeUSD"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )
    df_data = df.copy()

    print_rich_table(
        df.head(top), headers=list(df.columns), show_index=False, title="Uniswap Pools"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pools",
        df_data,
    )


@log_start_end(log=logger)
def display_last_uni_swaps(
    top: int = 20, sortby: str = "timestamp", descend: bool = False, export: str = ""
) -> None:
    """Displays last swaps done on Uniswap
    [Source: https://thegraph.com/en/]

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
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = graph_model.get_last_uni_swaps(limit=top).sort_values(
        by=sortby, ascending=descend
    )
    df["amountUSD"] = df["amountUSD"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )
    df_data = df.copy()

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Last Uniswap Swaps"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "swaps",
        df_data,
    )
