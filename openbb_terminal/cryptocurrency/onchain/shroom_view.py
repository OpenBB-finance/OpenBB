"""Shroom view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.cryptocurrency.onchain.shroom_model import (
    get_daily_transactions,
    get_dapp_stats,
    get_query_data,
    get_total_value_locked,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_query(
    query: str,
    sheet_name: Optional[str] = None,
    limit: int = 10,
    export: str = "",
):
    """Display query results from shroom
    [Source: https://sdk.flipsidecrypto.xyz/shroomdk]

    Parameters
    ----------
    query : str
        Query string
    raw : bool
        Show raw data
    limit : int
        Limit of rows
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = get_query_data(query)
    if df.empty:
        console.print("[red]No data found.[/red]")
    elif not df.empty:
        print_rich_table(df, limit=limit)

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "query", df, sheet_name
        )


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_daily_transactions(
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Get daily transactions for certain symbols in ethereum blockchain
    [Source: https://sdk.flipsidecrypto.xyz/shroomdk]

    Parameters
    ----------

    export : str
        Export dataframe data to csv,json,xlsx file
    """
    symbols = ["DAI", "USDT", "BUSD", "USDC"]
    df = get_daily_transactions(symbols)
    if df.empty:
        return console.print("[red]No data found.[/red]")

    fig = OpenBBFigure(yaxis_title="Transactions", xaxis_title="Date")
    fig.set_title("Daily Transactions in Ethereum")

    for name in symbols:
        fig.add_scatter(x=df.index, y=df[name], name=name)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dt",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_dapp_stats(
    platform: str,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Get daily transactions for certain symbols in ethereum blockchain
    [Source: https://sdk.flipsidecrypto.xyz/shroomdk]

    Parameters
    ----------
    platform : str
        Platform name (e.g., uniswap-v3)
    raw : bool
        Show raw data
    limit : int
        Limit of rows
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = get_dapp_stats(platform=platform)
    if df.empty:
        return console.print("[red]No data found.[/red]")

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            export=bool(export),
            limit=limit,
        )

    fig = OpenBBFigure.create_subplots(specs=[[{"secondary_y": True}]])
    fig.set_title(f"{platform} stats")

    fig.add_bar(
        x=df.index,
        y=df["n_users"],
        name="Number of Users",
        marker_color=theme.down_color,
        secondary_y=False,
    )

    fig.add_scatter(
        x=df.index,
        y=df["fees"],
        name="Platform Fees",
        marker_color=theme.up_color,
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Number of Users", secondary_y=False, side="left")
    fig.update_yaxes(title_text="Platform Fees [USD]", secondary_y=True)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ds",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_total_value_locked(
    user_address: str,
    address_name: str,
    symbol: str = "USDC",
    interval: int = 1,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    Get total value locked for a certain address
    TVL measures the total amount of a token that is locked in a contract.
    [Source: https://sdk.flipsidecrypto.xyz/shroomdk]

    Parameters
    ----------
    user_address : str
        Address of the user (e.g., 0xa5407eae9ba41422680e2e00537571bcc53efbfd)
    address_name : str
        Name of the address (e.g., makerdao gem join usdc)
    symbol : str
        Symbol of the token
    interval : int
        Interval of months
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    # example user_address :
    # example addres_name :

    df = get_total_value_locked(
        user_address=user_address,
        address_name=address_name,
        symbol=symbol,
        interval=interval,
    )

    if df.empty:
        return console.print("[red]No data found.[/red]")

    fig = OpenBBFigure(yaxis_title="Amount [USD M]", xaxis_title="Date")
    fig.set_title("Total value locked Ethereum ERC20")

    fig.add_bar(
        x=df.index,
        y=df["amount_usd"],
        name="amount_usd",
        marker_color=theme.down_color,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tvl",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
