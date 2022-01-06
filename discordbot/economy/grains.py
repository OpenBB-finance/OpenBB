import discord
import pandas as pd

from gamestonk_terminal.economy import finviz_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import logger


async def grains_command(ctx):
    """Displays grains futures data [Finviz]"""

    try:
        # Retrieve data
        d_futures = finviz_model.get_futures()

        df = pd.DataFrame(d_futures["Grains"])
        df = df.set_index("label")
        df = df.sort_values(by="ticker", ascending=False)

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df.to_string())

        # Output data
        if df.empty:
            df_str = "No available grains futures data"
        else:
            df_str = (
                df[["prevClose", "last", "change"]].fillna("").to_string(index=True)
            )

        embed = discord.Embed(
            title="Economy: [Finviz] Grains Futures",
            description="```" + df_str + "```",
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Economy: [Finviz] Grains Futures",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
