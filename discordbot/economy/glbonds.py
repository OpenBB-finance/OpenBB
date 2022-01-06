import discord

from gamestonk_terminal.economy import wsj_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import logger


async def glbonds_command(ctx):
    """Global bonds overview [Wall St. Journal]"""

    try:
        # Retrieve data
        df_data = wsj_model.global_bonds()

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df_data.to_string())

        # Output data
        if df_data.empty:
            df_data_str = "No global bonds data available"
        else:
            df_data_str = "```" + df_data.to_string(index=False) + "```"

        embed = discord.Embed(
            title="Economy: [WSJ] Global Bonds",
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
            title="ERROR Economy: [WSJ] Global Bonds",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
