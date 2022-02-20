import disnake

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.menus.menu import Menu
from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_model


def shorted_command(num: int = 10):
    """Show most shorted stocks [Yahoo Finance]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dps-shorted %s", num)

    # Check for argument
    if num < 0:
        raise Exception("Number has to be above 0")

    # Retrieve data
    df = yahoofinance_model.get_most_shorted().head(num)

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df.to_string())

    # Output data
    title = "Stocks: [Yahoo Finance] Most Shorted"
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")
    future_column_name = df["Symbol"]
    df = df.transpose()
    df.columns = future_column_name
    df.drop("Symbol")
    embeds = []
    choices = [
        disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
    ]
    initial_str = "Overview"
    i = 1
    for col_name in df.columns.values:
        menu = f"\nPage {i}: {col_name}"
        initial_str += f"\nPage {i}: {col_name}"
        if i < 19:
            choices.append(
                disnake.SelectOption(label=menu, value=f"{i}", emoji="🟢"),
            )
        if i == 20:
            choices.append(
                disnake.SelectOption(label="Max Reached", value=f"{i}", emoji="🟢"),
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
