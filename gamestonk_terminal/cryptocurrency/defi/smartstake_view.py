"""SentimentInvestor View"""
__docformat__ = "numpy"

import os
from typing import Optional, List

from matplotlib import pyplot as plt

from gamestonk_terminal.cryptocurrency.defi import smartstake_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.rich_config import console

# pylint: disable=E1101

LUNA_CIR_SUPPLY_CHANGE = "lunaSupplyChallengeStats"


def display_luna_circ_supply_change(
    days: int,
    export: str,
    supply_type: str = LUNA_CIR_SUPPLY_CHANGE,
    limit: int = 5,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display Luna circulating supply stats

    Parameters
    ----------
    days: int
        Number of days
    supply_type: str
        Supply type to unpack json
    export: str
        Export type
    limit: int
        Number of results display on the terminal
        Default: 5
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    Returns
        None
    -------
    """

    df = smartstake_model.get_luna_supply_stats(supply_type, days)

    if df.empty:
        print("Error in SmartStake request")
    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        ax.plot(
            df.index,
            df["circulatingSupplyInMil"],
            c="black",
            label="Circulating Supply",
        )
        ax.plot(
            df.index,
            df["liquidCircSupplyInMil"],
            c="red",
            label="Liquid Circulating Supply",
        )
        ax.plot(
            df.index, df["stakeFromCircSupplyInMil"], c="green", label="Stake of Supply"
        )
        ax.plot(
            df.index,
            df["recentTotalLunaBurntInMil"],
            c="blue",
            label="Supply Reduction (Luna Burnt)",
        )

        ax.grid()
        ax.set_ylabel("Millions")
        ax.set_xlabel("Time")
        ax.set_title("Luna Circulating Supply Changes (In Millions)")
        ax.set_xlim(df.index[0], df.index[-1])
        ax.legend(loc="best")

        theme.style_primary_axis(ax)

        if external_axes is None:
            theme.visualize_output()

        RAW_COLS = [
            "circulatingSupplyInMil",
            "liquidCircSupplyInMil",
            "circSupplyChangeInMil",
            "recentTotalLunaBurntInMil",
        ]

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "lcsc",
            df[RAW_COLS],
        )

        df.index = df.index.strftime("%Y-%m-%d")
        df = df.sort_index(ascending=False)

        print_rich_table(
            df[RAW_COLS].head(limit),
            headers=[
                "Circ Supply",
                "Liquid Circ Supply",
                "Supply Change",
                "Supply Reduction (Luna Burnt)",
            ],
            show_index=True,
            index_name="Time",
            title="Luna Circulating Supply Changes (in Millions)",
        )
