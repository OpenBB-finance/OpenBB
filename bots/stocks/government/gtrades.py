import io
import logging
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt

from bots import imps
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def gtrades_command(
    ticker: str = "",
    gov_type="",
    past_transactions_months: int = 10,
    raw: bool = False,
):
    """Displays government trades [quiverquant.com]"""
    # Debug user input
    if imps.DEBUG:
        logger.debug(
            "gov gtrades %s %s %s %s",
            ticker,
            gov_type,
            past_transactions_months,
            raw,
        )

    if ticker == "":
        raise Exception("A ticker is required")

    possible_args = ["congress", "senate", "house"]
    if gov_type == "":
        gov_type = "congress"
    elif gov_type not in possible_args:
        raise Exception(
            "Enter a valid government argument, options are: congress, senate and house"
        )

    # Retrieve Data
    df_gov = quiverquant_model.get_government_trading(gov_type, ticker)

    if df_gov.empty:
        raise Exception(f"No {gov_type} trading data found")

    # Output Data
    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date]

    if df_gov.empty:
        logger.debug("No recent %s trading data found", gov_type)
        raise Exception(f"No recent {gov_type} trading data found")

    df_gov["min"] = df_gov["Range"].apply(
        lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
    )
    df_gov["max"] = df_gov["Range"].apply(
        lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
        if "-" in x
        else x.strip("$").replace(",", "").split("\n")[0]
    )

    df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: int(float(x["min"]))
        if x["Transaction"] == "Purchase"
        else -int(float(x["max"])),
        axis=1,
    )
    df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: int(float(x["max"]))
        if x["Transaction"] == "Purchase"
        else -1 * int(float(x["min"])),
        axis=1,
    )

    df_gov = df_gov.sort_values("TransactionDate", ascending=True)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.fill_between(
        df_gov["TransactionDate"].unique(),
        df_gov.groupby("TransactionDate")["lower"].sum().values / 1000,
        df_gov.groupby("TransactionDate")["upper"].sum().values / 1000,
    )

    ax.set_xlim(
        [
            df_gov["TransactionDate"].values[0],
            df_gov["TransactionDate"].values[-1],
        ]
    )
    ax.grid()
    ax.set_title(f"{gov_type.capitalize()} trading on {ticker}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount ($1k)")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
    plt.gcf().autofmt_xdate()
    fig.tight_layout()
    imagefile = "gov_gtrades.png"

    dataBytesIO = io.BytesIO()
    plt.savefig(dataBytesIO)
    dataBytesIO.seek(0)
    plt.close("all")

    imagefile = imps.image_border(imagefile, base64=dataBytesIO)

    return {
        "title": "Stocks: [quiverquant.com] Government Trades",
        "imagefile": imagefile,
    }
