import disnake
import pandas as pd

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.menus.menu import Menu
from gamestonk_terminal.stocks.government import quiverquant_model


def lastcontracts_command(past_transactions_days: int = 2, num: int = 20):
    """Displays last government contracts [quiverquant.com]"""

    # Debug user input
    if cfg.DEBUG:
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
            colour=cfg.COLOR,
        ).set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
    )
    for column in df_contracts.columns.values:
        description = "```" + df_contracts[column].fillna("").to_string() + "```"
        embeds.append(
            disnake.Embed(description=description, colour=cfg.COLOR,).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        reports.append(f"{description}")

    return {
        "view": Menu,
        "title": title,
        "description": reports,
        "embed": embeds,
        "choices": choices,
    }
