import discord

from gamestonk_terminal.stocks.due_diligence import marketwatch_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import logger


async def sec_command(ctx, ticker=""):
    """Displays sec filings [Market Watch]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dd.sec %s", ticker)

        if ticker == "":
            raise Exception("A ticker is required")

        df_financials = marketwatch_model.get_sec_filings(ticker)

        if df_financials.empty:
            raise Exception("Enter a valid ticker")

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df_financials.to_string())

        # Output data
        report = "```" + df_financials.to_string() + "```"
        embed = discord.Embed(
            title="Stocks: [Market Watch] SEC Filings",
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
            title="ERROR Stocks: [Market Watch] SEC Filings",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
