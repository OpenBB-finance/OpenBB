import io
import logging
from datetime import datetime, timedelta

import pandas as pd
from matplotlib import pyplot as plt

from bots import imps
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale
from openbb_terminal.stocks.government import quiverquant_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def topbuys_command(
    gov_type="",
    past_transactions_months: int = 5,
    num: int = 20,
    raw: bool = False,
):
    """Displays most purchased stocks by the congress/senate/house [quiverquant.com]"""
    # Debug user input
    if imps.DEBUG:
        logger.debug(
            "gov-topbuys %s %s %s %s",
            gov_type,
            past_transactions_months,
            num,
            raw,
        )

    possible_args = ["congress", "senate", "house"]
    if gov_type == "":
        gov_type = "congress"
    elif gov_type not in possible_args:
        raise Exception(
            "Enter a valid government argument, options are: congress, senate and house"
        )

    # Retrieve Data
    df_gov = quiverquant_model.get_government_trading(gov_type)

    if df_gov.empty:
        logger.debug("No %s trading data found", gov_type)
        raise Exception("No trading data found")

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)
    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna()
    # Catch bug where error shown for purchase of >5,000,000
    df_gov["Range"] = df_gov["Range"].apply(
        lambda x: "$5,000,001-$5,000,001" if x == ">$5,000,000" else x
    )
    df_gov["min"] = df_gov["Range"].apply(
        lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
    )
    df_gov["max"] = df_gov["Range"].apply(
        lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
        if "-" in x
        else x.strip("$").replace(",", "")
    )
    df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["min"])
        if x["Transaction"] == "Purchase"
        else -float(x["max"]),
        axis=1,
    )
    df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["max"])
        if x["Transaction"] == "Purchase"
        else -float(x["min"]),
        axis=1,
    )
    description = None

    df_gov = df_gov.sort_values("TransactionDate", ascending=True)
    if raw:
        df = pd.DataFrame(
            df_gov.groupby("Ticker")["upper"]
            .sum()
            .div(1000)
            .sort_values(ascending=False)
            .head(n=num)
        )
        description = "```" + df.to_string() + "```"

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values(ascending=False).head(
        n=num
    ).plot(kind="bar", rot=0, ax=ax)

    ax.set_ylabel("Amount [1k $]")
    ax.set_title(
        f"Top {num} purchased stocks over last {past_transactions_months} "
        f"months (upper bound) for {gov_type.upper()}"
    )
    plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
    fig.tight_layout()
    imagefile = "gov_topbuys.png"

    dataBytesIO = io.BytesIO()
    plt.savefig(dataBytesIO)
    dataBytesIO.seek(0)
    plt.close("all")

    imagefile = imps.image_border(imagefile, base64=dataBytesIO)

    return {
        "title": f"Stocks: [quiverquant.com] Top purchases for {gov_type.upper()}",
        "imagefile": imagefile,
        "description": description,
    }
