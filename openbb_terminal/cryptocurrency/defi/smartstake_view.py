"""SentimentInvestor View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.defi import smartstake_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

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
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = smartstake_model.get_luna_supply_stats(supply_type, days)

    if df.empty:
        return None

    fig = OpenBBFigure(xaxis_title="Time", yaxis_title="Luna Circulating Supply [M]")
    fig.set_title("Luna Circulating Supply Changes (In Millions)")

    fig.add_scatter(
        x=df.index,
        y=df["circulatingSupplyInMil"],
        mode="lines",
        name="Circulating Supply",
        line=dict(color="black"),
    )
    fig.add_scatter(
        x=df.index,
        y=df["liquidCircSupplyInMil"],
        mode="lines",
        name="Liquid Circulating Supply",
        line=dict(color="red"),
    )
    fig.add_scatter(
        x=df.index,
        y=df["stakeFromCircSupplyInMil"],
        mode="lines",
        name="Stake of Supply",
        line=dict(color="green"),
    )
    fig.add_scatter(
        x=df.index,
        y=df["recentTotalLunaBurntInMil"],
        mode="lines",
        name="Supply Reduction (Luna Burnt)",
        line=dict(color="blue"),
    )

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
        fig,
    )

    df.index = df.index.strftime("%Y-%m-%d")
    df = df.sort_index(ascending=False)

    print_rich_table(
        df[RAW_COLS],
        headers=[
            "Circ Supply",
            "Liquid Circ Supply",
            "Supply Change",
            "Supply Reduction (Luna Burnt)",
        ],
        show_index=True,
        index_name="Time",
        title="Luna Circulating Supply Changes (in Millions)",
        export=bool(export),
        limit=limit,
    )

    return fig.show(external=external_axes)
