"""AlphaQuery View"""
__docforma__ = "numpy"

from typing import Optional, List
import logging
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.options import alphaquery_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_put_call_ratio(
    ticker: str,
    window: int = 30,
    start_date: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display put call ratio [Source: AlphaQuery.com]

    Parameters
    ----------
    ticker : str
        Stock ticker
    window : int, optional
        Window length to look at, by default 30
    start_date : str, optional
        Starting date for data, by default (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    pcr = alphaquery_model.get_put_call_ratio(ticker, window, start_date)
    if pcr.empty:
        console.print("No data found.\n")
        return

    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(pcr.index, pcr.values)
    ax.set_title(f"Put Call Ratio for {ticker.upper()}")
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pcr",
        pcr,
    )
