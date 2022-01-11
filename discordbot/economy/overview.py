import discord

from gamestonk_terminal.economy import wsj_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import logger


async def overview_command(ctx):
    """Market data overview [Wall St. Journal]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!economy.overview")

        # Retrieve data
        df_data = wsj_model.market_overview()

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df_data.to_string())

        # Output data
        if df_data.empty:
            df_data_str = "No overview data available"
        else:
            df_data_str = "```" + df_data.to_string(index=False) + "```"

        embed = discord.Embed(
            title="Economy: [WSJ] Market Overview",
            description=df_data_str,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Economy: [WSJ] Market Overview",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
