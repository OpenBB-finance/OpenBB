import disnake

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.stocks.screener import screener_options as so


async def presets_custom_command(ctx):
    """Displays every custom preset"""
    try:

        # Debug
        if cfg.DEBUG:
            logger.debug("!stocks.scr.presets")

        description = ""
        for preset in so.presets:
            with open(
                so.presets_path + preset + ".ini",
                encoding="utf8",
            ) as f:
                preset_line = ""
                for line in f:
                    if line.strip() == "[General]":
                        break
                    preset_line += line.strip()
            description += f"**{preset}:** *{preset_line.split('Description: ')[1].replace('#', '')}*\n"

        embed = disnake.Embed(
            title="Stocks: Screener Custom Presets",
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
