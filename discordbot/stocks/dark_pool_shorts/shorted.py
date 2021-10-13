import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_model


async def shorted_command(ctx, arg="5"):
    try:
        # Debug
        if cfg.DEBUG:
            print(f"!stocks.dps.shorted {arg}")

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
            try:
                # Parse argument
                num = int(arg)
                if num < 0:
                    raise ValueError("Number has to be above 0")
            except ValueError:
                title = "ERROR Stocks: [Yahoo Finance] Most Shorted"
                embed = discord.Embed(title=title, colour=cfg.COLOR)
                embed.set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                embed.set_description(
                    "No number (int) entered."
                    "\nEnter a valid (positive) number, example: 10"
                )
                await ctx.send(embed=embed)
                if cfg.DEBUG:
                    print("ERROR: No (positive) int entered")
                return

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

    except Exception as e:
        title = "INTERNAL ERROR"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_description(
            "Try updating the bot, make sure DEBUG is True in the config "
            "and restart it.\nIf the error still occurs open a issue at: "
            "https://github.com/GamestonkTerminal/GamestonkTerminal/issues"
            f"\n{e}"
        )
        await ctx.send(embed=embed)
        if cfg.DEBUG:
            print(e)
