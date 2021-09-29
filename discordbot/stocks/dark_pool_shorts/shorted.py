import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_model


async def shorted_command(ctx, arg):
    # Help
    if arg == "-h" or arg == "help":
        help_txt = "Display most shorted stocks screener. [Source: Yahoo Finance]\n"
        help_txt += "\nPossible arguments:\n"
        help_txt += "<NUM> Number of stocks to display. Default: 5"
        embed = discord.Embed(
            title="Stocks: [Yahoo Finance] Most Shorted HELP",
            description=help_txt,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    else:
        # Select default
        if not arg:
            arg = "5"

        # Parse argument
        num = int(arg)

        df = yahoofinance_model.get_most_shorted().head(num)

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
