import discord
from tabulate import tabulate

import discordbot.config_discordbot as cfg
from gamestonk_terminal.stocks.options import barchart_model


async def iv_command(ctx, ticker: str = None):
    """Options IV"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.opt.iv {ticker}")

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")

        df = barchart_model.get_options_info(ticker)
        tickerr = ticker.upper()

        report = "```" + tabulate(df, tablefmt="fancy_grid", showindex=False) + "```"
        embed = discord.Embed(
            title=" " + tickerr.__str__() + " Options: IV",
            description=report,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Options: IV",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
