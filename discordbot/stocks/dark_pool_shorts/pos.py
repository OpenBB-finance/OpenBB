import disnake
from menus.menu import Menu

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


async def pos_command(ctx, sort="dpp_dollar", num: int = 10):
    """Dark pool short position [Stockgrid]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dps.pos %s %s", sort, num)

        # Check for argument
        possible_sorts = ("sv", "sv_pct", "nsv", "nsv_dollar", "dpp", "dpp_dollar")

        if sort not in possible_sorts:
            raise Exception(f"The possible sorts are: {', '.join(possible_sorts)}")

        if num < 0:
            raise Exception("Number has to be above 0")

        # Retrieve data
        df = stockgrid_model.get_dark_pool_short_positions(sort, False)
        df = df.iloc[:num]

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df.to_string())

        # Output data
        dp_date = df["Date"].values[0]
        df = df.drop(columns=["Date"])
        df["Net Short Volume $"] = df["Net Short Volume $"] / 100_000_000
        df["Short Volume"] = df["Short Volume"] / 1_000_000
        df["Net Short Volume"] = df["Net Short Volume"] / 1_000_000
        df["Short Volume %"] = df["Short Volume %"] * 100
        df["Dark Pools Position $"] = df["Dark Pools Position $"] / (1_000_000_000)
        df["Dark Pools Position"] = df["Dark Pools Position"] / 1_000_000
        df.columns = [
            "Ticker",
            "Short Vol. (1M)",
            "Short Vol. %",
            "Net Short Vol. (1M)",
            "Net Short Vol. ($100M)",
            "DP Position (1M)",
            "DP Position ($1B)",
        ]
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
                title="Stocks: [Stockgrid] Dark Pool Short Position",
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
                    title="High Short Interest",
                    description="```The following data corresponds to the date: "
                    + dp_date
                    + "\n\n"
                    + df[column].fillna("").to_string()
                    + "```",
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        await ctx.send(embed=columns[0], view=Menu(columns, choices))

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: [Stockgrid] Dark Pool Short Position",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
