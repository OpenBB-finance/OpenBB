import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_model


async def shorted_command(ctx, num="10"):
    """Show most shorted stocks [Yahoo Finance]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"\n!stocks.dps.shorted {num}")

        # Check for argument
        if not num.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")

        num = int(num)

        if num < 0:
            raise Exception("Number has to be above 0")

        # Retrieve data
        df = yahoofinance_model.get_most_shorted().head(num)

        # Debug user output
        if cfg.DEBUG:
            print(df.to_string())

        # Output data
        df.dropna(how="all", axis=1, inplace=True)
        df = df.replace(float("NaN"), "")
        future_column_name = df["Symbol"]
        df = df.transpose()
        df.columns = future_column_name
        df.drop("Symbol")
        columns = []

        initial_str = "Page 0: Overview"
        i = 1

        for col_name in df.columns.values:
            initial_str += f"\nPage {i}: {col_name}"
            i += 1

        columns.append(
            discord.Embed(
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
                discord.Embed(
                    description="```" + df[column].fillna("").to_string() + "```",
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        await pagination(columns, ctx)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [Yahoo Finance] Most Shorted",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
