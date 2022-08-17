"""NYSE Short Data View"""
__docformat__ = "numpy"


import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import seaborn as sns
from plotly import express as px

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import nyse_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_short_by_exchange(
    symbol: str,
    raw: bool = False,
    sortby: str = "",
    ascending: bool = False,
    mpl: bool = True,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display short data by exchange

    Parameters
    ----------
    symbol : str
        Stock ticker
    raw : bool
        Flag to display raw data
    sortby: str
        Column to sort by
    ascending: bool
        Sort in ascending order
    mpl: bool
        Display using matplotlib
    export : str, optional
        Format  of export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    volume_by_exchange = nyse_model.get_short_data_by_exchange(symbol).sort_values(
        by="Date"
    )
    if volume_by_exchange.empty:
        console.print("No short data found. Please send us a question on discord")

    if sortby:
        if sortby in volume_by_exchange.columns:
            volume_by_exchange = volume_by_exchange.sort_values(
                by=sortby, ascending=ascending
            )
        else:
            console.print(
                f"{sortby} not a valid option. Selectone of {list(volume_by_exchange.columns)}. Not sorting."
            )

    if mpl:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        sns.lineplot(
            data=volume_by_exchange, x="Date", y="NetShort", hue="Exchange", ax=ax
        )

        # remove the scientific notion on the left hand side
        ax.ticklabel_format(style="plain", axis="y")

        ax.set_xlim(
            volume_by_exchange.Date.iloc[0],
            volume_by_exchange.Date.iloc[-1],
        )

        ax.set_title(f"Net Short Volume for {symbol}")
        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    else:
        fig = px.line(
            volume_by_exchange,
            x="Date",
            y="NetShort",
            color="Exchange",
            title=f"Net Short Volume for {symbol}",
        )
        fig.show()

    if raw:
        print_rich_table(
            volume_by_exchange.head(20),
            show_index=False,
            title="Short Data",
            headers=list(volume_by_exchange.columns),
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "volexch",
            volume_by_exchange,
        )
