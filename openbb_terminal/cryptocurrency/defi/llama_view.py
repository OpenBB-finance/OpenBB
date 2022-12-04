"""Llama View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
from matplotlib import ticker

from openbb_terminal import config_terminal as cfg
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import read_data_file
from openbb_terminal.cryptocurrency.defi import llama_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_grouped_defi_protocols(
    limit: int = 50, export: str = "", external_axes: Optional[List[plt.Axes]] = None
) -> None:
    """Plots top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    num: int
        Number of top dApps to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = llama_model.get_defi_protocols(limit, drop_chain=False)
    chains = llama_model.get_grouped_defi_protocols(limit)

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=(14, 8), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = iter(cfg.theme.get_colors(reverse=True))

    for chain in chains:
        chain_filter = df.loc[df.Chain == chain]
        ax.barh(
            y=chain_filter.index,
            width=chain_filter["TVL ($)"],
            label=chain,
            height=0.5,
            color=next(colors, "#B6A9CB"),
        )

    ax.set_xlabel("Total Value Locked ($)")
    ax.set_ylabel("Decentralized Application Name")
    ax.get_xaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )

    ax.set_title(f"Top {limit} dApp TVL grouped by chain")
    cfg.theme.style_primary_axis(ax)
    ax.tick_params(axis="y", labelsize=8)

    ax.yaxis.set_label_position("left")
    ax.yaxis.set_ticks_position("left")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc="best")

    if not external_axes:
        cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gdapps",
        chains,
    )


@log_start_end(log=logger)
def display_defi_protocols(
    sortby: str,
    limit: int = 20,
    ascend: bool = False,
    description: bool = False,
    export: str = "",
) -> None:
    """Prints table showing information about listed DeFi protocols, their current TVL and changes to it in
    the last hour/day/week. [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    description: bool
        Flag to display description of protocol
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = llama_model.get_defi_protocols(limit, sortby, ascend, description)

    print_rich_table(df.head(limit), headers=list(df.columns), show_index=False)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ldapps",
        df,
    )


@log_start_end(log=logger)
def display_historical_tvl(
    dapps: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots historical TVL of different dApps
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    dapps: str
        dApps to search historical TVL. Should be split by , e.g.: anchor,sushiswap,pancakeswap
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    available_protocols = read_data_file("defillama_dapps.json")

    if isinstance(available_protocols, dict):
        for dapp in dapps.split(","):
            if dapp in available_protocols.keys():
                df = llama_model.get_defi_protocol(dapp)
                if not df.empty:
                    ax.plot(df, label=available_protocols[dapp])
            else:
                print(f"{dapp} not found\n")

        ax.set_ylabel("Total Value Locked ($)")
        ax.get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
        )
        cfg.theme.style_primary_axis(ax)
        ax.legend()
        ax.set_title("TVL in dApps")

        if not external_axes:
            cfg.theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "dtvl",
            None,
        )


@log_start_end(log=logger)
def display_defi_tvl(
    limit: int = 5,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        Number of records to display, by default 5
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    df = llama_model.get_defi_tvl()
    df_data = df.copy()
    df = df.tail(limit)

    ax.plot(df["date"], df["totalLiquidityUSD"], ms=2)
    # ax.set_xlim(df["date"].iloc[0], df["date"].iloc[-1])

    ax.set_ylabel("Total Value Locked ($)")
    ax.set_title("Total Value Locked in DeFi")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )
    cfg.theme.style_primary_axis(ax)

    if not external_axes:
        cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stvl",
        df_data,
    )
