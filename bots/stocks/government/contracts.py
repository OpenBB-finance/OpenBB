from typing import Union

from matplotlib import pyplot as plt
import pandas as pd
from bots.config_discordbot import logger
import bots.config_discordbot as cfg
from bots.helpers import image_border
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model


def contracts_command(
    ticker: str = "", past_transaction_days: Union[int, str] = 10, raw: bool = False
):
    """Displays contracts associated with tickers [quiverquant.com]"""
    past_transaction_days = int(past_transaction_days)
    # Debug user input
    if cfg.DEBUG:
        logger.debug("gov-contracts %s %s %s", ticker, past_transaction_days, raw)

    if ticker == "":
        raise Exception("A ticker is required")

    # Retrieve Data
    df_contracts = quiverquant_model.get_government_trading("contracts", ticker)

    if df_contracts.empty:
        return {
            "title": f"Stocks: [quiverquant.com] Contracts by {ticker}",
            "description": f"{ticker} does not have any contracts",
        }

    # Output Data
    df_contracts["Date"] = pd.to_datetime(df_contracts["Date"]).dt.date

    df_contracts = df_contracts[
        df_contracts["Date"].isin(df_contracts["Date"].unique()[:past_transaction_days])
    ]

    df_contracts.drop_duplicates(inplace=True)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    df_contracts.groupby("Date").sum().div(1000).plot(kind="bar", rot=0, ax=ax)
    ax.set_ylabel("Amount ($1k)")
    ax.set_title(f"Sum of latest government contracts to {ticker}")
    fig.tight_layout()

    plt.savefig("gov_contracts.png")
    imagefile = "gov_contracts.png"

    imagefile = image_border(imagefile)
    return {
        "title": f"Stocks: [quiverquant.com] Contracts by {ticker}",
        "imagefile": imagefile,
    }
