"""AlphaQuery View"""
__docforma__ = "numpy"

import logging
import os
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from gamestonk_terminal import feature_flags as gtff
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
    """
    pcr = alphaquery_model.get_put_call_ratio(ticker, window, start_date)
    if pcr.empty:
        console.print("No data found.\n")
        return
    dateFmt = mdates.DateFormatter("%m/%d/%Y")
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(pcr.index, pcr.values)
    ax.xaxis.set_major_formatter(dateFmt)
    ax.tick_params(axis="x", labelrotation=45)
    ax.grid("on")
    ax.axhline(y=1, lw=2, c="k")
    ax.set_title(f"Put Call Ratio for {ticker.upper()}")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pcr",
        pcr,
    )
