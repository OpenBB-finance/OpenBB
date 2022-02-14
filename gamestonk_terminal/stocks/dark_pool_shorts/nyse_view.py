"""NYSE Short Data View"""
__docformat__ = "numpy"


import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import seaborn as sns
from plotly import express as px

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.dark_pool_shorts import nyse_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_short_by_exchange(
    ticker: str,
    raw: bool = False,
    sort: str = "",
    asc: bool = False,
    mpl: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display short data by exchange

    Parameters
    ----------
    ticker : str
        Stock ticker
    raw : bool
        Flag to display raw data
    sort: str
        Column to sort by
    asc: bool
        Flag to sort in ascending order
    mpl: bool
        Flag to display using matplotlib
    export : str, optional
        Format  of export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    volume_by_exchange = nyse_model.get_short_data_by_exchange(ticker).sort_values(
        by="Date"
    )
    if volume_by_exchange.empty:
        console.print("No short data found. Please send us a question on discord")

    if sort:
        if sort in volume_by_exchange.columns:
            volume_by_exchange = volume_by_exchange.sort_values(by=sort, ascending=asc)
        else:
            console.print(
                f"{sort} not a valid option.  Selectone of {list(volume_by_exchange.columns)}.  Not sorting."
            )

    if mpl:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        sns.lineplot(
            data=volume_by_exchange, x="Date", y="NetShort", hue="Exchange", ax=ax
        )

        # remove the scientific notion on the left hand side
        ax.ticklabel_format(style="plain", axis="y")

        ax.set_xlim(
            volume_by_exchange.Date.iloc[0],
            volume_by_exchange.Date.iloc[-1],
        )

        ax.set_title(f"Net Short Volume for {ticker}")
        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    else:
        fig = px.line(
            volume_by_exchange,
            x="Date",
            y="NetShort",
            color="Exchange",
            title=f"Net Short Volume for {ticker}",
        )
        fig.show()

    if raw:
        print_rich_table(
            volume_by_exchange.head(20),
            show_index=False,
            title="Short Data",
            headers=list(volume_by_exchange.columns),
        )
    console.print("")

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "volexch",
            volume_by_exchange,
        )
