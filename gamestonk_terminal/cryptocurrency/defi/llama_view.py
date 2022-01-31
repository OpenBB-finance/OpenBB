"""Llama View"""
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from matplotlib import ticker

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import read_data_file
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    replace_underscores_in_column_names,
)
from gamestonk_terminal.cryptocurrency.defi import llama_model
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    long_number_format,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_grouped_defi_protocols(num: int = 50, export: str = "") -> None:
    """Display top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    num: int
        Number of top dApps to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = llama_model.get_defi_protocols()
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    df = df.sort_values("tvl", ascending=False).head(num)
    df = df.set_index("name")

    chains = df.groupby("chain").size().index.values.tolist()

    for chain in chains:
        chain_filter = df.loc[df.chain == chain]
        ax.bar(x=chain_filter.index, height=chain_filter.tvl, label=chain)

    ax.set_ylabel("Total Value Locked ($)")
    ax.set_xlabel("dApp name")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: long_number_format(x))
    )
    fig.tight_layout(pad=8)
    ax.legend(ncol=2)
    ax.set_title(f"Top {num} dApp TVL grouped by chain")
    ax.grid(alpha=0.5)
    ax.tick_params(axis="x", labelrotation=90)
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gdapps",
        df,
    )


@log_start_end(log=logger)
def display_defi_protocols(
    top: int, sortby: str, descend: bool, description: bool, export: str = ""
) -> None:
    """Display information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    description: bool
        Flag to display description of protocol
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = llama_model.get_defi_protocols()
    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend)
    df = df.drop(columns="chain")

    df["tvl"] = df["tvl"].apply(lambda x: long_number_format(x))

    if not description:
        df.drop(["description", "url"], axis=1, inplace=True)
    else:
        df = df[
            [
                "name",
                "symbol",
                "category",
                "description",
                "url",
            ]
        ]

    df.columns = [replace_underscores_in_column_names(val) for val in df.columns]
    df.rename(
        columns={
            "Change 1H": "Change 1H (%)",
            "Change 1D": "Change 1D (%)",
            "Change 7D": "Change 7D (%)",
            "Tvl": "TVL ($)",
        },
        inplace=True,
    )

    print_rich_table(df.head(top), headers=list(df.columns), show_index=False)
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ldapps",
        df_data,
    )


@log_start_end(log=logger)
def display_historical_tvl(dapps: str = "", export: str = ""):
    """Displays historical TVL of different dApps
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    dapps: str
        dApps to search historical TVL. Should be split by , e.g.: anchor,sushiswap,pancakeswap
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
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
        ax.set_xlabel("Time")
        dateFmt = mdates.DateFormatter("%m/%d/%Y")

        ax.xaxis.set_major_formatter(dateFmt)
        ax.get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, _: long_number_format(x))
        )
        ax.legend()

        ax.set_title("TVL in dApps")
        ax.grid(alpha=0.5)
        ax.tick_params(axis="x", labelrotation=45)
        fig.tight_layout(pad=2)

        if gtff.USE_ION:
            plt.ion()
        plt.show()
        print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "dtvl",
            None,
        )


@log_start_end(log=logger)
def display_defi_tvl(top: int, export: str = "") -> None:
    """Displays historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = llama_model.get_defi_tvl()
    df_data = df.copy()

    df = df.tail(top)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(df["date"], df["totalLiquidityUSD"], "-ok", ms=2)
    ax.set_xlabel("Time")
    ax.set_xlim(df["date"].iloc[0], df["date"].iloc[-1])
    dateFmt = mdates.DateFormatter("%m/%d/%Y")

    ax.xaxis.set_major_formatter(dateFmt)
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_ylabel("Total Value Locked ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax.set_title("Total Value Locked in DeFi")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: long_number_format(x))
    )
    fig.tight_layout(pad=2)

    if gtff.USE_ION:
        plt.ion()
    plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stvl",
        df_data,
    )
