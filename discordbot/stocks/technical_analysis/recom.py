import discord

from gamestonk_terminal.stocks.technical_analysis import tradingview_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import logger


async def recom_command(ctx, ticker=""):
    """Displays text of a given stocks recommendation based on ta [Tradingview API]"""

    try:

        # Debug
        if cfg.DEBUG:
            logger.debug("!stocks.ta.recom %s", ticker)

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        recom = tradingview_model.get_tradingview_recommendation(
            ticker, "america", "", ""
        )

        recom = recom[["BUY", "NEUTRAL", "SELL", "RECOMMENDATION"]]

        report = "```" + recom.to_string() + "```"
        embed = discord.Embed(
            title="Stocks: [Tradingview API] Recommendation based on TA",
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
            title="ERROR Stocks: [Tradingview API] Recommendation based on TA",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
