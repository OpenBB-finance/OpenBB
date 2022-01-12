import discord

from gamestonk_terminal.stocks.due_diligence import csimarket_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import logger


async def customer_command(ctx, ticker=""):
    """Displays customers of the company [CSIMarket]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dd.customer %s", ticker)

        if ticker == "":
            raise Exception("A ticker is required")

        tickers = csimarket_model.get_customers(ticker)

        if tickers == "":
            raise Exception("Enter a valid ticker")

        # Debug user output
        if cfg.DEBUG:
            logger.debug(tickers)

        # Output data
        embed = discord.Embed(
            title="Stocks: [CSIMarket] Company Customers",
            description=tickers,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [CSIMarket] Company Customers",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
