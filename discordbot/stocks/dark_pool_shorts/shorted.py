import disnake
from menus.menu import Menu

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_model


async def shorted_command(ctx, num: int = 10):
    """Show most shorted stocks [Yahoo Finance]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dps.shorted %s", num)

        # Check for argument
        if num < 0:
            raise Exception("Number has to be above 0")

        # Retrieve data
        df = yahoofinance_model.get_most_shorted().head(num)

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df.to_string())

        # Output data
        df.dropna(how="all", axis=1, inplace=True)
        df = df.replace(float("NaN"), "")
        future_column_name = df["Symbol"]
        df = df.transpose()
        df.columns = future_column_name
        df.drop("Symbol")
        columns = []
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

        columns.append(
            disnake.Embed(
                title="Stocks: [Yahoo Finance] Most Shorted",
                description=initial_str,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        for column in df.columns.values:
            columns.append(
                disnake.Embed(
                    description="```" + df[column].fillna("").to_string() + "```",
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        await ctx.send(embed=columns[0], view=Menu(columns, choices))

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: [Yahoo Finance] Most Shorted",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
