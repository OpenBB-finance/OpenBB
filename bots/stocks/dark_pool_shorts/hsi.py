import disnake

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.menus.menu import Menu
from gamestonk_terminal.stocks.dark_pool_shorts import shortinterest_model


def hsi_command(num: int = 10):
    """Show top high short interest stocks of over 20% ratio [shortinterest.com]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dps-hsi %s", num)

    # Check for argument
    if num < 0:
        raise Exception("Number has to be above 0")

    # Retrieve data
    df = shortinterest_model.get_high_short_interest()
    df = df.iloc[1:].head(n=num)

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df.to_string())

    # Output data
    title = "Stocks: [highshortinterest.com] Top High Short Interest"

    future_column_name = df["Ticker"]
    df = df.transpose()
    df.columns = future_column_name
    df.drop("Ticker")
    embeds = []
    choices = [
        disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
    ]
    initial_str = "Overview"
    i = 1
    for col_name in df.columns.values:
        menu = f"\nPage {i}: {col_name}"
        initial_str += f"\nPage {i}: {col_name}"
        choices.append(
            disnake.SelectOption(label=menu, value=f"{i}", emoji="🟢"),
        )
        i += 1

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
    for column in df.columns.values:
        description = "```" + df[column].fillna("").to_string() + "```"
        embeds.append(
            disnake.Embed(
                title=title,
                description=description,
                colour=cfg.COLOR,
            ).set_author(
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
