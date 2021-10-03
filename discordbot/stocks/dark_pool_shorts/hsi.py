import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.dark_pool_shorts import shortinterest_model


async def hsi_command(ctx, arg="10"):
    try:
        # Debug
        if cfg.DEBUG:
            print(f"!stocks.dps.hsi {arg}")

        # Help
        if arg == "-h" or arg == "help":
            help_txt = "Display top high shorted interest stocks [Source: highshortinterest.com]\n"
            help_txt += "\nPossible arguments:\n"
            help_txt += "<NUM> Number of stocks to display. Default: 10"
            embed = discord.Embed(
                title="Stocks: [highshortinterest.com] Top High Short Interest HELP",
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
                title = "ERROR Stocks: [SEC] Failure-to-deliver"
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

            df = shortinterest_model.get_high_short_interest()
            df = df.iloc[1:].head(n=num)

            future_column_name = df["Ticker"]
            df = df.transpose()
            df.columns = future_column_name
            df.drop("Ticker")
            columns = []
            initial_str = "Page 0: Overview"
            i = 1
            for column in df.columns.values:
                initial_str = initial_str + "\nPage " + str(i) + ": " + column
                i += 1
            columns.append(
                discord.Embed(
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
                    discord.Embed(
                        title="Stocks: [highshortinterest.com] Top High Short Interest",
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
