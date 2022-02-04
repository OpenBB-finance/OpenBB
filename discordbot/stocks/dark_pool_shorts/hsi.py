import disnake
from menus.menu import Menu

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from gamestonk_terminal.stocks.dark_pool_shorts import shortinterest_model


async def hsi_command(ctx, num: int = 10):
    """Show top high short interest stocks of over 20% ratio [shortinterest.com]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dps.hsi %s", num)

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
        future_column_name = df["Ticker"]
        df = df.transpose()
        df.columns = future_column_name
        df.drop("Ticker")
        columns = []
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
        columns.append(
            disnake.Embed(
                title="Stocks: [highshortinterest.com] Top High Short Interest",
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
                    title="Stocks: [highshortinterest.com] Top High Short Interest",
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
            title="ERROR Stocks: [highshortinterest.com] Top High Short Interest",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
