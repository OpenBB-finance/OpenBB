"""Llama View"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
import matplotlib.pyplot as plt
from gamestonk_terminal.cryptocurrency.defi import llama_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    long_number_format,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI


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
        "llama",
        df_data,
    )


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
    df["totalLiquidityUSD"] = df["totalLiquidityUSD"] / 1_000_000_000

    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    plt.plot(df["date"], df["totalLiquidityUSD"], "-ok", ms=2)
    plt.xlabel("Time")
    plt.xlim(df["date"].iloc[0], df["date"].iloc[-1])
    plt.gcf().autofmt_xdate()
    plt.ylabel("Total Value Locked USD [1B]")
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    plt.title("Total Value Locked in DeFi [Billions USD]")
    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tvl",
        df_data,
    )
