import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


async def sidtc_command(ctx, arg, arg2):
    try:
        # Debug
        if cfg.DEBUG:
            print("-- STARTED COMMAND: !stocks.dps.sidtc " + arg + " " + arg2 + " --")

        # Help
        if arg == "-h" or arg == "help":
            dark_pool_sort = {
                "float": "Float Short %",
                "dtc": "Days to Cover",
                "si": "Short Interest",
            }

            help_txt = "Get short interest and days to cover. [Source: Stockgrid]\n"

            possible_args = ""
            for k, v in dark_pool_sort.items():
                possible_args += f"\n{k}: {v}"

            help_txt += "\nPossible arguments:\n"
            help_txt += "<SORT> Field for which to sort by. Default: float\n"
            help_txt += f"The choices are:{possible_args}\n"
            help_txt += "<NUM> Number of top tickers to show. Default: 10"

            embed = discord.Embed(
                title="Stocks: [Stockgrid] Short Interest and Days to Cover HELP",
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
                arg = "float"
            if not arg2:
                arg2 = "10"

            # Parse argument
            if arg == "float" or arg == "dtc" or arg == "si":
                sort = arg
            else:
                title = "ERROR Stocks: [Stockgrid] Short Interest and Days to Cover"
                embed = discord.Embed(title=title, colour=cfg.COLOR)
                embed.set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                embed.set_description(
                    "Entered sort argument: "
                    + arg
                    + "\nEnter a valid sort argument, example: float"
                )
                if cfg.DEBUG:
                    print(
                        "-- ERROR at COMMAND: !stocks.dps.sidtc "
                        + arg
                        + " "
                        + arg2
                        + " --"
                    )
                    print("   ERROR: Bad sort argument entered")
                    print("-- Command stopped before error --")
                return

            try:
                num = int(arg2)
                if num < 0:
                    raise ValueError("Number has to be above 0")
            except ValueError:
                title = "ERROR Stocks: [Stockgrid] Short Interest and Days to Cover"
                embed = discord.Embed(title=title, colour=cfg.COLOR)
                embed.set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                embed.set_description(
                    "No number (int) entered in the second argument."
                    "\nEnter a valid (positive) number, example: 10"
                )
                if cfg.DEBUG:
                    print(
                        "-- ERROR at COMMAND: !stocks.dps.sidtc "
                        + arg
                        + " "
                        + arg2
                        + " --"
                    )
                    print("   ERROR: No (positive) int for second argument entered")
                    print("-- Command stopped before error --")
                return

            df = stockgrid_model.get_short_interest_days_to_cover(sort)
            df = df.iloc[:num]
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
            columns = []
            initial_str = "Page 0: Overview"
            i = 1
            for column in df.columns.values:
                initial_str = initial_str + "\nPage " + str(i) + ": " + column
                i += 1
            columns.append(
                discord.Embed(
                    title="Dark Pool Shorts", description=initial_str, colour=cfg.COLOR
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )
            for column in df.columns.values:
                columns.append(
                    discord.Embed(
                        title="Stocks: [Stockgrid] Short Interest and Days to Cover",
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
        )
        if cfg.DEBUG:
            print("-- ERROR at COMMAND: !stocks.dps.sidtc " + arg + " " + arg2 + " --")
            print(
                "   Try updating the bot and restart it. If the error still occurs open "
                "a issue at:\n   https://github.com/GamestonkTerminal/GamestonkTerminal/issues"
            )
            print("-- DETAILED REPORT: --\n\n" + e + "\n")
