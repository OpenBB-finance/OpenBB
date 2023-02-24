"""Shroom view"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

from matplotlib import pyplot as plt

from openbb_terminal import (
    config_plot as cfgPlot,
    config_terminal as cfg,
)
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.onchain.shroom_model import (
    get_daily_transactions,
    get_dapp_stats,
    get_total_value_locked,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_daily_transactions(
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
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
        console.print("[red]No data found.[/red]")
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    for name in symbols:
        ax.plot(df.index, df[name] / 1_000_000_000, label=name, lw=0.5)

    ax.set_title("Daily Transactions in Ethereum")
    ax.set_ylabel("Transactions [in billions]")
    ax.set_xlabel("Date")
    ax.set_xlim(df.index[0], df.index[-1])
    ax.legend()

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dt",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_dapp_stats(
    platform: str,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
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
    """
    df = get_dapp_stats(platform=platform)
    if df.empty:
        console.print("[red]No data found.[/red]")
    elif not df.empty:
        if raw:
            print_rich_table(df.head(limit), headers=list(df.columns), show_index=True)

        # This plot has 1 axis
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes

        ax.bar(df.index, df["n_users"], color=theme.down_color, label="Number of Users")
        ax.set_xlim(
            df.index[0],
            df.index[-1],
        )

        ax2 = ax.twinx()
        ax2.plot(df["fees"] / 1_000_000, color=theme.up_color, label="Platform Fees")
        # ax2.plot(df["volume"], label="Volume")
        ax2.set_ylabel("Number of Users", labelpad=30)
        ax2.set_zorder(ax2.get_zorder() + 1)
        ax.patch.set_visible(False)
        ax2.yaxis.set_label_position("left")
        ax.set_ylabel(
            "Platforms Fees [USD M]", labelpad=30
        )  # attribute Deb because of $ -> USD
        ax.set_title(f"{platform} stats")
        ax.legend(loc="upper left")
        ax2.legend(loc="upper right")
        cfg.theme.style_primary_axis(ax)

        if external_axes is None:
            cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ds",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_total_value_locked(
    user_address: str,
    address_name: str,
    symbol: str = "USDC",
    interval: int = 1,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
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
        console.print("[red]No data found.[/red]")
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    # ax.plot(df.index, df["amount_usd"], label="", lw=0.5)
    ax.bar(df.index, df["amount_usd"], color=theme.down_color, label="amount_usd")
    ax.set_title("Total value locked Ethereum ERC20")
    ax.set_ylabel("Amount [USD M]")
    ax.set_xlabel("Date")
    ax.set_xlim(df.index[0], df.index[-1])
    ax.legend()

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tvl",
        df,
        sheet_name,
    )
