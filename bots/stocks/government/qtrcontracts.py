import io
import logging

import numpy as np
from matplotlib import pyplot as plt

import bots.config_discordbot as cfg
from bots.helpers import image_border
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def qtrcontracts_command(num: int = 20, analysis=""):
    """Displays a look at government contracts [quiverquant.com]"""
    # Debug user input
    if cfg.DEBUG:
        logger.debug("gov-qtrcontracts %s %s", num, analysis)

    possible_args = ["total", "upmom", "downmom"]
    if analysis == "":
        analysis = "total"
    elif analysis not in possible_args:
        raise Exception(
            "Enter a valid analysis argument, options are: total, upmom and downmom"
        )

    # Retrieve Data
    df_contracts = quiverquant_model.get_government_trading("quarter-contracts")

    if df_contracts.empty:
        raise Exception("No quarterly government contracts found")

    tickers = quiverquant_model.analyze_qtr_contracts(analysis, num)

    # Output Data
    if analysis in {"upmom", "downmom"}:
        description = tickers.to_string()
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        max_amount = 0
        quarter_ticks = []
        for symbol in tickers:
            amounts = (
                df_contracts[df_contracts["Ticker"] == symbol]
                .sort_values(by=["Year", "Qtr"])["Amount"]
                .values
            )

            qtr = (
                df_contracts[df_contracts["Ticker"] == symbol]
                .sort_values(by=["Year", "Qtr"])["Qtr"]
                .values
            )
            year = (
                df_contracts[df_contracts["Ticker"] == symbol]
                .sort_values(by=["Year", "Qtr"])["Year"]
                .values
            )

            ax.plot(np.arange(0, len(amounts)), amounts / 1_000_000, "-*", lw=2, ms=15)

            if len(amounts) > max_amount:
                max_amount = len(amounts)
                quarter_ticks = [
                    f"{quarter[0]} - Q{quarter[1]} " for quarter in zip(year, qtr)
                ]

        ax.set_xlim([-0.5, max_amount - 0.5])
        ax.set_xticks(np.arange(0, max_amount))
        ax.set_xticklabels(quarter_ticks)
        ax.grid()
        ax.legend(tickers)
        titles = {
            "upmom": "Highest increasing quarterly Government Contracts",
            "downmom": "Highest decreasing quarterly Government Contracts",
        }
        ax.set_title(titles[analysis])
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount ($1M)")
        fig.tight_layout()
        imagefile = "gov_qtrcontracts.png"

        dataBytesIO = io.BytesIO()
        plt.savefig(dataBytesIO)
        dataBytesIO.seek(0)

        imagefile = image_border(imagefile, base64=dataBytesIO)
        output = {
            "title": "Stocks: [quiverquant.com] Government Contracts",
            "imagefile": imagefile,
            "description": description,
        }

    elif analysis == "total":

        tickers.index = [ind + " " * (7 - len(ind)) for ind in tickers.index]
        tickers[:] = [str(round(val[0] / 1e9, 2)) for val in tickers.values]
        tickers.columns = ["Amount [M]"]

        output = {
            "title": "Stocks: [quiverquant.com] Government Contracts",
            "description": tickers.to_string(),
        }

    return output
