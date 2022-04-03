import logging

import disnake
import pandas as pd

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.government import quiverquant_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def lastcontracts_command(past_transactions_days: int = 2, num: int = 20):
    """Displays last government contracts [quiverquant.com]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("gov lastcontracts %s %s", past_transactions_days, num)

    df_contracts = quiverquant_model.get_government_trading("contracts")

    if df_contracts.empty:
        logger.debug("No government contracts found")
        raise Exception("No government contracts found")

    df_contracts.sort_values("Date", ascending=False)

    df_contracts["Date"] = pd.to_datetime(df_contracts["Date"])
    df_contracts["Date"] = df_contracts["Date"].dt.date

    df_contracts.drop_duplicates(inplace=True)
    df_contracts = df_contracts[
        df_contracts["Date"].isin(
            df_contracts["Date"].unique()[:past_transactions_days]
        )
    ]

    df_contracts = df_contracts[["Date", "Ticker", "Amount", "Agency"]][:num]
    choices = [
        disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
    ]
    title = "Stocks: [quiverquant.com] Top buy government trading"
    initial_str = "Overview"
    i = 1
    for col_name in df_contracts["Ticker"].values:
        menu = f"\nPage {i}: {col_name}"
        initial_str += f"\nPage {i}: {col_name}"
        choices.append(
            disnake.SelectOption(label=menu, value=f"{i}", emoji="🟢"),
        )
        i += 1

    embeds = []
    df_contracts = df_contracts.T
    reports = [f"{initial_str}"]
    embeds.append(
        disnake.Embed(
            title=title,
            description=initial_str,
            colour=imps.COLOR,
        ).set_author(
            name=imps.AUTHOR_NAME,
            icon_url=imps.AUTHOR_ICON_URL,
        )
    )
    for column in df_contracts.columns.values:
        description = "```" + df_contracts[column].fillna("").to_string() + "```"
        embeds.append(
            disnake.Embed(description=description, colour=imps.COLOR,).set_author(
                name=imps.AUTHOR_NAME,
                icon_url=imps.AUTHOR_ICON_URL,
            )
        )
        reports.append(f"{description}")

    return {
        "view": imps.Menu,
        "title": title,
        "description": reports,
        "embed": embeds,
        "choices": choices,
    }
