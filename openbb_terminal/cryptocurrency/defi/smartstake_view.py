"""SentimentInvestor View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.defi import smartstake_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)

# pylint: disable=E1101

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_SMARTSTAKE_KEY", "API_SMARTSTAKE_TOKEN"])
def display_luna_circ_supply_change(
    days: int = 30,
    export: str = "",
    sheet_name: Optional[str] = None,
    supply_type: str = "lunaSupplyChallengeStats",
    limit: int = 5,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots and prints table showing Luna circulating supply stats

    Parameters
    ----------
    days: int
        Number of days
    supply_type: str
        Supply type to unpack json
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export type
    limit: int
        Number of results display on the terminal
        Default: 5
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = smartstake_model.get_luna_supply_stats(supply_type, days)

    if df.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

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
        sheet_name,
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
