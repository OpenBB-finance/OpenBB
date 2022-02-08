import disnake

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.stocks.screener import screener_options as so


async def presets_default_command(ctx):
    """Displays default presets"""
    try:

        # Debug
        if cfg.DEBUG:
            logger.debug("!stocks.scr.presets")

        description = ""
        for signame, sigdesc in so.d_signals_desc.items():
            description += f"**{signame}:** *{sigdesc}*\n"
        embed = disnake.Embed(
            title="Stocks: Screener Default Presets",
            description=description,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: Screener Presets",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
