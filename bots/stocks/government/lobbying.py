from typing import Any, Dict
import disnake

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.menus.menu import Menu
from gamestonk_terminal.stocks.government import quiverquant_model


def lobbying_command(ticker="", num: int = 10):
    """Displays lobbying details [quiverquant.com]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("gov-lobbying %s", ticker)

    if ticker == "":
        raise Exception("A ticker is required")

    # Retrieve Data
    df_lobbying = quiverquant_model.get_government_trading(
        "corporate-lobbying", ticker=ticker
    )

    if df_lobbying.empty:
        logger.debug("No corporate lobbying found")
        raise Exception("No corporate lobbying found")

    # Output Data
    report = ""
    title = (f"Stocks: [quiverquant.com] {ticker.upper()} Lobbying Details",)
    choices = [
        disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
    ]
    for _, row in (
        df_lobbying.sort_values(by=["Date"], ascending=False).head(num).iterrows()
    ):
        amount = (
            "$" + str(int(float(row["Amount"]))) if row["Amount"] is not None else "N/A"
        )
        report += f"{row['Date']}: {row['Client']} {amount}"
        if row["Amount"] is not None:
            report += "\t" + row["Specific_Issue"].replace("\n", " ").replace("\r", "")
        report += "\n"

    if len(report) <= 4000:
        description = f"```{report}```"
        embed = disnake.Embed(
            title=title,
            description=description,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        output: Dict[str, Any] = {
            "title": title,
            "description": description,
        }
    else:
        i = 0
        str_start = 0
        str_end = 4000
        embeds = []
        reports = []
        while i <= len(report) / 4000:
            descript = f"```{report[str_start:str_end]}```"
            embeds.append(
                disnake.Embed(
                    title=title,
                    description=descript,
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )
            reports.append(f"{descript}")
            str_end = str_start
            str_start += 4000
            i += 1

            output = {
                "view": Menu,
                "title": title,
                "description": reports,
                "embed": embeds,
                "choices": choices,
            }

    return output
