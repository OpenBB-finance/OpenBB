import logging

import disnake

import bots.config_discordbot as cfg
from bots.menus.menu import Menu
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def sidtc_command(sort="float", num: int = 10):
    """Short interest and days to cover [Stockgrid]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("dps-sidtc %s %s", sort, num)

    # Check for argument
    possible_sorts = ("float", "dtc", "si")

    if sort not in possible_sorts:
        raise Exception(f"The possible sorts are: {', '.join(possible_sorts)}")

    if num < 0:
        raise Exception("Number has to be above 0")

    # Retrieve data
    df = stockgrid_model.get_short_interest_days_to_cover(sort)
    df = df.iloc[:num]

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df.to_string())

    # Output data
    title = "Stocks: [Stockgrid] Short Interest and Days to Cover"
    dp_date = df["Date"].values[0]
    df = df.drop(columns=["Date"])
    df["Short Interest"] = df["Short Interest"] / 1_000_000
    df.head()
    df.columns = [
        "Ticker",
        "Float Short %",
        "Days to Cover",
        "Short Interest (1M)",
    ]
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
            title="Dark Pool Shorts", description=initial_str, colour=cfg.COLOR
        ).set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
    )

    for column in df.columns.values:
        description = (
            "```The following data corresponds to the date: "
            + dp_date
            + "\n\n"
            + df[column].fillna("").to_string()
            + "```",
        )
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
