import numpy as np
from matplotlib import pyplot as plt

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import image_border
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model


def histcont_command(ticker=""):
    """Displays historical quarterly-contracts [quiverquant.com]"""
    # Debug user input
    if cfg.DEBUG:
        logger.debug("gov-histcont %s", ticker)

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

    plt.savefig("gov_histcont.png")
    imagefile = "gov_histcont.png"

    imagefile = image_border(imagefile)
    return {
        "title": "Stocks: Historical Quarterly Government Contract ",
        "imagefile": imagefile,
    }
