import os

import df2img
import disnake
import numpy as np
from PIL import Image

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import autocrop_image, quote


async def quote_command(ctx, ticker: str = None):
    """Ticker Quote"""

    try:
        # Debug
        if cfg.DEBUG:
            logger.debug("quote %s", ticker)

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")

        df = quote(ticker)
        fig = df2img.plot_dataframe(
            df,
            fig_size=(600, 1500),
            col_width=[2, 3],
            tbl_cells=dict(
                align="left",
                height=35,
            ),
            template="plotly_dark",
            font=dict(
                family="Consolas",
                size=20,
            ),
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = f"quote{np.random.randint(69420)}.png"
        df2img.save_dataframe(fig=fig, filename=imagefile)
        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)
        image = disnake.File(imagefile)
        title = f"{ticker.upper()} Quote"
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(url=f"attachment://{imagefile}")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        os.remove(imagefile)

        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Quote",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
