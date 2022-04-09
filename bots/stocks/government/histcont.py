import io
import logging

import numpy as np
from matplotlib import pyplot as plt

from bots import imps
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale
from openbb_terminal.stocks.government import quiverquant_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def histcont_command(ticker=""):
    """Displays historical quarterly-contracts [quiverquant.com]"""
    # Debug user input
    if imps.DEBUG:
        logger.debug("gov histcont %s", ticker)

    if ticker == "":
        raise Exception("A ticker is required")

    # Retrieve Data
    df_contracts = quiverquant_model.get_government_trading(
        "quarter-contracts", ticker=ticker
    )

    if df_contracts.empty:
        logger.debug("No quarterly government contracts found")
        raise Exception("No quarterly government contracts found")

    # Output Data
    amounts = df_contracts.sort_values(by=["Year", "Qtr"])["Amount"].values

    qtr = df_contracts.sort_values(by=["Year", "Qtr"])["Qtr"].values
    year = df_contracts.sort_values(by=["Year", "Qtr"])["Year"].values

    quarter_ticks = [
        f"{quarter[0]}" if quarter[1] == 1 else "" for quarter in zip(year, qtr)
    ]

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(np.arange(0, len(amounts)), amounts / 1000, "-*", lw=2, ms=15)

    ax.set_xlim([-0.5, len(amounts) - 0.5])
    ax.set_xticks(np.arange(0, len(amounts)))
    ax.set_xticklabels(quarter_ticks)
    ax.grid()
    ax.set_title(f"Historical Quarterly Government Contracts for {ticker.upper()}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount ($1k)")
    fig.tight_layout()
    imagefile = "gov_histcont.png"

    dataBytesIO = io.BytesIO()
    plt.savefig(dataBytesIO)
    dataBytesIO.seek(0)
    plt.close("all")

    imagefile = imps.image_border(imagefile, base64=dataBytesIO)

    return {
        "title": "Stocks: Historical Quarterly Government Contract ",
        "imagefile": imagefile,
    }
